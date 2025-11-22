"""
E-Commerce Analytics: Excel Report Generator
Author: Portfolio Project
Date: 2025-11-21

This script generates a comprehensive Excel workbook with multiple sheets,
pivot tables, and formatted analysis.
"""

import pandas as pd
import json
from datetime import datetime
import xlsxwriter
import duckdb

print("=" * 80)
print("EXCEL REPORT GENERATION")
print("=" * 80)

# Connect to database
con = duckdb.connect('../data/ecommerce.db', read_only=True)

# Load data
print("\n[1/6] Loading data from database and analysis files...")

transactions = con.execute("SELECT * FROM transactions").df()
customers = con.execute("SELECT * FROM customers").df()

rfm_data = pd.read_csv('../outputs/rfm_customer_data.csv')
segment_summary = pd.read_csv('../outputs/rfm_segment_summary.csv')
cohort_data = pd.read_csv('../outputs/cohort_data.csv')
retention_matrix = pd.read_csv('../outputs/retention_matrix.csv', index_col=0)
revenue_by_month = pd.read_csv('../outputs/revenue_by_month.csv')
revenue_by_region = pd.read_csv('../outputs/revenue_by_region.csv')
product_performance = pd.read_csv('../outputs/product_performance.csv')

with open('../outputs/comprehensive_metrics.json', 'r') as f:
    metrics = json.load(f)

with open('../outputs/ab_test_results.json', 'r') as f:
    ab_results = json.load(f)

print("   ✓ Data loaded successfully")

# Create Excel writer
print("\n[2/6] Creating Excel workbook...")

excel_file = '../outputs/ecommerce_analytics_report.xlsx'
writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
workbook = writer.book

# Define formats
header_format = workbook.add_format({
    'bold': True,
    'bg_color': '#4472C4',
    'font_color': 'white',
    'border': 1,
    'align': 'center',
    'valign': 'vcenter'
})

currency_format = workbook.add_format({'num_format': '£#,##0.00'})
percent_format = workbook.add_format({'num_format': '0.00%'})
number_format = workbook.add_format({'num_format': '#,##0'})
title_format = workbook.add_format({
    'bold': True,
    'font_size': 16,
    'bg_color': '#D9E1F2',
    'border': 1
})
metric_label_format = workbook.add_format({
    'bold': True,
    'bg_color': '#F2F2F2',
    'border': 1
})
metric_value_format = workbook.add_format({
    'bg_color': '#FFFFFF',
    'border': 1,
    'num_format': '#,##0.00'
})

print("   ✓ Excel workbook created")

# Sheet 1: Executive Summary
print("\n[3/6] Creating Executive Summary sheet...")

summary_sheet = workbook.add_worksheet('Executive Summary')

# Title
summary_sheet.merge_range('A1:F1', 'E-COMMERCE ANALYTICS - EXECUTIVE SUMMARY', title_format)
summary_sheet.merge_range('A2:F2', f"Analysis Period: {metrics['analysis_period']['start_date']} to {metrics['analysis_period']['end_date']}", metric_label_format)

row = 4

# Business Overview
summary_sheet.merge_range(f'A{row}:F{row}', 'BUSINESS OVERVIEW', header_format)
row += 1

overview_metrics = [
    ['Total Revenue', f"£{metrics['overview']['total_revenue']:,.2f}"],
    ['Total Customers', f"{metrics['overview']['total_customers']:,}"],
    ['Total Orders', f"{metrics['overview']['total_orders']:,}"],
    ['Average Order Value', f"£{metrics['overview']['avg_order_value']:.2f}"],
    ['Average CLV', f"£{metrics['customer_value']['avg_clv']:.2f}"]
]

for metric in overview_metrics:
    summary_sheet.write(f'A{row}', metric[0], metric_label_format)
    summary_sheet.write(f'B{row}', metric[1], metric_value_format)
    row += 1

row += 1

# A/B Testing Results
summary_sheet.merge_range(f'A{row}:F{row}', 'A/B TESTING RESULTS - DISCOUNT STRATEGY', header_format)
row += 1

ab_metrics = [
    ['Revenue Uplift', f"{metrics['ab_testing']['revenue_uplift_pct']:.2f}%"],
    ['Order Frequency Uplift', f"{metrics['ab_testing']['order_frequency_uplift_pct']:.2f}%"],
    ['Repeat Rate Uplift', f"{metrics['ab_testing']['repeat_rate_uplift_pct']:.2f}pp"],
    ['ROI', f"{metrics['ab_testing']['roi_pct']:.2f}%"],
    ['Statistical Significance', 'Yes' if metrics['ab_testing']['statistically_significant'] else 'No'],
    ['P-Value', f"{metrics['ab_testing']['p_value']:.4f}"],
    ['Recommendation', metrics['ab_testing']['recommendation']]
]

