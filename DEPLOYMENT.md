# 📦 Deployment Guide

## Production Deployment

### Prerequisites
- Python 3.10+
- 2GB RAM minimum
- Stable internet connection (for data fetching)
- SQLite support

---

## Docker Deployment (Optional)

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501"]
```

### Build & Run
```bash
docker build -t ohlcv-validator .
docker run -p 8501:8501 -v $(pwd)/data:/app/data ohlcv-validator
```

---

## Linux/Unix Deployment

### System Setup
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3-pip

# Install project
cd ohlcv-validator
pip install -r requirements.txt
```

### Run as Service (systemd)

Create `/etc/systemd/system/ohlcv-pipeline.service`:
```ini
[Unit]
Description=OHLCV Data Pipeline
After=network.target

[Service]
Type=simple
User=ohlcv
WorkingDirectory=/opt/ohlcv-validator
ExecStart=/usr/bin/python3 /opt/ohlcv-validator/main.py
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ohlcv-pipeline
sudo systemctl start ohlcv-pipeline
sudo systemctl status ohlcv-pipeline
```

### Run Dashboard as Service

Create `/etc/systemd/system/ohlcv-dashboard.service`:
```ini
[Unit]
Description=OHLCV Data Dashboard
After=network.target

[Service]
Type=simple
User=ohlcv
WorkingDirectory=/opt/ohlcv-validator
ExecStart=/usr/bin/streamlit run dashboard/app.py --server.port 8501
Environment="PYTHONUNBUFFERED=1"
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ohlcv-dashboard
sudo systemctl start ohlcv-dashboard
```

---

## Windows Deployment

### Setup
```batch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run as Task Scheduler

**For Pipeline:**
1. Create `run_pipeline.bat`:
```batch
@echo off
cd C:\ohlcv-validator
python main.py
```

2. Open Task Scheduler
3. Create Basic Task
4. Set trigger (daily, hourly, etc.)
5. Set action: Run `run_pipeline.bat`

**For Dashboard:**
1. Create `run_dashboard.bat`:
```batch
@echo off
cd C:\ohlcv-validator
streamlit run dashboard/app.py
```

2. Create similar Task Scheduler task

---

## Kubernetes Deployment

### ConfigMap (config.yaml)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ohlcv-config
data:
  DEFAULT_TICKERS: "AAPL,MSFT,GOOGL"
  LOG_LEVEL: "INFO"
```

### Deployment (deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ohlcv-pipeline
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ohlcv
  template:
    metadata:
      labels:
        app: ohlcv
    spec:
      containers:
      - name: pipeline
        image: ohlcv-validator:latest
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: ohlcv-config
              key: LOG_LEVEL
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ohlcv-data-pvc
```

Deploy:
```bash
kubectl apply -f config.yaml
kubectl apply -f deployment.yaml
```

---

## Cloud Deployment

### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04)
ssh -i key.pem ubuntu@<instance-ip>

# Install dependencies
sudo apt-get update
sudo apt-get install python3.10 python3-pip git

# Clone repository
git clone <repo-url>
cd ohlcv-validator

# Setup
pip install -r requirements.txt

# Run with nohup
nohup python main.py > pipeline.log 2>&1 &
nohup streamlit run dashboard/app.py --server.port 8501 > dashboard.log 2>&1 &

# Access dashboard
# http://<instance-ip>:8501
```

### Google Cloud Run (Dashboard only)

```bash
# Create Dockerfile
# Push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ohlcv-dashboard

# Deploy
gcloud run deploy ohlcv-dashboard \
  --image gcr.io/PROJECT_ID/ohlcv-dashboard \
  --platform managed \
  --region us-central1 \
  --port 8501
```

### Heroku (Dashboard)

```bash
# Create Procfile
echo "web: streamlit run dashboard/app.py --server.port=\$PORT" > Procfile

# Deploy
heroku create ohlcv-app
git push heroku main
```

---

## Database Backup

### Backup SQLite Database
```bash
# Manual backup
cp ohlcv_data.db backups/ohlcv_data_$(date +%Y%m%d_%H%M%S).db

# Automated backup (cron)
0 2 * * * cd /opt/ohlcv-validator && cp ohlcv_data.db backups/ohlcv_data_$(date +\%Y\%m\%d_\%H\%M\%S).db
```

### Backup CSV Files
```bash
# Archive cleaned data
tar -czf data_clean_backup_$(date +%Y%m%d).tar.gz data/clean/

# Keep 7 days of backups
find backups/ -name "*.tar.gz" -mtime +7 -delete
```

---

## Monitoring & Health Checks

### Health Check Script
```python
import sqlite3
from pathlib import Path

def check_health():
    db_path = Path("ohlcv_data.db")
    
    # Check database exists
    if not db_path.exists():
        return False, "Database not found"
    
    # Check database integrity
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clean_ohlcv")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            return False, "No data in database"
        
        return True, f"OK - {count} records"
    except Exception as e:
        return False, f"Database error: {str(e)}"

if __name__ == "__main__":
    status, msg = check_health()
    print(f"Status: {'✓' if status else '✗'} {msg}")
    exit(0 if status else 1)
```

Run as health check:
```bash
# systemd
ExecStartPost=/usr/bin/python3 check_health.py

# Docker
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python check_health.py || exit 1
```

---

## Logging & Monitoring

### Log Aggregation (ELK Stack)

**Filebeat Configuration (filebeat.yml):**
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /opt/ohlcv-validator/logs/*.log

output.elasticsearch:
  hosts: ["localhost:9200"]

setup.kibana:
  host: "localhost:5601"
```

### Prometheus Metrics (optional)

Extend `main.py` to export metrics:
```python
from prometheus_client import Counter, Gauge, start_http_server

pipeline_success = Counter('ohlcv_pipeline_success', 'Successful pipelines', ['ticker'])
pipeline_failure = Counter('ohlcv_pipeline_failure', 'Failed pipelines', ['ticker'])
data_quality = Gauge('ohlcv_data_quality', 'Data quality score', ['ticker'])

# Start metrics server
start_http_server(8000)
```

---

## Performance Tuning

### Memory Optimization
- Process tickers in batches
- Use data chunking for large datasets
- Monitor memory usage

### Network Optimization
- Set connection timeouts
- Use retry backoff
- Cache frequently accessed data

### Database Optimization
- Create indices on date, ticker
- Use connection pooling
- Regular vacuum operations

```sql
-- Create indices
CREATE INDEX idx_date ON clean_ohlcv(date);
CREATE INDEX idx_ticker ON clean_ohlcv(ticker);
CREATE INDEX idx_ticker_date ON clean_ohlcv(ticker, date);

-- Vacuum
VACUUM;
```

---

## Security Considerations

1. **Environment Variables**
   - Don't commit credentials
   - Use `.env` files (gitignored)
   - Load via environment

2. **Database Encryption**
   - Enable encryption at rest
   - Use SQLCipher for encrypted databases

3. **Network Security**
   - Use HTTPS for dashboard
   - Implement authentication
   - Use firewall rules

4. **API Rate Limiting**
   - Limit yfinance requests
   - Implement caching
   - Handle rate limit errors

---

## Maintenance

### Daily
- Monitor logs for errors
- Check disk space
- Verify database integrity

### Weekly
- Review performance metrics
- Check data quality scores
- Backup critical data

### Monthly
- Database optimization
- Log rotation
- Dependency updates

---

For additional support, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)
