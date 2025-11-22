"""
E-Commerce Analytics: Cohort Retention Analysis
Author: Portfolio Project
Date: 2025-11-21

This script performs cohort analysis to track customer retention over time,
calculating monthly retention rates and visualizing cohort behavior.
"""

import pandas as pd
import numpy as np
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

print("=" * 80)
print("COHORT RETENTION ANALYSIS")
print("=" * 80)

# Connect to database
con = duckdb.connect('../data/ecommerce.db', read_only=True)

# Load transaction data
print("\n[1/6] Loading transaction data...")

transactions = con.execute("""
    SELECT
        CustomerID,
        InvoiceNo,
        InvoiceDate,
        Revenue,
        YearMonth
    FROM transactions
    ORDER BY CustomerID, InvoiceDate
""").df()

print(f"   ✓ Loaded {len(transactions):,} transactions")

# Create cohort data
print("\n[2/6] Creating cohort assignments...")

# Get first purchase date for each customer (cohort assignment)
customer_cohorts = con.execute("""
    SELECT
        CustomerID,
        MIN(InvoiceDate) as FirstPurchaseDate,
        strftime(MIN(InvoiceDate), '%Y-%m') as CohortMonth
    FROM transactions
    GROUP BY CustomerID
""").df()

print(f"   ✓ Identified {len(customer_cohorts):,} customers across cohorts")

# Merge cohort info back to transactions
transactions = transactions.merge(customer_cohorts[['CustomerID', 'CohortMonth']],
                                   on='CustomerID', how='left')

# Calculate cohort period (months since first purchase)
transactions['InvoiceMonth'] = transactions['InvoiceDate'].dt.to_period('M')
transactions['CohortPeriod'] = transactions['InvoiceDate'].dt.to_period('M')

# Calculate months since first purchase
def get_cohort_period(row):
    cohort_date = pd.Period(row['CohortMonth'], freq='M')
    invoice_period = row['InvoiceMonth']
    return (invoice_period - cohort_date).n

transactions['MonthsSinceFirst'] = transactions.apply(get_cohort_period, axis=1)

print(f"   ✓ Calculated cohort periods")

# Create cohort analysis table
print("\n[3/6] Building cohort retention matrix...")

# Count unique customers in each cohort-period combination
cohort_data = transactions.groupby(['CohortMonth', 'MonthsSinceFirst']).agg({
    'CustomerID': 'nunique',
    'Revenue': 'sum'
}).reset_index()

cohort_data.columns = ['CohortMonth', 'MonthsSinceFirst', 'Customers', 'Revenue']

# Get cohort sizes (customers in month 0)
cohort_sizes = cohort_data[cohort_data['MonthsSinceFirst'] == 0][['CohortMonth', 'Customers']]
cohort_sizes.columns = ['CohortMonth', 'CohortSize']

# Merge cohort sizes
cohort_data = cohort_data.merge(cohort_sizes, on='CohortMonth', how='left')

# Calculate retention rate
cohort_data['RetentionRate'] = (cohort_data['Customers'] / cohort_data['CohortSize']) * 100

# Pivot for heatmap
retention_matrix = cohort_data.pivot(index='CohortMonth',
                                      columns='MonthsSinceFirst',
                                      values='RetentionRate')

print(f"   ✓ Created retention matrix: {retention_matrix.shape[0]} cohorts × {retention_matrix.shape[1]} periods")

# Revenue cohort analysis
revenue_matrix = cohort_data.pivot(index='CohortMonth',
                                    columns='MonthsSinceFirst',
                                    values='Revenue')

print("\n[4/6] Calculating cohort metrics...")

# Overall retention metrics
cohort_metrics = {}

for months in range(retention_matrix.shape[1]):
    retention_values = retention_matrix[months].dropna()
    if len(retention_values) > 0:
        cohort_metrics[f'month_{months}_avg_retention'] = retention_values.mean()
        cohort_metrics[f'month_{months}_median_retention'] = retention_values.median()

# Calculate churn rates (inverse of retention)
churn_matrix = 100 - retention_matrix

# Average retention by period
avg_retention_by_period = retention_matrix.mean(axis=0)
avg_churn_by_period = churn_matrix.mean(axis=0)

