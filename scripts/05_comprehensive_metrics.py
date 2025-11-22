"""
E-Commerce Analytics: Comprehensive Metrics Dashboard
Author: Portfolio Project
Date: 2025-11-21

This script consolidates all key metrics from previous analyses and generates
additional insights for the executive dashboard.
"""

import pandas as pd
import numpy as np
import duckdb
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print("COMPREHENSIVE METRICS CALCULATION")
print("=" * 80)

# Connect to database
con = duckdb.connect('../data/ecommerce.db', read_only=True)

# Load all previous analysis results
print("\n[1/5] Loading analysis results...")

with open('../outputs/ab_test_results.json', 'r') as f:
    ab_results = json.load(f)

with open('../outputs/cohort_metrics.json', 'r') as f:
    cohort_results = json.load(f)

with open('../outputs/rfm_metrics.json', 'r') as f:
    rfm_results = json.load(f)

print("   ✓ Loaded A/B test results")
print("   ✓ Loaded cohort analysis results")
print("   ✓ Loaded RFM segmentation results")

# Calculate additional business metrics
print("\n[2/5] Calculating additional business metrics...")

# Revenue metrics by time period
revenue_by_month = con.execute("""
    SELECT
        YearMonth,
        COUNT(DISTINCT CustomerID) as ActiveCustomers,
        COUNT(DISTINCT InvoiceNo) as TotalOrders,
        SUM(Revenue) as TotalRevenue,
        AVG(Revenue) as AvgTransactionValue,
        SUM(Quantity) as TotalItems
    FROM transactions
    GROUP BY YearMonth
    ORDER BY YearMonth
""").df()

# Revenue by region (UK focus)
revenue_by_region = con.execute("""
    SELECT
        Region,
        COUNT(DISTINCT CustomerID) as Customers,
        SUM(Revenue) as Revenue,
        COUNT(DISTINCT InvoiceNo) as Orders
    FROM transactions
    WHERE Country = 'United Kingdom'
    GROUP BY Region
    ORDER BY Revenue DESC
""").df()

# Product performance
product_performance = con.execute("""
    SELECT
        StockCode,
        MAX(Description) as ProductName,
        COUNT(DISTINCT CustomerID) as UniqueCustomers,
        SUM(Quantity) as TotalQuantity,
        SUM(Revenue) as TotalRevenue,
        AVG(UnitPrice) as AvgPrice
    FROM transactions
    GROUP BY StockCode
    ORDER BY TotalRevenue DESC
    LIMIT 20
""").df()

# Customer acquisition by month
customer_acquisition = con.execute("""
    SELECT
        strftime(FirstPurchaseDate, '%Y-%m') as Month,
        COUNT(*) as NewCustomers,
        SUM(TotalRevenue) as Revenue
    FROM customers
    GROUP BY Month
    ORDER BY Month
""").df()

print("   ✓ Revenue trends calculated")
print("   ✓ Regional performance calculated")
print("   ✓ Product performance calculated")
print("   ✓ Customer acquisition calculated")

# Consolidate all metrics
print("\n[3/5] Consolidating all metrics...")

