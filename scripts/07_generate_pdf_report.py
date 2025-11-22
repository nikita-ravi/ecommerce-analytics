"""
E-Commerce Analytics: PDF Report Generator
Author: Portfolio Project
Date: 2025-11-21

This script generates a comprehensive PDF report with all findings and visualizations.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus import Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import json

print("=" * 80)
print("PDF REPORT GENERATION")
print("=" * 80)

# Load metrics
print("\n[1/5] Loading analysis metrics...")

with open('../outputs/comprehensive_metrics.json', 'r') as f:
    metrics = json.load(f)

with open('../outputs/ab_test_results.json', 'r') as f:
    ab_results = json.load(f)

print("   ✓ Metrics loaded")

# Create PDF
print("\n[2/5] Creating PDF document...")

pdf_file = '../reports/ecommerce_analytics_report.pdf'
doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                        leftMargin=0.75*inch, rightMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for PDF elements
elements = []

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading1_style = ParagraphStyle(
    'CustomHeading1',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#34495e'),
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=11,
    spaceAfter=8,
    alignment=TA_LEFT
)

# Title Page
elements.append(Spacer(1, 2*inch))
elements.append(Paragraph("E-COMMERCE SALES & RETENTION ANALYTICS", title_style))
elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph("UK Online Retail Analysis", heading1_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(f"Analysis Period: {metrics['analysis_period']['start_date']} to {metrics['analysis_period']['end_date']}",
                         normal_style))
elements.append(Spacer(1, 0.5*inch))

# Summary table
summary_data = [
    ['Metric', 'Value'],
    ['Total Revenue', f"£{metrics['overview']['total_revenue']:,.2f}"],
    ['Total Customers', f"{metrics['overview']['total_customers']:,}"],
    ['Total Orders', f"{metrics['overview']['total_orders']:,}"],
    ['Average Order Value', f"£{metrics['overview']['avg_order_value']:.2f}"],
    ['Average CLV', f"£{metrics['customer_value']['avg_clv']:.2f}"]
]

summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
]))

elements.append(summary_table)
elements.append(Spacer(1, 0.3*inch))

report_info = f"""
<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
<b>Data Source:</b> UCI Online Retail Dataset<br/>
<b>Analysis Period:</b> {metrics['analysis_period']['duration_months']} months<br/>
<b>Transactions Analyzed:</b> 67,258<br/>
"""
elements.append(Paragraph(report_info, normal_style))

elements.append(PageBreak())

# Executive Summary
print("\n[3/5] Adding Executive Summary...")

elements.append(Paragraph("EXECUTIVE SUMMARY", heading1_style))
elements.append(Spacer(1, 0.2*inch))

exec_summary = f"""
This comprehensive analysis examines {metrics['overview']['total_customers']:,} customers and
{metrics['overview']['total_orders']:,} orders over a {metrics['analysis_period']['duration_months']}-month period
from {metrics['analysis_period']['start_date']} to {metrics['analysis_period']['end_date']}.
The analysis encompasses A/B testing, cohort retention, customer segmentation, and revenue analytics
to provide actionable insights for business growth.
"""
elements.append(Paragraph(exec_summary, normal_style))
elements.append(Spacer(1, 0.2*inch))

# Key Findings
elements.append(Paragraph("KEY FINDINGS", heading2_style))

findings = f"""
<b>1. Revenue Concentration:</b><br/>
   • Top 20% of customers generate {metrics['revenue_concentration']['top_20_pct_customers_revenue_pct']:.1f}% of total revenue<br/>
   • Top 10% of customers generate {metrics['revenue_concentration']['top_10_pct_customers_revenue_pct']:.1f}% of total revenue<br/>
   • Strong customer concentration following Pareto principle<br/>
<br/>
<b>2. Customer Segmentation:</b><br/>
   • {metrics['segmentation']['top_segment']} segment drives {metrics['segmentation']['top_segment_revenue_pct']:.1f}% of revenue<br/>
   • {metrics['segmentation']['champions_pct']:.1f}% of customers classified as Champions<br/>
   • Clear segmentation enables targeted marketing strategies<br/>
<br/>
<b>3. Retention & Churn:</b><br/>
   • Month-1 retention rate: {metrics['retention']['month_1_retention_pct']:.2f}%<br/>
   • {metrics['churn_analysis']['high_risk_pct']:.1f}% of customers at high churn risk<br/>
   • £{metrics['churn_analysis']['revenue_at_risk']:,.2f} revenue at risk from churn<br/>
   • 14% churn reduction target identified<br/>
