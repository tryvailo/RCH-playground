# 🔑 API Keys Setup Guide

**Status:** ✅ CRITICAL ISSUE #2 - Configuration Instructions  
**Created:** 23 Dec 2025  
**Audience:** DevOps, System Administrators

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Copy Environment Template
```bash
cp .env.local.example .env.local
```

### Step 2: Get API Keys (see table below)

### Step 3: Edit .env.local
```bash
# Edit the file and replace placeholders with real keys
nano .env.local
# or
vim .env.local
```

### Step 4: Verify Configuration
```bash
# Check if keys are set
npm run check:env

# Expected output:
# ✅ Companies House API - Configured
# ✅ Google Places API - Configured
# ✅ CQC API - Configured
# ✅ Perplexity API - Configured
# ✅ All required API keys are configured!
```

### Step 5: Deploy
```bash
npm run build
npm start
```

---

## 📋 API Keys Required

| API | Cost | Effort | Priority | Link |
|-----|------|--------|----------|------|
| **Companies House** | Free | 5 min | 🔴 CRITICAL | https://beta.companieshouse.gov.uk/developer/applications |
| **Google Places** | Paid (~$7/1000) | 10 min | 🔴 CRITICAL | https://console.cloud.google.com |
| **CQC** | Free | 5 min | 🔴 CRITICAL | https://www.cqc.org.uk/news/stories/new-cqc-api-now-available |
| **Perplexity** | Paid (~$0.002/request) | 5 min | 🔴 CRITICAL | https://www.perplexity.ai/api |
| **OS Places** | Paid (optional) | 10 min | 🟡 OPTIONAL | https://www.ordnancesurvey.co.uk/business-government/products/os-places-api |

---

## 🔐 Companies House API

### Getting the Key (5 minutes)
1. Go to: https://beta.companieshouse.gov.uk/developer/applications
2. Sign in (create account if needed - free)
3. Create new application
4. Copy the API Key
5. Add to `.env.local`:
```
COMPANIES_HOUSE_API_KEY=your_key_here
```

### Verify
```bash
curl -H "Authorization: Bearer $COMPANIES_HOUSE_API_KEY" \
  'https://api.companieshouse.gov.uk/company/search?q=test'

# Expected: 200 OK response with companies
```

### Service Impact
- ✅ Financial Enrichment (Altman Z-score, bankruptcy risk)
- 📊 Used in: Professional Report Section 12
- 🎯 Critical for: Financial stability assessment

---

## 🌍 Google Places API

### Getting the Key (10 minutes)
1. Go to: https://console.cloud.google.com
2. Create new project (or select existing)
3. Enable "Places API" (not "Places SDK")
4. Create API Key (Credentials → Create Credentials → API Key)
5. Set API restrictions:
   - Restrict to "Places API"
   - Add HTTP referrer restrictions (for security)
6. Copy the API Key
7. Add to `.env.local`:
```
GOOGLE_PLACES_API_KEY=your_key_here
```

### Setup Application Restrictions (IMPORTANT!)
```
In Google Cloud Console:
1. Select your API Key
2. Click "Edit"
3. Under "Application restrictions":
   - Select "HTTP referrers (web sites)"
   - Add: https://yourdomain.com/*
   - Add: http://localhost:3000/* (for local development)
4. Under "API restrictions":
   - Select "Places API"
5. Save
```

### Cost Management
```
Free tier: $0 for first $200/month
After that: $7 per 1,000 requests

Estimate for your needs:
- 100 homes enriched = ~100 requests
- Cost: ~$0.70

Recommendation:
1. Set up billing alert in Google Cloud
2. Set daily quota limit (e.g., 1000 requests)
3. Monitor in Google Cloud Console
```

### Verify
```bash
curl -s "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=test&inputtype=textquery&key=$GOOGLE_PLACES_API_KEY" | jq

# Expected: JSON response with places
```

### Service Impact
- ✅ Google Places Enrichment (reviews, photos, ratings)
- 📊 Used in: Professional Report Sections 10, 11, 15, 16
- 🎯 Critical for: Community reputation assessment

---

## 🏥 CQC API

### Getting the Key (5 minutes)
1. Go to: https://www.cqc.org.uk/news/stories/new-cqc-api-now-available
2. Request API access (form)
3. Wait for approval (usually 1-2 business days)
4. Receive API Key via email
5. Add to `.env.local`:
```
CQC_API_KEY=your_key_here
```

### Documentation
- API Docs: https://www.cqc.org.uk/guidance-providers/all-services/api-guidance
- Rate limits: 100 requests/minute
- Free tier: Yes, no cost

### Verify
```bash
curl -H "Authorization: Bearer $CQC_API_KEY" \
  'https://api.cqc.org.uk/api/v1/locations/1-1234567890'

# Expected: 200 OK with location details
```

### Service Impact
- ✅ CQC Deep Dive Enrichment (inspection history, ratings)
- 📊 Used in: Professional Report Sections 6, 8
- 🎯 Critical for: Safety analysis, regulated activity verification

---

## 🧠 Perplexity AI API

### Getting the Key (5 minutes)
1. Go to: https://www.perplexity.ai/api
2. Sign up for free trial or paid account
3. Create API Key in dashboard
4. Add to `.env.local`:
```
PERPLEXITY_API_KEY=your_key_here
```

### Cost Management
```
Free trial: $5 credit
Pricing: ~$0.002 per request (varies by model)

Estimate for your needs:
- 100 homes enriched = ~100 requests
- Cost: ~$0.20

Recommendation:
1. Start with free trial ($5)
2. Monitor usage in dashboard
3. Set spending limit in account settings
4. Can be disabled via feature flag if needed
```

