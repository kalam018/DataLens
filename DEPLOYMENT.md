# 🚀 Deployment Guide

Deploy DataLens to production on various platforms.

---

## 1. Streamlit Cloud (Easiest)

### Prerequisites
- GitHub account
- Your code pushed to a public repo

### Steps

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app" → "Deploy an app"
3. Paste your GitHub repo URL
4. Select `app.py` as the main file
5. Click "Deploy"

**Pros**: Free tier, auto-scaling, custom domain  
**Cons**: Limited to Streamlit Cloud infrastructure

---

## 2. Docker (Recommended)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run

```bash
# Build image
docker build -t datalens:latest .

# Run container
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/exports:/app/exports \
  datalens:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  datalens:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_CLIENT_TOOLBARMODE=minimal
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

**Pros**: Portable, consistent environments, easy scaling  
**Cons**: Requires Docker knowledge

---

## 3. AWS EC2

### Launch Instance

1. Go to AWS EC2 Console
2. Click "Launch instance"
3. Choose **Ubuntu 22.04 LTS** AMI
4. Select **t3.medium** or larger (min 4GB RAM)
5. Add security group:
   - Allow port 22 (SSH)
   - Allow port 8501 (Streamlit)
6. Launch and connect

### Setup on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Clone repo
git clone https://github.com/yourusername/data-analyzer.git
cd data-analyzer

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Use PM2 for Auto-Restart

```bash
# Install PM2 globally
sudo npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: "datalens",
    script: "./venv/bin/streamlit",
    args: "run app.py --server.port 8501",
    instances: 1,
    exec_mode: "cluster",
    env: {
      "NODE_ENV": "production"
    }
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

**Pros**: Full control, cost-effective, scalable  
**Cons**: Requires server management

---

## 4. Heroku

### Setup

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
3. Create `.streamlit/config.toml` (already included)

### Deploy

```bash
heroku create datalens-app
heroku config:set STREAMLIT_SERVER_HEADLESS=true
git push heroku main
```

**Pros**: Simple, automatic scaling  
**Cons**: Limited free tier, slow on large datasets

---

## 5. Google Cloud Run

### Steps

```bash
# Create Docker image
docker build -t datalens .

# Tag for GCR
docker tag datalens gcr.io/YOUR-PROJECT/datalens

# Push to GCR
docker push gcr.io/YOUR-PROJECT/datalens

# Deploy to Cloud Run
gcloud run deploy datalens \
  --image gcr.io/YOUR-PROJECT/datalens \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --allow-unauthenticated
```

**Pros**: Serverless, auto-scaling, pay-per-use  
**Cons**: Stateless (no persistent storage), cold start delays

---

## 6. Azure App Service

### Create Container Registry

```bash
az acr create --resource-group mygroup --name myregistry --sku Basic
```

### Build & Push

```bash
docker build -t datalens .
az acr build --registry myregistry --image datalens:latest .
```

### Deploy

```bash
az webapp create --resource-group mygroup \
  --plan myappplan \
  --name datalens \
  --deployment-container-image-name myregistry.azurecr.io/datalens:latest
```

---

## 7. On-Premises / Self-Hosted

### Nginx Reverse Proxy

```nginx
upstream streamlit {
    server localhost:8501;
}

server {
    listen 80;
    server_name datalens.example.com;

    location / {
        proxy_pass http://streamlit;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### With Systemd Service

```ini
[Unit]
Description=DataLens Analyzer
After=network.target

[Service]
Type=simple
User=dataanalyst
WorkingDirectory=/home/dataanalyst/data-analyzer
ExecStart=/home/dataanalyst/data-analyzer/venv/bin/streamlit run app.py --server.port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable with:
```bash
sudo systemctl enable datalens
sudo systemctl start datalens
```

---

## Performance Tuning

### For Production

1. **Increase upload size** (in `.streamlit/config.toml`):
   ```
   maxUploadSize = 5000  # MB
   ```

2. **Disable logs for performance**:
   ```
   logger.level = "error"
   ```

3. **Enable caching aggressively**:
   - Already implemented via `@st.cache_data`
   - Clear cache if needed: `streamlit cache clear`

4. **Set memory limits** (Docker):
   ```bash
   docker run --memory=8g --cpus=4 datalens:latest
   ```

5. **Use Parquet format** for imports (50% smaller than CSV)

---

## SSL/HTTPS

### Let's Encrypt (Free)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d datalens.example.com
```

Then in Nginx config:
```nginx
listen 443 ssl http2;
ssl_certificate /etc/letsencrypt/live/datalens.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/datalens.example.com/privkey.pem;
```

---

## Monitoring & Logging

### Logs
```bash
# Docker
docker logs -f datalens

# Systemd
journalctl -u datalens -f

# Streamlit Cloud
View directly in dashboard
```

### Health Checks
```bash
curl -f http://localhost:8501/_stcore/health || exit 1
```

### Resource Monitoring
```bash
# Check memory usage
ps aux | grep streamlit

# Monitor with htop
htop
```

---

## Database Integration (Optional)

Connect to external databases for scalability:

```python
# In app.py
import duckdb
import sqlalchemy

# PostgreSQL
engine = sqlalchemy.create_engine("postgresql://user:pass@localhost/datalens")
df = pl.read_database("SELECT * FROM data", connection=engine)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port already in use** | `lsof -i :8501` then kill process |
| **Out of memory** | Increase RAM, enable swapfile |
| **Slow uploads** | Use Parquet format, increase `maxUploadSize` |
| **CORS errors** | Enable in `.streamlit/config.toml` |
| **Connection timeout** | Increase `client.toolbarMode = "minimal"` |

---

**Happy deploying! 🎉**
