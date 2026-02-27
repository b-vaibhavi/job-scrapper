import streamlit as st
import pandas as pd
import time
import plotly.express as px
from jobspy import scrape_jobs

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Sniper 🎯",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f;
    color: #e0e7ff;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #1a1a2e 100%);
    border-right: 1px solid #2d2d5e;
}
/* Hero */
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}
.hero-subtitle {
    font-size: 1.25rem;
    color: #94a3b8;
    margin-bottom: 2rem;
}
/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d2d5e;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2.25rem;
    font-weight: 700;
    color: #6366f1;
}
.metric-label {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 0.25rem;
}
/* Job card */
.job-card {
    background: linear-gradient(135deg, #111128 0%, #1a1a2e 100%);
    border: 1px solid #2d2d5e;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}
.job-card:hover {
    border-color: #6366f1;
}
.job-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e0e7ff;
    margin-bottom: 0.25rem;
}
.job-company {
    font-size: 0.95rem;
    color: #818cf8;
    font-weight: 600;
}
.job-meta {
    font-size: 0.82rem;
    color: #64748b;
    margin-top: 0.25rem;
}
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 0.4rem;
}
.badge-red   { background: rgba(239,68,68,0.2);  color: #ef4444; border: 1px solid #ef4444; }
.badge-yellow{ background: rgba(234,179,8,0.2);  color: #eab308; border: 1px solid #eab308; }
.badge-blue  { background: rgba(99,102,241,0.2); color: #818cf8; border: 1px solid #818cf8; }
.badge-gray  { background: rgba(100,116,139,0.2);color: #94a3b8; border: 1px solid #475569; }
/* Apply button */
.apply-btn {
    display: inline-block;
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: #fff !important;
    text-decoration: none !important;
    padding: 0.45rem 1.1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.9rem;
    transition: opacity 0.2s;
    margin-top: 0.75rem;
}
.apply-btn:hover { opacity: 0.85; }
/* How it works */
.step-card {
    background: #111128;
    border: 1px solid #2d2d5e;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
/* Section header */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #a78bfa;
    margin: 1.5rem 0 1rem;
    border-bottom: 1px solid #2d2d5e;
    padding-bottom: 0.5rem;
}
/* Progress */
.stProgress > div > div > div { background: #6366f1; }
/* Sidebar label */
.sidebar-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.25rem;
}
/* Streamlit tweaks */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    padding: 0.6rem 1.5rem;
    width: 100%;
    font-size: 1rem;
}
div[data-testid="stButton"] > button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ── Job title categories ──────────────────────────────────────────────────────
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

QUICK_TITLES = [
    "Software Engineer", "Backend Engineer", "Frontend Engineer",
    "Full Stack Engineer", "AI Engineer", "Machine Learning Engineer",
    "Data Engineer", "DevOps Engineer", "Cloud Engineer", "Platform Engineer",
]

# ── Session state init ────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "scan_done" not in st.session_state:
    st.session_state.scan_done = False


# ── Helpers ───────────────────────────────────────────────────────────────────
def applicant_badge(num):
    if pd.isna(num):
        return '<span class="badge badge-gray">⚪ Unknown</span>'
    n = int(num)
    if n < 10:
        return f'<span class="badge badge-red">🔥 {n} applicants</span>'
    if n < 25:
        return f'<span class="badge badge-yellow">🟡 {n} applicants</span>'
    return f'<span class="badge badge-blue">🔵 {n} applicants</span>'


def run_scrape(titles, location, max_applicants, max_days, results_per_search, sites):
    all_dfs = []
    seen_urls = set()
    total = len(titles)
    progress = st.progress(0)
    status = st.empty()
    errors = []

    for i, title in enumerate(titles):
        pct = i / total
        progress.progress(pct)
        status.markdown(
            f'<div style="color:#94a3b8;font-size:0.95rem;">'
            f'🔍 <b>{i+1}/{total}</b> — Searching: <span style="color:#818cf8">{title}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        try:
            df = scrape_jobs(
                site_name=sites,
                search_term=title,
                location=location,
                results_wanted=results_per_search,
                hours_old=max_days * 24,
                country_indeed="USA",
            )
            if df is not None and not df.empty:
                # Deduplicate
                df = df[~df["job_url"].isin(seen_urls)]
                seen_urls.update(df["job_url"].tolist())
                # Filter by applicants
                mask = df["num_applicants"].isna() | (df["num_applicants"] < max_applicants)
                df = df[mask]
                if not df.empty:
                    all_dfs.append(df)
        except Exception as exc:
            errors.append(f"`{title}`: {exc}")
        if i < total - 1:
            time.sleep(1)

    if errors:
        with st.expander(f"⚠️ {len(errors)} search error(s) — click to expand"):
            for e in errors:
                st.markdown(f"- {e}")

    progress.progress(1.0)
    status.empty()

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        # Final dedup pass
        combined = combined.drop_duplicates(subset=["job_url"])
        return combined
    return pd.DataFrame()


def sort_df(df, sort_by):
    if sort_by == "Applicants (low → high)":
        return df.sort_values("num_applicants", ascending=True, na_position="last")
    if sort_by == "Date (newest first)":
        if "date_posted" in df.columns:
            return df.sort_values("date_posted", ascending=False, na_position="last")
    if sort_by == "Company (A → Z)":
        return df.sort_values("company", ascending=True, na_position="last")
    return df


def render_card(row):
    title = row.get("title", "N/A")
    company = row.get("company", "N/A")
    location = row.get("location", "")
    num_app = row.get("num_applicants", float("nan"))
    date_posted = row.get("date_posted", "")
    salary = row.get("min_amount", None)
    salary_max = row.get("max_amount", None)
    url = row.get("job_url", "#")

    salary_str = ""
    if pd.notna(salary) and salary:
        salary_str = f"💰 ${int(salary):,}"
        if pd.notna(salary_max) and salary_max:
            salary_str += f" – ${int(salary_max):,}"

    date_str = str(date_posted)[:10] if date_posted else ""

    meta_parts = [p for p in [location, date_str, salary_str] if p]
    meta_str = " &nbsp;·&nbsp; ".join(meta_parts)

    badge = applicant_badge(num_app)

    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-title">{title}</div>
            <div class="job-company">{company}</div>
            <div class="job-meta">{meta_str}</div>
            <div style="margin-top:0.6rem">{badge}</div>
            <a class="apply-btn" href="{url}" target="_blank">Apply →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.4rem;font-weight:800;color:#6366f1;margin-bottom:0.5rem;">⚙️ Scan Settings</div>',
        unsafe_allow_html=True,
    )

    location = st.text_input("📍 Location", value="United States")
    sites = st.multiselect(
        "🌐 Job Boards",
        options=["linkedin", "indeed", "zip_recruiter", "glassdoor"],
        default=["linkedin"],
    )
    max_applicants = st.slider("Max applicants", 1, 100, 50)
    max_days = st.slider("Max job age (days)", 1, 14, 7)
    results_per_search = st.slider("Results per title", 10, 50, 20)

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Job Title Categories</div>', unsafe_allow_html=True)

    selected_titles = []
    default_on = {"Core SWE", "AI/ML"}
    for cat, titles in JOB_CATEGORIES.items():
        checked = st.checkbox(cat, value=(cat in default_on))
        if checked:
            selected_titles.extend(titles)

    st.markdown("---")
    scan_btn = st.button("🎯 Start Scanning", use_container_width=True)
    quick_btn = st.button("⚡ Quick Scan (Top 10)", use_container_width=True)

# ── Main area ─────────────────────────────────────────────────────────────────
if not st.session_state.scan_done:
    # Hero
    st.markdown('<div class="hero-title">Job Sniper 🎯</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Find low-competition jobs before the crowd</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="step-card"><b style="color:#6366f1">1. Configure</b><br>'
            '<span style="color:#94a3b8;font-size:0.9rem">Set your location, applicant limit, '
            "and choose job categories from the sidebar.</span></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="step-card"><b style="color:#6366f1">2. Scan</b><br>'
            '<span style="color:#94a3b8;font-size:0.9rem">Hit "Start Scanning" — the app searches '
            "LinkedIn for every selected title and collects results.</span></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="step-card"><b style="color:#6366f1">3. Apply</b><br>'
            '<span style="color:#94a3b8;font-size:0.9rem">Browse low-competition jobs sorted by '
            "fewest applicants and hit Apply before the crowd shows up.</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div style="background:#111128;border:1px solid #2d2d5e;border-radius:12px;padding:1.25rem 1.5rem;margin-top:1.5rem">
    <b style="color:#a78bfa">Why low-applicant jobs?</b><br>
    <span style="color:#94a3b8;font-size:0.9rem">
    Jobs with fewer than 25 applicants are statistically far more likely to get your resume reviewed.
    Most job seekers apply to the same handful of high-visibility listings.
    Job Sniper surfaces the overlooked ones — the same quality, just less crowded.
    </span>
    </div>
    """, unsafe_allow_html=True)

# ── Trigger scan ──────────────────────────────────────────────────────────────
if scan_btn or quick_btn:
    titles_to_scan = QUICK_TITLES if quick_btn else list(dict.fromkeys(selected_titles))
    if not titles_to_scan:
        st.warning("Please select at least one job category.")
    else:
        st.session_state.scan_done = False
        st.session_state.results = None

        boards = sites if sites else ["indeed", "zip_recruiter"]
        board_label = " + ".join(s.title() for s in boards)
        st.markdown(f'<div class="section-header">🔍 Scanning {board_label}…</div>', unsafe_allow_html=True)
        df = run_scrape(titles_to_scan, location, max_applicants, max_days, results_per_search, boards)
        st.session_state.results = df
        st.session_state.scan_done = True
        st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.scan_done and st.session_state.results is not None:
    df = st.session_state.results.copy()

    if df.empty:
        st.warning("No jobs matched your criteria. Try relaxing the filters.")
    else:
        # ── Metrics ───────────────────────────────────────────────────────────
        total_jobs = len(df)
        avg_app = df["num_applicants"].mean()
        lt10 = int((df["num_applicants"] < 10).sum())
        lt25 = int((df["num_applicants"] < 25).sum())

        c1, c2, c3, c4 = st.columns(4)
        for col, val, label in [
            (c1, total_jobs, "Total Jobs Found"),
            (c2, f"{avg_app:.0f}" if not pd.isna(avg_app) else "N/A", "Avg Applicants"),
            (c3, lt10, "Jobs with < 10 Apps"),
            (c4, lt25, "Jobs with < 25 Apps"),
        ]:
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">{val}</div>'
                    f'<div class="metric-label">{label}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # ── Filter / sort controls ────────────────────────────────────────────
        fc1, fc2 = st.columns([2, 3])
        with fc1:
            sort_by = st.selectbox(
                "Sort by",
                ["Applicants (low → high)", "Date (newest first)", "Company (A → Z)"],
            )
        with fc2:
            keyword = st.text_input("🔎 Filter by keyword", placeholder="e.g. Python, remote, fintech…")

        filtered = sort_df(df, sort_by)
        if keyword:
            kw = keyword.lower()
            mask = (
                filtered["title"].str.lower().str.contains(kw, na=False)
                | filtered["company"].str.lower().str.contains(kw, na=False)
                | filtered["location"].str.lower().str.contains(kw, na=False)
                | filtered.get("description", pd.Series(dtype=str)).str.lower().str.contains(kw, na=False)
            )
            filtered = filtered[mask]

        st.markdown(
            f'<div style="color:#64748b;font-size:0.85rem;margin-bottom:0.75rem;">'
            f"Showing <b style='color:#818cf8'>{len(filtered)}</b> of {total_jobs} jobs</div>",
            unsafe_allow_html=True,
        )

        # ── Download CSV ──────────────────────────────────────────────────────
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV",
            data=csv_data,
            file_name="job_sniper_results.csv",
            mime="text/csv",
        )

        st.markdown("---")

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab_cards, tab_table = st.tabs(["🃏 Card View", "📊 Table View"])

        with tab_cards:
            if filtered.empty:
                st.info("No results match your filter.")
            else:
                cols = st.columns(2)
                for idx, (_, row) in enumerate(filtered.iterrows()):
                    with cols[idx % 2]:
                        render_card(row)

        with tab_table:
            display_cols = [
                c for c in
                ["title", "company", "location", "num_applicants", "date_posted",
                 "min_amount", "max_amount", "job_url"]
                if c in filtered.columns
            ]
            st.dataframe(filtered[display_cols], use_container_width=True, height=500)

        # ── Chart ─────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="section-header">📊 Applicant Distribution</div>', unsafe_allow_html=True)
        chart_df = df["num_applicants"].dropna()
        if not chart_df.empty:
            fig = px.histogram(
                chart_df,
                x=chart_df,
                nbins=20,
                labels={"x": "Number of Applicants", "y": "Job Count"},
                color_discrete_sequence=["#6366f1"],
            )
            fig.update_layout(
                paper_bgcolor="#0a0a0f",
                plot_bgcolor="#111128",
                font_color="#e0e7ff",
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(gridcolor="#2d2d5e"),
                yaxis=dict(gridcolor="#2d2d5e"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No applicant data available for chart.")
