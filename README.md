# Job Sniper 🎯

> Find low-competition LinkedIn jobs before the crowd.

A Streamlit web app + CLI tool that scrapes LinkedIn for software engineering jobs posted in the last 7 days with fewer than 50 applicants — so your resume actually gets read.

---

## Features

- **40+ job title categories** across SWE, AI/ML, Data, Cloud/DevOps, Quant, and Specialized roles
- **Applicant-count badges** — color-coded competition indicators (🔥 <10 / 🟡 <25 / 🔵 <50)
- **Live progress** while scanning — title-by-title status updates
- **Card + Table views** with sort, keyword filter, and CSV download
- **Apply buttons** directly to LinkedIn job pages
- **CLI mode** for headless runs (cron / GitHub Actions)
- **Email alerts** via Gmail SMTP with CSV attachment
- **GitHub Actions** for daily automated scans at 8 AM EST

---

## Quick Start

### 1. Clone & install

```bash
git clone <your-repo-url>
cd linkedin-job-sniper
pip install -r requirements.txt
```

### 2. Run the web app

```bash
streamlit run app.py
```

Open http://localhost:8501

### 3. Run the CLI

```bash
python cli.py --location "New York" --max-applicants 25 --max-days 3
```

With email alert:

```bash
export SMTP_EMAIL="you@gmail.com"
export SMTP_PASSWORD="your-app-password"
export ALERT_EMAIL="alerts@example.com"

python cli.py --email "$ALERT_EMAIL"
```

---

## CLI Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--location` | `"United States"` | Job location to search |
| `--max-applicants` | `50` | Only keep jobs with fewer applicants |
| `--max-days` | `7` | Only return jobs posted within N days |
| `--results-per-search` | `20` | Results to fetch per job title |
| `--output` | `jobs.csv` | Output CSV file path |
| `--email` | env `ALERT_EMAIL` | Send results to this address |
| `--quick` | off | Scan only the top 10 titles (faster) |
| `--remote-only` | off | Filter for remote positions only |

---

## GitHub Actions — Daily Scan

The workflow at `.github/workflows/daily_scan.yml` runs every day at 8 AM EST.

### Required Secrets

Set these in your repo → Settings → Secrets → Actions:

| Secret | Description |
|--------|-------------|
| `SMTP_EMAIL` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Password (not your account password) |
| `ALERT_EMAIL` | Where to send the daily results |

```bash
gh secret set SMTP_EMAIL
gh secret set SMTP_PASSWORD
gh secret set ALERT_EMAIL
```

### Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Create an app password for "Mail"
3. Use that 16-character password as `SMTP_PASSWORD`

---

## Project Structure

```
linkedin-job-sniper/
├── app.py                          # Streamlit web app
├── cli.py                          # CLI scraper + email
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Dark theme
└── .github/
    └── workflows/
        └── daily_scan.yml          # GitHub Actions cron
```

---

## Requirements

- Python 3.9+
- `streamlit`, `python-jobspy`, `pandas`, `plotly`

---

## Notes

- Scraping LinkedIn is subject to their Terms of Service. Use responsibly.
- Add `time.sleep` delays are built in (2 s between searches) to avoid rate limiting.
- Results are deduplicated by job URL across all title searches.
