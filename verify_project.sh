#!/bin/bash

echo "=================================="
echo "PROJECT VERIFICATION"
echo "=================================="
echo ""

check_file() {
    if [ -f "$1" ]; then
        size=$(ls -lh "$1" | awk '{print $5}')
        echo "✅ $1 ($size)"
        return 0
    else
        echo "❌ MISSING: $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        count=$(ls -1 "$1" | wc -l | xargs)
        echo "✅ $1 ($count files)"
        return 0
    else
        echo "❌ MISSING: $1"
        return 1
    fi
}

echo "📂 DIRECTORY STRUCTURE"
echo "----------------------"
check_dir "data"
check_dir "scripts"
check_dir "dashboards"
check_dir "outputs"
check_dir "reports"
echo ""

echo "📊 DATA FILES"
echo "-------------"
check_file "data/ecommerce.db"
check_file "data/cleaned_retail_data.csv"
echo ""

echo "🐍 PYTHON SCRIPTS"
echo "-----------------"
check_file "scripts/01_data_preparation.py"
check_file "scripts/02_ab_testing_analysis.py"
check_file "scripts/03_cohort_analysis.py"
check_file "scripts/04_rfm_segmentation.py"
check_file "scripts/05_comprehensive_metrics.py"
check_file "scripts/06_generate_excel_report.py"
check_file "scripts/07_generate_pdf_report.py"
echo ""

echo "📊 DASHBOARDS"
echo "-------------"
check_file "dashboards/streamlit_dashboard.py"
echo ""

echo "📈 OUTPUTS"
echo "----------"
check_file "outputs/ab_test_results.json"
check_file "outputs/cohort_metrics.json"
check_file "outputs/rfm_metrics.json"
check_file "outputs/comprehensive_metrics.json"
check_file "outputs/ab_test_analysis.png"
check_file "outputs/cohort_analysis.png"
check_file "outputs/rfm_analysis.png"
check_file "outputs/ecommerce_analytics_report.xlsx"
echo ""

echo "📄 REPORTS"
echo "----------"
check_file "reports/ecommerce_analytics_report.pdf"
echo ""

echo "📚 DOCUMENTATION"
echo "----------------"
check_file "README.md"
check_file "PROJECT_SUMMARY.md"
check_file "requirements.txt"
echo ""

echo "=================================="
echo "✅ VERIFICATION COMPLETE"
echo "=================================="
