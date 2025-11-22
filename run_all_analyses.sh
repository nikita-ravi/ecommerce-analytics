#!/bin/bash

# E-Commerce Analytics - Master Run Script
# This script runs all analyses in sequence

echo "=================================="
echo "E-COMMERCE ANALYTICS PIPELINE"
echo "=================================="
echo ""

# Navigate to scripts directory
cd "$(dirname "$0")/scripts"

echo "[1/7] Running data preparation..."
python 01_data_preparation.py
if [ $? -ne 0 ]; then
    echo "ERROR: Data preparation failed!"
    exit 1
fi
echo ""

echo "[2/7] Running A/B testing analysis..."
python 02_ab_testing_analysis.py
if [ $? -ne 0 ]; then
    echo "ERROR: A/B testing analysis failed!"
    exit 1
fi
echo ""

echo "[3/7] Running cohort retention analysis..."
python 03_cohort_analysis.py
if [ $? -ne 0 ]; then
    echo "ERROR: Cohort analysis failed!"
    exit 1
fi
echo ""

echo "[4/7] Running RFM segmentation..."
python 04_rfm_segmentation.py
if [ $? -ne 0 ]; then
    echo "ERROR: RFM segmentation failed!"
    exit 1
fi
echo ""

echo "[5/7] Calculating comprehensive metrics..."
python 05_comprehensive_metrics.py
if [ $? -ne 0 ]; then
    echo "ERROR: Metrics calculation failed!"
    exit 1
fi
echo ""

echo "[6/7] Generating Excel report..."
python 06_generate_excel_report.py
if [ $? -ne 0 ]; then
    echo "ERROR: Excel generation failed!"
    exit 1
fi
echo ""

echo "[7/7] Generating PDF report..."
python 07_generate_pdf_report.py
if [ $? -ne 0 ]; then
    echo "ERROR: PDF generation failed!"
    exit 1
fi
echo ""

echo "=================================="
echo "✅ ALL ANALYSES COMPLETE!"
echo "=================================="
echo ""
echo "Generated outputs:"
echo "  • Database: data/ecommerce.db"
echo "  • Excel: outputs/ecommerce_analytics_report.xlsx"
echo "  • PDF: reports/ecommerce_analytics_report.pdf"
echo "  • Visualizations: outputs/*.png"
echo "  • Data exports: outputs/*.csv"
echo ""
echo "To launch the interactive dashboard:"
echo "  cd dashboards"
echo "  streamlit run streamlit_dashboard.py"
echo ""
