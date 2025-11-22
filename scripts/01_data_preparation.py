"""
E-Commerce Analytics: Data Preparation and Database Setup
Author: Portfolio Project
Date: 2025-11-21

This script loads the UCI Online Retail dataset, cleans it, and creates a DuckDB database
with additional fields for A/B testing and advanced analytics.
"""

import pandas as pd
import numpy as np
import duckdb
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("E-COMMERCE ANALYTICS - DATA PREPARATION")
print("=" * 80)

# Load the dataset
print("\n[1/6] Loading UCI Online Retail dataset...")
df = pd.read_excel('../data/online_retail.xlsx')
print(f"   ✓ Loaded {len(df):,} transactions")
print(f"   ✓ Columns: {list(df.columns)}")

# Initial data exploration
print("\n[2/6] Initial Data Overview:")
print(f"   • Date Range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
print(f"   • Unique Customers: {df['CustomerID'].nunique()}")
print(f"   • Unique Products: {df['StockCode'].nunique()}")
print(f"   • Countries: {df['Country'].nunique()}")

# Data Cleaning
print("\n[3/6] Cleaning data...")
initial_rows = len(df)

# Remove cancelled orders (InvoiceNo starting with 'C')
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
print(f"   ✓ Removed {initial_rows - len(df):,} cancelled orders")

# Remove rows with missing CustomerID
df = df.dropna(subset=['CustomerID'])
print(f"   ✓ Removed records with missing CustomerID")

# Remove negative quantities and prices
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
print(f"   ✓ Removed negative quantities/prices")

# Calculate Revenue
df['Revenue'] = df['Quantity'] * df['UnitPrice']

# Remove extreme outliers (Revenue > 99.9th percentile)
revenue_threshold = df['Revenue'].quantile(0.999)
df = df[df['Revenue'] <= revenue_threshold]
print(f"   ✓ Removed extreme outliers (Revenue > £{revenue_threshold:,.2f})")

# Convert CustomerID to integer
df['CustomerID'] = df['CustomerID'].astype(int)

# Extract date components
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
df['Hour'] = df['InvoiceDate'].dt.hour

print(f"\n   Final dataset: {len(df):,} transactions")

# Focus on UK data for regional analysis and filter to Dec 2024 - Feb 2025 simulation
print("\n[4/6] Preparing dataset for Dec 2024 - Feb 2025 simulation...")

# Since original data is from 2010-2011, we'll adjust dates to Dec 2024 - Feb 2025
# Take 3 months of data from the original dataset
date_range_start = df['InvoiceDate'].min()
date_range_end = date_range_start + timedelta(days=90)
df_filtered = df[(df['InvoiceDate'] >= date_range_start) &
                  (df['InvoiceDate'] <= date_range_end)].copy()

# Shift dates to Dec 2024 - Feb 2025
date_shift = (datetime(2024, 12, 1) - date_range_start).days
df_filtered['InvoiceDate'] = df_filtered['InvoiceDate'] + timedelta(days=date_shift)

# Recalculate date components
df_filtered['Year'] = df_filtered['InvoiceDate'].dt.year
df_filtered['Month'] = df_filtered['InvoiceDate'].dt.month
df_filtered['YearMonth'] = df_filtered['InvoiceDate'].dt.to_period('M').astype(str)
df_filtered['DayOfWeek'] = df_filtered['InvoiceDate'].dt.day_name()
df_filtered['Hour'] = df_filtered['InvoiceDate'].dt.hour

print(f"   ✓ Adjusted dates to Dec 2024 - Feb 2025")
print(f"   ✓ Dataset: {len(df_filtered):,} transactions")
print(f"   ✓ Date Range: {df_filtered['InvoiceDate'].min()} to {df_filtered['InvoiceDate'].max()}")

df = df_filtered

# Add A/B Testing Fields (Discount Strategy Experiment)
print("\n[5/6] Adding A/B testing fields for discount strategy...")

# Randomly assign customers to control (A) or treatment (B) groups
np.random.seed(42)
customer_groups = df.groupby('CustomerID').first().reset_index()[['CustomerID']]
customer_groups['TestGroup'] = np.random.choice(['Control', 'Treatment'],
                                                  size=len(customer_groups),
                                                  p=[0.5, 0.5])

# Merge back to main dataframe
df = df.merge(customer_groups, on='CustomerID', how='left')

# Apply discount to Treatment group (10-20% discount randomly)
df['DiscountRate'] = 0.0
treatment_mask = df['TestGroup'] == 'Treatment'
df.loc[treatment_mask, 'DiscountRate'] = np.random.uniform(0.10, 0.20, treatment_mask.sum())

# Calculate discounted revenue
df['DiscountedRevenue'] = df['Revenue'] * (1 - df['DiscountRate'])
df['DiscountAmount'] = df['Revenue'] - df['DiscountedRevenue']

print(f"   ✓ Control Group: {(df['TestGroup'] == 'Control').sum():,} transactions")
print(f"   ✓ Treatment Group: {(df['TestGroup'] == 'Treatment').sum():,} transactions")

# Add UK Regions for geographic analysis
print("\n[6/6] Adding geographic regions...")

uk_data = df[df['Country'] == 'United Kingdom'].copy()
non_uk_data = df[df['Country'] != 'United Kingdom'].copy()

# Assign UK regions based on customer distribution
np.random.seed(42)
uk_regions = ['London', 'South East', 'North West', 'East of England',
              'West Midlands', 'South West', 'Yorkshire', 'East Midlands',
              'North East', 'Wales', 'Scotland', 'Northern Ireland']

region_weights = [0.25, 0.18, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.03, 0.03, 0.02, 0.01]

customer_regions = uk_data.groupby('CustomerID').first().reset_index()[['CustomerID']]
customer_regions['Region'] = np.random.choice(uk_regions,
                                               size=len(customer_regions),
                                               p=region_weights)

uk_data = uk_data.merge(customer_regions, on='CustomerID', how='left')
non_uk_data['Region'] = 'International'

df = pd.concat([uk_data, non_uk_data], ignore_index=True)

print(f"   ✓ UK Transactions: {len(uk_data):,}")
print(f"   ✓ International Transactions: {len(non_uk_data):,}")

# Create DuckDB Database
print("\n[7/7] Creating DuckDB database...")

con = duckdb.connect('../data/ecommerce.db')

# Create main transactions table
con.execute("DROP TABLE IF EXISTS transactions")
con.execute("""
    CREATE TABLE transactions AS
    SELECT * FROM df
""")

# Create customer summary table
con.execute("DROP TABLE IF EXISTS customers")
con.execute("""
    CREATE TABLE customers AS
    SELECT
        CustomerID,
        Country,
        MAX(Region) as Region,
        MAX(TestGroup) as TestGroup,
        MIN(InvoiceDate) as FirstPurchaseDate,
        MAX(InvoiceDate) as LastPurchaseDate,
        COUNT(DISTINCT InvoiceNo) as TotalOrders,
        SUM(Quantity) as TotalQuantity,
        SUM(Revenue) as TotalRevenue,
        AVG(Revenue) as AvgOrderValue,
        COUNT(DISTINCT StockCode) as UniqueProducts
    FROM transactions
    GROUP BY CustomerID, Country
""")

# Verify data
transaction_count = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
customer_count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]