print(f"\n   Average Retention Rates by Month:")
for month, retention in avg_retention_by_period.items():
    if not pd.isna(retention):
        print(f"   • Month {month}: {retention:.2f}%")

# Cohort quality comparison
cohort_summary = cohort_data[cohort_data['MonthsSinceFirst'] == 0].copy()
cohort_summary = cohort_summary.merge(
    cohort_data.groupby('CohortMonth').agg({
        'Revenue': 'sum',
        'Customers': 'sum'
    }).reset_index(),
    on='CohortMonth',
    suffixes=('_first', '_total')
)
cohort_summary['AvgLTV'] = cohort_summary['Revenue_total'] / cohort_summary['CohortSize']

print(f"\n   Cohort Quality Metrics:")
for idx, row in cohort_summary.iterrows():
    print(f"   • {row['CohortMonth']}: {row['CohortSize']} customers, Avg LTV: £{row['AvgLTV']:.2f}")

# Calculate overall churn reduction potential
baseline_churn = avg_churn_by_period.iloc[1] if len(avg_churn_by_period) > 1 else 0
target_churn = baseline_churn * 0.86  # 14% reduction
churn_reduction_pct = ((baseline_churn - target_churn) / baseline_churn) * 100 if baseline_churn > 0 else 0

cohort_metrics['baseline_month1_churn'] = float(baseline_churn)
cohort_metrics['target_month1_churn'] = float(target_churn)
cohort_metrics['churn_reduction_pct'] = float(churn_reduction_pct)

print(f"\n   Churn Analysis:")
print(f"   • Baseline Month-1 Churn: {baseline_churn:.2f}%")
print(f"   • Target Churn (14% reduction): {target_churn:.2f}%")
print(f"   • Potential Customers Saved: {(baseline_churn - target_churn):.2f}pp")

# Save metrics
print("\n[5/6] Saving cohort analysis results...")

cohort_metrics['analysis_date'] = datetime.now().isoformat()
cohort_metrics['total_cohorts'] = len(retention_matrix)
cohort_metrics['max_cohort_age_months'] = int(retention_matrix.shape[1] - 1)

with open('../outputs/cohort_metrics.json', 'w') as f:
    json.dump(cohort_metrics, f, indent=2)

# Save full cohort data
cohort_data.to_csv('../outputs/cohort_data.csv', index=False)
retention_matrix.to_csv('../outputs/retention_matrix.csv')

print(f"   ✓ Saved metrics to '../outputs/cohort_metrics.json'")
print(f"   ✓ Saved cohort data to '../outputs/cohort_data.csv'")
print(f"   ✓ Saved retention matrix to '../outputs/retention_matrix.csv'")