comprehensive_metrics = {
    'report_generated': datetime.now().isoformat(),
    'analysis_period': {
        'start_date': '2024-12-01',
        'end_date': '2025-02-28',
        'duration_months': 3
    },

    # Overview metrics
    'overview': {
        'total_revenue': float(ab_results['control_revenue'] + ab_results['treatment_revenue']),
        'total_customers': rfm_results['total_customers'],
        'total_orders': int(revenue_by_month['TotalOrders'].sum()),
        'avg_order_value': float(revenue_by_month['AvgTransactionValue'].mean()),
        'total_products': int(product_performance['StockCode'].nunique())
    },

    # A/B Testing Results
    'ab_testing': {
        'revenue_uplift_pct': ab_results['revenue_uplift_pct'],
        'order_frequency_uplift_pct': ab_results['order_frequency_uplift_pct'],
        'repeat_rate_uplift_pct': ab_results['repeat_rate_uplift_pct'],
        'roi_pct': ab_results['roi'],
        'statistically_significant': ab_results['significant_revenue'],
        'p_value': ab_results['p_value_revenue'],
        'recommendation': 'Do not implement' if ab_results['revenue_uplift_pct'] < 0 else 'Continue testing'
    },

    # Cohort & Retention
    'retention': {
        'month_0_retention_pct': cohort_results.get('month_0_avg_retention', 100),
        'month_1_retention_pct': cohort_results.get('month_1_avg_retention', 0),
        'month_2_retention_pct': cohort_results.get('month_2_avg_retention', 0),
        'month_3_retention_pct': cohort_results.get('month_3_avg_retention', 0),
        'baseline_churn_pct': cohort_results.get('baseline_month1_churn', 0),
        'target_churn_pct': cohort_results.get('target_month1_churn', 0),
        'churn_reduction_target_pct': cohort_results.get('churn_reduction_pct', 14.0),
        'avg_ltv': cohort_results.get('month_0_avg_retention', 0)  # placeholder
    },

    # Customer Segmentation
    'segmentation': {
        'total_segments': len(rfm_results['segments']),
        'top_segment': rfm_results['segments'][0]['Segment'],
        'top_segment_revenue_pct': rfm_results['segments'][0]['RevenuePercent'],
        'champions_pct': next((s['CustomerPercent'] for s in rfm_results['segments']
                               if s['Segment'] == 'Champions'), 0),
        'at_risk_pct': rfm_results['churn_risk_pct']
    },

    # Revenue Concentration
    'revenue_concentration': {
        'top_10_pct_customers_revenue_pct': rfm_results['top_10_pct_revenue_concentration'],
        'top_20_pct_customers_revenue_pct': rfm_results['top_20_pct_revenue_concentration'],
        'pareto_ratio': f"{rfm_results['top_20_pct_revenue_concentration']:.1f}% from top 20%"
    },

    # Customer Value
    'customer_value': {
        'avg_clv': rfm_results['avg_clv'],
        'median_clv': rfm_results['median_clv'],
        'high_value_customers': int(rfm_results['total_customers'] * 0.2),
        'high_value_revenue': float(rfm_results['total_revenue'] *
                                    rfm_results['top_20_pct_revenue_concentration'] / 100)
    },

    # Churn & Risk
    'churn_analysis': {
        'high_risk_customers': rfm_results['churn_risk_customers'],
        'high_risk_pct': rfm_results['churn_risk_pct'],
        'revenue_at_risk': rfm_results['churn_risk_revenue'],
        'revenue_at_risk_pct': rfm_results['churn_risk_revenue_pct']
    },

    # Growth metrics
    'growth': {
        'monthly_revenue_trend': revenue_by_month[['YearMonth', 'TotalRevenue']].to_dict('records'),
        'customer_acquisition_trend': customer_acquisition[['Month', 'NewCustomers']].to_dict('records'),
        'total_new_customers': int(customer_acquisition['NewCustomers'].sum())
    },

    # Geographic insights
    'geographic': {
        'top_region': revenue_by_region.iloc[0]['Region'] if len(revenue_by_region) > 0 else 'N/A',
        'top_region_revenue': float(revenue_by_region.iloc[0]['Revenue']) if len(revenue_by_region) > 0 else 0,
        'uk_regions_count': len(revenue_by_region),
        'regional_distribution': revenue_by_region.head(5).to_dict('records')
    },

    # Product insights
    'products': {
        'top_product_revenue': float(product_performance.iloc[0]['TotalRevenue']) if len(product_performance) > 0 else 0,
        'top_products': product_performance.head(10)[['StockCode', 'ProductName', 'TotalRevenue']].to_dict('records')
    }
}

# Save comprehensive metrics
with open('../outputs/comprehensive_metrics.json', 'w') as f:
    json.dump(comprehensive_metrics, f, indent=2)

