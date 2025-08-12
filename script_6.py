# Create deployment configuration files and scripts

# 1. Create .streamlit/config.toml for Streamlit configuration
streamlit_config = '''[global]
dataFrameSerialization = "legacy"

[server]
headless = true
enableCORS = false
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
'''

import os
os.makedirs('.streamlit', exist_ok=True)
with open('.streamlit/config.toml', 'w') as f:
    f.write(streamlit_config)

# 2. Create Dockerfile for containerization
dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver for Selenium
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \\
    && wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \\
    && unzip chromedriver_linux64.zip \\
    && rm chromedriver_linux64.zip \\
    && mv chromedriver /usr/local/bin/chromedriver \\
    && chmod +x /usr/local/bin/chromedriver

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
'''

with open('Dockerfile', 'w') as f:
    f.write(dockerfile_content)

# 3. Create docker-compose.yml for local development
docker_compose_content = '''version: '3.8'

services:
  vahan-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
'''

with open('docker-compose.yml', 'w') as f:
    f.write(docker_compose_content)

# 4. Create deployment script
deployment_script = '''#!/bin/bash

echo "🚀 Vahan Dashboard Deployment Script"
echo "===================================="

# Check if running locally or on cloud
if [ "$1" = "local" ]; then
    echo "📦 Building and running locally with Docker..."
    
    # Build the Docker image
    docker build -t vahan-dashboard .
    
    # Run the container
    docker run -d \\
        --name vahan-dashboard \\
        -p 8501:8501 \\
        --restart unless-stopped \\
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
        echo "web: streamlit run main.py --server.port=\\$PORT --server.address=0.0.0.0" > Procfile
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
'''

with open('deploy.sh', 'w') as f:
    f.write(deployment_script)

# Make deployment script executable
os.chmod('deploy.sh', 0o755)

# 5. Create environment setup script
setup_script = '''#!/bin/bash

echo "🛠️ Vahan Dashboard Environment Setup"
echo "====================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
required_version="3.9"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 1 ]]; then
    echo "✅ Python $python_version found"
else
    echo "❌ Python $required_version or higher required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create data directory
mkdir -p data

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the dashboard:"
echo "  streamlit run main.py"
echo ""
echo "To run with Docker:"
echo "  ./deploy.sh local"
'''

with open('setup.sh', 'w') as f:
    f.write(setup_script)

# Make setup script executable
os.chmod('setup.sh', 0o755)

# 6. Create .gitignore
gitignore_content = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
env/
.venv/

# Data files
*.csv
*.xlsx
*.json
data/

# Logs
*.log
logs/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# Chrome driver
chromedriver
chromedriver.exe

# Temporary files
temp/
tmp/

# Environment variables
.env
.env.local

# Build files
build/
dist/
*.egg-info/
'''

with open('.gitignore', 'w') as f:
    f.write(gitignore_content)

print("Created deployment and configuration files:")
print("✅ .streamlit/config.toml - Streamlit configuration")
print("✅ Dockerfile - Container configuration")
print("✅ docker-compose.yml - Local Docker setup")
print("✅ deploy.sh - Deployment automation script")
print("✅ setup.sh - Environment setup script")
print("✅ .gitignore - Git ignore patterns")
print("\nDeployment options available:")
print("🐳 Docker: ./deploy.sh local")
print("☁️ Streamlit Cloud: ./deploy.sh cloud") 
print("🦄 Heroku: ./deploy.sh heroku")