### Models Available
- sonar-pro (default, fastest)
- sonar (cheaper)

### Verify
```bash
curl -s https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "test"}]
  }' | jq

# Expected: JSON response with completion
```

### Service Impact
- ✅ Staff Enrichment (Glassdoor data, staff research)
- 📊 Used in: Professional Report Section 9
- 🎯 Critical for: Staff quality assessment

---

## 🗺️ OS Places API (Optional)

### About
- **Cost:** Paid (pricing varies)
- **Requirement:** Optional - falls back to OSM Overpass if not configured
- **Impact:** Improves neighbourhood enrichment accuracy

### Getting the Key
1. Go to: https://www.ordnancesurvey.co.uk/business-government/products/os-places-api
2. Request API access
3. Wait for approval
4. Receive API Key
5. Add to `.env.local`:
```
OS_PLACES_API_KEY=your_key_here
```

### Decision Tree
```
Does your budget allow paid APIs?
├─ Yes → Get OS Places API for best accuracy
└─ No → Skip (OSM Overpass works fine)
```

---

## ✅ Deployment Checklist

### For Development
```
[ ] Copy .env.local.example to .env.local
[ ] Get Companies House API key (5 min)
[ ] Get Google Places API key (10 min)
[ ] Get CQC API key (5 min - may take 1-2 days for approval)
[ ] Get Perplexity API key (5 min)
[ ] Run: npm run check:env
[ ] Verify: npm test -- --testPathPatterns="enrichment"
[ ] Start dev server: npm run dev
```

### For Staging
```
[ ] Copy .env.local to Vercel Preview env vars
[ ] Or set in CI/CD pipeline
[ ] Run build: npm run build
[ ] Run tests: npm test
[ ] Deploy to staging
[ ] Test enrichment with real data
```

### For Production
```
[ ] Set all 4 required API keys in Vercel Production env vars
[ ] Set feature flags to match production needs
[ ] Run: npm run build (verify compilation)
[ ] Run: npm test (verify tests pass)
[ ] Set up monitoring/alerts for API failures
[ ] Set daily quota limits in API dashboards
[ ] Enable rate limiting in code (if needed)
[ ] Deploy to production
[ ] Monitor API usage and costs
[ ] Have fallback plan if API goes down
```

---

## 🔍 Verification Commands

### Check if keys are configured
```bash
# In Node script or bash:
echo "Companies House: $COMPANIES_HOUSE_API_KEY"
echo "Google Places: $GOOGLE_PLACES_API_KEY"
echo "CQC: $CQC_API_KEY"
echo "Perplexity: $PERPLEXITY_API_KEY"

# Expected: Non-empty strings (not "your_xxx_here")
```

### Run automated verification
```bash
# Add this to your CI/CD pipeline
npm run check:env

# Add to package.json scripts:
# "check:env": "node -e \"require('./lib/shared/utils/env-validation').checkEnvironmentAtStartup()\""
```

### Test each API individually
```bash
# Companies House
curl -H "Authorization: Bearer $COMPANIES_HOUSE_API_KEY" \
  'https://api.companieshouse.gov.uk/company/search?q=test'

# Google Places
curl "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=test&inputtype=textquery&key=$GOOGLE_PLACES_API_KEY"

# CQC
curl -H "Authorization: Bearer $CQC_API_KEY" \
  'https://api.cqc.org.uk/api/v1/locations'

# Perplexity
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar-pro","messages":[{"role":"user","content":"test"}]}'
```

---

## 🚨 Troubleshooting

### "Missing required API keys"
**Solution:** 
1. Check `.env.local` exists (cp .env.local.example .env.local)
2. Fill in actual key values (not placeholders)
3. Restart server: npm run dev

### "401 Unauthorized" error
**Solutions:**
- Verify key is correct (no typos, copy-paste issues)
- Check API restrictions in dashboard (may need to add your domain)
- Check if key is still valid (may have expired)

### "429 Too Many Requests" error
**Solution:**
- Set daily quota limit in API dashboard
- Implement rate limiting (already in code, can be tuned)
- Cache results more aggressively (TTL settings in .env)

### "API working locally but not in production"
**Common causes:**
- API key not set in Vercel environment variables
- API key set only in .env.local (not synced to production)
- Domain IP whitelisting issue (Google Places)
**Solutions:**
1. Go to Vercel Project Settings → Environment Variables
2. Add all 4 API keys to Production environment
3. Redeploy (new deployment picks up env vars)
4. Verify: npm run check:env in production logs

### "Enrichment service slow/timing out"
**Possible causes:**
- API is slow (check status page)
- Network latency
- Timeout too short
**Solution:**
1. Increase timeout in .env: ENRICHMENT_TIMEOUT_PER_SOURCE=45
2. Check API status page
3. Review logs for specific failures

---

## 📞 Support

### Check Logs
```bash
# Development
npm run dev
# Look for "Enrichment" in logs

# Production (Vercel)
# Go to Vercel dashboard → Deployments → Logs
```

### Monitoring
```
Add to your dashboard:
- API key validation check
- API response times
- Error rates per API
- Rate limit approaching alerts
```

### Gradual Rollout
```
If deploying to production for first time:
1. Deploy to staging first
2. Run enrichment for 10 homes
3. Verify all services work
4. Monitor costs for 1 day
5. Deploy to production
6. Monitor 24/7 for first week
```

---

**Created:** 23 Dec 2025  
**Last Updated:** 23 Dec 2025  
**Status:** READY FOR USE
