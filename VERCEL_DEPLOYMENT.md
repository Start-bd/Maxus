# Deploying Manus Agent System to Vercel

## Overview

This guide walks you through deploying the Manus Agent System to Vercel in just 5 minutes.

## Prerequisites

Before starting, make sure you have:
- GitHub account (connected to your code repository)
- Vercel account (free at https://vercel.com)
- API key from OpenAI OR Anthropic

## Step 1: Prepare Your Repository

First, ensure all changes are committed to your GitHub repository:

```bash
# Check git status
git status

# Add all changes
git add .

# Commit
git commit -m "Ready for Vercel deployment"

# Push to GitHub (main or your deployment branch)
git push origin main
```

**IMPORTANT:** Never commit your `.env` file! The `.gitignore` should already prevent this, but verify:

```bash
git status
# .env should NOT appear in the list
```

## Step 2: Connect to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repository (jshkbt-create/Maxus)
4. Click "Import"

## Step 3: Configure Environment Variables

Vercel will ask you to configure environment variables. Add these:

### Required Variables

**OPENAI_API_KEY** (choose one provider):
```
sk-... (your OpenAI API key)
```

OR

**ANTHROPIC_API_KEY**:
```
sk-ant-... (your Anthropic API key)
```

### Optional but Recommended

**NEWS_API_KEY**:
```
(your NewsAPI key for real news fetching)
```

**DATABASE_URL** (leave as-is for SQLite):
```
sqlite:////tmp/manus_agent.db
```

### Framework & Build Settings

- **Framework Preset**: Other
- **Build Command**: Leave empty (not needed)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

## Step 4: Deploy

1. Click "Deploy"
2. Vercel will:
   - Build your Python app
   - Run the verification script
   - Deploy to the cloud
3. Wait for deployment to complete (usually 2-3 minutes)

## Step 5: Verify Deployment

Once deployed, Vercel will give you a URL like:
```
https://maxus-xxxxx.vercel.app
```

Test your deployment:

### Health Check
```bash
curl https://maxus-xxxxx.vercel.app/health
```

Expected response:
```json
{"status": "healthy", "service": "manus-agent"}
```

### API Docs
Open in browser:
```
https://maxus-xxxxx.vercel.app/docs
```

### Root Endpoint
```bash
curl https://maxus-xxxxx.vercel.app/
```

Expected response:
```json
{
  "status": "running",
  "service": "Manus Agent System",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## Common API Endpoints

After deployment, you can use these endpoints:

### Execute Agent Task
```bash
curl -X POST https://maxus-xxxxx.vercel.app/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "fetch latest technology news",
    "context": {
      "category": "technology",
      "limit": 5
    }
  }'
```

### Create Project
```bash
curl -X POST https://maxus-xxxxx.vercel.app/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "domain": "example.com",
    "description": "Test project"
  }'
```

## Troubleshooting

### Deployment fails with "Python version error"

**Solution**: The vercel.json specifies Python 3.11. Ensure `runtime.txt` exists with:
```
python-3.11.0
```

### "Module not found" error

**Solution**: Check that `requirements.txt` has all dependencies:
```bash
# Verify it contains at least:
fastapi==0.115.5
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.6.1
sqlalchemy==2.0.36
openai>=1.54.0
anthropic>=0.39.0
```

### API key not found error

**Solution**: 
1. Go to Vercel dashboard
2. Select your project
3. Go to Settings > Environment Variables
4. Ensure OPENAI_API_KEY or ANTHROPIC_API_KEY is set
5. Redeploy (click "Redeploy" button)

### Database error

**Solution**: The SQLite database is stored in `/tmp/` which is temporary on Vercel. For production:
1. Use PostgreSQL (recommended)
2. Update DATABASE_URL in environment variables
3. Redeploy

## Setting Up PostgreSQL (Optional but Recommended)

For production with persistent database:

1. Get a PostgreSQL database URL from:
   - Railway.app
   - Supabase
   - AWS RDS
   - Any PostgreSQL provider

2. Add to Vercel environment variables:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

3. Redeploy

## Monitoring & Debugging

### View Logs
```
Vercel Dashboard > Your Project > Deployments > Click deployment > Logs
```

### Check Status
```bash
curl -I https://maxus-xxxxx.vercel.app/
```

Should return status 200.

## Advanced: Custom Domain

1. Go to Vercel Dashboard
2. Select your project
3. Settings > Domains
4. Add your custom domain
5. Update DNS records as instructed

## Rollback

If something breaks after deployment:

1. Go to Vercel Dashboard
2. Select your project
3. Deployments > Click previous good deployment
4. Click "Redeploy"

## Support

If you encounter issues:

1. Check Vercel logs
2. Check `.env` variables are set
3. Ensure API keys are valid
4. Try redeploy
5. Check GitHub issues

## Next Steps

- Set up a custom domain (optional)
- Configure alerts/monitoring
- Set up scheduled tasks (coming soon)
- Connect to database for production
- Configure backup strategy

---

**Deployment Summary:**
- Deployment time: ~3-5 minutes
- Cost: Free tier includes plenty of requests
- Automatic HTTPS: Yes
- Auto-scaling: Yes
- Database: SQLite (included) or PostgreSQL (your choice)

Good luck! 🚀
