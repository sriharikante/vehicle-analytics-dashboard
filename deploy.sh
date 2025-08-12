#!/bin/bash

echo "🚀 Vahan Dashboard Deployment Script"
echo "===================================="

# Check if running locally or on cloud
if [ "$1" = "local" ]; then
    echo "📦 Building and running locally with Docker..."

    # Build the Docker image
    docker build -t vahan-dashboard .

    # Run the container
    docker run -d \
        --name vahan-dashboard \
        -p 8501:8501 \
        --restart unless-stopped \
        vahan-dashboard

    echo "✅ Dashboard running at http://localhost:8501"

elif [ "$1" = "cloud" ]; then
    echo "☁️ Deploying to Streamlit Cloud..."
    echo "Please ensure you have:"
    echo "1. Pushed code to GitHub"
    echo "2. Connected repository to Streamlit Cloud"
    echo "3. Set main.py as entry point"
    echo ""
    echo "Visit: https://share.streamlit.io to deploy"

elif [ "$1" = "heroku" ]; then
    echo "🦄 Deploying to Heroku..."

    # Create Procfile if it doesn't exist
    if [ ! -f Procfile ]; then
        echo "web: streamlit run main.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
        echo "Created Procfile"
    fi

    # Initialize git if needed
    if [ ! -d .git ]; then
        git init
        git add .
        git commit -m "Initial commit"
    fi

    # Create Heroku app
    heroku create vahan-dashboard-$(date +%s)

    # Set buildpacks
    heroku buildpacks:set heroku/python
    heroku buildpacks:add --index 1 heroku-community/apt

    # Create Aptfile for Chrome dependencies
    echo "google-chrome-stable" > Aptfile

    # Deploy
    git push heroku main

    echo "✅ Deployed to Heroku"

else
    echo "Usage: ./deploy.sh [local|cloud|heroku]"
    echo ""
    echo "Options:"
    echo "  local  - Run locally with Docker"
    echo "  cloud  - Deploy to Streamlit Cloud (manual steps)"
    echo "  heroku - Deploy to Heroku"
fi
