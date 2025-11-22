"""
E-Commerce Analytics: RFM Segmentation and Customer Value Analysis
Author: Portfolio Project
Date: 2025-11-21

This script performs RFM (Recency, Frequency, Monetary) analysis to segment customers
and calculate customer lifetime value, revenue concentration, and customer insights.
"""

import pandas as pd
import numpy as np
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json

print("=" * 80)
print("RFM SEGMENTATION & CUSTOMER VALUE ANALYSIS")
print("=" * 80)

# Connect to database
con = duckdb.connect('../data/ecommerce.db', read_only=True)

# Load customer data
print("\n[1/7] Loading customer transaction data...")

# Get analysis date (max date in dataset + 1 day)
analysis_date = con.execute("SELECT MAX(InvoiceDate) FROM transactions").fetchone()[0]
analysis_date = pd.to_datetime(analysis_date) + timedelta(days=1)

print(f"   Analysis Date: {analysis_date.date()}")

# Calculate RFM metrics
rfm_data = con.execute(f"""
    SELECT
        CustomerID,
        MAX(InvoiceDate) as LastPurchaseDate,
        COUNT(DISTINCT InvoiceNo) as Frequency,
        SUM(Revenue) as Monetary,
        COUNT(*) as TotalTransactions,
        AVG(Revenue) as AvgTransactionValue,
        MAX(Country) as Country,
        MAX(Region) as Region
    FROM transactions
    GROUP BY CustomerID
""").df()

print(f"   ✓ Loaded {len(rfm_data):,} customers")

# Calculate Recency (days since last purchase)
rfm_data['Recency'] = (analysis_date - pd.to_datetime(rfm_data['LastPurchaseDate'])).dt.days

print("\n[2/7] Calculating RFM scores...")

