# Week 8 Assignment: CORD-19 Data Analysis & Streamlit Application

This project is part of **Python Week 8**, where the focus is on analyzing real-world datasets and presenting results through an interactive web app.  
I worked with the **CORD-19 Research Dataset** (specifically the `metadata.csv` file), which contains metadata about COVID-19 research papers such as titles, abstracts, authors, journals, and publication dates.

---

## 📌 Assignment Objectives
By completing this assignment, I practiced:
- Loading and exploring a **large real-world dataset** using pandas.
- Cleaning and preparing data for analysis (handling missing values, converting dates, creating new columns).
- Performing **basic analysis** such as:
  - Number of papers published per year.
  - Identifying top journals publishing COVID-19 research.
  - Finding the most common words in research paper titles.
  - Distribution of publications across sources.
- Creating **visualizations** using matplotlib, seaborn, and wordcloud.
- Building a **Streamlit application** to present findings interactively.
- Documenting results and reflecting on key insights.

---

## 📊 Features Implemented
- **Data Loading & Cleaning**
  - Loaded a trimmed sample of `metadata.csv` (for performance).
  - Converted `publish_time` to datetime and extracted publication year.
  - Handled missing values and created derived columns like abstract word counts.

- **Exploratory Analysis**
  - Counted publications per year to show research trends.
  - Identified top journals and sources.
  - Extracted most frequent words from titles.
  
- **Visualizations**
  - Line chart: publications over time.
  - Bar chart: top journals.
  - Histogram: abstract word counts.
  - Word cloud: frequent words in titles.
  - Source distribution.

- **Streamlit Web App**
  - Interactive sliders and filters (e.g., select year range).
  - Displays data samples and charts interactively.
  - Lightweight and easy to run.

---