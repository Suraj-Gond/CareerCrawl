"""
CAREERCRAWL - Streamlit Web Application Interface.
Offers an interactive web dashboard for internship & job searching, filtering, analytics, and file management.
"""

import os
import json
import pandas as pd
import streamlit as st

from scraper.hybrid_scraper import HybridScraper
from storage.handlers import DataHandler
from storage.history import SearchHistory
from utils.filters import apply_filters
from utils.stats import compute_statistics
from utils.helpers import parse_stipend, shorten_url

# ─── STREAMLIT PAGE CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerCrawl - Internship & Job Finder",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ─── INITIALIZE SERVICES ─────────────────────────────────────────────────────
@st.cache_resource
def get_scraper():
    return HybridScraper()


scraper = get_scraper()

# ─── SIDEBAR NAVIGATION ──────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/briefcase.png", width=70)
st.sidebar.title("CareerCrawl Navigation")
menu = st.sidebar.radio(
    "Select Feature",
    [
        "🔍 New Search",
        "📂 Saved Datasets",
        "🔎 Interactive Filters",
        "📊 Analytics Dashboard",
        "📜 Search History",
        "⚙️ Config & Info"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("CAREERCRAWL v1.0 | Hybrid Web Scraping")


# ─── 1. NEW SEARCH ───────────────────────────────────────────────────────────
if menu == "🔍 New Search":
    st.markdown('<div class="main-header">🔍 Internship & Job Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Scrape live listings from Internshala with primary & backup fallback scrapers.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        job_type = st.selectbox("Search Type", ["Internship", "Job"], index=0)
    with col2:
        keyword = st.text_input("Keyword / Skill", value="Python", placeholder="e.g., Python, Data Science, Web Development")
    with col3:
        location = st.text_input("Location (Optional)", value="", placeholder="e.g., Bangalore, Remote")

    if st.button("🚀 Start Crawling", type="primary", use_container_width=True):
        if not keyword.strip():
            st.warning("Please enter a search keyword.")
        else:
            with st.spinner(f"Scraping {job_type} listings for '{keyword}'... Please wait."):
                results, method = scraper.scrape(
                    keyword.strip(),
                    job_type.lower(),
                    location.strip() if location else None
                )

            if results:
                # Log search history
                SearchHistory.log_search(keyword, job_type, location, len(results), method)
                st.success(f"✓ Found **{len(results)}** listings via **{method}** method!")

                # Store in session state for export/saving
                st.session_state["latest_results"] = results
                st.session_state["latest_job_type"] = job_type
            else:
                SearchHistory.log_search(keyword, job_type, location, 0, "Failed")
                st.error("✗ No results found. Try different keywords or check network connection.")

    # Display results if available
    if "latest_results" in st.session_state and st.session_state["latest_results"]:
        results = st.session_state["latest_results"]
        current_job_type = st.session_state["latest_job_type"]

        st.markdown("---")
        st.subheader("📋 Scraped Listings Preview")

        df_display = pd.DataFrame(results)

        # Reorder and pick columns for display
        cols = ["title", "company", "location", "stipend_salary", "duration", "skills", "posted_on"]
        display_cols = [c for c in cols if c in df_display.columns]

        # Convert skills array to comma-separated string for table display
        if "skills" in df_display.columns:
            df_display["skills_str"] = df_display["skills"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else str(x)
            )
            display_cols[display_cols.index("skills")] = "skills_str"

        st.dataframe(df_display[display_cols], use_container_width=True)

        # Save / Export Buttons
        save_col, json_col, excel_col = st.columns(3)

        with save_col:
            if st.button("💾 Save Dataset to Local Storage", use_container_width=True):
                paths = DataHandler.save_data(results, current_job_type)
                if paths:
                    st.success(f"Saved to `{paths[0]}` and `{paths[1]}`!")

        with json_col:
            json_str = json.dumps(results, indent=4, ensure_ascii=False)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"{current_job_type.lower()}_scraped.json",
                mime="application/json",
                use_container_width=True
            )

        with excel_col:
            # Create Excel in memory for download
            df_export = pd.DataFrame(results)
            if "skills" in df_export.columns:
                df_export["skills"] = df_export["skills"].apply(
                    lambda x: ", ".join(x) if isinstance(x, list) else x
                )
            excel_path = "temp_export.xlsx"
            df_export.to_excel(excel_path, index=False)
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📊 Download Excel",
                    data=f,
                    file_name=f"{current_job_type.lower()}_scraped.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            if os.path.exists(excel_path):
                os.remove(excel_path)

        # Apply links expander
        st.markdown("---")
        with st.expander("🔗 Open Apply Links in Web Browser"):
            for idx, r in enumerate(results, 1):
                url = r.get("apply_link", "N/A")
                if url != "N/A":
                    st.markdown(f"**{idx}. {r.get('title')}** @ *{r.get('company')}*  \n👉 [{url}]({url})")


# ─── 2. SAVED DATASETS ───────────────────────────────────────────────────────
elif menu == "📂 Saved Datasets":
    st.markdown('<div class="main-header">📂 Saved Dataset Files</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Browse, inspect, and download previously saved JSON/Excel datasets.</div>', unsafe_allow_html=True)

    filter_type = st.radio("Filter Files by Category", ["All", "Internship", "Job"], horizontal=True)
    jtype = None if filter_type == "All" else filter_type.lower()

    files_dict = DataHandler.list_saved_files(jtype)
    all_files = []
    for cat, files in files_dict.items():
        for f in files:
            f["category"] = cat.capitalize()
            all_files.append(f)

    if not all_files:
        st.info("No saved dataset files found in `saved/` directory.")
    else:
        file_options = [f"[{f['category']}] {f['filename']} ({f['size_kb']} KB) - {f['modified']}" for f in all_files]
        selected_idx = st.selectbox("Select a Saved File to View", range(len(file_options)), format_func=lambda x: file_options[x])

        selected_file = all_files[selected_idx]
        st.success(f"Viewing: `{selected_file['path']}`")

        data = DataHandler.load_data(selected_file["path"])
        if data:
            st.metric("Total Listings in File", len(data))
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

            # Download button
            json_str = json.dumps(data, indent=4, ensure_ascii=False)
            st.download_button(
                label="📥 Download Selected JSON",
                data=json_str,
                file_name=selected_file["filename"],
                mime="application/json"
            )


# ─── 3. INTERACTIVE FILTERS ──────────────────────────────────────────────────
elif menu == "🔎 Interactive Filters":
    st.markdown('<div class="main-header">🔎 Filter Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Apply dynamic multi-criteria filters to saved datasets.</div>', unsafe_allow_html=True)

    files_dict = DataHandler.list_saved_files()
    all_files = []
    for cat, files in files_dict.items():
        for f in files:
            f["category"] = cat.capitalize()
            all_files.append(f)

    if not all_files:
        st.warning("No saved files available to filter. Perform a search first!")
    else:
        file_names = [f"[{f['category']}] {f['filename']}" for f in all_files]
        sel_file_idx = st.selectbox("Choose File to Filter", range(len(file_names)), format_func=lambda i: file_names[i])

        raw_data = DataHandler.load_data(all_files[sel_file_idx]["path"])

        st.subheader("Filter Controls")
        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            skill_filter = st.text_input("Skill Tags (comma separated)", placeholder="e.g., Python, SQL")
        with f_col2:
            loc_filter = st.text_input("Location Contains", placeholder="e.g., Bangalore, Remote")
        with f_col3:
            title_filter = st.text_input("Title Contains", placeholder="e.g., Developer, Analyst")

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            min_stipend = st.number_input("Minimum Stipend (₹)", min_value=0, value=0, step=1000)
        with r_col2:
            max_stipend = st.number_input("Maximum Stipend (₹)", min_value=0, value=100000, step=5000)

        # Apply filters
        filter_dict = {}
        if skill_filter.strip():
            filter_dict["skills"] = [s.strip() for s in skill_filter.split(",")]
        if loc_filter.strip():
            filter_dict["location"] = loc_filter.strip()
        if title_filter.strip():
            filter_dict["title_keyword"] = title_filter.strip()
        if min_stipend > 0:
            filter_dict["min_stipend"] = min_stipend
        if max_stipend < 100000:
            filter_dict["max_stipend"] = max_stipend

        filtered_results = apply_filters(raw_data, filter_dict)

        st.markdown("---")
        st.subheader(f"Results: {len(filtered_results)} matching (out of {len(raw_data)})")

        if filtered_results:
            st.dataframe(pd.DataFrame(filtered_results), use_container_width=True)
        else:
            st.info("No listings match the specified filter criteria.")


# ─── 4. ANALYTICS DASHBOARD ──────────────────────────────────────────────────
elif menu == "📊 Analytics Dashboard":
    st.markdown('<div class="main-header">📊 Data Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Visual breakdown of skill frequencies, stipend distribution, and locations.</div>', unsafe_allow_html=True)

    files_dict = DataHandler.list_saved_files()
    all_files = []
    for cat, files in files_dict.items():
        for f in files:
            f["category"] = cat.capitalize()
            all_files.append(f)

    if not all_files:
        st.warning("No saved dataset available for analytics.")
    else:
        file_names = [f"[{f['category']}] {f['filename']}" for f in all_files]
        sel_file_idx = st.selectbox("Select File for Analysis", range(len(file_names)), format_func=lambda i: file_names[i])

        data = DataHandler.load_data(all_files[sel_file_idx]["path"])
        stats = compute_statistics(data)

        # Key Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        rvo = stats.get("remote_vs_onsite", {})

        m1.metric("Total Listings", stats["total"])
        m2.metric("Remote Count", rvo.get("remote", 0))
        m3.metric("Onsite Count", rvo.get("onsite", 0))
        m4.metric("Avg Stipend", stats["average_stipend"].split("(")[0])

        st.markdown("---")

        # Charts Row
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("🔥 Top Required Skills")
            skills_data = stats.get("most_common_skills", [])
            if skills_data:
                df_skills = pd.DataFrame(skills_data, columns=["Skill", "Frequency"])
                st.bar_chart(df_skills.set_index("Skill"))
            else:
                st.info("No skills data available.")

        with c2:
            st.subheader("📍 Location Distribution")
            loc_data = stats.get("location_distribution", [])
            if loc_data:
                df_loc = pd.DataFrame(loc_data, columns=["Location", "Count"])
                st.bar_chart(df_loc.set_index("Location"))
            else:
                st.info("No location data available.")


# ─── 5. SEARCH HISTORY ───────────────────────────────────────────────────────
elif menu == "📜 Search History":
    st.markdown('<div class="main-header">📜 Search History Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Audit trail of past searches, queries, and scraping execution methods.</div>', unsafe_allow_html=True)

    history = SearchHistory.load_history()

    if not history:
        st.info("No search history logged yet.")
    else:
        df_hist = pd.DataFrame(list(reversed(history)))
        st.dataframe(df_hist, use_container_width=True)

        if st.button("🗑️ Clear Search History", type="secondary"):
            SearchHistory.clear_history()
            st.experimental_rerun()


# ─── 6. CONFIG & INFO ────────────────────────────────────────────────────────
elif menu == "⚙️ Config & Info":
    st.markdown('<div class="main-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Active settings from config.json and module status.</div>', unsafe_allow_html=True)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        st.json(config)
    except Exception as e:
        st.error(f"Failed to read config.json: {e}")

    st.markdown("---")
    st.subheader("Architecture Overview")
    st.markdown("""
    - **Primary Engine:** Requests + BeautifulSoup4 (Lightweight & Fast)
    - **Backup Engine:** Selenium WebDriver (Automated JS rendering fallback)
    - **Anti-Blocking:** User-Agent Pool Rotation + Randomized Request Delays
    - **Data Formats:** Standard JSON Schema + Formatted Excel Exporter
    """)