# Create quintile-based RFM scores (1-5, where 5 is best)
# For Recency: lower is better, so we reverse the score
rfm_data['R_Score'] = pd.qcut(rfm_data['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
rfm_data['F_Score'] = pd.qcut(rfm_data['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
rfm_data['M_Score'] = pd.qcut(rfm_data['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert to numeric
rfm_data['R_Score'] = rfm_data['R_Score'].astype(int)
rfm_data['F_Score'] = rfm_data['F_Score'].astype(int)
rfm_data['M_Score'] = rfm_data['M_Score'].astype(int)

# Calculate RFM Score (concatenated)
rfm_data['RFM_Score'] = rfm_data['R_Score'].astype(str) + \
                         rfm_data['F_Score'].astype(str) + \
                         rfm_data['M_Score'].astype(str)

# Calculate RFM Total Score (sum)
rfm_data['RFM_Total'] = rfm_data['R_Score'] + rfm_data['F_Score'] + rfm_data['M_Score']

print(f"   ✓ Calculated RFM scores (1-5 scale)")

# Define customer segments based on RFM scores
def segment_customer(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']

    # Champions: Best customers
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'

    # Loyal: Regular high-value customers
    elif r >= 3 and f >= 4 and m >= 3:
        return 'Loyal Customers'

    # Potential Loyalist: Recent customers with potential
    elif r >= 4 and f >= 2 and m >= 2:
        return 'Potential Loyalist'

    # New Customers: Recent first-time buyers
    elif r >= 4 and f == 1:
        return 'New Customers'

    # Promising: Recent with moderate activity
    elif r >= 3 and f >= 2 and m >= 2:
        return 'Promising'

    # Need Attention: Above average recency/frequency/monetary
    elif r >= 3 and f >= 3 and m >= 3:
        return 'Need Attention'

    # About to Sleep: Declining engagement
    elif r >= 2 and r <= 3:
        return 'About To Sleep'

    # At Risk: Used to be engaged but declining
    elif r <= 2 and f >= 3 and m >= 3:
        return 'At Risk'

    # Cannot Lose: High value but haven't purchased recently
    elif r <= 2 and f >= 4 and m >= 4:
        return 'Cannot Lose Them'

    # Hibernating: Low recent activity
    elif r <= 2 and f <= 2:
        return 'Hibernating'

    # Lost: Lowest scores
    else:
        return 'Lost'

rfm_data['Segment'] = rfm_data.apply(segment_customer, axis=1)

print("\n[3/7] Customer segmentation complete...")

segment_summary = rfm_data.groupby('Segment').agg({
    'CustomerID': 'count',
    'Monetary': 'sum',
    'Frequency': 'mean',
    'Recency': 'mean',
    'AvgTransactionValue': 'mean'
}).reset_index()

segment_summary.columns = ['Segment', 'Customers', 'TotalRevenue', 'AvgFrequency',
                            'AvgRecency', 'AvgTransactionValue']
segment_summary['RevenuePercent'] = (segment_summary['TotalRevenue'] /
                                     segment_summary['TotalRevenue'].sum()) * 100
segment_summary['CustomerPercent'] = (segment_summary['Customers'] /
                                      segment_summary['Customers'].sum()) * 100
segment_summary = segment_summary.sort_values('TotalRevenue', ascending=False)

print(f"\n   Customer Segments:")
for idx, row in segment_summary.iterrows():
    print(f"   • {row['Segment']:<20} {row['Customers']:>5} customers ({row['CustomerPercent']:>5.1f}%) | "
          f"£{row['TotalRevenue']:>10,.0f} ({row['RevenuePercent']:>5.1f}%)")

# Calculate Customer Lifetime Value (CLV)
print("\n[4/7] Calculating Customer Lifetime Value (CLV)...")

# Simple CLV calculation: (Avg Order Value × Purchase Frequency × Customer Lifespan)
# For this analysis, we'll use total revenue as historical CLV

rfm_data['Historical_CLV'] = rfm_data['Monetary']

# Predicted CLV based on RFM scores (weighted formula)
rfm_data['Predicted_CLV'] = (
    rfm_data['AvgTransactionValue'] *
    rfm_data['Frequency'] *
    (rfm_data['R_Score'] / 5) * 2  # Recency weight
)

clv_by_segment = rfm_data.groupby('Segment').agg({
    'Historical_CLV': 'mean',
    'Predicted_CLV': 'mean'
}).reset_index()

print(f"\n   Average CLV by Segment:")
for idx, row in clv_by_segment.iterrows():
    print(f"   • {row['Segment']:<20} Historical: £{row['Historical_CLV']:>8,.2f} | "
          f"Predicted: £{row['Predicted_CLV']:>8,.2f}")

# Revenue Concentration Analysis (Pareto Analysis)
print("\n[5/7] Analyzing revenue concentration (Pareto Analysis)...")

# Sort customers by revenue
rfm_sorted = rfm_data.sort_values('Monetary', ascending=False).reset_index(drop=True)
rfm_sorted['CumulativeRevenue'] = rfm_sorted['Monetary'].cumsum()
rfm_sorted['CumulativeRevenuePercent'] = (rfm_sorted['CumulativeRevenue'] /
                                           rfm_sorted['Monetary'].sum()) * 100
rfm_sorted['CustomerPercent'] = ((rfm_sorted.index + 1) / len(rfm_sorted)) * 100

# Find 80-20 rule metrics
top_20_pct_customers = int(len(rfm_sorted) * 0.2)
top_20_pct_revenue = rfm_sorted.iloc[:top_20_pct_customers]['Monetary'].sum()
top_20_pct_revenue_percent = (top_20_pct_revenue / rfm_sorted['Monetary'].sum()) * 100

top_10_pct_customers = int(len(rfm_sorted) * 0.1)
top_10_pct_revenue = rfm_sorted.iloc[:top_10_pct_customers]['Monetary'].sum()
top_10_pct_revenue_percent = (top_10_pct_revenue / rfm_sorted['Monetary'].sum()) * 100

print(f"\n   Revenue Concentration:")
print(f"   • Top 10% of customers generate: {top_10_pct_revenue_percent:.2f}% of revenue")
print(f"   • Top 20% of customers generate: {top_20_pct_revenue_percent:.2f}% of revenue")

# Churn risk analysis
print("\n[6/7] Analyzing churn risk...")

# Define high churn risk: R_Score <= 2
high_churn_risk = rfm_data[rfm_data['R_Score'] <= 2]
churn_risk_pct = (len(high_churn_risk) / len(rfm_data)) * 100
churn_risk_revenue = high_churn_risk['Monetary'].sum()
churn_risk_revenue_pct = (churn_risk_revenue / rfm_data['Monetary'].sum()) * 100

print(f"\n   Churn Risk Analysis:")
print(f"   • High-risk customers: {len(high_churn_risk):,} ({churn_risk_pct:.2f}%)")
print(f"   • Revenue at risk: £{churn_risk_revenue:,.2f} ({churn_risk_revenue_pct:.2f}%)")
print(f"   • Average value of at-risk customer: £{high_churn_risk['Monetary'].mean():,.2f}")

# Save results
print("\n[7/7] Saving RFM analysis results...")

# Save RFM data
rfm_data.to_csv('../outputs/rfm_customer_data.csv', index=False)
segment_summary.to_csv('../outputs/rfm_segment_summary.csv', index=False)

# Save metrics
metrics = {
    'analysis_date': analysis_date.isoformat(),
    'total_customers': int(len(rfm_data)),
    'total_revenue': float(rfm_data['Monetary'].sum()),
    'avg_clv': float(rfm_data['Historical_CLV'].mean()),
    'median_clv': float(rfm_data['Historical_CLV'].median()),
    'top_10_pct_revenue_concentration': float(top_10_pct_revenue_percent),
    'top_20_pct_revenue_concentration': float(top_20_pct_revenue_percent),
    'churn_risk_customers': int(len(high_churn_risk)),
    'churn_risk_pct': float(churn_risk_pct),
    'churn_risk_revenue': float(churn_risk_revenue),
    'churn_risk_revenue_pct': float(churn_risk_revenue_pct),
    'segments': segment_summary.to_dict('records')
}

with open('../outputs/rfm_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"   ✓ Saved RFM data to '../outputs/rfm_customer_data.csv'")
print(f"   ✓ Saved segment summary to '../outputs/rfm_segment_summary.csv'")
print(f"   ✓ Saved metrics to '../outputs/rfm_metrics.json'")

# Create visualizations
print("\n[8/8] Creating visualizations...")

fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. RFM Segment Distribution
ax1 = fig.add_subplot(gs[0, 0])
segment_counts = segment_summary.sort_values('Customers', ascending=True)
ax1.barh(segment_counts['Segment'], segment_counts['Customers'], color='#3498db', alpha=0.7)
ax1.set_xlabel('Number of Customers', fontsize=11)
ax1.set_title('Customer Distribution by Segment', fontsize=12, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# 2. Revenue by Segment
ax2 = fig.add_subplot(gs[0, 1])
segment_revenue = segment_summary.sort_values('TotalRevenue', ascending=True)
bars = ax2.barh(segment_revenue['Segment'], segment_revenue['TotalRevenue'], color='#2ecc71', alpha=0.7)
ax2.set_xlabel('Total Revenue (£)', fontsize=11)
ax2.set_title('Revenue by Customer Segment', fontsize=12, fontweight='bold')
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}K'))
ax2.grid(axis='x', alpha=0.3)

# 3. Segment Revenue Percentage (Pie)
ax3 = fig.add_subplot(gs[0, 2])
top_segments = segment_summary.nlargest(6, 'TotalRevenue')
other_revenue = segment_summary.iloc[6:]['TotalRevenue'].sum() if len(segment_summary) > 6 else 0
if other_revenue > 0:
    plot_data = pd.concat([top_segments, pd.DataFrame({
        'Segment': ['Others'],
        'TotalRevenue': [other_revenue]
    })])
else:
    plot_data = top_segments

colors_pie = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
wedges, texts, autotexts = ax3.pie(plot_data['TotalRevenue'],
                                     labels=plot_data['Segment'],
                                     autopct='%1.1f%%',
                                     colors=colors_pie,
                                     startangle=90)
ax3.set_title('Revenue Share by Segment', fontsize=12, fontweight='bold')
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

# 4. RFM Score Distribution (3D scatter)
ax4 = fig.add_subplot(gs[1, :], projection='3d')
scatter = ax4.scatter(rfm_data['R_Score'],
                       rfm_data['F_Score'],
                       rfm_data['M_Score'],
                       c=rfm_data['Monetary'],
                       cmap='viridis',
                       s=50,
                       alpha=0.6)
ax4.set_xlabel('Recency Score', fontsize=11)
ax4.set_ylabel('Frequency Score', fontsize=11)
ax4.set_zlabel('Monetary Score', fontsize=11)
ax4.set_title('RFM Score Distribution (3D)', fontsize=12, fontweight='bold')
cbar = plt.colorbar(scatter, ax=ax4, pad=0.1, shrink=0.8)
cbar.set_label('Revenue (£)', fontsize=10)

# 5. Pareto Chart (Revenue Concentration)
ax5 = fig.add_subplot(gs[2, :2])
ax5_twin = ax5.twinx()

# Sample every Nth customer for visualization clarity
sample_rate = max(1, len(rfm_sorted) // 100)
pareto_sample = rfm_sorted.iloc[::sample_rate]

ax5.bar(pareto_sample['CustomerPercent'],
        pareto_sample['Monetary'],
        width=0.8,
        color='#3498db',
        alpha=0.6,
        label='Customer Revenue')
ax5_twin.plot(pareto_sample['CustomerPercent'],
              pareto_sample['CumulativeRevenuePercent'],
              color='#e74c3c',
              linewidth=3,
              marker='o',
              markersize=4,
              label='Cumulative %')

# Add 80-20 line
ax5_twin.axhline(y=80, color='green', linestyle='--', linewidth=2, label='80% Revenue')
ax5_twin.axvline(x=20, color='orange', linestyle='--', linewidth=2, label='20% Customers')

ax5.set_xlabel('Customer Percentile', fontsize=11)
ax5.set_ylabel('Revenue (£)', fontsize=11)
ax5_twin.set_ylabel('Cumulative Revenue (%)', fontsize=11)
ax5.set_title('Pareto Analysis: Customer Revenue Concentration', fontsize=12, fontweight='bold')
ax5.legend(loc='upper left')
ax5_twin.legend(loc='upper right')
ax5.grid(True, alpha=0.3)

# 6. CLV Distribution by Segment
ax6 = fig.add_subplot(gs[2, 2])
segment_order = clv_by_segment.sort_values('Historical_CLV', ascending=True)
y_pos = np.arange(len(segment_order))
ax6.barh(y_pos, segment_order['Historical_CLV'], alpha=0.7, color='#9b59b6', label='Historical CLV')
ax6.set_yticks(y_pos)
ax6.set_yticklabels(segment_order['Segment'], fontsize=9)
ax6.set_xlabel('Average CLV (£)', fontsize=11)
ax6.set_title('Customer Lifetime Value by Segment', fontsize=12, fontweight='bold')
ax6.grid(axis='x', alpha=0.3)

plt.suptitle('RFM Analysis & Customer Segmentation', fontsize=16, fontweight='bold', y=0.995)
plt.savefig('../outputs/rfm_analysis.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved visualization to '../outputs/rfm_analysis.png'")

# Summary report
print("\n" + "=" * 80)
print("RFM SEGMENTATION SUMMARY")
print("=" * 80)

print(f"\n📊 CUSTOMER BASE:")
print(f"   • Total Customers: {len(rfm_data):,}")
print(f"   • Total Revenue: £{rfm_data['Monetary'].sum():,.2f}")
print(f"   • Average CLV: £{rfm_data['Historical_CLV'].mean():,.2f}")

print(f"\n🎯 TOP SEGMENTS:")
for idx, row in segment_summary.head(3).iterrows():
    print(f"   • {row['Segment']}: {row['Customers']} customers, £{row['TotalRevenue']:,.2f} ({row['RevenuePercent']:.1f}%)")

print(f"\n💎 REVENUE CONCENTRATION:")
print(f"   • Top 10% of customers: {top_10_pct_revenue_percent:.2f}% of revenue")
print(f"   • Top 20% of customers: {top_20_pct_revenue_percent:.2f}% of revenue")

print(f"\n⚠️  CHURN RISK:")
print(f"   • High-risk customers: {len(high_churn_risk):,} ({churn_risk_pct:.2f}%)")
print(f"   • Revenue at risk: £{churn_risk_revenue:,.2f} ({churn_risk_revenue_pct:.2f}%)")

print(f"\n✅ RFM analysis complete!")
print("=" * 80)

con.close()
