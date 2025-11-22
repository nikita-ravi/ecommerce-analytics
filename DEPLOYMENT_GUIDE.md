# 🚀 Deployment Guide - GitHub & Streamlit Cloud

This guide will walk you through:
1. Pushing your project to GitHub
2. Deploying the interactive dashboard to Streamlit Cloud (FREE!)

---

## 📦 Part 1: Push to GitHub

### Step 1: Create a GitHub Repository

1. Go to [https://github.com](https://github.com)
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in the details:
   - **Repository name:** `ecommerce-analytics` (or your preferred name)
   - **Description:** "Comprehensive E-Commerce Analytics with A/B Testing, Cohort Analysis, and RFM Segmentation"
   - **Visibility:** Public (recommended for portfolio) or Private
   - **Do NOT** initialize with README (we already have one)
4. Click **"Create repository"**

### Step 2: Initialize Git and Push

Open terminal and run these commands:

```bash
# Navigate to your project
cd /Users/nikitaravi/ecommerce-analytics

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Complete E-Commerce Analytics Project

- 7 Python analysis scripts (A/B testing, cohorts, RFM)
- Interactive Streamlit dashboard
- Excel and PDF reports
- 67K transactions analyzed
- DuckDB database with SQL queries
- Professional visualizations
- Complete documentation"

# Add your GitHub repository as remote
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-analytics.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```bash
# If your username is "johndoe"
git remote add origin https://github.com/johndoe/ecommerce-analytics.git
git branch -M main
git push -u origin main
```

You'll be prompted for GitHub credentials. Enter your username and **Personal Access Token** (not password).

### Step 3: Get GitHub Personal Access Token (if needed)

If you don't have a token:
1. GitHub → Settings (your profile) → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token → Give it a name
4. Select scopes: **repo** (full control)
5. Generate token → **COPY IT** (you won't see it again!)
6. Use this token as your password when pushing

---

## ☁️ Part 2: Deploy Dashboard to Streamlit Cloud

### Option A: Streamlit Cloud (Recommended - FREE!)

#### Prerequisites
- GitHub account (done above)
- Streamlit Cloud account (free)

#### Step 1: Sign Up for Streamlit Cloud

1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Click **"Sign up"**
3. Sign up with your **GitHub account**
4. Authorize Streamlit to access your repositories

#### Step 2: Create Streamlit Config (if needed for data)

Since your dashboard loads data from local files, you have two options:

**Option A: Include data in repository** (Easier - data is public)
- Data files are already in your repo
- No changes needed
- Works immediately

**Option B: Use secrets for sensitive data** (If data is private)
- We'll set this up below if needed

#### Step 3: Deploy Your Dashboard

1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Click **"New app"**
3. Fill in the deployment form:
   - **Repository:** `YOUR_USERNAME/ecommerce-analytics`
   - **Branch:** `main`
   - **Main file path:** `dashboards/streamlit_dashboard.py`
4. Click **"Deploy"**

🎉 **Your dashboard will be live in 2-3 minutes!**

You'll get a URL like: `https://YOUR_USERNAME-ecommerce-analytics.streamlit.app`

#### Step 4: Fix Relative Paths (Important!)

The dashboard uses relative paths (`../data/`, `../outputs/`). We need to fix this for deployment.

I'll create an updated version below that works both locally and on Streamlit Cloud.

### Troubleshooting Streamlit Cloud

**Issue: "File not found" errors**
- Solution: Make sure data files are committed to GitHub
- Check paths are correct relative to the dashboard script

**Issue: "Module not found"**
- Solution: Make sure all dependencies are in `requirements.txt`
- Streamlit Cloud auto-installs from this file

**Issue: Dashboard shows errors**
- Click "Manage app" → "Logs" to see detailed error messages
- Usually it's a missing file or incorrect path

---

## 🌐 Alternative Deployment Options

### Option B: Heroku (Free Tier Available)

1. Create `Procfile`:
```
web: streamlit run dashboards/streamlit_dashboard.py --server.port=$PORT
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option C: AWS/Azure/GCP

For production deployment, you can use:
- **AWS EC2** with Docker
- **Azure App Service**
- **Google Cloud Run**

---

## 📝 Post-Deployment Checklist

After deploying:

- [ ] Test all dashboard pages
- [ ] Verify visualizations load correctly
- [ ] Check data displays properly
- [ ] Test filters and interactions
- [ ] Share your dashboard URL!

---

## 🔗 Add Links to Your README

Update your README.md with:

```markdown
## 🌐 Live Demo

**Interactive Dashboard:** [https://YOUR_USERNAME-ecommerce-analytics.streamlit.app](https://YOUR_USERNAME-ecommerce-analytics.streamlit.app)

**GitHub Repository:** [https://github.com/YOUR_USERNAME/ecommerce-analytics](https://github.com/YOUR_USERNAME/ecommerce-analytics)
```

---

## 🎓 Tips for Portfolio Presentation

1. **Add screenshots** to README
2. **Create demo video** (Loom/Screen recording)
3. **Add LinkedIn badge** on GitHub
4. **Star your own repo** (shows activity)
5. **Write a blog post** about the project
6. **Share on LinkedIn** with dashboard link

---

## 🛠️ Maintenance

### Updating Your Deployment

After making changes locally:

```bash
# Stage changes
git add .

# Commit with message
git commit -m "Update: Description of changes"

# Push to GitHub
git push

# Streamlit Cloud auto-redeploys from GitHub!
```

### Viewing Deployment Logs

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app" → "Logs"
4. See real-time deployment and runtime logs

---

## ❓ Common Questions

**Q: Is Streamlit Cloud free?**
A: Yes! Free tier includes unlimited public apps.

**Q: Can I make my dashboard private?**
A: Yes, but requires Streamlit Cloud paid plan. Use password protection instead (see Streamlit docs).

**Q: How much data can I include?**
A: GitHub has 100MB file limit per file, 1GB repo limit.

**Q: Can I use a custom domain?**
A: Yes, on paid Streamlit Cloud plans.

**Q: What if my data is too large?**
A: Use cloud storage (AWS S3, Google Cloud Storage) and load data from there.

---

## 🚨 Important Notes

1. **Don't commit sensitive data** (API keys, passwords)
2. **Use .gitignore** to exclude secrets
3. **Large files (>100MB)** need Git LFS or cloud storage
4. **Test locally first** before deploying

---

## 📞 Need Help?

- **Streamlit Community:** [https://discuss.streamlit.io/](https://discuss.streamlit.io/)
- **Streamlit Docs:** [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **GitHub Docs:** [https://docs.github.com/](https://docs.github.com/)

---

**Ready to share your analytics dashboard with the world!** 🚀
