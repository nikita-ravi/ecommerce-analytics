"""
E-Commerce Analytics Dashboard
Interactive Streamlit Dashboard for UK Online Retail Analysis

Run with: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import duckdb
from datetime import datetime
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ecc71;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Get base directory (works both locally and on Streamlit Cloud)
def get_project_root():
    """Get the project root directory"""
    current_file = Path(__file__).resolve()
    # Go up from dashboards/ to project root
    return current_file.parent.parent

# Load data
@st.cache_data
def load_data():
    """Load all analysis data"""
    project_root = get_project_root()
    data_dir = project_root / 'data'
    outputs_dir = project_root / 'outputs'

    con = duckdb.connect(str(data_dir / 'ecommerce.db'), read_only=True)

    # Load comprehensive metrics
    with open(outputs_dir / 'comprehensive_metrics.json', 'r') as f:
        metrics = json.load(f)

    # Load detailed data
    rfm_data = pd.read_csv(outputs_dir / 'rfm_customer_data.csv')
    cohort_data = pd.read_csv(outputs_dir / 'cohort_data.csv')
    retention_matrix = pd.read_csv(outputs_dir / 'retention_matrix.csv', index_col=0)
    segment_summary = pd.read_csv(outputs_dir / 'rfm_segment_summary.csv')
    revenue_by_month = pd.read_csv(outputs_dir / 'revenue_by_month.csv')
    revenue_by_region = pd.read_csv(outputs_dir / 'revenue_by_region.csv')
    product_performance = pd.read_csv(outputs_dir / 'product_performance.csv')

    # Load transaction data for detailed analysis
    transactions = con.execute("SELECT * FROM transactions").df()

    con.close()

    return {
        'metrics': metrics,
        'rfm_data': rfm_data,
        'cohort_data': cohort_data,
        'retention_matrix': retention_matrix,
        'segment_summary': segment_summary,
        'revenue_by_month': revenue_by_month,
        'revenue_by_region': revenue_by_region,
        'product_performance': product_performance,
        'transactions': transactions
    }

# Load all data
data = load_data()
metrics = data['metrics']

# Header
st.markdown('<h1 class="main-header">📊 E-Commerce Sales & Retention Analytics Dashboard</h1>',
            unsafe_allow_html=True)
st.markdown(f"**Analysis Period:** {metrics['analysis_period']['start_date']} to "
            f"{metrics['analysis_period']['end_date']} "
            f"({metrics['analysis_period']['duration_months']} months)")

# Sidebar
with st.sidebar:
    st.header("🎯 Navigation")
    page = st.radio(
        "Select Analysis",
        ["Executive Overview", "A/B Testing", "Cohort Retention",
         "Customer Segmentation", "Geographic Analysis", "Product Performance"]
    )

    st.markdown("---")
    st.header("📈 Quick Insights")
    st.metric("Total Revenue", f"£{metrics['overview']['total_revenue']:,.0f}")
    st.metric("Total Customers", f"{metrics['overview']['total_customers']:,}")
    st.metric("Avg CLV", f"£{metrics['customer_value']['avg_clv']:.2f}")

    st.markdown("---")
    st.info("""
    **Data Source:** UCI Online Retail Dataset
    **Period:** Dec 2024 - Feb 2025
    **Customers:** 1,677
    **Transactions:** 67,258
    """)

# ============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ============================================================================
if page == "Executive Overview":
    st.header("📊 Executive Overview")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Revenue",
            f"£{metrics['overview']['total_revenue']:,.0f}",
            delta=None
        )

    with col2:
        st.metric(
            "Total Customers",
            f"{metrics['overview']['total_customers']:,}",
            delta=None
        )

    with col3:
        st.metric(
            "Average Order Value",
            f"£{metrics['overview']['avg_order_value']:.2f}",
            delta=None
        )

    with col4:
        st.metric(
            "Total Orders",
            f"{metrics['overview']['total_orders']:,}",
            delta=None
        )

    st.markdown("---")

    # Revenue Trend
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Monthly Revenue Trend")
        revenue_df = pd.DataFrame(metrics['growth']['monthly_revenue_trend'])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=revenue_df['YearMonth'],
            y=revenue_df['TotalRevenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)'
        ))

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (£)",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 Key Findings")
        st.markdown(f"""
        <div class="insight-box">
        <b>Top Segment:</b> {metrics['segmentation']['top_segment']}<br>
        <b>Revenue Share:</b> {metrics['segmentation']['top_segment_revenue_pct']:.1f}%<br><br>

        <b>Revenue Concentration:</b><br>
        • Top 20% of customers drive <b>{metrics['revenue_concentration']['top_20_pct_customers_revenue_pct']:.1f}%</b> of revenue<br><br>

        <b>Churn Risk:</b><br>
        • <b>{metrics['churn_analysis']['high_risk_pct']:.1f}%</b> of customers at risk<br>
        • <b>£{metrics['churn_analysis']['revenue_at_risk']:,.0f}</b> revenue at risk
        </div>
        """, unsafe_allow_html=True)

    # Customer Segments
    st.markdown("---")
    st.subheader("👥 Customer Segmentation Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Segment distribution pie chart
        segment_df = data['segment_summary']
        fig = px.pie(
            segment_df,
            values='Customers',
            names='Segment',
            title='Customer Distribution by Segment',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Segment revenue bar chart
        fig = px.bar(
            segment_df.sort_values('TotalRevenue', ascending=True),
            x='TotalRevenue',
            y='Segment',
            orientation='h',
            title='Revenue by Customer Segment',
            labels={'TotalRevenue': 'Revenue (£)', 'Segment': 'Customer Segment'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 2: A/B TESTING
# ============================================================================
elif page == "A/B Testing":
    st.header("🧪 A/B Testing Analysis: Discount Strategy")

    ab_metrics = metrics['ab_testing']

    # Key Results
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Revenue Impact",
            f"{ab_metrics['revenue_uplift_pct']:+.2f}%",
            delta=None,
            delta_color="normal"
        )

    with col2:
        st.metric(
            "Order Frequency",
            f"{ab_metrics['order_frequency_uplift_pct']:+.2f}%",
            delta=None
        )

    with col3:
        st.metric(
            "ROI",
            f"{ab_metrics['roi_pct']:.2f}%",
            delta=None
        )

    with col4:
        significance = "✅ Significant" if ab_metrics['statistically_significant'] else "❌ Not Significant"
        st.metric(
            "Statistical Significance",
            significance,
            delta=f"p={ab_metrics['p_value']:.4f}"
        )

    st.markdown("---")

    # Recommendation
    if ab_metrics['revenue_uplift_pct'] < 0:
        st.error(f"""
        **❌ RECOMMENDATION: DO NOT IMPLEMENT**

        The discount strategy resulted in a **{abs(ab_metrics['revenue_uplift_pct']):.2f}% decrease in revenue**,
        despite increasing order frequency by {ab_metrics['order_frequency_uplift_pct']:.2f}%.

        The negative ROI of {ab_metrics['roi_pct']:.2f}% indicates this strategy is not profitable.
        """)
    elif not ab_metrics['statistically_significant']:
        st.warning(f"""
        **⚠️ RECOMMENDATION: CONTINUE TESTING**

        While showing a {ab_metrics['revenue_uplift_pct']:+.2f}% revenue change,
        the results are not statistically significant (p={ab_metrics['p_value']:.4f} > 0.05).

        Recommend increasing sample size for conclusive results.
        """)
    else:
        st.success(f"""
        **✅ RECOMMENDATION: IMPLEMENT**

        The discount strategy shows a statistically significant
        {ab_metrics['revenue_uplift_pct']:+.2f}% revenue increase with strong ROI of {ab_metrics['roi_pct']:.2f}%.
        """)

    # A/B Test Results Visualization
    st.subheader("📊 Test Group Comparison")

    # Load A/B test results
    with open('../outputs/ab_test_results.json', 'r') as f:
        ab_data = json.load(f)

    col1, col2 = st.columns(2)

    with col1:
        # Revenue comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Control', 'Treatment'],
            y=[ab_data['control_revenue'], ab_data['treatment_revenue']],
            marker_color=['#3498db', '#2ecc71'],
            text=[f"£{ab_data['control_revenue']:,.0f}", f"£{ab_data['treatment_revenue']:,.0f}"],
            textposition='outside'
        ))
        fig.update_layout(
            title="Total Revenue by Group",
            yaxis_title="Revenue (£)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Orders per customer comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Control', 'Treatment'],
            y=[ab_data['control_avg_orders_per_customer'], ab_data['treatment_avg_orders_per_customer']],
            marker_color=['#3498db', '#2ecc71'],
            text=[f"{ab_data['control_avg_orders_per_customer']:.2f}",
                  f"{ab_data['treatment_avg_orders_per_customer']:.2f}"],
            textposition='outside'
        ))
        fig.update_layout(
            title="Avg Orders per Customer",
            yaxis_title="Orders",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 3: COHORT RETENTION
# ============================================================================
elif page == "Cohort Retention":
    st.header("📅 Cohort Retention Analysis")

    retention_metrics = metrics['retention']

    # Retention metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Month 0 Retention", f"{retention_metrics['month_0_retention_pct']:.1f}%")

    with col2:
        st.metric("Month 1 Retention", f"{retention_metrics['month_1_retention_pct']:.1f}%")

    with col3:
        st.metric("Month 2 Retention", f"{retention_metrics['month_2_retention_pct']:.1f}%")

    with col4:
        st.metric("Month 3 Retention", f"{retention_metrics['month_3_retention_pct']:.1f}%")

    st.markdown("---")

    # Retention heatmap
    st.subheader("🔥 Cohort Retention Heatmap")

    retention_matrix = data['retention_matrix']

    fig = go.Figure(data=go.Heatmap(
        z=retention_matrix.values,
        x=retention_matrix.columns,
        y=retention_matrix.index,
        colorscale='RdYlGn',
        text=retention_matrix.values,
        texttemplate='%{text:.1f}%',
        textfont={"size": 10},
        colorbar=dict(title="Retention %")
    ))

    fig.update_layout(
        title="Customer Retention by Cohort and Month",
        xaxis_title="Months Since First Purchase",
        yaxis_title="Cohort (First Purchase Month)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Retention curve
    st.subheader("📉 Average Retention Curve")

    avg_retention = retention_matrix.mean(axis=0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=avg_retention.index.astype(int),
        y=avg_retention.values,
        mode='lines+markers',
        name='Average Retention',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=12),
        fill='tozeroy',
        fillcolor='rgba(46, 204, 113, 0.2)'
    ))

    fig.update_layout(
        xaxis_title="Months Since First Purchase",
        yaxis_title="Retention Rate (%)",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Churn insights
    st.markdown("---")
    st.subheader("⚠️ Churn Reduction Opportunity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="insight-box">
        <b>Current Month-1 Churn:</b> {retention_metrics['baseline_churn_pct']:.2f}%<br>
        <b>Target Churn (14% reduction):</b> {retention_metrics['target_churn_pct']:.2f}%<br>
        <b>Improvement Needed:</b> {retention_metrics['baseline_churn_pct'] - retention_metrics['target_churn_pct']:.2f} percentage points
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Churn visualization
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Current Churn', 'Target Churn'],
            y=[retention_metrics['baseline_churn_pct'], retention_metrics['target_churn_pct']],
            marker_color=['#e74c3c', '#2ecc71'],
            text=[f"{retention_metrics['baseline_churn_pct']:.2f}%",
                  f"{retention_metrics['target_churn_pct']:.2f}%"],
            textposition='outside'
        ))
        fig.update_layout(
            title="Churn Rate: Current vs Target",
            yaxis_title="Churn Rate (%)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 4: CUSTOMER SEGMENTATION
# ============================================================================
elif page == "Customer Segmentation":
    st.header("👥 RFM Customer Segmentation")

    rfm_data = data['rfm_data']
    segment_summary = data['segment_summary']

    # Segment summary table
    st.subheader("📊 Segment Performance Summary")

    # Format the dataframe for display
    display_df = segment_summary.copy()
    display_df['TotalRevenue'] = display_df['TotalRevenue'].apply(lambda x: f"£{x:,.0f}")
    display_df['AvgFrequency'] = display_df['AvgFrequency'].apply(lambda x: f"{x:.2f}")
    display_df['AvgRecency'] = display_df['AvgRecency'].apply(lambda x: f"{x:.0f} days")
    display_df['AvgTransactionValue'] = display_df['AvgTransactionValue'].apply(lambda x: f"£{x:.2f}")
    display_df['RevenuePercent'] = display_df['RevenuePercent'].apply(lambda x: f"{x:.1f}%")
    display_df['CustomerPercent'] = display_df['CustomerPercent'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(display_df, use_container_width=True)

    st.markdown("---")

    # RFM Distribution
    st.subheader("📈 RFM Score Distribution")

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.histogram(rfm_data, x='R_Score', nbins=5,
                           title='Recency Score Distribution',
                           labels={'R_Score': 'Recency Score', 'count': 'Customers'})
        fig.update_traces(marker_color='#3498db')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(rfm_data, x='F_Score', nbins=5,
                           title='Frequency Score Distribution',
                           labels={'F_Score': 'Frequency Score', 'count': 'Customers'})
        fig.update_traces(marker_color='#2ecc71')
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = px.histogram(rfm_data, x='M_Score', nbins=5,
                           title='Monetary Score Distribution',
                           labels={'M_Score': 'Monetary Score', 'count': 'Customers'})
        fig.update_traces(marker_color='#9b59b6')
        st.plotly_chart(fig, use_container_width=True)

    # Pareto Analysis
    st.markdown("---")
    st.subheader("💎 Revenue Concentration (Pareto Analysis)")

    # Calculate cumulative revenue
    rfm_sorted = rfm_data.sort_values('Monetary', ascending=False).reset_index(drop=True)
    rfm_sorted['CumulativeRevenue'] = rfm_sorted['Monetary'].cumsum()
    rfm_sorted['CumulativeRevenuePercent'] = (rfm_sorted['CumulativeRevenue'] /
                                              rfm_sorted['Monetary'].sum()) * 100
    rfm_sorted['CustomerPercent'] = ((rfm_sorted.index + 1) / len(rfm_sorted)) * 100

    # Sample for visualization
    sample_rate = max(1, len(rfm_sorted) // 200)
    pareto_sample = rfm_sorted.iloc[::sample_rate]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=pareto_sample['CustomerPercent'], y=pareto_sample['Monetary'],
               name="Customer Revenue", marker_color='#3498db', opacity=0.6),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=pareto_sample['CustomerPercent'], y=pareto_sample['CumulativeRevenuePercent'],
                   name="Cumulative %", mode='lines+markers',
                   line=dict(color='#e74c3c', width=3), marker=dict(size=8)),
        secondary_y=True
    )

    # Add 80-20 lines
    fig.add_hline(y=80, line_dash="dash", line_color="green",
                  annotation_text="80% Revenue", secondary_y=True)
    fig.add_vline(x=20, line_dash="dash", line_color="orange",
                  annotation_text="20% Customers")

    fig.update_xaxes(title_text="Customer Percentile")
    fig.update_yaxes(title_text="Revenue (£)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative Revenue (%)", secondary_y=True)
    fig.update_layout(title="Pareto Chart: Customer Revenue Concentration", height=500)

    st.plotly_chart(fig, use_container_width=True)

    st.info(f"""
    **Key Insight:** Top 20% of customers generate **{metrics['revenue_concentration']['top_20_pct_customers_revenue_pct']:.1f}%** of total revenue.
    This is close to the classic 80-20 Pareto principle.
    """)

# ============================================================================
# PAGE 5: GEOGRAPHIC ANALYSIS
# ============================================================================
elif page == "Geographic Analysis":
    st.header("🌍 Geographic Sales Analysis")

    revenue_by_region = data['revenue_by_region']

    # Top regions
    col1, col2, col3 = st.columns(3)

    with col1:
        top_region = revenue_by_region.iloc[0]
        st.metric(
            "Top Region",
            top_region['Region'],
            delta=f"£{top_region['Revenue']:,.0f}"
        )

    with col2:
        st.metric(
            "Total UK Regions",
            len(revenue_by_region),
            delta=None
        )

    with col3:
        st.metric(
            "Avg Revenue per Region",
            f"£{revenue_by_region['Revenue'].mean():,.0f}",
            delta=None
        )

    st.markdown("---")

    # Regional performance
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Revenue by Region")
        fig = px.bar(
            revenue_by_region.sort_values('Revenue', ascending=True),
            x='Revenue',
            y='Region',
            orientation='h',
            labels={'Revenue': 'Revenue (£)', 'Region': 'UK Region'},
            color='Revenue',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("👥 Customers by Region")
        fig = px.bar(
            revenue_by_region.sort_values('Customers', ascending=True),
            x='Customers',
            y='Region',
            orientation='h',
            labels={'Customers': 'Number of Customers', 'Region': 'UK Region'},
            color='Customers',
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    # Regional breakdown
    st.markdown("---")
    st.subheader("📍 Regional Performance Details")

    display_df = revenue_by_region.copy()
    display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"£{x:,.0f}")
    display_df['AvgRevenuePerCustomer'] = (revenue_by_region['Revenue'] /
                                           revenue_by_region['Customers']).apply(lambda x: f"£{x:,.0f}")

    st.dataframe(display_df, use_container_width=True)

# ============================================================================
# PAGE 6: PRODUCT PERFORMANCE
# ============================================================================
elif page == "Product Performance":
    st.header("🛍️ Product Performance Analysis")

    product_performance = data['product_performance']

    # Top products metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Top Product Revenue",
            f"£{product_performance.iloc[0]['TotalRevenue']:,.0f}",
            delta=None
        )

    with col2:
        st.metric(
            "Total Products Analyzed",
            len(product_performance),
            delta="Top 20 products"
        )

    with col3:
        st.metric(
            "Avg Product Revenue",
            f"£{product_performance['TotalRevenue'].mean():,.0f}",
            delta=None
        )

    st.markdown("---")

    # Product performance charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Top 10 Products by Revenue")
        top_10 = product_performance.head(10)
        fig = px.bar(
            top_10,
            x='TotalRevenue',
            y='StockCode',
            orientation='h',
            hover_data=['ProductName', 'TotalQuantity'],
            labels={'TotalRevenue': 'Revenue (£)', 'StockCode': 'Product Code'},
            color='TotalRevenue',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("👥 Top 10 Products by Customers")
        top_customers = product_performance.nlargest(10, 'UniqueCustomers')
        fig = px.bar(
            top_customers,
            x='UniqueCustomers',
            y='StockCode',
            orientation='h',
            hover_data=['ProductName', 'TotalRevenue'],
            labels={'UniqueCustomers': 'Unique Customers', 'StockCode': 'Product Code'},
            color='UniqueCustomers',
            color_continuous_scale='Plasma'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Product details table
    st.markdown("---")
    st.subheader("📋 Top 20 Products - Detailed View")

    display_df = product_performance.copy()
    display_df['TotalRevenue'] = display_df['TotalRevenue'].apply(lambda x: f"£{x:,.0f}")
    display_df['AvgPrice'] = display_df['AvgPrice'].apply(lambda x: f"£{x:.2f}")
    display_df = display_df[['StockCode', 'ProductName', 'TotalRevenue',
                              'TotalQuantity', 'UniqueCustomers', 'AvgPrice']]

    st.dataframe(display_df, use_container_width=True, height=600)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem 0;'>
    <p><b>E-Commerce Analytics Dashboard</b> | Built with Streamlit & Plotly</p>
    <p>Data Source: UCI Online Retail Dataset | Analysis Period: Dec 2024 - Feb 2025</p>
</div>
""", unsafe_allow_html=True)
