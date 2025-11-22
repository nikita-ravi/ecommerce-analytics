#!/bin/bash

# GitHub Setup Script for E-Commerce Analytics Project
# This script helps you push your project to GitHub

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║           GitHub Setup for E-Commerce Analytics                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first:"
    echo "   brew install git"
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if already initialized
if [ -d ".git" ]; then
    echo "⚠️  Git repository already initialized."
    echo ""
    read -p "Do you want to continue? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ]; then
        echo "Exiting..."
        exit 0
    fi
else
    # Initialize git
    echo "📦 Initializing Git repository..."
    git init
    echo "✓ Git initialized"
    echo ""
fi

# Get GitHub username
echo "Enter your GitHub information:"
echo "──────────────────────────────"
read -p "GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "❌ Username cannot be empty!"
    exit 1
fi

# Get repository name
read -p "Repository name [ecommerce-analytics]: " repo_name
repo_name=${repo_name:-ecommerce-analytics}

echo ""
echo "📋 Summary:"
echo "──────────────────────────────"
echo "Username: $github_username"
echo "Repository: $repo_name"
echo "URL: https://github.com/$github_username/$repo_name"
echo ""

read -p "Is this correct? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Exiting..."
    exit 0
fi

echo ""
echo "🔧 Setting up Git..."

# Configure git user if not set
if [ -z "$(git config user.name)" ]; then
    read -p "Enter your name for Git commits: " user_name
    git config user.name "$user_name"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Enter your email for Git commits: " user_email
    git config user.email "$user_email"
fi

echo "✓ Git configured"
echo ""

# Add all files
echo "📦 Adding files to Git..."
git add .
echo "✓ Files added"
echo ""

# Create commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Complete E-Commerce Analytics Project

- 7 Python analysis scripts (A/B testing, cohorts, RFM)
- Interactive Streamlit dashboard
- Excel and PDF reports
- 67K transactions analyzed
- DuckDB database with SQL queries
- Professional visualizations
- Complete documentation"

echo "✓ Commit created"
echo ""

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "⚠️  Remote 'origin' already exists"
    git remote remove origin
fi

# Add remote
echo "🔗 Adding GitHub remote..."
git remote add origin "https://github.com/$github_username/$repo_name.git"
echo "✓ Remote added"
echo ""

# Set main branch
git branch -M main

echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Git setup complete!"
echo ""
echo "📌 NEXT STEPS:"
echo "──────────────────────────────"
echo ""
echo "1. CREATE GITHUB REPOSITORY:"
echo "   → Go to: https://github.com/new"
echo "   → Repository name: $repo_name"
echo "   → Make it PUBLIC"
echo "   → Don't add README, .gitignore, or license"
echo "   → Click 'Create repository'"
echo ""
echo "2. PUSH TO GITHUB:"
echo "   → Run: git push -u origin main"
echo "   → Enter your GitHub username: $github_username"
echo "   → Enter your Personal Access Token (NOT password)"
echo ""
echo "   Need a token? Get one here:"
echo "   → https://github.com/settings/tokens"
echo "   → Generate new token (classic)"
echo "   → Select 'repo' scope"
echo "   → Copy the token (you won't see it again!)"
echo ""
echo "3. DEPLOY TO STREAMLIT CLOUD:"
echo "   → Go to: https://share.streamlit.io/"
echo "   → Sign in with GitHub"
echo "   → Click 'New app'"
echo "   → Repository: $github_username/$repo_name"
echo "   → Branch: main"
echo "   → Main file: dashboards/streamlit_dashboard.py"
echo "   → Click 'Deploy'"
echo ""
echo "   Your dashboard will be live at:"
echo "   → https://$github_username-$repo_name.streamlit.app"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Ask if user wants to push now
read -p "Do you want to push to GitHub now? (y/n): " push_now

if [ "$push_now" = "y" ]; then
    echo ""
    echo "🚀 Pushing to GitHub..."
    echo "   (You'll be prompted for credentials)"
    echo ""

    git push -u origin main

    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Successfully pushed to GitHub!"
        echo ""
        echo "View your repository at:"
        echo "https://github.com/$github_username/$repo_name"
        echo ""
        echo "Next: Deploy to Streamlit Cloud (see instructions above)"
    else
        echo ""
        echo "❌ Push failed. Please check:"
        echo "   1. Repository exists on GitHub"
        echo "   2. You have the correct credentials"
        echo "   3. You're using a Personal Access Token (not password)"
        echo ""
        echo "Try again with: git push -u origin main"
    fi
else
    echo ""
    echo "No problem! Push when ready with:"
    echo "   git push -u origin main"
fi

echo ""
echo "📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo ""
