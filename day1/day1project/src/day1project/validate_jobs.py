from datetime import datetime

from pydantic import BaseModel, HttpUrl, ValidationError


class FetchedJob(BaseModel):
    company: str
    platform: str
    title: str
    location: str | None = None
    department: str | None = None
    remote: bool | None = None
    url: HttpUrl
    posted_at: datetime | None = None
    salary: float | None = None


def validate_jobs(raw_jobs: list[dict]) -> tuple[list[FetchedJob], list[str]]:
    clean: list[FetchedJob] = []
    errors: list[str] = []
    for i, record in enumerate(raw_jobs, start=1):
        try:
            clean.append(FetchedJob.model_validate(record))
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                errors.append(f"record {i}: {field}: {err['msg']}")
    return clean, errors
