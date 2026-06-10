# Production Deployment Checklist

## ✅ Pre-Deployment Verification

### Code Quality

- [ ] All tests passing: `pytest --cov`
- [ ] Code formatted with Black: `black .`
- [ ] No linting errors: `flake8`
- [ ] Type hints added where needed
- [ ] Security warnings checked: `python manage.py check --deploy`
- [ ] No hardcoded secrets in code
- [ ] `.env` file in `.gitignore`

### Security Verification

- [ ] `DEBUG = False` in production .env
- [ ] `SECRET_KEY` is random (50+ chars)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS/SSL enabled (`SECURE_SSL_REDIRECT = True`)
- [ ] Database connection uses SSL
- [ ] Redis connection authenticated
- [ ] Email credentials are secure
- [ ] CORS configured for frontend domain only
- [ ] Rate limiting thresholds appropriate
- [ ] Audit logging enabled
- [ ] Password validator enforces strong passwords

### Database Setup

- [ ] [ ] All Neon tables created via manual SQL DDL
- [ ] [ ] Indexes created for performance
- [ ] [ ] Django migrations run: `python manage.py migrate`
- [ ] [ ] Database backups configured in Neon
- [ ] [ ] Connection pooling configured for Neon

### Environment Configuration

- [ ] DATABASE_URL set in production environment
- [ ] REDIS_URL configured (Redis Cloud or self-hosted)
- [ ] EMAIL_HOST credentials configured
- [ ] FRONTEND_URL set to production domain
- [ ] ALLOWED_HOSTS includes production domain
- [ ] CORS_ALLOWED_ORIGINS includes frontend domain
- [ ] All required .env variables are set

### Service Dependencies

- [ ] PostgreSQL database running (Neon)
- [ ] Redis cache running (Redis Cloud or Docker)
- [ ] Celery broker configured
- [ ] Celery worker service configured
- [ ] Celery beat scheduler configured (optional)

---

## 🚀 Deployment Steps

### 1. Database Setup (Run First!)

```bash
# In Neon SQL Editor:
# Run the complete DDL from SETUP_GUIDE.md
# Tables: roles, user_sectors, users, user_sessions, user_clients, audit_logs
```

### 2. Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --email admin@temacina.com
```

### 3. Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Deploy Application

**Using Gunicorn + Railway/Render/Heroku:**

```bash
# Install Gunicorn
pip install gunicorn

# Create Procfile (for Railway/Heroku)
echo "web: gunicorn config.wsgi:application" > Procfile

# Or run directly:
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

### 5. Start Background Workers

```bash
# Celery worker (required for async email)
celery -A config worker -l info --concurrency=4

# Celery beat (optional, for scheduled tasks)
celery -A config beat -l info
```

### 6. Verify Health

```bash
# Test API
curl https://api.yourdomain.com/api/v1/auth/login/
# Should return: 405 Method Not Allowed (correct - POST only)

# Test login endpoint
curl -X POST https://api.yourdomain.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@temacina.com","password":"YourPassword123!"}'
# Should return: 400 or 401 (credentials validation)
```

---

## 🔐 Security Post-Deployment

### HTTPS/SSL

