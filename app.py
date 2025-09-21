"""
app.py
Simple Streamlit CORD-19 Data Explorer
Requires: streamlit, pandas, matplotlib, seaborn, wordcloud
Run: streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud

sns.set(style="whitegrid")

# ---------- Helpers ----------

def load_data(path="metadata_sample.csv"):
    """
    Load the sample metadata CSV and perform minimal cleaning:
    - parse publish_time
    - extract year
    - fill missing title/abstract
    - keep source_x (if present)
    """
    df = pd.read_csv(path, low_memory=False)
    # Fill missing title/abstract
    df['title'] = df['title'].fillna("No title available")
    df['abstract'] = df['abstract'].fillna("No abstract available")
    # Parse publish_time to datetime (coerce invalids to NaT)
    if 'publish_time' in df.columns:
        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
        df['year'] = df['publish_time'].dt.year
    else:
        df['year'] = pd.NA

    # Add a quick numeric column for abstract word count
    df['abstract_word_count'] = df['abstract'].astype(str).apply(lambda x: len(x.split()))

    return df

# Streamlit caching (works with different streamlit versions)
try:
    # preferred new API
    load_data = st.cache_data(load_data)
except Exception:
    try:
        # fallback to older API
        load_data = st.cache(load_data)
    except Exception:
        # no caching available; use plain function
        pass

# ---------- App layout ----------

st.title("CORD-19 Metadata Explorer")
st.markdown(
    "A lightweight explorer for a sample of the CORD-19 metadata. "
    "Use the sidebar to filter by year and journals."
)

# Check file presence
DATA_PATH = "metadata_sample.csv"
if not os.path.exists(DATA_PATH):
    st.error(f"metadata_sample.csv not found. Put it in the same folder as app.py and re-run.")
    st.stop()

# Load data
with st.spinner("Loading data..."):
    df = load_data(DATA_PATH)

# Quick info for user
st.sidebar.header("Filters")
years = df['year'].dropna().astype(int) if 'year' in df.columns else pd.Series(dtype=int)
if len(years) > 0:
    min_year, max_year = int(years.min()), int(years.max())
else:
    min_year, max_year = 2019, 2022  # fallback values

# Sidebar widgets
year_range = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))
top_n = st.sidebar.slider("Top N journals to show", 5, 25, 10)

# Optional journal multi-select limited to top journals
top_journal_list = df['journal'].value_counts().head(50).index.tolist() if 'journal' in df.columns else []
selected_journals = st.sidebar.multiselect("Filter by journals (optional)", top_journal_list, default=[])

# Apply filters
df_filtered = df.copy()
# Year filter
if 'year' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['year'].between(year_range[0], year_range[1], inclusive="both")]

# Journal filter (if user chose any)
if selected_journals:
    df_filtered = df_filtered[df_filtered['journal'].isin(selected_journals)]

# Show basic metrics
st.subheader("Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total records (sample)", f"{len(df)}")
col2.metric("Records after filter", f"{len(df_filtered)}")
unique_journals = int(df_filtered['journal'].nunique()) if 'journal' in df_filtered.columns else 0
col3.metric("Unique journals (filtered)", f"{unique_journals}")

# ---------- Visualization 1: Publications by Year ----------
st.subheader("Publications by Year")
if 'year' in df_filtered.columns and df_filtered['year'].notna().any():
    year_counts = df_filtered['year'].value_counts().sort_index()
    fig1, ax1 = plt.subplots(figsize=(8,4))
    sns.lineplot(x=year_counts.index, y=year_counts.values, marker='o', ax=ax1)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of papers")
    ax1.set_title("Publications by Year (filtered)")
    plt.tight_layout()
    st.pyplot(fig1)
else:
    st.info("No valid 'year' values available for plotting.")

# ---------- Visualization 2: Top Journals ----------
st.subheader(f"Top {top_n} Journals")
if 'journal' in df_filtered.columns and df_filtered['journal'].notna().any():
    top_journals = df_filtered['journal'].value_counts().head(top_n)
    fig2, ax2 = plt.subplots(figsize=(8, 0.5 * top_n + 2))
    sns.barplot(x=top_journals.values, y=top_journals.index, ax=ax2)
    ax2.set_xlabel("Number of papers")
    ax2.set_ylabel("Journal")
    ax2.set_title("Top Journals (filtered)")
    plt.tight_layout()
    st.pyplot(fig2)
else:
    st.info("No journal information available to display.")

# ---------- Visualization 3: Word Cloud of Titles ----------
st.subheader("Word Cloud of Titles")
all_titles = " ".join(df_filtered['title'].dropna().astype(str).tolist()).lower()
# Basic cleaning to remove punctuation-like tokens can be added
if len(all_titles.strip()) > 0:
    wc = WordCloud(width=800, height=400, background_color="white", max_words=150).generate(all_titles)
    st.image(wc.to_array(), use_column_width=True)
else:
    st.info("No title text available to generate a word cloud.")

# ---------- Visualization 4: Distribution by Source (if present) ----------
st.subheader("Distribution by Source (top sources)")
if 'source_x' in df_filtered.columns and df_filtered['source_x'].notna().any():
    source_counts = df_filtered['source_x'].value_counts().head(10)
    fig3, ax3 = plt.subplots(figsize=(6,6))
    source_counts.plot.pie(autopct='%1.1f%%', startangle=90, ax=ax3)
    ax3.set_ylabel("")
    ax3.set_title("Top Sources (filtered)")
    plt.tight_layout()
    st.pyplot(fig3)
else:
    st.info("No 'source_x' column available in this dataset sample.")

# ---------- Data preview and download ----------
st.subheader("Data Preview")
cols_to_show = ['title', 'authors', 'journal', 'year'] if all(c in df_filtered.columns for c in ['title','authors','journal','year']) else df_filtered.columns[:5]
st.dataframe(df_filtered[cols_to_show].head(200))

# Provide optional CSV download of filtered sample
@st.experimental_memo
def convert_df_to_csv(d):
    return d.to_csv(index=False).encode('utf-8')

csv_bytes = convert_df_to_csv(df_filtered[cols_to_show])
st.download_button("Download filtered data (CSV)", data=csv_bytes, file_name="filtered_metadata_sample.csv", mime="text/csv")

# ---------- Footer: short guidance ----------
st.markdown("---")
st.markdown(
    "Notes:\n"
    "- This app uses a local 'metadata_sample.csv' file. For larger full dataset processing use chunking or a database.\n"
    "- The word cloud and plots reflect the current filters in the sidebar."
)
