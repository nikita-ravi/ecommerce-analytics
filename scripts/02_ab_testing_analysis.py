"""
E-Commerce Analytics: A/B Testing Analysis for Discount Strategies
Author: Portfolio Project
Date: 2025-11-21

This script performs comprehensive A/B testing analysis comparing Control vs Treatment groups
for discount strategy effectiveness with statistical significance testing.
"""

import pandas as pd
import numpy as np
import duckdb
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime

print("=" * 80)
print("A/B TESTING ANALYSIS - DISCOUNT STRATEGY EFFECTIVENESS")
print("=" * 80)

# Connect to database
con = duckdb.connect('../data/ecommerce.db', read_only=True)

# Extract A/B test data
print("\n[1/7] Loading A/B test data...")

ab_data = con.execute("""
    SELECT
        CustomerID,
        TestGroup,
        InvoiceNo,
        InvoiceDate,
        Revenue,
        DiscountedRevenue,
        DiscountAmount,
        DiscountRate,
        Quantity
    FROM transactions
""").df()

print(f"   ✓ Loaded {len(ab_data):,} transactions")

# Customer-level aggregation
print("\n[2/7] Aggregating customer-level metrics...")

customer_metrics = con.execute("""
    SELECT
        CustomerID,
        TestGroup,
        COUNT(DISTINCT InvoiceNo) as TotalOrders,
        SUM(Quantity) as TotalItems,
        SUM(Revenue) as TotalRevenue,
        SUM(DiscountedRevenue) as TotalDiscountedRevenue,
        SUM(DiscountAmount) as TotalDiscountAmount,
        AVG(Revenue) as AvgOrderValue,
        COUNT(*) as TotalTransactions,
        MIN(InvoiceDate) as FirstPurchase,
        MAX(InvoiceDate) as LastPurchase
    FROM transactions
    GROUP BY CustomerID, TestGroup
""").df()

control_customers = customer_metrics[customer_metrics['TestGroup'] == 'Control']
treatment_customers = customer_metrics[customer_metrics['TestGroup'] == 'Treatment']

print(f"   ✓ Control Group: {len(control_customers):,} customers")
print(f"   ✓ Treatment Group: {len(treatment_customers):,} customers")

# Calculate key metrics
print("\n[3/7] Calculating A/B test metrics...")

results = {}

# Revenue metrics
control_revenue = control_customers['TotalRevenue'].sum()
treatment_revenue = treatment_customers['TotalDiscountedRevenue'].sum()
treatment_cost = treatment_customers['TotalDiscountAmount'].sum()

results['control_revenue'] = control_revenue
results['treatment_revenue'] = treatment_revenue
results['treatment_cost'] = treatment_cost
results['revenue_uplift_pct'] = ((treatment_revenue - control_revenue) / control_revenue) * 100
results['roi'] = ((treatment_revenue - control_revenue - treatment_cost) / treatment_cost) * 100 if treatment_cost > 0 else 0

# Customer metrics
results['control_customers'] = len(control_customers)
results['treatment_customers'] = len(treatment_customers)
results['control_avg_revenue_per_customer'] = control_customers['TotalRevenue'].mean()
results['treatment_avg_revenue_per_customer'] = treatment_customers['TotalDiscountedRevenue'].mean()
results['control_avg_orders_per_customer'] = control_customers['TotalOrders'].mean()
results['treatment_avg_orders_per_customer'] = treatment_customers['TotalOrders'].mean()

# Order frequency uplift
results['order_frequency_uplift_pct'] = ((results['treatment_avg_orders_per_customer'] -
                                          results['control_avg_orders_per_customer']) /
                                         results['control_avg_orders_per_customer']) * 100

# Average order value
control_aov = control_customers['AvgOrderValue'].mean()
treatment_aov = treatment_customers['AvgOrderValue'].mean()
results['control_aov'] = control_aov
results['treatment_aov'] = treatment_aov
results['aov_change_pct'] = ((treatment_aov - control_aov) / control_aov) * 100