- [ ] Obtain SSL certificate (Let's Encrypt free, auto-renewing)
- [ ] Configure HTTPS redirect (HTTP → HTTPS)
- [ ] Enable HSTS header (`Strict-Transport-Security`)
- [ ] Test SSL with: https://www.ssllabs.com/ssltest/

### Database Security

- [ ] Enable Neon backups (automatic daily)
- [ ] Test restore from backup
- [ ] Set database password policy
- [ ] Enable IP whitelist in Neon console
- [ ] Monitor slow queries logs

### Application Security

- [ ] Monitor error logs for exceptions
- [ ] Set up Sentry for error tracking
- [ ] Configure WAF (Web Application Firewall)
- [ ] Enable rate limiting by IP
- [ ] Monitor audit logs for suspicious activity
- [ ] Set up alerts for failed logins

### Access Control

- [ ] Limit SSH/admin access to IP whitelist
- [ ] Use service accounts with minimal permissions
- [ ] Enable MFA for admin access
- [ ] Regularly rotate credentials
- [ ] Audit user access logs

---

## 📊 Monitoring & Observability

### Logs

Configure centralized logging:

```python
# config/settings.py already has rotating file handlers
# LOGGING = {
#     "handlers": {
#         "file": "/path/to/logs/django.log",
#         "audit_file": "/path/to/logs/audit.log"
#     }
# }
```

### Metrics

- Monitor these metrics in production:
  - API response times (target: < 500ms)
  - Database query times (target: < 100ms)
  - Error rate (target: < 0.1%)
  - Successful logins vs failed logins
  - Cache hit rate (target: > 80%)
  - Worker queue depth (target: < 100)

### Alerts

Set up alerts for:

- [ ] High error rate (> 1%)
- [ ] Slow response times (> 1s)
- [ ] Database connection failures
- [ ] Redis connection failures
- [ ] Celery worker offline
- [ ] Disk space low (< 10%)
- [ ] High CPU usage (> 80%)
- [ ] High memory usage (> 85%)

### Example Monitoring Stack:

```
Docker + Prometheus + Grafana
OR
New Relic
OR
DataDog
OR
Sentry + LogRocket
```

---

## 🔄 Continuous Deployment

### GitHub Actions / CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest --cov

      - name: Run security checks
        run: python manage.py check --deploy

      - name: Deploy to Railway
        run: railway deploy
```

---

## 🆘 Incident Response

### Database Issues

1. Check Neon dashboard for connection errors
2. Verify IP whitelist settings
3. Check database size and storage quota
4. Review slow query logs
5. Trigger database backup restore if corrupted

### API Down

1. Check Gunicorn process status
2. Review logs for exceptions
3. Verify database connectivity
4. Check Redis availability
5. Verify environment variables are set

### Email Not Sending

1. Check Celery worker logs
2. Verify SMTP credentials
3. Test with direct SMTP: `python manage.py shell`
4. Check email queue depth
5. Review rate limiting - might be throttled

### Authentication Issues

1. Check JWT configuration
2. Verify SECRET_KEY hasn't changed
3. Review audit logs for failed logins
4. Check token expiry settings
5. Verify password reset token generation

### High CPU/Memory Usage

1. Check for runaway database queries
2. Review slow query logs
3. Increase cache timeout
4. Scale workers horizontally
5. Optimize N+1 queries

---

## 📈 Performance Optimization

### Database

- [ ] All indexes present
- [ ] Analyze query execution plans
- [ ] Enable query caching where appropriate
- [ ] Set connection pool size appropriately
- [ ] Monitor connection usage

### Caching

- [ ] User profile caching: 300s TTL ✅
- [ ] Session storage in Redis ✅
- [ ] Account lockout caching ✅
- [ ] API response caching (add if needed)
- [ ] Database query caching (add if needed)

### API Response

- [ ] Pagination implemented ✅
- [ ] Field filtering available ✅
- [ ] Lazy loading for related objects
- [ ] Response compression enabled
- [ ] CDN for static files

### Celery

- [ ] Concurrency set to 2-4x CPU cores
- [ ] Task timeouts configured
- [ ] Task retry logic for failures
- [ ] Monitor worker queue depth
- [ ] Scale workers horizontally under load

---

## 🔄 Maintenance

### Weekly

- [ ] Review error logs
- [ ] Monitor audit logs for suspicious activity
- [ ] Check performance metrics

### Monthly

- [ ] Database maintenance (analyze, reindex)
- [ ] Review and prune audit logs (optional)
- [ ] Update dependencies for security patches
- [ ] Rotate credentials
- [ ] Backup audit trail

### Quarterly

- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Compliance audit
- [ ] Architecture review

---

## 📞 Support & Escalation

### On-Call Runbook

1. **API down** → Check Gunicorn logs → Restart if needed
2. **Auth failing** → Check JWT config → Review audit logs
3. **Emails not sending** → Check Celery worker → Verify SMTP
4. **DB slow** → Check slow query logs → Analyze execution plans
5. **Memory leak** → Check worker processes → Restart if needed

### Escalation Path

- Level 1: Monitor alerts → Check logs → Restart services
- Level 2: Database admin → Infrastructure team
- Level 3: Security audit → External security firm

---

## ✅ Post-Deployment Checklist

- [ ] All services running and healthy
- [ ] SSL certificate active and valid
- [ ] Database backups working
- [ ] Monitoring and alerts active
- [ ] Team trained on runbooks
- [ ] Documentation updated
- [ ] Incident response plan reviewed
- [ ] User feedback collected
- [ ] Performance baseline established
- [ ] Security audit passed

---

**Last Updated:** June 2026  
**Status:** Ready for Production Deployment ✅
