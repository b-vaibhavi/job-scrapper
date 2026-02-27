#!/usr/bin/env python3
"""
LinkedIn Job Sniper — CLI mode
Scrapes LinkedIn for low-competition software engineering jobs and optionally
sends an email alert with the CSV attached.

Usage:
    python cli.py --location "United States" --max-applicants 50 --max-days 7 \
                  --output jobs.csv --email recipient@example.com

Environment variables for email:
    SMTP_EMAIL      Your Gmail address
    SMTP_PASSWORD   Your Gmail app password
"""
import argparse
import os
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

# ── Job title lists (mirrors app.py) ─────────────────────────────────────────
JOB_CATEGORIES = {
    "Core SWE": [
        "Software Engineer", "Software Developer", "Backend Engineer",
        "Frontend Engineer", "Full Stack Engineer", "Full Stack Developer",
        "Web Developer", "Application Developer",
    ],
    "AI/ML": [
        "AI Engineer", "AI Software Engineer", "Machine Learning Engineer",
        "ML Engineer", "LLM Engineer", "NLP Engineer", "Deep Learning Engineer",
        "AI Research Engineer", "Applied Scientist", "MLOps Engineer",
    ],
    "Data": ["Data Engineer", "Data Scientist", "Analytics Engineer"],
    "Cloud/DevOps": [
        "Cloud Engineer", "DevOps Engineer", "Platform Engineer",
        "Site Reliability Engineer", "SRE", "Infrastructure Engineer",
    ],
    "Quant/Finance": [
        "Quant Developer", "Quantitative Developer", "Quant Analyst",
        "Quantitative Analyst", "Quantitative Engineer", "Financial Software Engineer",
    ],
    "Specialized": [
        "Python Developer", "Java Developer", "React Developer",
        "Solutions Engineer", "API Engineer", "Automation Engineer",
        "Systems Engineer", "Embedded Software Engineer",
    ],
}

ALL_TITLES = [t for titles in JOB_CATEGORIES.values() for t in titles]

QUICK_TITLES = [
    "Software Engineer", "Backend Engineer", "Frontend Engineer",
    "Full Stack Engineer", "AI Engineer", "Machine Learning Engineer",
    "Data Engineer", "DevOps Engineer", "Cloud Engineer", "Platform Engineer",
]


# ── Scraping ──────────────────────────────────────────────────────────────────
def scrape(titles, location, max_applicants, max_days, results_per_search=20, remote_only=False,
           sites=None):
    if sites is None:
        sites = ["linkedin"]
    all_dfs = []
    seen_urls: set = set()
    total = len(titles)

    for i, title in enumerate(titles, start=1):
        print(f"[{i}/{total}] Searching: {title}")
        try:
            kwargs = dict(
                site_name=sites,
                search_term=title,
                location=location,
                results_wanted=results_per_search,
                hours_old=max_days * 24,
                country_indeed="USA",
            )
            if remote_only:
                kwargs["is_remote"] = True
            df = scrape_jobs(**kwargs)
            if df is not None and not df.empty:
                df = df[~df["job_url"].isin(seen_urls)]
                seen_urls.update(df["job_url"].tolist())
                mask = df["num_applicants"].isna() | (df["num_applicants"] < max_applicants)
                df = df[mask]
                if not df.empty:
                    all_dfs.append(df)
                    print(f"  → {len(df)} jobs kept")
                else:
                    print("  → 0 jobs after filtering")
            else:
                print("  → No results")
        except Exception as exc:
            print(f"  ✗ Error: {exc}")

        if i < total:
            time.sleep(1)

    if not all_dfs:
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=["job_url"])
    combined = combined.sort_values("num_applicants", ascending=True, na_position="last")
    return combined


# ── Email ─────────────────────────────────────────────────────────────────────
def send_email(to_addr: str, csv_path: Path, job_count: int, lt10: int, lt25: int):
    smtp_email = os.environ.get("SMTP_EMAIL", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")

    if not smtp_email or not smtp_password:
        print("⚠  SMTP_EMAIL / SMTP_PASSWORD not set — skipping email.")
        return

    subject = f"Job Sniper 🎯 — {job_count} low-competition jobs found"
    body = f"""
Job Sniper Daily Report
=======================
Total jobs found : {job_count}
< 10 applicants  : {lt10}
< 25 applicants  : {lt25}

The full results are attached as a CSV.

Good luck! 🚀
"""
    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open(csv_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{csv_path.name}"')
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, to_addr, msg.as_string())
        print(f"✅ Email sent to {to_addr}")
    except Exception as exc:
        print(f"✗ Failed to send email: {exc}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="LinkedIn Job Sniper CLI")
    p.add_argument("--location", default="United States", help="Job location")
    p.add_argument("--max-applicants", type=int, default=50, help="Max applicants filter")
    p.add_argument("--max-days", type=int, default=7, help="Max job age in days")
    p.add_argument("--results-per-search", type=int, default=20, help="Results per title")
    p.add_argument("--output", default="jobs.csv", help="Output CSV file path")
    p.add_argument("--email", default=os.environ.get("ALERT_EMAIL", ""), help="Alert email recipient")
    p.add_argument("--quick", action="store_true", help="Quick scan (top 10 titles only)")
    p.add_argument("--remote-only", action="store_true", help="Remote jobs only")
    p.add_argument(
        "--sites",
        default="linkedin",
        help="Comma-separated job boards: linkedin,indeed,zip_recruiter,glassdoor",
    )
    return p.parse_args()


def main():
    args = parse_args()
    titles = QUICK_TITLES if args.quick else ALL_TITLES

    sites = [s.strip() for s in args.sites.split(",") if s.strip()]

    print(f"\n🎯 Job Sniper — CLI Mode")
    print(f"   Location      : {args.location}")
    print(f"   Job boards    : {', '.join(sites)}")
    print(f"   Max applicants: {args.max_applicants}")
    print(f"   Max age       : {args.max_days} days")
    print(f"   Titles        : {len(titles)}")
    print(f"   Output        : {args.output}\n")

    df = scrape(
        titles=titles,
        location=args.location,
        max_applicants=args.max_applicants,
        max_days=args.max_days,
        results_per_search=args.results_per_search,
        remote_only=args.remote_only,
        sites=sites,
    )

    if df.empty:
        print("\nNo jobs found matching criteria.")
        return

    out_path = Path(args.output)
    df.to_csv(out_path, index=False)

    lt10 = int((df["num_applicants"] < 10).sum())
    lt25 = int((df["num_applicants"] < 25).sum())

    print(f"\n✅ Done!")
    print(f"   Total jobs    : {len(df)}")
    print(f"   < 10 apps     : {lt10}")
    print(f"   < 25 apps     : {lt25}")
    print(f"   Saved to      : {out_path}")

    if args.email:
        send_email(args.email, out_path, len(df), lt10, lt25)


if __name__ == "__main__":
    main()
