"""Concurrent job-board fetcher.
 
Reads companies from a CSV, fetches their public job boards concurrently
(Greenhouse, Lever, Ashby, SmartRecruiters, Workable), retries transient
failures with backoff, normalizes every platform into one job schema,
and saves the results as JSON.
 
Usage:
    uv run day1project companies.csv -o jobs.json --keywords "data engineer,python"
"""
 
from __future__ import annotations
 
import argparse
import asyncio
import csv
import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypedDict
 
import aiohttp
 
# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
 
PLATFORMS = {"greenhouse", "lever", "ashby", "smartrecruiters", "workable"}
 
# Statuses worth retrying: rate limited (429) or the server is having trouble (5xx).
# Anything else (404, 403, ...) won't fix itself, so we stop immediately.
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
 
SMARTRECRUITERS_PAGE_SIZE = 100
USER_AGENT = "day1project-job-fetcher/0.1 (personal job-search tool)"
 
 
# --------------------------------------------------------------------------
# Data shapes
# --------------------------------------------------------------------------
 
class Company(TypedDict):
    name: str
    platform: str
    token: str
 
 
class FetchResult(TypedDict):
    url: str
    status: int | None
    attempts: int
    data: Any
    error: str | None
 
 
class Job(TypedDict):
    """One job posting, in the same shape no matter which platform it came from."""
    company: str
    platform: str
    title: str
    location: str | None
    department: str | None
    remote: bool | None
    url: str
    posted_at: str | None
    salary: str | None
 
 
class CompanyResult(TypedDict):
    """What happened when fetching one company. Saved to the run report."""
    company: str
    platform: str
    url: str
    status: int | None
    attempts: int
    error: str | None
    job_count: int
 
 
# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------
 
def read_companies(path: Path) -> list[Company]:
    """Read companies.csv (columns: name, platform, token)."""
    companies: list[Company] = []
    with path.open(newline="", encoding="utf-8") as f:
        # line 1 is the header, so data rows start at line 2
        for line_number, row in enumerate(csv.DictReader(f), start=2):
            name = (row.get("name") or "").strip()
            platform = (row.get("platform") or "").strip().lower()
            # Keep the token's case: SmartRecruiters IDs are case-sensitive.
            token = (row.get("token") or "").strip()
 
            if not (name or platform or token):
                continue  # skip blank lines
            if platform not in PLATFORMS:
                raise SystemExit(
                    f"{path}:{line_number}: unknown platform {platform!r} "
                    f"(expected one of: {', '.join(sorted(PLATFORMS))})"
                )
            if not token:
                raise SystemExit(f"{path}:{line_number}: missing token for {name!r}")
 
            companies.append({"name": name, "platform": platform, "token": token})
    return companies
 
 
def build_url(platform: str, token: str, offset: int = 0) -> str:
    """Build the public job-board API URL for one company."""
    match platform:
        case "greenhouse":
            return f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        case "lever":
            return f"https://api.lever.co/v0/postings/{token}?mode=json"
        case "ashby":
            return f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true"
        case "smartrecruiters":
            return (
                f"https://api.smartrecruiters.com/v1/companies/{token}/postings"
                f"?limit={SMARTRECRUITERS_PAGE_SIZE}&offset={offset}"
            )
        case "workable":
            return f"https://apply.workable.com/api/v1/widget/accounts/{token}?details=true"
        case _:
            raise ValueError(f"Unknown platform: {platform!r}")
 
 
# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------
 
def _result(url: str, status: int | None, attempts: int,
            data: Any = None, error: str | None = None) -> FetchResult:
    return {"url": url, "status": status, "attempts": attempts, "data": data, "error": error}
 
 
