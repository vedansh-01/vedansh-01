# scripts/fetch_contributions.py
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

USERNAME = "vedansh-01"  # swap to your github username
URL = f"https://github.com/users/vedansh-01/contributions"

def fetch():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        level = td.get("data-level")
        if date is None:
            continue

        # count lives in sibling tool-tip text, not an attribute
        cell_id = td.get("id")
        count = 0
        if cell_id:
            tip = soup.find("tool-tip", attrs={"for": cell_id})
            if tip and tip.text:
                text = tip.text.strip()
                if text.startswith("No contributions"):
                    count = 0
                else:
                    # "3 contributions on August 5th." -> grab leading number
                    first_word = text.split()[0]
                    count = int(first_word) if first_word.isdigit() else 0

        days.append({
            "date": date,
            "count": count,
            "level": int(level) if level is not None else 0,
        })

    days.sort(key=lambda d: d["date"])
    return days
def compute_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default=None)

    # current streak: walk back from most recent day
    cur_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            cur_streak += 1
        else:
            break

    # longest streak
    longest = run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    # monthly totals
    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total": total,
        "current_streak": cur_streak,
        "longest_streak": longest,
        "best_day": best,
        "monthly": monthly,
    }

if __name__ == "__main__":
    days = fetch()
    stats = compute_stats(days)
    out = {"days": days, "stats": stats, "fetched_at": datetime.utcnow().isoformat()}
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"wrote data/contributions.json — {stats['total']} contributions, "
          f"streak {stats['current_streak']}")