print(f"\n   CONTROL GROUP METRICS:")
print(f"   • Total Revenue: £{control_revenue:,.2f}")
print(f"   • Customers: {len(control_customers):,}")
print(f"   • Avg Revenue/Customer: £{results['control_avg_revenue_per_customer']:,.2f}")
print(f"   • Avg Orders/Customer: {results['control_avg_orders_per_customer']:.2f}")
print(f"   • Average Order Value: £{control_aov:.2f}")

print(f"\n   TREATMENT GROUP METRICS:")
print(f"   • Total Revenue (after discount): £{treatment_revenue:,.2f}")
print(f"   • Discount Cost: £{treatment_cost:,.2f}")
print(f"   • Customers: {len(treatment_customers):,}")
print(f"   • Avg Revenue/Customer: £{results['treatment_avg_revenue_per_customer']:,.2f}")
print(f"   • Avg Orders/Customer: {results['treatment_avg_orders_per_customer']:.2f}")
print(f"   • Average Order Value: £{treatment_aov:.2f}")

# Statistical significance tests
print("\n[4/7] Performing statistical significance tests...")

# 1. Two-sample t-test for revenue per customer
t_stat_revenue, p_value_revenue = stats.ttest_ind(
    control_customers['TotalRevenue'],
    treatment_customers['TotalDiscountedRevenue']
)
results['t_stat_revenue'] = t_stat_revenue
results['p_value_revenue'] = p_value_revenue
results['significant_revenue'] = p_value_revenue < 0.05

print(f"\n   Revenue per Customer T-Test:")
print(f"   • t-statistic: {t_stat_revenue:.4f}")
print(f"   • p-value: {p_value_revenue:.4f}")
print(f"   • Significant (p < 0.05): {'✓ YES' if results['significant_revenue'] else '✗ NO'}")

# 2. Two-sample t-test for orders per customer
t_stat_orders, p_value_orders = stats.ttest_ind(
    control_customers['TotalOrders'],
    treatment_customers['TotalOrders']
)
results['t_stat_orders'] = t_stat_orders
results['p_value_orders'] = p_value_orders
results['significant_orders'] = p_value_orders < 0.05

print(f"\n   Orders per Customer T-Test:")
print(f"   • t-statistic: {t_stat_orders:.4f}")
print(f"   • p-value: {p_value_orders:.4f}")
print(f"   • Significant (p < 0.05): {'✓ YES' if results['significant_orders'] else '✗ NO'}")

# 3. Effect size (Cohen's d)
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (group1.mean() - group2.mean()) / pooled_std

cohens_d_revenue = cohens_d(treatment_customers['TotalDiscountedRevenue'],
                             control_customers['TotalRevenue'])
results['cohens_d_revenue'] = cohens_d_revenue

cohens_d_orders = cohens_d(treatment_customers['TotalOrders'],
                           control_customers['TotalOrders'])
results['cohens_d_orders'] = cohens_d_orders

print(f"\n   Effect Sizes (Cohen's d):")
print(f"   • Revenue: {cohens_d_revenue:.4f} ({'Small' if abs(cohens_d_revenue) < 0.5 else 'Medium' if abs(cohens_d_revenue) < 0.8 else 'Large'})")
print(f"   • Orders: {cohens_d_orders:.4f} ({'Small' if abs(cohens_d_orders) < 0.5 else 'Medium' if abs(cohens_d_orders) < 0.8 else 'Large'})")

# 4. Confidence intervals
from scipy import stats as st

def confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = data.mean()
    se = stats.sem(data)
    margin = se * st.t.ppf((1 + confidence) / 2, n - 1)
    return mean - margin, mean + margin

control_ci = confidence_interval(control_customers['TotalRevenue'])
treatment_ci = confidence_interval(treatment_customers['TotalDiscountedRevenue'])

results['control_revenue_ci_lower'] = control_ci[0]
results['control_revenue_ci_upper'] = control_ci[1]
results['treatment_revenue_ci_lower'] = treatment_ci[0]
results['treatment_revenue_ci_upper'] = treatment_ci[1]

print(f"\n   95% Confidence Intervals (Revenue per Customer):")
print(f"   • Control: £{control_ci[0]:.2f} - £{control_ci[1]:.2f}")
print(f"   • Treatment: £{treatment_ci[0]:.2f} - £{treatment_ci[1]:.2f}")