for metric in ab_metrics:
    summary_sheet.write(f'A{row}', metric[0], metric_label_format)
    summary_sheet.write(f'B{row}', metric[1], metric_value_format)
    row += 1

row += 1

# Customer Segmentation
summary_sheet.merge_range(f'A{row}:F{row}', 'CUSTOMER SEGMENTATION', header_format)
row += 1

seg_metrics = [
    ['Top Segment', metrics['segmentation']['top_segment']],
    ['Top Segment Revenue Share', f"{metrics['segmentation']['top_segment_revenue_pct']:.1f}%"],
    ['Champions %', f"{metrics['segmentation']['champions_pct']:.1f}%"],
    ['Top 20% Revenue Concentration', f"{metrics['revenue_concentration']['top_20_pct_customers_revenue_pct']:.1f}%"],
    ['Customers at Risk', f"{metrics['churn_analysis']['high_risk_pct']:.1f}%"]
]

for metric in seg_metrics:
    summary_sheet.write(f'A{row}', metric[0], metric_label_format)
    summary_sheet.write(f'B{row}', metric[1], metric_value_format)
    row += 1

row += 1

# Retention Metrics
summary_sheet.merge_range(f'A{row}:F{row}', 'RETENTION & CHURN', header_format)
row += 1

retention_metrics_list = [
    ['Month-1 Retention', f"{metrics['retention']['month_1_retention_pct']:.2f}%"],
    ['Month-2 Retention', f"{metrics['retention']['month_2_retention_pct']:.2f}%"],
    ['Baseline Churn', f"{metrics['retention']['baseline_churn_pct']:.2f}%"],
    ['Target Churn', f"{metrics['retention']['target_churn_pct']:.2f}%"],
    ['Revenue at Risk', f"£{metrics['churn_analysis']['revenue_at_risk']:,.2f}"]
]

for metric in retention_metrics_list:
    summary_sheet.write(f'A{row}', metric[0], metric_label_format)
    summary_sheet.write(f'B{row}', metric[1], metric_value_format)
    row += 1

# Set column widths
summary_sheet.set_column('A:A', 30)
summary_sheet.set_column('B:B', 25)

print("   ✓ Executive Summary created")

# Sheet 2: Transaction Data
print("\n[4/6] Creating Transaction Data sheet...")

transactions_display = transactions[['InvoiceNo', 'InvoiceDate', 'CustomerID', 'Country',
                                     'Region', 'StockCode', 'Description', 'Quantity',
                                     'UnitPrice', 'Revenue', 'TestGroup']].copy()
transactions_display.to_excel(writer, sheet_name='Transactions', index=False, startrow=0)

trans_sheet = writer.sheets['Transactions']
for col_num, col_name in enumerate(transactions_display.columns):
    trans_sheet.write(0, col_num, col_name, header_format)
    if col_name in ['UnitPrice', 'Revenue']:
        trans_sheet.set_column(col_num, col_num, 15, currency_format)
    elif col_name in ['Quantity']:
        trans_sheet.set_column(col_num, col_num, 12, number_format)
    else:
        trans_sheet.set_column(col_num, col_num, 18)

print("   ✓ Transaction Data sheet created")

# Sheet 3: Customer Summary
print("\n[5/6] Creating Customer Analysis sheets...")

customers.to_excel(writer, sheet_name='Customer Summary', index=False)
cust_sheet = writer.sheets['Customer Summary']
for col_num, col_name in enumerate(customers.columns):
    cust_sheet.write(0, col_num, col_name, header_format)
    if 'Revenue' in col_name or 'Value' in col_name:
        cust_sheet.set_column(col_num, col_num, 15, currency_format)
    else:
        cust_sheet.set_column(col_num, col_num, 18)

# RFM Analysis
rfm_display = rfm_data[['CustomerID', 'Segment', 'Recency', 'Frequency', 'Monetary',
                        'R_Score', 'F_Score', 'M_Score', 'RFM_Score',
                        'Historical_CLV', 'Country', 'Region']].copy()
rfm_display.to_excel(writer, sheet_name='RFM Analysis', index=False)

rfm_sheet = writer.sheets['RFM Analysis']
for col_num, col_name in enumerate(rfm_display.columns):
    rfm_sheet.write(0, col_num, col_name, header_format)
    if col_name in ['Monetary', 'Historical_CLV']:
        rfm_sheet.set_column(col_num, col_num, 15, currency_format)
    else:
        rfm_sheet.set_column(col_num, col_num, 18)

# Segment Summary
segment_summary.to_excel(writer, sheet_name='Segment Summary', index=False)
seg_sheet = writer.sheets['Segment Summary']
for col_num, col_name in enumerate(segment_summary.columns):
    seg_sheet.write(0, col_num, col_name, header_format)
    if 'Revenue' in col_name or 'Value' in col_name:
        seg_sheet.set_column(col_num, col_num, 15, currency_format)
    elif 'Percent' in col_name:
        seg_sheet.set_column(col_num, col_num, 15, percent_format)
    else:
        seg_sheet.set_column(col_num, col_num, 18)

