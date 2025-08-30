# 🚂 Railway Deployment Guide

Deploy your Credit Risk & Loan Approval System to Railway in minutes!

## 🎯 Why Railway?

- ✅ **Free Tier**: 500 hours/month + $5 credit
- ✅ **Zero Config**: Automatic deployments from GitHub
- ✅ **Fast**: Global edge network
- ✅ **Simple**: No complex configuration needed
- ✅ **Reliable**: Built-in monitoring and health checks

## 🚀 Quick Deployment (5 minutes)

### Step 1: Prepare Your Code
```bash
# Test locally first
python deploy_setup.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 3: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway automatically detects the configuration
6. Click **"Deploy"**

### Step 4: Access Your App
- Your app will be live at: `https://your-app-name.railway.app`
- Railway provides the URL in the dashboard

## 🔧 Configuration

Railway will automatically use the `railway.json` configuration:

```json
{
  "build": { "builder": "DOCKERFILE" },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/v1/health"
  }
}
```

## 📊 What Gets Deployed

Your Railway deployment includes:
- ✅ **FastAPI Application** with all endpoints
- ✅ **SQLite Database** (automatically created)
- ✅ **ML Models** (trained on first startup)
- ✅ **Static Files** (CSS, JS, images)
- ✅ **Modern UI** with fixed tenure dropdown
- ✅ **Health Monitoring** at `/api/v1/health`

## 🌐 Features Available

Once deployed, users can:
- 📝 **Apply for loans** with the modern form
- 🤖 **Get instant decisions** via ML models
- 📊 **View application history**
- 📱 **Use on mobile/desktop** (responsive design)
- 🔍 **Check application status**

## 🔍 Monitoring Your App

Railway provides:
- **Real-time logs** in the dashboard
- **Resource usage** monitoring
- **Automatic restarts** if the app crashes
- **Health checks** every 30 seconds
- **Deployment history** and rollbacks

## 🚨 Troubleshooting

### App Not Starting?
1. Check Railway logs in the dashboard
2. Verify all files are committed to Git
3. Ensure `railway.json` is in the root directory

### Database Issues?
- SQLite database is created automatically
- Check logs for any initialization errors
- Database file is stored in Railway's persistent storage

### Static Files Not Loading?
- Verify `static/` folder is in your repository
- Check that paths in templates are correct
- Railway serves static files automatically

## 💰 Cost Estimation

**Free Tier Limits:**
- 500 execution hours/month
- $5 in usage credits
- Perfect for demos and small applications

**Typical Usage:**
- Small app: ~100-200 hours/month (FREE)
- Medium app: ~300-400 hours/month (FREE)
- Production app: $5-15/month

## 🔄 Updates & Redeployments

Railway automatically redeploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Updated feature"
git push origin main
# Railway automatically redeploys!
```

## 🎯 Production Tips

1. **Custom Domain**: Add your domain in Railway dashboard
2. **Environment Variables**: Set in Railway dashboard if needed
3. **Monitoring**: Use Railway's built-in monitoring
4. **Backups**: Railway handles automatic backups
5. **SSL**: Automatic HTTPS certificates

## 📈 Scaling

As your app grows:
- Railway automatically handles traffic spikes
- Upgrade to paid plan for more resources
- Add Railway database service if needed
- Monitor usage in the dashboard

## 🎉 You're Live!

After deployment, your Credit Risk & Loan Approval System will be:
- 🌍 **Accessible worldwide**
- 🔒 **Secured with HTTPS**
- 📱 **Mobile-friendly**
- ⚡ **Fast and reliable**
- 🤖 **AI-powered**

**Your app URL**: `https://your-app-name.railway.app`

---

## 🆘 Need Help?

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Active community support
- **GitHub Issues**: Create issues in your repository

**Happy deploying! 🚀**