print("   ✓ Consolidated all metrics")
print("   ✓ Saved to '../outputs/comprehensive_metrics.json'")

# Create KPI summary visualization
print("\n[4/5] Creating KPI summary visualization...")

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('E-Commerce Analytics - Key Performance Indicators', fontsize=16, fontweight='bold')

# 1. Total Revenue
ax1 = axes[0, 0]
ax1.text(0.5, 0.6, f"£{comprehensive_metrics['overview']['total_revenue']:,.0f}",
         ha='center', va='center', fontsize=32, fontweight='bold', color='#2ecc71')
ax1.text(0.5, 0.3, 'Total Revenue', ha='center', va='center', fontsize=14, color='#555')
ax1.text(0.5, 0.15, f"{comprehensive_metrics['analysis_period']['duration_months']} months",
         ha='center', va='center', fontsize=11, color='#888')
ax1.axis('off')

# 2. Total Customers
ax2 = axes[0, 1]
ax2.text(0.5, 0.6, f"{comprehensive_metrics['overview']['total_customers']:,}",
         ha='center', va='center', fontsize=32, fontweight='bold', color='#3498db')
ax2.text(0.5, 0.3, 'Total Customers', ha='center', va='center', fontsize=14, color='#555')
ax2.text(0.5, 0.15, f"Avg CLV: £{comprehensive_metrics['customer_value']['avg_clv']:.2f}",
         ha='center', va='center', fontsize=11, color='#888')
ax2.axis('off')

# 3. Average Order Value
ax3 = axes[0, 2]
ax3.text(0.5, 0.6, f"£{comprehensive_metrics['overview']['avg_order_value']:.2f}",
         ha='center', va='center', fontsize=32, fontweight='bold', color='#9b59b6')
ax3.text(0.5, 0.3, 'Avg Order Value', ha='center', va='center', fontsize=14, color='#555')
ax3.text(0.5, 0.15, f"{comprehensive_metrics['overview']['total_orders']:,} total orders",
         ha='center', va='center', fontsize=11, color='#888')
ax3.axis('off')

# 4. Revenue Concentration
ax4 = axes[1, 0]
ax4.text(0.5, 0.6, f"{comprehensive_metrics['revenue_concentration']['top_20_pct_customers_revenue_pct']:.1f}%",
         ha='center', va='center', fontsize=32, fontweight='bold', color='#e67e22')
ax4.text(0.5, 0.3, 'Revenue from Top 20%', ha='center', va='center', fontsize=14, color='#555')
ax4.text(0.5, 0.15, 'Customer Concentration',
         ha='center', va='center', fontsize=11, color='#888')
ax4.axis('off')

# 5. Churn Risk
ax5 = axes[1, 1]
ax5.text(0.5, 0.6, f"{comprehensive_metrics['churn_analysis']['high_risk_pct']:.1f}%",
         ha='center', va='center', fontsize=32, fontweight='bold', color='#e74c3c')
ax5.text(0.5, 0.3, 'Customers at Risk', ha='center', va='center', fontsize=14, color='#555')
ax5.text(0.5, 0.15, f"£{comprehensive_metrics['churn_analysis']['revenue_at_risk']:,.0f} revenue at risk",
         ha='center', va='center', fontsize=11, color='#888')
ax5.axis('off')

# 6. Month-1 Retention
ax6 = axes[1, 2]
retention_val = comprehensive_metrics['retention']['month_1_retention_pct']
ax6.text(0.5, 0.6, f"{retention_val:.1f}%",
         ha='center', va='center', fontsize=32, fontweight='bold', color='#16a085')
ax6.text(0.5, 0.3, 'Month-1 Retention', ha='center', va='center', fontsize=14, color='#555')
ax6.text(0.5, 0.15, f"Target: {100 - comprehensive_metrics['retention']['target_churn_pct']:.1f}%",
         ha='center', va='center', fontsize=11, color='#888')
ax6.axis('off')