print("   ✓ Customer Analysis sheets created")

# Sheet 4: Cohort Analysis
cohort_data.to_excel(writer, sheet_name='Cohort Data', index=False)
cohort_sheet = writer.sheets['Cohort Data']
for col_num, col_name in enumerate(cohort_data.columns):
    cohort_sheet.write(0, col_num, col_name, header_format)
    if 'Revenue' in col_name:
        cohort_sheet.set_column(col_num, col_num, 15, currency_format)
    elif 'Rate' in col_name or 'Percent' in col_name:
        cohort_sheet.set_column(col_num, col_num, 15, percent_format)
    else:
        cohort_sheet.set_column(col_num, col_num, 18)

# Retention Matrix
retention_matrix.to_excel(writer, sheet_name='Retention Matrix')
ret_matrix_sheet = writer.sheets['Retention Matrix']
ret_matrix_sheet.set_column('A:A', 15)
for col in range(1, retention_matrix.shape[1] + 1):
    ret_matrix_sheet.set_column(col, col, 12, percent_format)

print("   ✓ Cohort Analysis sheets created")

# Sheet 5: Revenue Analysis
print("\n[6/6] Creating Revenue Analysis sheets...")

revenue_by_month.to_excel(writer, sheet_name='Revenue by Month', index=False)
month_sheet = writer.sheets['Revenue by Month']
for col_num, col_name in enumerate(revenue_by_month.columns):
    month_sheet.write(0, col_num, col_name, header_format)
    if 'Revenue' in col_name or 'Value' in col_name:
        month_sheet.set_column(col_num, col_num, 15, currency_format)
    else:
        month_sheet.set_column(col_num, col_num, 18)

revenue_by_region.to_excel(writer, sheet_name='Revenue by Region', index=False)
region_sheet = writer.sheets['Revenue by Region']
for col_num, col_name in enumerate(revenue_by_region.columns):
    region_sheet.write(0, col_num, col_name, header_format)
    if 'Revenue' in col_name:
        region_sheet.set_column(col_num, col_num, 15, currency_format)
    else:
        region_sheet.set_column(col_num, col_num, 18)

product_performance.to_excel(writer, sheet_name='Product Performance', index=False)
product_sheet = writer.sheets['Product Performance']
for col_num, col_name in enumerate(product_performance.columns):
    product_sheet.write(0, col_num, col_name, header_format)
    if 'Revenue' in col_name or 'Price' in col_name:
        product_sheet.set_column(col_num, col_num, 15, currency_format)
    else:
        product_sheet.set_column(col_num, col_num, 20)

print("   ✓ Revenue Analysis sheets created")

# Create Charts sheet with summary charts
charts_sheet = workbook.add_worksheet('Charts & Insights')

# Add chart for revenue by month
chart1 = workbook.add_chart({'type': 'line'})
chart1.add_series({
    'name': 'Monthly Revenue',
    'categories': "='Revenue by Month'!$A$2:$A$" + str(len(revenue_by_month) + 1),
    'values': "='Revenue by Month'!$D$2:$D$" + str(len(revenue_by_month) + 1),
})
chart1.set_title({'name': 'Monthly Revenue Trend'})
chart1.set_x_axis({'name': 'Month'})
chart1.set_y_axis({'name': 'Revenue (£)'})
chart1.set_style(10)
charts_sheet.insert_chart('A2', chart1, {'x_scale': 2, 'y_scale': 1.5})

# Add chart for segment distribution
chart2 = workbook.add_chart({'type': 'column'})
chart2.add_series({
    'name': 'Revenue by Segment',
    'categories': "='Segment Summary'!$A$2:$A$" + str(len(segment_summary) + 1),
    'values': "='Segment Summary'!$C$2:$C$" + str(len(segment_summary) + 1),
})
chart2.set_title({'name': 'Revenue by Customer Segment'})
chart2.set_x_axis({'name': 'Segment'})
chart2.set_y_axis({'name': 'Revenue (£)'})
chart2.set_style(11)
charts_sheet.insert_chart('A25', chart2, {'x_scale': 2, 'y_scale': 1.5})

print("   ✓ Charts & Insights sheet created")

# Save workbook
writer.close()

print(f"\n✅ Excel report successfully generated!")
print(f"   File: {excel_file}")
print(f"   Sheets created:")
print(f"      • Executive Summary")
print(f"      • Transactions ({len(transactions):,} rows)")
print(f"      • Customer Summary ({len(customers):,} customers)")
print(f"      • RFM Analysis")
print(f"      • Segment Summary")
print(f"      • Cohort Data")
print(f"      • Retention Matrix")
print(f"      • Revenue by Month")
print(f"      • Revenue by Region")
print(f"      • Product Performance")
print(f"      • Charts & Insights")

print("\n" + "=" * 80)

con.close()