# Create visualizations
print("\n[6/6] Creating visualizations...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# 1. Retention Heatmap
ax1 = fig.add_subplot(gs[0:2, :])
sns.heatmap(retention_matrix,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=50,
            cbar_kws={'label': 'Retention Rate (%)'},
            ax=ax1,
            vmin=0,
            vmax=100)
ax1.set_title('Cohort Retention Heatmap (%)', fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel('Months Since First Purchase', fontsize=12)
ax1.set_ylabel('Cohort (First Purchase Month)', fontsize=12)

# 2. Average Retention by Period
ax2 = fig.add_subplot(gs[2, 0])
periods = avg_retention_by_period.index.tolist()
retentions = avg_retention_by_period.values
ax2.plot(periods, retentions, marker='o', linewidth=2, markersize=8, color='#2ecc71')
ax2.fill_between(periods, retentions, alpha=0.3, color='#2ecc71')
ax2.set_xlabel('Months Since First Purchase', fontsize=12)
ax2.set_ylabel('Average Retention Rate (%)', fontsize=12)
ax2.set_title('Average Retention Rate by Period', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 105)

# Add data labels
for i, (period, retention) in enumerate(zip(periods, retentions)):
    if not pd.isna(retention):
        ax2.text(period, retention + 2, f'{retention:.1f}%',
                ha='center', va='bottom', fontsize=9)

# 3. Cohort Size and LTV
ax3 = fig.add_subplot(gs[2, 1])
cohorts = cohort_summary['CohortMonth'].tolist()
x_pos = np.arange(len(cohorts))

ax3_twin = ax3.twinx()
bars = ax3.bar(x_pos, cohort_summary['CohortSize'], alpha=0.7,
               color='#3498db', label='Cohort Size')
line = ax3_twin.plot(x_pos, cohort_summary['AvgLTV'], marker='o',
                      color='#e74c3c', linewidth=2, markersize=8, label='Avg LTV')

ax3.set_xlabel('Cohort', fontsize=12)
ax3.set_ylabel('Cohort Size (Customers)', fontsize=12, color='#3498db')
ax3_twin.set_ylabel('Average LTV (£)', fontsize=12, color='#e74c3c')
ax3.set_title('Cohort Size and Customer Lifetime Value', fontsize=13, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(cohorts, rotation=45, ha='right')
ax3.tick_params(axis='y', labelcolor='#3498db')
ax3_twin.tick_params(axis='y', labelcolor='#e74c3c')

# Add legends
ax3.legend(loc='upper left')
ax3_twin.legend(loc='upper right')

plt.suptitle('E-Commerce Cohort Retention Analysis (Dec 2024 - Feb 2025)',
             fontsize=18, fontweight='bold', y=0.995)

plt.savefig('../outputs/cohort_analysis.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved visualization to '../outputs/cohort_analysis.png'")

# Create a focused retention curve chart
fig2, ax = plt.subplots(figsize=(12, 7))

# Plot retention curves for each cohort
for cohort in retention_matrix.index:
    cohort_retention = retention_matrix.loc[cohort].dropna()
    ax.plot(cohort_retention.index, cohort_retention.values,
            marker='o', alpha=0.6, linewidth=1.5, label=cohort)

# Plot average
ax.plot(avg_retention_by_period.index, avg_retention_by_period.values,
        marker='s', linewidth=3, markersize=10, color='black',
        label='Average', linestyle='--')

ax.set_xlabel('Months Since First Purchase', fontsize=12)
ax.set_ylabel('Retention Rate (%)', fontsize=12)
ax.set_title('Customer Retention Curves by Cohort', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 105)

plt.tight_layout()
plt.savefig('../outputs/retention_curves.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved retention curves to '../outputs/retention_curves.png'")

# Summary report
print("\n" + "=" * 80)
print("COHORT RETENTION ANALYSIS SUMMARY")
print("=" * 80)

print(f"\n📊 COHORT OVERVIEW:")
print(f"   • Total Cohorts: {len(retention_matrix)}")
print(f"   • Analysis Period: {retention_matrix.shape[1]} months")
print(f"   • Total Customers: {cohort_summary['CohortSize'].sum():,}")

print(f"\n📈 RETENTION METRICS:")
for i in range(min(4, len(avg_retention_by_period))):
    if not pd.isna(avg_retention_by_period.iloc[i]):
        print(f"   • Month {i} Retention: {avg_retention_by_period.iloc[i]:.2f}%")

if len(avg_retention_by_period) > 1:
    month_1_retention = avg_retention_by_period.iloc[1]
    month_0_retention = avg_retention_by_period.iloc[0]
    drop_rate = month_0_retention - month_1_retention
    print(f"\n   • First Month Drop-off: {drop_rate:.2f}pp")

print(f"\n💰 LIFETIME VALUE:")
print(f"   • Average LTV: £{cohort_summary['AvgLTV'].mean():.2f}")
print(f"   • Median LTV: £{cohort_summary['AvgLTV'].median():.2f}")
print(f"   • Max LTV: £{cohort_summary['AvgLTV'].max():.2f} ({cohort_summary.loc[cohort_summary['AvgLTV'].idxmax(), 'CohortMonth']})")

print(f"\n🎯 CHURN REDUCTION OPPORTUNITY:")
print(f"   • Current Month-1 Churn: {baseline_churn:.2f}%")
print(f"   • Target Churn (14% reduction): {target_churn:.2f}%")
print(f"   • Customers to Retain: {churn_reduction_pct:.2f}% improvement")

print("\n✅ Cohort analysis complete!")
print("=" * 80)

con.close()