plt.tight_layout()
plt.savefig('../outputs/kpi_summary.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved KPI summary to '../outputs/kpi_summary.png'")

# Create revenue trend chart
print("\n[5/5] Creating revenue trend visualization...")

fig, ax = plt.subplots(figsize=(12, 6))

months = [d['YearMonth'] for d in comprehensive_metrics['growth']['monthly_revenue_trend']]
revenues = [d['TotalRevenue'] for d in comprehensive_metrics['growth']['monthly_revenue_trend']]

ax.plot(months, revenues, marker='o', linewidth=3, markersize=10, color='#2ecc71')
ax.fill_between(range(len(months)), revenues, alpha=0.3, color='#2ecc71')

for i, (month, revenue) in enumerate(zip(months, revenues)):
    ax.text(i, revenue + max(revenues) * 0.05, f'£{revenue:,.0f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Revenue (£)', fontsize=12)
ax.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xticks(range(len(months)))
ax.set_xticklabels(months)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}K'))

plt.tight_layout()
plt.savefig('../outputs/revenue_trend.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved revenue trend to '../outputs/revenue_trend.png'")

# Save supporting data for dashboard
revenue_by_month.to_csv('../outputs/revenue_by_month.csv', index=False)
revenue_by_region.to_csv('../outputs/revenue_by_region.csv', index=False)
product_performance.to_csv('../outputs/product_performance.csv', index=False)
customer_acquisition.to_csv('../outputs/customer_acquisition.csv', index=False)

print("   ✓ Saved supporting data files")

# Print executive summary
print("\n" + "=" * 80)
print("EXECUTIVE SUMMARY - KEY FINDINGS")
print("=" * 80)

print(f"\n💼 BUSINESS OVERVIEW:")
print(f"   • Total Revenue: £{comprehensive_metrics['overview']['total_revenue']:,.2f}")
print(f"   • Total Customers: {comprehensive_metrics['overview']['total_customers']:,}")
print(f"   • Average Order Value: £{comprehensive_metrics['overview']['avg_order_value']:.2f}")
print(f"   • Total Orders: {comprehensive_metrics['overview']['total_orders']:,}")

print(f"\n📊 A/B TESTING (Discount Strategy):")
print(f"   • Revenue Impact: {comprehensive_metrics['ab_testing']['revenue_uplift_pct']:+.2f}%")
print(f"   • Order Frequency: {comprehensive_metrics['ab_testing']['order_frequency_uplift_pct']:+.2f}%")
print(f"   • ROI: {comprehensive_metrics['ab_testing']['roi_pct']:.2f}%")
print(f"   • Recommendation: {comprehensive_metrics['ab_testing']['recommendation']}")

print(f"\n👥 CUSTOMER INSIGHTS:")
print(f"   • Top Segment: {comprehensive_metrics['segmentation']['top_segment']} "
      f"({comprehensive_metrics['segmentation']['top_segment_revenue_pct']:.1f}% of revenue)")
print(f"   • Top 20% drive: {comprehensive_metrics['revenue_concentration']['top_20_pct_customers_revenue_pct']:.1f}% of revenue")
print(f"   • Average CLV: £{comprehensive_metrics['customer_value']['avg_clv']:.2f}")

print(f"\n📈 RETENTION & CHURN:")
print(f"   • Month-1 Retention: {comprehensive_metrics['retention']['month_1_retention_pct']:.2f}%")
print(f"   • Customers at Risk: {comprehensive_metrics['churn_analysis']['high_risk_pct']:.1f}%")
print(f"   • Revenue at Risk: £{comprehensive_metrics['churn_analysis']['revenue_at_risk']:,.2f}")

print(f"\n🌍 TOP REGION:")
print(f"   • {comprehensive_metrics['geographic']['top_region']}: "
      f"£{comprehensive_metrics['geographic']['top_region_revenue']:,.2f}")

print("\n✅ Comprehensive metrics analysis complete!")
print("=" * 80)

con.close()
