# Mini-project 2 · Validator for scraped job postings

**Day 2** · about 35 minutes · Pydantic models, validators, error handling

## The brief

A small job board for AI roles in India pulls postings from scrapers and a "post a job" form. The data is messy:

- salaries arrive as strings
- links are broken
- titles have stray spaces
- some on-site jobs forget to say where they are

Bad records end up on the site and recruiters complain. The founder's ask:

> "Let the clean ones through, and for every bad one tell me which record and what's wrong with it."

You're building the bouncer that sits in front of the database.

## What you'll build

- [ ] A `JobPosting` Pydantic model with the right types and defaults, where a salary can't be negative and the link must be a real URL
- [ ] A **field validator** that tidies titles (`" ML Engineer "` becomes `"ML Engineer"`) and rejects empty ones
- [ ] A **model validator** that says an on-site job must have a location
- [ ] A `parse_postings()` function that splits 10 raw records into clean postings and one clear error line per bad record, like `record 3: url: ...`

You edit `job_board.py`. The tests in `test_job_board.py` throw the same 10 messy records at your code that the scrapers would.

## Done means

- [ ] `python quest.py 2` is all green (4 checks)
- [ ] You can explain why `"24"` becomes `24.0` for the salary, but `"yes"` for `remote` gets rejected
- [ ] You can say when to use a field validator and when you need a model validator

## Run it

```bash
python quest.py 2   # checks your work and points at the next TODO
```

## Make it yours (optional)

Pick one to turn this into something you'd show in an interview:

- [ ] Read the postings from a JSON file and write the good ones to `clean.json` and the errors to `rejected.txt`
- [ ] Report every error for a bad record, not just the first, so a recruiter can fix them all in one go
- [ ] Put the model behind a `POST /postings` endpoint (Day 9's FastAPI) so the form gets the same checks

## Put it on your GitHub

You're working in your own fork of this repo, so this mini-project lives on your GitHub:

```bash
git add quests/day02
git commit -m "Mini-project 2: job posting validator"
git push
```

Then add one line about it to your fork's top `README.md` under **My mini-projects**.
