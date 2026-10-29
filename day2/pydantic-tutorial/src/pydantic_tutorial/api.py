from fastapi import FastAPI, status
from pydantic import BaseModel
from pydantic_tutorial.job_board import JobPosting, parse_postings


class JobPostingOut(JobPosting):
    id: int


app = FastAPI()
_db: list[JobPostingOut] = []


class ParseResult(BaseModel):     # from pydantic import BaseModel
    clean: list[JobPosting]
    errors: list[str]


@app.post("/job/", response_model=JobPostingOut, status_code=status.HTTP_201_CREATED)
def create_job_posting(job: JobPosting) -> JobPostingOut:
    job_out = JobPostingOut(id=len(_db) + 1, **job.model_dump(exclude={"id"}))
    _db.append(job_out)
    return job_out


@app.post("/job/parse", response_model=ParseResult, status_code=status.HTTP_200_OK)
def parse_postings_endpoint(raw_records: list[dict]) -> ParseResult:
    clean, errors = parse_postings(raw_records)
    return ParseResult(clean=clean, errors=errors)