async def fetch_json(session: aiohttp.ClientSession, sem: asyncio.Semaphore,
                     url: str, retries: int) -> FetchResult:
    """GET one URL and parse JSON, retrying transient failures with backoff.
 
    The semaphore is held only while a request is in flight, never while
    sleeping between retries, so other URLs can use the slot during backoff.
    """
    last = _result(url, None, 0, error="NotAttempted")
 
    for attempt in range(1, retries + 1):
        should_retry = False
        try:
            async with sem:
                async with session.get(url) as response:
                    if response.status in RETRYABLE_STATUSES:
                        last = _result(url, response.status, attempt, error=f"HTTP {response.status}")
                        should_retry = True
                    elif response.status != 200:
                        # 404 and friends: retrying won't help.
                        return _result(url, response.status, attempt, error=f"HTTP {response.status}")
                    else:
                        data = await response.json()
                        return _result(url, 200, attempt, data=data)
 
        # ContentTypeError: a 200 that wasn't JSON (Lever occasionally does this). Worth a retry.
        # Must come before ClientError, because it's a subclass of it.
        except (TimeoutError, aiohttp.ContentTypeError, aiohttp.ClientConnectionError) as e:
            last = _result(url, None, attempt, error=type(e).__name__)
            should_retry = True
        except aiohttp.ClientError as e:
            return _result(url, None, attempt, error=type(e).__name__)
        except ValueError:
            # Content-Type said JSON but the body wasn't valid JSON.
            return _result(url, 200, attempt, error="InvalidJSON")
 
        # Outside the semaphore and the connection: safe to wait.
        if should_retry and attempt < retries:
            backoff = 2 ** (attempt - 1)              # 1s, 2s, 4s, ...
            jitter = random.uniform(0, 0.5)           # spreads out simultaneous retries
            await asyncio.sleep(backoff + jitter)
 
    return last
 
 
async def fetch_company(session: aiohttp.ClientSession, sem: asyncio.Semaphore,
                        company: Company, retries: int) -> tuple[CompanyResult, list[Job]]:
    """Fetch one company's board (all pages, for SmartRecruiters) and normalize it."""
    name, platform, token = company["name"], company["platform"], company["token"]
    first = await fetch_json(session, sem, build_url(platform, token), retries)
 
    pages: list[Any] = []
    error = first["error"]
 
    if error is None:
        pages.append(first["data"])
 
        # SmartRecruiters is the only platform here that paginates.
        if platform == "smartrecruiters":
            total = int(first["data"].get("totalFound", 0) or 0)
            offsets = range(SMARTRECRUITERS_PAGE_SIZE, total, SMARTRECRUITERS_PAGE_SIZE)
            more = await asyncio.gather(
                *(fetch_json(session, sem, build_url(platform, token, off), retries) for off in offsets)
            )
            failed_pages = [p for p in more if p["error"] is not None]
            pages.extend(p["data"] for p in more if p["error"] is None)
            if failed_pages:
                error = f"Partial: {len(failed_pages)} of {len(more) + 1} pages failed"
 
    jobs: list[Job] = []
    try:
        for page in pages:
            jobs.extend(NORMALIZERS[platform](name, token, page))
    except (KeyError, TypeError, AttributeError) as e:
        # The response didn't have the shape we expected.
        error = f"UnexpectedShape: {type(e).__name__}"
        jobs = []
 
    result: CompanyResult = {
        "company": name,
        "platform": platform,
        "url": first["url"],
        "status": first["status"],
        "attempts": first["attempts"],
        "error": error,
        "job_count": len(jobs),
    }
    return result, jobs
 
 
async def fetch_all(companies: list[Company], retries: int, timeout: float,
                    concurrency: int) -> tuple[list[CompanyResult], list[Job]]:
    """Fetch every company concurrently, sharing one session and one semaphore."""
    sem = asyncio.Semaphore(concurrency)
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
 
    async with aiohttp.ClientSession(timeout=client_timeout, headers=headers) as session:
        outcomes = await asyncio.gather(
            *(fetch_company(session, sem, c, retries) for c in companies)
        )
 
    results = [result for result, _ in outcomes]
    jobs = [job for _, company_jobs in outcomes for job in company_jobs]
    return results, jobs
 
 
# --------------------------------------------------------------------------
# Normalizing: each platform's JSON -> the shared Job shape
# --------------------------------------------------------------------------
 
