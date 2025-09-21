# CORD-19 Metadata Assignment
# This script will trim the CORD-19 metadata file to a smaller sample, because the metadata file is too large to load directly.

import pandas as pd
import os

print("=== Week 8: CORD-19 Data Exploration ===\n")

# Step 1: Triming the original file if it exists
if os.path.exists("metadata.csv"):
    print("Full metadata.csv found. Creating a smaller sample file...")
    try:
        # Read in chunks and keep only first 5000 rows
        chunk_iter = pd.read_csv("metadata.csv", chunksize=5000, low_memory=False)
        sample_df = next(chunk_iter)  # Take the first chunk
        sample_df.to_csv("metadata_sample.csv", index=False)
        print("✓ metadata_sample.csv created with first 5000 rows.\n")
    except Exception as e:
        print(f"⚠ Error while creating sample: {e}")
        exit()
else:
    print("⚠ metadata.csv not found, skipping trimming.\n")

# Step 2: Loading the sample file for analysis
if os.path.exists("metadata_sample.csv"):
    try:
        df = pd.read_csv("metadata_sample.csv", low_memory=False)
        print("✓ Sample dataset loaded successfully.\n")
    except Exception as e:
        print(f"⚠ Could not load metadata_sample.csv: {e}")
        exit()
else:
    print("⚠ metadata_sample.csv not found. Please make sure it's in the folder.")
    exit()

# Step 3: Data exploration
print("--- Dataset Preview ---")
print(df.head(), "\n")

print("--- Shape ---")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}\n")

print("--- Info ---")
print(df.info(), "\n")

print("--- Missing Values (Top 10 columns with most missing) ---")
print(df.isnull().sum().sort_values(ascending=False).head(10), "\n")

print("--- Basic Statistics ---")
print(df.describe(include="all").transpose().head(10))


# === Part 2: Data Cleaning & Preparation ===

print("\n=== Part 2: Data Cleaning & Preparation ===")

# 1. Handling missing data
missing = df.isnull().sum().sort_values(ascending=False)
print("\n--- Missing values per column (top 10) ---")
print(missing.head(10))

# Droping irrelevant or sparse columns (too many NaNs)
drop_cols = ['sha', 'license', 'pmcid', 'pubmed_id', 
             'arxiv_id', 'who_covidence_id', 'has_full_text']
df = df.drop(columns=drop_cols, errors='ignore')

# Fill missing abstracts/titles with placeholder
df['abstract'] = df['abstract'].fillna("No abstract available")
df['title'] = df['title'].fillna("No title available")

# 2. Preparing data for analysis
# Converting publish_time to datetime
df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')

# Extracting publication year
df['year'] = df['publish_time'].dt.year

# Creating abstract word count column
df['abstract_word_count'] = df['abstract'].apply(lambda x: len(str(x).split()))

print("\n--- Cleaned Dataset Info ---")
print(df.info())

print("\n--- Sample after cleaning ---")
print(df[['title', 'year', 'abstract_word_count']].head())


import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud

print("\n--- Part 3: Data Analysis & Visualization ---")

# 1. Publications by Year
year_counts = df['year'].value_counts().sort_index()
print("\nPublications per Year:")
print(year_counts)

plt.figure(figsize=(8,5))
sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o")
plt.title("Publications by Year")
plt.xlabel("Year")
plt.ylabel("Number of Papers")
plt.tight_layout()
plt.savefig("plots/publications_by_year.png")
plt.close()

# 2. Top Journals
top_journals = df['journal'].value_counts().head(10)
print("\nTop Journals:")
print(top_journals)

plt.figure(figsize=(10,6))
sns.barplot(y=top_journals.index, x=top_journals.values, palette="viridis")
plt.title("Top 10 Journals by Publication Count")
plt.xlabel("Number of Papers")
plt.ylabel("Journal")
plt.tight_layout()
plt.savefig("plots/top_journals.png")
plt.close()

# 3. Word Frequency in Titles
all_titles = " ".join(df['title'].dropna().astype(str).tolist()).lower()
words = [w for w in all_titles.split() if len(w) > 3]  # filter short words
common_words = Counter(words).most_common(20)
print("\nMost Common Words in Titles:")
print(common_words)

wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_titles)
plt.figure(figsize=(10,5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud of Paper Titles")
plt.tight_layout()
plt.savefig("plots/wordcloud_titles.png")
plt.close()

# 4. Distribution by Source
source_counts = df['source_x'].value_counts().head(10)
print("\nTop Sources:")
print(source_counts)

plt.figure(figsize=(8,8))
source_counts.plot.pie(autopct='%1.1f%%', startangle=90, colormap="tab20")
plt.title("Distribution of Papers by Source (Top 10)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("plots/source_distribution.png")
plt.close()

print("\n✓ Analysis complete. Plots saved in 'plots/' folder.")