# Customer behavior analysis
print("\n[5/7] Analyzing customer behavior changes...")

# Repeat purchase analysis (customers with >1 order)
control_repeat = (control_customers['TotalOrders'] > 1).sum()
treatment_repeat = (treatment_customers['TotalOrders'] > 1).sum()

control_repeat_rate = control_repeat / len(control_customers) * 100
treatment_repeat_rate = treatment_repeat / len(treatment_customers) * 100

results['control_repeat_rate'] = control_repeat_rate
results['treatment_repeat_rate'] = treatment_repeat_rate
results['repeat_rate_uplift_pct'] = treatment_repeat_rate - control_repeat_rate

print(f"\n   Repeat Purchase Rates:")
print(f"   • Control: {control_repeat_rate:.2f}%")
print(f"   • Treatment: {treatment_repeat_rate:.2f}%")
print(f"   • Uplift: {results['repeat_rate_uplift_pct']:.2f} percentage points")

# Chi-square test for repeat purchase rates
contingency_table = np.array([
    [control_repeat, len(control_customers) - control_repeat],
    [treatment_repeat, len(treatment_customers) - treatment_repeat]
])

chi2, p_value_chi2, dof, expected = stats.chi2_contingency(contingency_table)
results['chi2_stat'] = chi2
results['p_value_chi2'] = p_value_chi2
results['significant_repeat_rate'] = p_value_chi2 < 0.05

print(f"\n   Chi-Square Test (Repeat Purchase Rates):")
print(f"   • χ² statistic: {chi2:.4f}")
print(f"   • p-value: {p_value_chi2:.4f}")
print(f"   • Significant (p < 0.05): {'✓ YES' if results['significant_repeat_rate'] else '✗ NO'}")

# Save results
print("\n[6/7] Saving A/B test results...")

# Convert numpy types to Python native types for JSON serialization
results_json = {}
for k, v in results.items():
    if isinstance(v, (np.integer, np.floating)):
        results_json[k] = float(v)
    elif isinstance(v, np.bool_):
        results_json[k] = bool(v)
    else:
        results_json[k] = v
results_json['analysis_date'] = datetime.now().isoformat()

with open('../outputs/ab_test_results.json', 'w') as f:
    json.dump(results_json, f, indent=2)

print(f"   ✓ Saved results to '../outputs/ab_test_results.json'")

# Create visualization
print("\n[7/7] Creating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('A/B Testing Analysis: Discount Strategy Performance', fontsize=16, fontweight='bold')

# 1. Revenue comparison
ax1 = axes[0, 0]
groups = ['Control', 'Treatment']
revenues = [control_revenue, treatment_revenue]
colors = ['#3498db', '#2ecc71']
bars = ax1.bar(groups, revenues, color=colors, alpha=0.7, edgecolor='black')
ax1.set_ylabel('Total Revenue (£)', fontsize=12)
ax1.set_title('Total Revenue by Group', fontsize=13, fontweight='bold')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}K'))
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'£{height:,.0f}', ha='center', va='bottom', fontsize=11)

# 2. Average revenue per customer
ax2 = axes[0, 1]
avg_revenues = [results['control_avg_revenue_per_customer'],
                results['treatment_avg_revenue_per_customer']]
bars = ax2.bar(groups, avg_revenues, color=colors, alpha=0.7, edgecolor='black')
ax2.set_ylabel('Avg Revenue per Customer (£)', fontsize=12)
ax2.set_title('Average Revenue per Customer', fontsize=13, fontweight='bold')
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'£{height:.2f}', ha='center', va='bottom', fontsize=11)

# 3. Orders per customer
ax3 = axes[0, 2]
avg_orders = [results['control_avg_orders_per_customer'],
              results['treatment_avg_orders_per_customer']]
bars = ax3.bar(groups, avg_orders, color=colors, alpha=0.7, edgecolor='black')
ax3.set_ylabel('Avg Orders per Customer', fontsize=12)
ax3.set_title('Average Orders per Customer', fontsize=13, fontweight='bold')
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}', ha='center', va='bottom', fontsize=11)