def _join(*parts: Any) -> str | None:
    """Join non-empty location parts: ('NYC', None, 'US') -> 'NYC, US'."""
    cleaned = [str(p).strip() for p in parts if p and str(p).strip()]
    return ", ".join(cleaned) or None
 
 
def _ms_to_iso(ms: Any) -> str | None:
    """Lever dates are milliseconds since 1970; convert to an ISO string."""
    if not isinstance(ms, (int, float)):
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
 
 
def normalize_greenhouse(company: str, token: str, data: dict) -> list[Job]:
    # Shape: {"jobs": [...], "meta": {...}}
    return [
        {
            "company": company,
            "platform": "greenhouse",
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name"),
            "department": None,  # only included with ?content=true
            "remote": None,
            "url": j.get("absolute_url", ""),
            "posted_at": j.get("first_published") or j.get("updated_at"),
            "salary": None,
        }
        for j in data.get("jobs", [])
    ]
 
 
def normalize_lever(company: str, token: str, data: list) -> list[Job]:
    # Shape: a bare list of postings (no wrapper key).
    jobs: list[Job] = []
    for j in data:
        categories = j.get("categories") or {}
        workplace = j.get("workplaceType")
        salary_range = j.get("salaryRange") or {}
        salary = None
        if salary_range.get("min") is not None and salary_range.get("max") is not None:
            salary = (f"{salary_range['min']}-{salary_range['max']} "
                      f"{salary_range.get('currency', '')} {salary_range.get('interval', '')}").strip()
        jobs.append({
            "company": company,
            "platform": "lever",
            "title": j.get("text", ""),
            "location": categories.get("location"),
            "department": categories.get("department") or categories.get("team"),
            "remote": (workplace == "remote") if workplace else None,
            "url": j.get("hostedUrl", ""),
            "posted_at": _ms_to_iso(j.get("createdAt")),
            "salary": salary,
        })
    return jobs
 
 
def normalize_ashby(company: str, token: str, data: dict) -> list[Job]:
    # Shape: {"apiVersion": "1", "jobs": [...]}
    jobs: list[Job] = []
    for j in data.get("jobs", []):
        if j.get("isListed") is False:
            continue
        compensation = j.get("compensation") or {}
        jobs.append({
            "company": company,
            "platform": "ashby",
            "title": j.get("title", ""),
            "location": j.get("location"),
            "department": j.get("department") or j.get("team"),
            "remote": j.get("isRemote"),
            "url": j.get("jobUrl", ""),
            "posted_at": j.get("publishedAt"),
            "salary": compensation.get("compensationTierSummary"),
        })
    return jobs
 
 
def normalize_smartrecruiters(company: str, token: str, data: dict) -> list[Job]:
    # Shape: {"offset": 0, "limit": 100, "totalFound": N, "content": [...]}
    jobs: list[Job] = []
    for j in data.get("content", []):
        location = j.get("location") or {}
        jobs.append({
            "company": company,
            "platform": "smartrecruiters",
            "title": j.get("name", ""),
            "location": _join(location.get("city"), location.get("region"), location.get("country")),
            "department": (j.get("department") or {}).get("label"),
            "remote": location.get("remote"),
            "url": f"https://jobs.smartrecruiters.com/{token}/{j.get('id', '')}",
            "posted_at": j.get("releasedDate"),
            "salary": None,  # SmartRecruiters has no pay field
        })
    return jobs
 
 
def normalize_workable(company: str, token: str, data: dict) -> list[Job]:
    # Shape: {"name": ..., "jobs": [...]}
    return [
        {
            "company": company,
            "platform": "workable",
            "title": j.get("title", ""),
            "location": _join(j.get("city"), j.get("state"), j.get("country")),
            "department": j.get("department") or None,
            "remote": j.get("telecommuting"),
            "url": j.get("url") or j.get("application_url") or "",
            "posted_at": j.get("published_on"),
            "salary": None,
        }
        for j in data.get("jobs", [])
    ]
 
 
NORMALIZERS: dict[str, Callable[[str, str, Any], list[Job]]] = {
    "greenhouse": normalize_greenhouse,
    "lever": normalize_lever,
    "ashby": normalize_ashby,
    "smartrecruiters": normalize_smartrecruiters,
    "workable": normalize_workable,
}
 
 
# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
 
