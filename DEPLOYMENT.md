# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

### 1. **Install Vercel CLI**
```bash
npm install -g vercel
```

### 2. **Login to Vercel**
```bash
vercel login
```

### 3. **Deploy**
```bash
vercel --prod
```

## 🔧 **Environment Variables Setup**

After deployment, add these environment variables in your Vercel dashboard:

### Required Variables:
- `GLM_API_KEY` = `44dfb6031e3a47bf87649c8fd8fd9991.k2MRawvKixDuy9Xr`
- `GEMINI_API_KEY_1` = `AIzaSyA0oUA9lh8l5KvjXxG2oQUtbiqBUjIDLLw`
- `GEMINI_API_KEY_2` = `AIzaSyDIPHgTyoFyg6YKkv66vKL0-b4clqbZPCE`
- `GEMINI_API_KEY_3` = `AIzaSyCz6nDDfQAPulfwigvbpXt8FUYNMgDTNb4`
- `GEMINI_API_KEY_4` = `AIzaSyAStEQqYdG4sDmnTHeGR4YlNG2g8lNoiUM`
- `GEMINI_API_KEY_5` = `AIzaSyD3YowBslUM4cgsWFQJRuDRRAEpp9NzJGI`

### Optional Variables:
- `DATABASE_URL` = `sqlite:///./insurance_ai.db`
- `SECRET_KEY` = `your-secret-key-here`
- `GLM_API_URL` = `https://open.bigmodel.cn/api/paas/v4/`

## 🎯 **Hackathon Endpoint**

Your deployed endpoint will be:
```
POST https://your-app.vercel.app/hackrx/run
```

## ⚠️ **Important Vercel Limitations**

1. **Function Timeout**: 300 seconds max (5 minutes)
2. **Memory Limit**: 1GB max
3. **Cold Starts**: First request may be slow
4. **File Storage**: Temporary only

## 🏆 **Alternative Deployment Options**

For better hackathon performance, consider:

### **Railway** (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### **Render**
1. Connect GitHub repo
2. Set environment variables
3. Deploy automatically

### **Heroku**
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set GLM_API_KEY=your-key

# Deploy
git push heroku main
```

## 🧪 **Testing Your Deployment**

Test the hackathon endpoint:
```bash
curl -X POST "https://your-app.vercel.app/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## 📋 **Submission Checklist**

- ✅ Frontend deployed and accessible
- ✅ Backend API responding
- ✅ `/hackrx/run` endpoint working
- ✅ Environment variables set
- ✅ API key authentication working
- ✅ Document processing functional
- ✅ Multi-AI system operational

Your Insurance AI Assistant is ready for hackathon submission! 🏆