# 4. Revenue distribution
ax4 = axes[1, 0]
ax4.hist(control_customers['TotalRevenue'], bins=50, alpha=0.6, label='Control',
         color='#3498db', edgecolor='black')
ax4.hist(treatment_customers['TotalDiscountedRevenue'], bins=50, alpha=0.6,
         label='Treatment', color='#2ecc71', edgecolor='black')
ax4.set_xlabel('Revenue per Customer (£)', fontsize=12)
ax4.set_ylabel('Frequency', fontsize=12)
ax4.set_title('Revenue Distribution by Group', fontsize=13, fontweight='bold')
ax4.legend()
ax4.set_xlim(0, 2000)

# 5. Key metrics summary
ax5 = axes[1, 1]
ax5.axis('off')
summary_text = f"""
KEY FINDINGS

Revenue Uplift: {results['revenue_uplift_pct']:.2f}%
Order Frequency Uplift: {results['order_frequency_uplift_pct']:.2f}%
Repeat Rate Increase: {results['repeat_rate_uplift_pct']:.2f}pp

STATISTICAL SIGNIFICANCE
Revenue p-value: {p_value_revenue:.4f}
{"✓ Significant" if results['significant_revenue'] else "✗ Not Significant"}

Orders p-value: {p_value_orders:.4f}
{"✓ Significant" if results['significant_orders'] else "✗ Not Significant"}

ROI: {results['roi']:.2f}%
Discount Cost: £{treatment_cost:,.2f}
Net Impact: £{treatment_revenue - control_revenue - treatment_cost:,.2f}
"""
ax5.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
         verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

# 6. Repeat purchase rates
ax6 = axes[1, 2]
repeat_rates = [control_repeat_rate, treatment_repeat_rate]
bars = ax6.bar(groups, repeat_rates, color=colors, alpha=0.7, edgecolor='black')
ax6.set_ylabel('Repeat Purchase Rate (%)', fontsize=12)
ax6.set_title('Repeat Purchase Rate by Group', fontsize=13, fontweight='bold')
for bar in bars:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}%', ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig('../outputs/ab_test_analysis.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved visualization to '../outputs/ab_test_analysis.png'")

# Summary report
print("\n" + "=" * 80)
print("A/B TEST SUMMARY - DISCOUNT STRATEGY")
print("=" * 80)
print(f"\n🎯 PRIMARY OUTCOME:")
print(f"   Revenue Uplift: {results['revenue_uplift_pct']:+.2f}%")
print(f"   Statistical Significance: {'✓ YES (p={p_value_revenue:.4f})' if results['significant_revenue'] else '✗ NO'}")

print(f"\n📊 SECONDARY OUTCOMES:")
print(f"   • Order Frequency Uplift: {results['order_frequency_uplift_pct']:+.2f}%")
print(f"   • Repeat Purchase Rate Increase: {results['repeat_rate_uplift_pct']:+.2f} percentage points")
print(f"   • Average Order Value Change: {results['aov_change_pct']:+.2f}%")

print(f"\n💰 FINANCIAL IMPACT:")
print(f"   • Control Revenue: £{control_revenue:,.2f}")
print(f"   • Treatment Revenue: £{treatment_revenue:,.2f}")
print(f"   • Discount Investment: £{treatment_cost:,.2f}")
print(f"   • Net Revenue Impact: £{treatment_revenue - control_revenue:,.2f}")
print(f"   • ROI: {results['roi']:.2f}%")

print(f"\n✅ RECOMMENDATION:")
if results['significant_revenue'] and results['revenue_uplift_pct'] > 0 and results['roi'] > 0:
    print(f"   → IMPLEMENT discount strategy across all customers")
    print(f"   → Expected revenue increase: {results['revenue_uplift_pct']:.2f}%")
    print(f"   → Strong ROI of {results['roi']:.2f}%")
elif results['revenue_uplift_pct'] > 0 and not results['significant_revenue']:
    print(f"   → CONTINUE TESTING with larger sample size")
    print(f"   → Current results show positive trend but lack statistical significance")
else:
    print(f"   → DO NOT IMPLEMENT discount strategy")
    print(f"   → No significant improvement detected")

print("\n" + "=" * 80)

con.close()