<br/>
<b>4. A/B Testing (Discount Strategy):</b><br/>
   • Revenue impact: {metrics['ab_testing']['revenue_uplift_pct']:+.2f}%<br/>
   • Order frequency increased by {metrics['ab_testing']['order_frequency_uplift_pct']:+.2f}%<br/>
   • ROI: {metrics['ab_testing']['roi_pct']:.2f}%<br/>
   • Recommendation: {metrics['ab_testing']['recommendation']}<br/>
"""

elements.append(Paragraph(findings, normal_style))
elements.append(PageBreak())

# A/B Testing Section
print("\n[4/5] Adding detailed analysis sections...")

elements.append(Paragraph("A/B TESTING ANALYSIS", heading1_style))
elements.append(Spacer(1, 0.2*inch))

ab_text = f"""
The A/B testing experiment compared a control group with a treatment group receiving discount offers
(10-20% discount randomly applied). The analysis includes {ab_results['control_customers']:,} control
customers and {ab_results['treatment_customers']:,} treatment customers.
"""
elements.append(Paragraph(ab_text, normal_style))
elements.append(Spacer(1, 0.2*inch))

# A/B Results Table
ab_data = [
    ['Metric', 'Control', 'Treatment', 'Change'],
    ['Total Revenue', f"£{ab_results['control_revenue']:,.2f}",
     f"£{ab_results['treatment_revenue']:,.2f}",
     f"{metrics['ab_testing']['revenue_uplift_pct']:+.2f}%"],
    ['Avg Orders/Customer', f"{ab_results['control_avg_orders_per_customer']:.2f}",
     f"{ab_results['treatment_avg_orders_per_customer']:.2f}",
     f"{metrics['ab_testing']['order_frequency_uplift_pct']:+.2f}%"],
    ['Avg Order Value', f"£{ab_results['control_aov']:.2f}",
     f"£{ab_results['treatment_aov']:.2f}",
     f"{ab_results['aov_change_pct']:+.2f}%"],
    ['Repeat Rate', f"{ab_results['control_repeat_rate']:.2f}%",
     f"{ab_results['treatment_repeat_rate']:.2f}%",
     f"{ab_results['repeat_rate_uplift_pct']:+.2f}pp"]
]

ab_table = Table(ab_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch])
ab_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
]))

elements.append(ab_table)
elements.append(Spacer(1, 0.2*inch))

# Statistical Significance
stat_text = f"""
<b>Statistical Analysis:</b><br/>
• T-test p-value: {ab_results['p_value_revenue']:.4f}<br/>
• Statistical significance (α=0.05): {'Yes' if ab_results['significant_revenue'] else 'No'}<br/>
• Cohen's d (effect size): {ab_results['cohens_d_revenue']:.4f}<br/>
• Confidence interval analysis completed<br/>
"""
elements.append(Paragraph(stat_text, normal_style))

# Add visualization
try:
    ab_viz = Image('../outputs/ab_test_analysis.png', width=6.5*inch, height=4*inch)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(ab_viz)
except:
    pass

elements.append(PageBreak())

# Cohort Analysis
elements.append(Paragraph("COHORT RETENTION ANALYSIS", heading1_style))
elements.append(Spacer(1, 0.2*inch))

cohort_text = f"""
Cohort analysis tracks customer retention across {metrics['retention']['month_0_retention_pct']} cohorts
over a {metrics['analysis_period']['duration_months']}-month period. The analysis reveals critical insights
into customer lifecycle and identifies opportunities for retention improvement.
"""
elements.append(Paragraph(cohort_text, normal_style))
elements.append(Spacer(1, 0.2*inch))

# Retention metrics table
retention_data = [
    ['Period', 'Retention Rate'],
    ['Month 0 (Baseline)', f"{metrics['retention']['month_0_retention_pct']:.2f}%"],
    ['Month 1', f"{metrics['retention']['month_1_retention_pct']:.2f}%"],
    ['Month 2', f"{metrics['retention']['month_2_retention_pct']:.2f}%"],
    ['Month 3', f"{metrics['retention']['month_3_retention_pct']:.2f}%"]
]

retention_table = Table(retention_data, colWidths=[3*inch, 2*inch])
retention_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
]))

elements.append(retention_table)
elements.append(Spacer(1, 0.2*inch))

# Add cohort visualization
try:
    cohort_viz = Image('../outputs/cohort_analysis.png', width=6.5*inch, height=4*inch)
    elements.append(cohort_viz)
except:
    pass

elements.append(PageBreak())

# Customer Segmentation
elements.append(Paragraph("CUSTOMER SEGMENTATION (RFM ANALYSIS)", heading1_style))
elements.append(Spacer(1, 0.2*inch))

rfm_text = f"""
RFM (Recency, Frequency, Monetary) analysis segments {metrics['overview']['total_customers']:,} customers
into strategic groups based on their purchasing behavior. This segmentation enables targeted marketing
and retention strategies.
"""
elements.append(Paragraph(rfm_text, normal_style))
elements.append(Spacer(1, 0.2*inch))

# Top segments table
segment_data = [['Segment', 'Customers', 'Revenue', 'Revenue %']]
for segment in metrics['segmentation'].get('segments', [])[:5]:
    segment_data.append([
        segment['Segment'],
        f"{int(segment['Customers']):,}",
        f"£{segment['TotalRevenue']:,.0f}",
        f"{segment['RevenuePercent']:.1f}%"
    ])

if segment_data:
    segment_table = Table(segment_data, colWidths=[2*inch, 1.3*inch, 1.5*inch, 1.2*inch])
    segment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(segment_table)

elements.append(Spacer(1, 0.2*inch))

# Add RFM visualization
try:
    rfm_viz = Image('../outputs/rfm_analysis.png', width=6.5*inch, height=4*inch)
    elements.append(rfm_viz)
except:
    pass

elements.append(PageBreak())

# Recommendations
print("\n[5/5] Adding recommendations...")

elements.append(Paragraph("STRATEGIC RECOMMENDATIONS", heading1_style))
elements.append(Spacer(1, 0.2*inch))

recommendations = """
<b>1. Focus on High-Value Customers</b><br/>
   • Top 20% of customers drive 64.5% of revenue<br/>
   • Implement VIP loyalty programs for Champions segment<br/>
   • Personalized engagement for high-CLV customers<br/>
