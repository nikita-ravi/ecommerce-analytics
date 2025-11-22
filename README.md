# E-Commerce Sales & Retention Analytics Dashboard

Find the Dashboard here: https://ecommerce-analytics-rdgjmktnurprlbdh3jwfxr.streamlit.app

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)](https://streamlit.io/)

> Comprehensive analytics project analyzing UK Online Retail data with A/B testing, cohort analysis, RFM segmentation, and interactive dashboards.

## 📊 Project Overview

This portfolio project demonstrates end-to-end data analytics capabilities including:
- **500K+ transactions** analyzed from UCI Online Retail dataset
- **Statistical A/B testing** for discount strategy effectiveness
- **Cohort retention analysis** with monthly retention tracking
- **RFM customer segmentation** for targeted marketing
- **Interactive dashboards** built with Streamlit and Plotly
- **Automated reporting** with Excel and PDF outputs

### Key Findings

- 📈 **Revenue Concentration**: Top 20% of customers drive 64.5% of revenue
- 👥 **Customer Segments**: Champions segment generates 52.4% of revenue
- 🔄 **Retention**: 33.15% Month-1 retention with 14% improvement opportunity
- 💰 **Churn Risk**: £291,241 revenue at risk from 39.3% high-risk customers
- 🧪 **A/B Testing**: Discount strategy showed -13.66% revenue impact (not recommended)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install required packages
pip install -r requirements.txt
```

### Installation

```bash
# Clone or download the project
cd ecommerce-analytics

# Run all analysis scripts
cd scripts
python 01_data_preparation.py
python 02_ab_testing_analysis.py
python 03_cohort_analysis.py
python 04_rfm_segmentation.py
python 05_comprehensive_metrics.py
python 06_generate_excel_report.py
python 07_generate_pdf_report.py

# Launch interactive dashboard
cd ../dashboards
streamlit run streamlit_dashboard.py
```

The dashboard will open at `http://localhost:8501`

---

## 📁 Project Structure

```
ecommerce-analytics/
│
├── data/
│   ├── online_retail.xlsx          # Source data (UCI dataset)
│   ├── cleaned_retail_data.csv     # Cleaned dataset
│   └── ecommerce.db               # DuckDB database
│
├── scripts/
│   ├── 01_data_preparation.py      # Data cleaning & DB setup
│   ├── 02_ab_testing_analysis.py   # A/B test statistical analysis
│   ├── 03_cohort_analysis.py       # Cohort retention analysis
│   ├── 04_rfm_segmentation.py      # RFM customer segmentation
│   ├── 05_comprehensive_metrics.py # Metrics consolidation
│   ├── 06_generate_excel_report.py # Excel workbook generator
│   └── 07_generate_pdf_report.py   # PDF report generator
│
├── dashboards/
│   └── streamlit_dashboard.py      # Interactive Streamlit dashboard
│
├── outputs/
│   ├── ab_test_results.json        # A/B test metrics
│   ├── cohort_metrics.json         # Cohort analysis metrics
│   ├── rfm_metrics.json            # RFM segmentation metrics
│   ├── comprehensive_metrics.json  # All consolidated metrics
│   ├── *.csv                       # Detailed data exports
│   ├── *.png                       # Visualization exports
│   └── ecommerce_analytics_report.xlsx  # Excel workbook (11 sheets)
│
├── reports/
│   └── ecommerce_analytics_report.pdf   # Comprehensive PDF report
│
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 📈 Analysis Components

### 1. Data Preparation & SQL Processing

**File**: `01_data_preparation.py`

- Loads UCI Online Retail dataset (500K+ transactions)
- Cleans data (removes cancellations, nulls, outliers)
- Creates DuckDB database with optimized schema
- Simulates Dec 2024 - Feb 2025 timeframe
- Adds A/B test groups and UK regional data
- **Output**: Clean database with 67,258 transactions, 1,677 customers

**Key SQL Tables**:
- `transactions` - Transaction-level data with enrichments
- `customers` - Customer summary with aggregated metrics

### 2. A/B Testing Analysis

**File**: `02_ab_testing_analysis.py`

Statistical analysis comparing Control vs Treatment groups (discount strategy):

**Metrics Analyzed**:
- Revenue uplift percentage
- Order frequency changes
- Repeat purchase rates
- Average order value impact
- ROI calculation

**Statistical Tests**:
- Two-sample t-tests (p < 0.05 significance)
- Chi-square tests for categorical data
- Effect size (Cohen's d)
- 95% Confidence intervals

**Results**:
- Revenue Impact: **-13.66%**
- Order Frequency: **+10.76%**
- ROI: **-189.68%**
- **Recommendation**: Do not implement

### 3. Cohort Retention Analysis

**File**: `03_cohort_analysis.py`

Tracks customer retention across monthly cohorts:

**Metrics**:
- Monthly retention rates (0-3 months)
- Cohort-specific performance
- Customer lifetime value by cohort
- Churn reduction opportunities

**Key Findings**:
- Month-1 Retention: **33.15%**
- Baseline Churn: **66.85%**
- Target: **14% churn reduction** → Save **9.36pp**
- Avg LTV: **£968.79**

**Visualizations**:
- Retention heatmap
- Cohort retention curves
- LTV by cohort

### 4. RFM Customer Segmentation

**File**: `04_rfm_segmentation.py`

Segments customers using Recency, Frequency, Monetary (RFM) analysis:

**Segments Identified**:
1. **Champions** (18.7% of customers, 52.4% of revenue)
2. **Loyal Customers** (10.7%, 11.9% revenue)
3. **Potential Loyalist** (9.9%, 5.4% revenue)
4. **About to Sleep** (26.7%, 15.8% revenue)
5. At Risk, Hibernating, Lost, New Customers

**Pareto Analysis**:
- Top 10% → **50.15%** of revenue
- Top 20% → **64.51%** of revenue

**Churn Risk**:
- 39.3% customers at high risk
- £291,241 revenue at risk

### 5. Comprehensive Metrics

**File**: `05_comprehensive_metrics.py`

Consolidates all analyses into unified metrics:

- Business overview KPIs
- A/B testing summary
- Retention & churn metrics
- Segmentation insights
- Revenue trends
- Geographic performance
- Product analytics

---

## 🎨 Interactive Dashboard

**File**: `dashboards/streamlit_dashboard.py`

Launch with: `streamlit run streamlit_dashboard.py`

### Dashboard Pages

1. **Executive Overview**
   - Key metrics cards
   - Revenue trends
   - Customer segmentation overview
   - Quick insights

2. **A/B Testing**
   - Test results comparison
   - Statistical significance
   - Visual comparisons
   - Recommendations

3. **Cohort Retention**
   - Retention heatmap
   - Retention curves
   - Churn analysis
   - Improvement opportunities

4. **Customer Segmentation**
   - RFM distribution
   - Segment performance
   - Pareto chart
   - CLV analysis

5. **Geographic Analysis**
   - Revenue by UK region
   - Customer distribution
   - Regional performance

6. **Product Performance**
   - Top products by revenue
   - Top products by customers
   - Product details table

### Features

- 📊 Interactive Plotly visualizations
- 🔄 Real-time filtering
- 📱 Responsive design
- 💾 Data export capabilities
- 🎯 Drill-down analysis

---

## 📑 Deliverables

### 1. Excel Workbook

**File**: `outputs/ecommerce_analytics_report.xlsx`

**11 Sheets**:
- Executive Summary (formatted metrics)
- Transactions (67K+ rows)
- Customer Summary
- RFM Analysis
- Segment Summary
- Cohort Data
- Retention Matrix
- Revenue by Month
- Revenue by Region
- Product Performance
- Charts & Insights

**Features**:
- Professional formatting
- Built-in charts
- Pivot-ready data
- Currency/percentage formatting

### 2. PDF Report

**File**: `reports/ecommerce_analytics_report.pdf`

**Sections**:
- Title page with key metrics
- Executive summary
- Detailed analysis (A/B, Cohort, RFM)
- Visualizations
- Strategic recommendations
- Conclusions

**Format**: Professional, presentation-ready

### 3. Data Exports

All analysis outputs available as:
- JSON (metrics)
- CSV (detailed data)
- PNG (visualizations)

---

## 🛠️ Technical Stack

### Languages & Libraries

**Python 3.8+**
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `duckdb` - SQL database (in-process)
- `scipy` - Statistical tests
- `statsmodels` - Statistical modeling

**Visualization**
- `plotly` - Interactive charts
- `matplotlib` - Static visualizations
- `seaborn` - Statistical graphics
- `streamlit` - Web dashboard

**Reporting**
- `xlsxwriter` - Excel generation
- `reportlab` - PDF creation
- `openpyxl` - Excel reading/writing

### Database

**DuckDB** - Fast in-process SQL OLAP database
- Efficient analytical queries
- No separate server required
- Full SQL support
- Optimized for analytics

---

## 📊 Key Metrics Calculated

### Revenue Metrics
- Total revenue
- Revenue by month/region/product
- Revenue growth trends
- Revenue concentration (Pareto)

### Customer Metrics
- Customer Lifetime Value (CLV)
- Customer Acquisition Cost (simulated)
- Average Order Value (AOV)
- Purchase frequency
- Recency, Frequency, Monetary (RFM) scores

### Retention Metrics
- Monthly retention rates
- Cohort retention curves
- Churn rate
- Customer lifespan

### A/B Testing Metrics
- Revenue uplift %
- Statistical significance (p-values)
- Effect sizes (Cohen's d)
- Confidence intervals
- ROI

---

## 🎯 Business Recommendations

Based on the analysis, key recommendations include:

### 1. **Focus on High-Value Customers**
- Top 20% drive 64.5% of revenue
- Implement VIP programs for Champions
- Personalized engagement strategies

### 2. **Improve Retention**
- Target 14% churn reduction
- Focus on "About to Sleep" segment
- Win-back campaigns for at-risk customers
- Save £291K in at-risk revenue

### 3. **Optimize Discount Strategy**
- Current approach shows negative ROI
- Do not implement broad discounts
- Test targeted, segment-specific offers

### 4. **Geographic Focus**
- London is top market (£312K revenue)
- Optimize for top 5 regions
- Expand in underserved areas

### 5. **Product Portfolio**
- Focus on top-performing products
- Cross-sell to high-value segments
- Monitor product trends

---

## 📝 Data Source

**UCI Machine Learning Repository - Online Retail Dataset**

- **Source**: [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/Online+Retail)
- **Description**: Transactional data from UK-based online retail
- **Period**: December 2010 - December 2011 (adapted to Dec 2024 - Feb 2025)
- **Size**: 541,909 transactions (cleaned to 67,258 for 3-month analysis)
- **Customers**: 4,372 (analyzed: 1,677)
- **Countries**: 38 countries

---

## 🚦 Running the Project

### Step-by-Step Guide

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run data preparation (creates database)
cd scripts
python 01_data_preparation.py

# 3. Run all analyses
python 02_ab_testing_analysis.py
python 03_cohort_analysis.py
python 04_rfm_segmentation.py
python 05_comprehensive_metrics.py

# 4. Generate reports
python 06_generate_excel_report.py
python 07_generate_pdf_report.py

# 5. Launch dashboard
cd ../dashboards
streamlit run streamlit_dashboard.py
```

### Expected Runtime

- Data preparation: ~30 seconds
- Each analysis: ~10-30 seconds
- Excel generation: ~15 seconds
- PDF generation: ~5 seconds
- **Total**: ~2-3 minutes for complete analysis

---

## 📸 Screenshots

*(Dashboard screenshots would be included here in a real portfolio)*

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Portfolio Project**
Data Analytics Demonstration
*E-Commerce Sales & Retention Analysis*

---

## 🔗 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [UCI ML Repository](https://archive.ics.uci.edu/ml/)

---

## ✅ Project Checklist

- [x] Data acquisition & cleaning
- [x] SQL database setup (DuckDB)
- [x] A/B testing with statistical significance
- [x] Cohort retention analysis
- [x] RFM customer segmentation
- [x] Comprehensive metrics calculation
- [x] Interactive Streamlit dashboard
- [x] Excel workbook with 11 sheets
- [x] Professional PDF report
- [x] Complete documentation
- [x] Portfolio-ready presentation

---

**Built with Python, SQL, Streamlit, and Plotly** | **2025**
