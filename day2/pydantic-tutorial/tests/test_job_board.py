import pytest
from pydantic import ValidationError

from pydantic_tutorial.job_board import JobPosting, parse_postings

GOOD = {
    "title": "ML Engineer Intern",
    "description": "Build and ship ML features.",
    "salary": 1500000,
    "url": "https://rynovi.dev/jobs/1",
    "remote": True,
}

RAW = [
    {"title": "AI Engineer", "description": "Build AI systems.", "url": "https://jobs.example.com/1", "salary": 1800000, "remote": True},
    {"title": "  Data   Scientist ", "description": "Analyze data pipelines.", "url": "https://jobs.example.com/2", "salary": 1500000, "location": "Mumbai"},
    {"title": "ML Intern", "description": "Assist with model training.", "url": "https://jobs.example.com/3", "salary": -5, "remote": True},
    {"title": "LLM Engineer", "description": "Work on large language models.", "url": "not-a-link", "salary": 2000000, "remote": True},
    {"title": "Applied Scientist", "description": "Research applied ML methods.", "url": "https://jobs.example.com/5", "salary": 2500000, "location": "Bengaluru"},
    {"title": "   ", "description": "Empty title case.", "url": "https://jobs.example.com/6", "salary": 1200000, "remote": True},
    {"title": "Backend + AI", "description": "Backend engineering with AI features.", "url": "https://jobs.example.com/7", "salary": 1900000},
    {"title": "GenAI Developer", "description": "Build generative AI products.", "url": "https://jobs.example.com/8", "salary": 1700000, "remote": True},
    {"title": "MLOps Engineer", "description": "Manage ML infrastructure.", "url": "https://jobs.example.com/9", "salary": 1600000, "location": "Bengaluru"},
    {"description": "Missing title field.", "url": "https://jobs.example.com/10", "salary": 1000000, "remote": True},
]


def test_job_posting_good_values_and_defaults():
    job = JobPosting(**GOOD)

    assert job.title == "ML Engineer Intern"
    assert str(job.url) == "https://rynovi.dev/jobs/1"
    assert job.remote is True and job.location is None


def test_job_posting_bad_values():
    with pytest.raises(ValidationError):
        JobPosting(**GOOD | {"salary": -5})
    with pytest.raises(ValidationError):
        JobPosting(**GOOD | {"url": "not-a-link"})
    with pytest.raises(ValidationError):
        JobPosting(**GOOD | {"url": "rynovi dot dev"})
    with pytest.raises(ValidationError):
        JobPosting(**GOOD | {"location": ""})


def test_job_posting_salary():
    job = JobPosting(**GOOD | {"salary": 2400000})
    assert job.salary == 2400000


def test_job_posting_title_is_stripped():
    job = JobPosting(**GOOD | {"title": "  Data   Scientist "})
    assert job.title == "Data Scientist"


def test_job_posting_empty_title():
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        JobPosting(**GOOD | {"title": "  "})


def test_job_posting_onsite_needs_location():
    with pytest.raises(ValidationError, match="On-site jobs must have a location"):
        JobPosting(**GOOD | {"remote": False, "location": None})


def test_job_posting_parse_postings():
    clean, errors = parse_postings(RAW)

    assert len(clean) == 5
    assert len(errors) == 5
    for job in clean:
        assert isinstance(job, JobPosting)
