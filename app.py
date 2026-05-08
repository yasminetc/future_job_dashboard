import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.figure_factory as ff

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Future Jobs Dashboard",
    page_icon="💼",
    layout="wide"
)

# ── Load Data with Caching ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("future_jobs_dataset.csv")
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    df["posting_month"] = df["posting_date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ── Sidebar Filters ──────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

selected_industry = st.sidebar.multiselect(
    "Industry",
    options=sorted(df["industry"].unique()),
    default=sorted(df["industry"].unique())
)

selected_location = st.sidebar.multiselect(
    "Location",
    options=sorted(df["location"].unique()),
    default=sorted(df["location"].unique())
)

selected_remote = st.sidebar.multiselect(
    "Remote Option",
    options=df["remote_option"].unique().tolist(),
    default=df["remote_option"].unique().tolist()
)

selected_size = st.sidebar.multiselect(
    "Company Size",
    options=df["company_size"].unique().tolist(),
    default=df["company_size"].unique().tolist()
)

salary_min, salary_max = st.sidebar.slider(
    "Salary Range (USD)",
    min_value=int(df["salary_usd"].min()),
    max_value=int(df["salary_usd"].max()),
    value=(int(df["salary_usd"].min()), int(df["salary_usd"].max())),
    step=1000
)

# Apply filters
filtered_df = df[
    (df["industry"].isin(selected_industry)) &
    (df["location"].isin(selected_location)) &
    (df["remote_option"].isin(selected_remote)) &
    (df["company_size"].isin(selected_size)) &
    (df["salary_usd"] >= salary_min) &
    (df["salary_usd"] <= salary_max)
]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("💼 Future Jobs Market — Data Visualization Dashboard")
st.markdown("Explore **10,000 future job listings** across industries, locations, and salary ranges.")
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("📋 Total Jobs", f"{len(filtered_df):,}")
col2.metric("💰 Avg Salary", f"${filtered_df['salary_usd'].mean():,.0f}")
col3.metric("📈 Max Salary", f"${filtered_df['salary_usd'].max():,.0f}")
col4.metric("📉 Min Salary", f"${filtered_df['salary_usd'].min():,.0f}")

st.markdown("---")

# ── Section 1: Salary Distribution ──────────────────────────────────────────
st.subheader("📊 Section 1 — Salary Distribution")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Salary Histogram**")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(filtered_df["salary_usd"], bins=40, color="steelblue", edgecolor="white")
    ax.set_xlabel("Salary (USD)")
    ax.set_ylabel("Number of Jobs")
    ax.set_title("Salary Distribution")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    st.pyplot(fig)
    plt.close()

with col_b:
    st.markdown("**Salary by Remote Option**")
    fig2 = px.box(
        filtered_df, x="remote_option", y="salary_usd",
        color="remote_option",
        labels={"salary_usd": "Salary (USD)", "remote_option": "Remote"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig2.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Section 2: Job Title Analysis ───────────────────────────────────────────
st.subheader("👔 Section 2 — Job Titles")

col_c, col_d = st.columns(2)

with col_c:
    st.markdown("**Number of Postings per Job Title**")
    job_counts = filtered_df["job_title"].value_counts().reset_index()
    job_counts.columns = ["job_title", "count"]
    st.bar_chart(job_counts.set_index("job_title")["count"])

with col_d:
    st.markdown("**Average Salary by Job Title**")
    avg_salary_job = (
        filtered_df.groupby("job_title")["salary_usd"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig3 = px.bar(
        avg_salary_job, x="salary_usd", y="job_title",
        orientation="h",
        labels={"salary_usd": "Avg Salary (USD)", "job_title": ""},
        color="salary_usd",
        color_continuous_scale="Blues"
    )
    fig3.update_layout(height=380, coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── Section 3: Industry Analysis ────────────────────────────────────────────
st.subheader("🏭 Section 3 — Industry Breakdown")

col_e, col_f = st.columns(2)

with col_e:
    st.markdown("**Job Count by Industry**")
    industry_counts = filtered_df["industry"].value_counts()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.bar(industry_counts.index, industry_counts.values, color=["#4C72B0","#DD8452","#55A868","#C44E52"])
    ax4.set_xlabel("Industry")
    ax4.set_ylabel("Count")
    ax4.set_title("Jobs per Industry")
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    plt.xticks(rotation=15, ha="right")
    st.pyplot(fig4)
    plt.close()

with col_f:
    st.markdown("**Salary Distribution by Industry**")
    fig5 = px.violin(
        filtered_df, x="industry", y="salary_usd",
        color="industry",
        box=True,
        labels={"salary_usd": "Salary (USD)", "industry": "Industry"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig5.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── Section 4: Location Analysis ────────────────────────────────────────────
st.subheader("📍 Section 4 — Location Insights")

col_g, col_h = st.columns(2)

with col_g:
    st.markdown("**Job Postings by City**")
    loc_counts = filtered_df["location"].value_counts().reset_index()
    loc_counts.columns = ["location", "count"]
    fig6 = px.pie(
        loc_counts, names="location", values="count",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig6.update_layout(height=370)
    st.plotly_chart(fig6, use_container_width=True)

with col_h:
    st.markdown("**Average Salary by City**")
    avg_salary_loc = (
        filtered_df.groupby("location")["salary_usd"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig7 = px.bar(
        avg_salary_loc, x="location", y="salary_usd",
        labels={"salary_usd": "Avg Salary (USD)", "location": "City"},
        color="salary_usd",
        color_continuous_scale="Teal"
    )
    fig7.update_layout(height=370, coloraxis_showscale=False)
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ── Section 5: Company Size ──────────────────────────────────────────────────
st.subheader("🏢 Section 5 — Company Size")

col_i, col_j = st.columns(2)

with col_i:
    st.markdown("**Job Count by Company Size**")
    size_counts = filtered_df["company_size"].value_counts()
    st.bar_chart(size_counts)

with col_j:
    st.markdown("**Salary vs Company Size (Line View)**")
    avg_salary_size = (
        filtered_df.groupby("company_size")["salary_usd"]
        .mean()
        .reindex(["Small", "Medium", "Large"])
    )
    st.line_chart(avg_salary_size)

st.markdown("---")

# ── Section 6: Skills & Trends ───────────────────────────────────────────────
st.subheader("🛠️ Section 6 — Skills & Posting Trends")

col_k, col_l = st.columns(2)

with col_k:
    st.markdown("**Top 15 Most Required Skills**")
    all_skills = filtered_df["skills_required"].str.split(", ").explode()
    top_skills = all_skills.value_counts().head(15).reset_index()
    top_skills.columns = ["skill", "count"]
    fig8 = px.bar(
        top_skills, x="count", y="skill",
        orientation="h",
        labels={"count": "Frequency", "skill": ""},
        color="count",
        color_continuous_scale="Purples"
    )
    fig8.update_layout(height=420, coloraxis_showscale=False)
    st.plotly_chart(fig8, use_container_width=True)

with col_l:
    st.markdown("**Monthly Job Postings Trend**")
    monthly_posts = (
        filtered_df.groupby("posting_month")
        .size()
        .reset_index(name="postings")
        .sort_values("posting_month")
    )
    st.area_chart(monthly_posts.set_index("posting_month")["postings"])

st.markdown("---")

st.subheader("📈 Section 7 — Salary Density by Industry")

if st.checkbox("Show Salary Density Distribution"):
    fig_ff = px.histogram(
        filtered_df,
        x="salary_usd",
        color="industry",
        nbins=40,
        opacity=0.6,
        marginal="box"
    )

    fig_ff.update_layout(
        title="Salary Distribution per Industry",
        xaxis_title="Salary (USD)",
        height=420
    )

    st.plotly_chart(fig_ff, use_container_width=True)
# ── Section 8: Raw Data Explorer ────────────────────────────────────────────
st.subheader("🗂️ Section 8 — Raw Data Explorer")

if st.checkbox("Show Raw Data Table"):
    st.write(f"Showing **{len(filtered_df):,}** rows after filters")
    st.dataframe(filtered_df.drop(columns=["job_id"]).reset_index(drop=True), height=350)
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_future_jobs.csv",
        mime="text/csv"
    )

st.markdown("---")

# ── Section 9: Salary Predictor ─────────────────────────────────────────────
st.subheader("🔮 Section 9 — Quick Salary Lookup")
st.markdown("Select job attributes to see the **average salary** for that profile in the dataset.")

col_m, col_n, col_o = st.columns(3)

with col_m:
    lookup_title    = st.selectbox("Job Title",    sorted(df["job_title"].unique()))
with col_n:
    lookup_location = st.selectbox("Location",     sorted(df["location"].unique()))
with col_o:
    lookup_remote   = st.selectbox("Remote Option", df["remote_option"].unique().tolist())

lookup_size = st.selectbox("Company Size", df["company_size"].unique().tolist())

if st.button("🔍 Look Up Salary"):
    match = df[
        (df["job_title"]    == lookup_title) &
        (df["location"]     == lookup_location) &
        (df["remote_option"]== lookup_remote) &
        (df["company_size"] == lookup_size)
    ]
    if len(match) > 0:
        avg = match["salary_usd"].mean()
        mn  = match["salary_usd"].min()
        mx  = match["salary_usd"].max()
        st.success(f"✅ Found **{len(match)}** matching jobs")
        c1, c2, c3 = st.columns(3)
        c1.metric("Average Salary", f"${avg:,.0f}")
        c2.metric("Min Salary",     f"${mn:,.0f}")
        c3.metric("Max Salary",     f"${mx:,.0f}")
    else:
        st.warning("⚠️ No exact match found. Try changing the filters.")

st.markdown("---")
st.caption("💼 Future Jobs Dashboard | Built with Streamlit | Dataset: 10,000 job listings")
