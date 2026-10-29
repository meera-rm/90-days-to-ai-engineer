### Mini-project 3 · Concurrent page fetcher with asyncio
### Day 3 · about 35 minutes · async/await, asyncio.gather, timeouts

### The brief
A data team checks 20 partner pages every morning for price changes. Their script fetches one page, waits, then fetches the next, so a run that should feel instant takes ages. Worse, one partner's site sometimes hangs and the whole job sits there. Their lead says: "fetch them together, don't hammer anyone's server, and don't let one slow site hold up the rest."

You're building that fetcher. A pretend internet (fake_web.py) stands in for the real sites: every page takes 0.2 seconds, and any URL with slow in it hangs for 5.

### What you'll build
fetch_one(), which awaits one page and returns its URL and length
fetch_all(), which fetches all 20 pages at the same time with asyncio.gather, in about 0.2 seconds instead of 4, and keeps the results in order
fetch_all_limited(), which never runs more than 3 fetches at once, using a Semaphore
fetch_all_safe(), which gives up on a page after a timeout and returns None for it instead of making everyone wait
You edit speed_run.py. The tests in test_speed_run.py time your code and count how many fetches ran at once, so a sneaky one-by-one loop won't pass.

### Done means
 pytest is all green (4 checks)
 You can explain why 20 pages take about the same time as one when you use gather
 You can say why you'd cap the number of requests even when your code could send them all at once

### Commands to run
```
cd day3/day3project
python my_fake_webpage.py  
python -m pytest test_speed_run.py -v
```
Make it yours (optional)
Pick one to turn this into something you'd show in an interview:

Swap fake_web.fetch for real requests with httpx.AsyncClient and fetch 20 real pages you care about
Print a small timing table: one by one, all at once, limit 3, limit 10
Retry pages that time out once before giving up (Day 4's retries)
Put it on your GitHub
You're working in your own fork of this repo, so this mini-project lives on your GitHub:

git add quests/day03
git commit -m "Mini-project 3: concurrent page fetcher"
git push
Then add one line about it to your fork's top README under My mini-projects.