print(f"   ✓ Created 'transactions' table: {transaction_count:,} rows")
print(f"   ✓ Created 'customers' table: {customer_count:,} customers")

# Save cleaned dataframe as CSV for reference
df.to_csv('../data/cleaned_retail_data.csv', index=False)
print(f"\n   ✓ Saved cleaned data to '../data/cleaned_retail_data.csv'")

# Display sample statistics
print("\n" + "=" * 80)
print("DATA PREPARATION COMPLETE - SUMMARY STATISTICS")
print("=" * 80)

summary_stats = con.execute("""
    SELECT
        COUNT(*) as TotalTransactions,
        COUNT(DISTINCT CustomerID) as UniqueCustomers,
        COUNT(DISTINCT InvoiceNo) as TotalOrders,
        COUNT(DISTINCT StockCode) as UniqueProducts,
        COUNT(DISTINCT Country) as Countries,
        SUM(Revenue) as TotalRevenue,
        AVG(Revenue) as AvgTransactionValue,
        MIN(InvoiceDate) as StartDate,
        MAX(InvoiceDate) as EndDate
    FROM transactions
""").df()

for col in summary_stats.columns:
    value = summary_stats[col].values[0]
    if 'Revenue' in col or 'Value' in col:
        print(f"   • {col}: £{value:,.2f}")
    elif 'Date' in col:
        print(f"   • {col}: {value}")
    else:
        print(f"   • {col}: {value:,}")

print("\n✅ Database ready for analysis at: ../data/ecommerce.db")
print("=" * 80)

con.close()