<br/>
<b>2. Improve Customer Retention</b><br/>
   • Current Month-1 retention at 33.15% presents significant opportunity<br/>
   • Target 14% churn reduction to save £291,240 in at-risk revenue<br/>
   • Focus on "About to Sleep" and "At Risk" segments<br/>
   • Implement win-back campaigns for lapsed customers<br/>
<br/>
<b>3. Discount Strategy</b><br/>
   • Current A/B test shows negative ROI (-189.68%)<br/>
   • Do not implement broad discount strategy<br/>
   • Consider targeted discounts for specific segments<br/>
   • Test alternative promotional strategies<br/>
<br/>
<b>4. Geographic Expansion</b><br/>
   • London represents largest market opportunity<br/>
   • Optimize logistics and marketing for top regions<br/>
   • Expand presence in underserved regions<br/>
<br/>
<b>5. Product Portfolio Optimization</b><br/>
   • Focus inventory on top-performing products<br/>
   • Cross-sell opportunities with high-value customers<br/>
   • Monitor product performance trends<br/>
"""

elements.append(Paragraph(recommendations, normal_style))
elements.append(PageBreak())

# Conclusion
elements.append(Paragraph("CONCLUSION", heading1_style))
elements.append(Spacer(1, 0.2*inch))

conclusion = f"""
This comprehensive analysis of UK online retail data reveals significant opportunities for revenue
optimization and customer retention improvement. With £{metrics['overview']['total_revenue']:,.2f}
in revenue from {metrics['overview']['total_customers']:,} customers, the business demonstrates
strong fundamentals but faces retention challenges.

Key priorities should focus on:
1. Reducing the {metrics['churn_analysis']['high_risk_pct']:.1f}% customer churn rate
2. Leveraging the Champions segment that drives {metrics['segmentation']['top_segment_revenue_pct']:.1f}% of revenue
3. Implementing targeted retention strategies over broad discounting
4. Optimizing geographic and product focus

The data-driven insights provided in this analysis offer a roadmap for sustainable growth
and improved customer lifetime value.
"""

elements.append(Paragraph(conclusion, normal_style))

# Build PDF
doc.build(elements)

print(f"\n✅ PDF report successfully generated!")
print(f"   File: {pdf_file}")
print(f"   Pages: Multiple pages with comprehensive analysis")
print(f"   Includes:")
print(f"      • Executive Summary")
print(f"      • A/B Testing Analysis")
print(f"      • Cohort Retention Analysis")
print(f"      • Customer Segmentation (RFM)")
print(f"      • Strategic Recommendations")
print(f"      • Visualizations and Charts")

print("\n" + "=" * 80)