def filter_by_keywords(jobs: list[Job], keywords: list[str]) -> list[Job]:
    """Keep jobs whose title contains any keyword (case-insensitive)."""
    if not keywords:
        return jobs
    lowered = [k.lower() for k in keywords]
    return [j for j in jobs if any(k in j["title"].lower() for k in lowered)]
 
 
def load_previous_urls(path: Path) -> set[str] | None:
    """Job URLs from the last run's output, or None if there's no usable previous run."""
    if not path.exists():
        return None
    try:
        with path.open(encoding="utf-8") as f:
            return {job["url"] for job in json.load(f) if job.get("url")}
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None
 
 
def save_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
 
 
def print_summary(results: list[CompanyResult], jobs: list[Job], new_jobs: list[Job] | None,
                  elapsed: float) -> None:
    ok = [r for r in results if r["error"] is None]
    failed = [r for r in results if r["error"] is not None]
 
    print(f"Fetched {len(results)} companies in {elapsed:.1f}s: {len(ok)} ok, {len(failed)} with problems")
    for r in failed:
        plural = "s" if r["attempts"] != 1 else ""
        print(f"  ✗ {r['company']} ({r['platform']}): {r['error']} after {r['attempts']} attempt{plural}")
    for r in ok:
        if r["job_count"] == 0:
            print(f"  · {r['company']} ({r['platform']}): board found, 0 open jobs")
 
    print(f"Jobs saved: {len(jobs)}")
    if new_jobs is None:
        print("First run: nothing to compare against yet.")
    else:
        print(f"New since last run: {len(new_jobs)}")
        for j in new_jobs:
            print(f"  + {j['company']} | {j['title']} | {j['location'] or 'n/a'} | {j['url']}")
 
 
# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
 
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="day1project",
        description="Concurrently fetch public job boards, retry failures, and save clean JSON.",
    )
    parser.add_argument("input", type=Path, help="CSV with columns: name,platform,token")
    parser.add_argument("-o", "--output", type=Path, default=Path("jobs.json"),
                        help="where to save jobs (default: jobs.json)")
    parser.add_argument("-r", "--report", type=Path, default=Path("run_report.json"),
                        help="where to save per-company results (default: run_report.json)")
    parser.add_argument("--keywords", default="",
                        help='comma-separated title keywords, e.g. "data engineer,python"')
    parser.add_argument("--retries", type=int, default=3, help="max attempts per request (default: 3)")
    parser.add_argument("--timeout", type=float, default=10.0, help="seconds per request (default: 10)")
    parser.add_argument("--concurrency", type=int, default=5,
                        help="max requests in flight at once (default: 5)")
    args = parser.parse_args(argv)
 
    if not args.input.exists():
        parser.error(f"input file not found: {args.input}")
    if args.retries < 1 or args.concurrency < 1 or args.timeout <= 0:
        parser.error("--retries and --concurrency must be at least 1, and --timeout above 0")
    return args
 
 
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    companies = read_companies(args.input)
    if not companies:
        print(f"No companies found in {args.input}")
        return 1
 
    start = time.perf_counter()
    results, jobs = asyncio.run(fetch_all(companies, args.retries, args.timeout, args.concurrency))
    elapsed = time.perf_counter() - start
 
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    jobs = filter_by_keywords(jobs, keywords)
 
    # Compare against the previous output BEFORE overwriting it.
    # (Use the same --keywords each run so the comparison is apples to apples.)
    previous_urls = load_previous_urls(args.output)
    new_jobs = None if previous_urls is None else [j for j in jobs if j["url"] not in previous_urls]
 
    save_json(args.output, jobs)
    save_json(args.report, results)
 
    print_summary(results, jobs, new_jobs, elapsed)
    print(f"Saved {args.output} and {args.report}")
 
    # Non-zero exit code if every company failed, so scripts and CI notice.
    return 0 if any(r["error"] is None for r in results) else 1
 
 
if __name__ == "__main__":
    raise SystemExit(main())
 