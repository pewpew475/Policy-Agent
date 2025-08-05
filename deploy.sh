#!/bin/bash

# Insurance AI Assistant - Vercel Deployment Script

echo "🚀 Deploying Insurance AI Assistant to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
echo "🔐 Checking Vercel authentication..."
vercel whoami || vercel login

# Set environment variables
echo "🔧 Setting up environment variables..."
echo "Please set these environment variables in your Vercel dashboard:"
echo "- GLM_API_KEY"
echo "- GEMINI_API_KEY_1 through GEMINI_API_KEY_5"
echo "- DATABASE_URL"
echo "- SECRET_KEY"

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "📋 Next steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Test the /hackrx/run endpoint"
echo "3. Submit your Vercel URL to the hackathon"
