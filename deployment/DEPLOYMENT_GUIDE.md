# Quick Deployment Guide

This guide will walk you through deploying your Sign Language Recognition API to Hugging Face Spaces in under 10 minutes.

## Prerequisites

✅ Hugging Face account (free)
✅ Git installed on your computer
✅ All files in the `deployment` directory

## 🚀 Deployment Steps

### Step 1: Create Hugging Face Account (2 minutes)

1. Go to https://huggingface.co/join
2. Sign up with email or GitHub
3. Verify your email address

### Step 2: Create a New Space (1 minute)

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"** (top right)
3. Fill in the form:
   - **Owner**: Your username
   - **Space name**: `msl-recognition-api` (or your choice)
   - **License**: Apache 2.0
   - **Select SDK**: **Docker** (important!)
   - **Space hardware**: CPU basic - **Free!** (0$/h)
   - **Visibility**: Public (or Private if you prefer)
4. Click **"Create Space"**

### Step 3: Deploy Your Files (5 minutes)

You have two options:

#### Option A: Using Git (Recommended)

```bash
# Navigate to deployment directory
cd deployment

# Initialize git (if not already a repo)
git init

# Configure git (if first time)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add Hugging Face remote
# Replace YOUR-USERNAME and YOUR-SPACE-NAME
git remote add space https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME

# Add all files
git add .

# Commit
git commit -m "Deploy MSL Recognition API"

# Push to Hugging Face
git push space main
```

**Authentication**: When prompted for username/password:
- **Username**: Your Hugging Face username
- **Password**: Your Hugging Face **Access Token** (not your password!)
  - Get token at: https://huggingface.co/settings/tokens
  - Click "New token" → "Write" access → Copy token

#### Option B: Using Web Interface (Easier for beginners)

1. In your Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files:
   - ✅ `app.py`
   - ✅ `model.py`
   - ✅ `preprocessing.py`
   - ✅ `requirements.txt`
   - ✅ `trained_model.pth`
   - ✅ `Dockerfile`
   - ✅ `SPACE_README.md` (rename to `README.md` during upload)
4. Add commit message: "Initial deployment"
5. Click **"Commit changes to main"**

### Step 4: Wait for Build (5-10 minutes)

1. Hugging Face will automatically start building your Space
2. You'll see the build progress in the **"Logs"** tab
3. Watch for these stages:
   - ✅ Building Docker image
   - ✅ Installing dependencies
   - ✅ Starting application
   - ✅ Running on port 7860

### Step 5: Test Your Deployment (1 minute)

Once the build completes, your API is live! 🎉

Your API URL will be:
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space
```

#### Quick Tests:

**1. Health Check (in browser):**
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health
```

**2. API Documentation (in browser):**
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/docs
```

**3. Test with Python:**
```python
import requests

API_URL = "https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space"
response = requests.get(f"{API_URL}/health")
print(response.json())
```

---

## 🎯 What You Should See

### Successful Deployment:

1. **Logs Tab**: Shows "Application startup complete"
2. **App Tab**: Shows your API documentation
3. **Health Endpoint**: Returns JSON with status "healthy"

### Example Health Response:
```json
{
  "status": "healthy",
  "device": "cpu",
  "model_loaded": true,
  "gestures": ["minum", "berjalan", "berlari", "bola", "dari", "hi", "jangan", "mohon", "pen", "teh tarik", "tolong"]
}
```

---

## 🔧 Common Issues & Solutions

### Issue 1: Build Fails
**Error**: "Could not install requirements"

**Solution**: Check your requirements.txt for typos
```bash
# Verify locally first
pip install -r requirements.txt
```

### Issue 2: Port Error
**Error**: "Port 7860 is already in use"

**Solution**: The Dockerfile is correctly configured for port 7860. This shouldn't happen on Hugging Face. If it does, check that your Dockerfile has:
```dockerfile
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Issue 3: Model Not Found
**Error**: "FileNotFoundError: trained_model.pth"

**Solution**: Ensure `trained_model.pth` is in the same directory as `app.py`

### Issue 4: CORS Errors (when connecting frontend)
**Solution**: CORS is already configured in `app.py` to allow all origins. If you still have issues, check that your frontend is using the correct API URL.

---

## 📊 Monitoring Your Space

### Check Logs:
1. Go to your Space page
2. Click **"Logs"** tab
3. Monitor real-time logs

### Check Usage:
1. Go to **Settings** tab
2. View **Analytics** (available after 24 hours)

### Restart Space:
1. Go to **Settings** tab
2. Click **"Factory reboot"**
3. Wait for rebuild

---

## 💰 Cost Breakdown

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| CPU | ✅ Free | - |
| GPU | ❌ Not available | $0.60/hour |
| Storage | 50 GB | 50 GB |
| Bandwidth | Unlimited* | Unlimited |
| Uptime | May sleep after inactivity | Always on |

*Fair use policy applies

**For your use case**: Free CPU tier is sufficient for testing and low traffic!

---

## 🎉 Next Steps

After successful deployment:

1. ✅ Note your API URL
2. ✅ Test all endpoints
3. ✅ Share API URL with your frontend team
4. ✅ Create frontend web app (next phase)
5. ✅ Integrate webcam → API → display predictions

---

## 📝 Important URLs to Save

Replace `YOUR-USERNAME` and `YOUR-SPACE-NAME`:

- **Space URL**: https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
- **API URL**: https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space
- **API Docs**: https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/docs
- **Health**: https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health

---

## 🆘 Need Help?

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Community**: https://discuss.huggingface.co/

---

## ✅ Deployment Checklist

Before deployment:
- [ ] All files in `deployment` directory
- [ ] `trained_model.pth` is present (489KB)
- [ ] `Dockerfile` is configured for port 7860
- [ ] `requirements.txt` has all dependencies

After deployment:
- [ ] Build completes successfully
- [ ] Health endpoint returns "healthy"
- [ ] API docs are accessible
- [ ] Can make test prediction
- [ ] API URL is saved

---

**Congratulations!** 🎊 Your API is now live and ready to receive webcam frames from your frontend!
