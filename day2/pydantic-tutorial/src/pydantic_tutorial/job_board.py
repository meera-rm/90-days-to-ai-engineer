
from datetime import UTC, datetime


from ast import pattern
from functools import partial
import json
from operator import ge


from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, ValidationError,computed_field, HttpUrl, SecretStr, EmailStr, ValidationInfo, field_validator, model_validator
from datetime import UTC, datetime
from typing import Literal, Annotated
from pathlib import Path

class JobPosting(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    salary: float= Field(ge=0)
    location: str | None = None
    url: HttpUrl | None = None
    remote: bool = False
    #posted_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    posted_at: datetime = Field(default_factory=partial(datetime.now, tz=UTC))

    @field_validator("title")
    @classmethod
    def title_must_be_non_empty(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    @field_validator("location")
    @classmethod
    def location_must_be_non_empty(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Location cannot be empty")
        return value

    @model_validator(mode="after")
    def on_site_jobs_need_location(self) -> "JobPosting":
        if not self.remote and not self.location:
            raise ValueError("On-site jobs must have a location")
        return self

def parse_postings(raw_records: list[dict]) -> tuple[list[JobPosting], list[str]]:
    clean: list[JobPosting] = []
    errors: list[str] = []
    for i, record in enumerate(raw_records, start=1):
        try:
            clean.append(JobPosting.model_validate(record))
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                errors.append(f"record {i}: {field}: {err['msg']}")
    return clean, errors

def load_raw_records(path: str) -> list[dict]:
    with Path(path).open() as f:
        data = json.load(f)          # JSON text → Python objects
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}, got {type(data).__name__}")
    return data


def main() -> None:
    raw = load_raw_records("postings.json")
    postings, errors = parse_postings(raw)

    print(f"{len(postings)} valid, {len(errors)} errors")
    for err in errors:
        print("  ", err)


if __name__ == "__main__":
    main()