# 🚀 Quick Start: Push to GitHub & Deploy

## ⚡ Fast Track (5 minutes)

### Step 1: Create GitHub Repository (2 min)

1. Go to https://github.com/new
2. Repository name: `ecommerce-analytics`
3. Public ✓
4. **Don't** add README, gitignore, or license
5. Click "Create repository"

### Step 2: Push Code (2 min)

```bash
cd /Users/nikitaravi/ecommerce-analytics

# Initialize git
git init
git add .
git commit -m "Initial commit: E-Commerce Analytics Dashboard"

# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-analytics.git

git branch -M main
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/ecommerce-analytics.git
git branch -M main
git push -u origin main
```

Enter your GitHub username and **Personal Access Token** when prompted.

#### Need a Token?
https://github.com/settings/tokens → Generate new token → Select `repo` scope

---

### Step 3: Deploy to Streamlit Cloud (1 min)

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Settings:
   - **Repository:** YOUR_USERNAME/ecommerce-analytics
   - **Branch:** main
   - **Main file:** dashboards/streamlit_dashboard.py
5. Click "Deploy"

**Done!** Your dashboard will be live at:
`https://YOUR_USERNAME-ecommerce-analytics.streamlit.app`

---

## 🎯 What's Included in This Repo

```
ecommerce-analytics/
├── data/                    # Database & cleaned data
├── scripts/                 # 7 analysis scripts
├── dashboards/              # Streamlit dashboard ⭐
├── outputs/                 # Excel, visualizations, metrics
├── reports/                 # PDF report
├── requirements.txt         # Python dependencies
├── .streamlit/config.toml   # Dashboard config
└── README.md               # Full documentation
```

---

## 📊 File Sizes (GitHub Limits)

Check if any files are > 100MB:

```bash
find . -type f -size +100M
```

If yes, consider:
- Using Git LFS
- Excluding from Git (.gitignore)
- Hosting on cloud storage

Current project: ~30MB total ✓

---

## 🔄 Update After Changes

```bash
git add .
git commit -m "Update: description of changes"
git push
```

Streamlit Cloud auto-deploys! ⚡

---

## 📝 Update Your README

Add these badges to the top of README.md:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR_USERNAME-ecommerce-analytics.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/YOUR_USERNAME/ecommerce-analytics)
```

---

## ✅ Checklist

- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Deployed to Streamlit Cloud
- [ ] Dashboard is live and working
- [ ] Updated README with live demo link
- [ ] Tested all dashboard features
- [ ] Shared on LinkedIn!

---

**Need detailed instructions?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
