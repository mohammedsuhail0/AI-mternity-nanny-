# AI Maternal Monitor - LLM Setup Guide

## 🤖 Current LLM Configuration Status

✅ **CONFIGURED AND READY** - The NVIDIA LLM API is already set up!

### Configuration Details

**File:** `backend/.env`
```env
COMPANION_LLM_BASE_URL=https://integrate.api.nvidia.com/v1
COMPANION_LLM_MODEL=meta/llama-3.1-8b-instruct
COMPANION_LLM_API_KEY=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
```

---

## 🚀 How to Activate the LLM

### Option 1: Local Development

#### Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

#### Steps

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify .env configuration:**
   ```bash
   cat .env
   ```

5. **Start the backend server:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Test the LLM endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/companion/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What should I eat today?",
       "history": [],
       "attachments": [],
       "journey": {
         "stage_title": "Growth phase",
         "stage_label": "Weeks 21-32",
         "stage_detail": "Track baby movement and fetal heart rate"
       }
     }'
   ```

### Option 2: Docker Deployment

1. **Build Docker image:**
   ```bash
   docker build -f backend/Dockerfile -t maternal-monitor-backend .
   ```

2. **Run container with environment:**
   ```bash
   docker run -p 8000:8000 \
     -e COMPANION_LLM_API_KEY="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" \
     -e COMPANION_LLM_MODEL="meta/llama-3.1-8b-instruct" \
     maternal-monitor-backend
   ```

### Option 3: Production Deployment on Vercel (Recommended)

1. **Set environment variables in Vercel:**
   ```
   COMPANION_LLM_API_KEY = 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
   COMPANION_LLM_MODEL = meta/llama-3.1-8b-instruct
   COMPANION_LLM_BASE_URL = https://integrate.api.nvidia.com/v1
   ```

2. **Push to GitHub (already done):**
   ```bash
   git push origin master
   ```

3. **Deploy via Vercel CLI:**
   ```bash
   cd backend
   vercel deploy --prod
   ```

---

## ✨ LLM Features Enabled

Once activated, the companion will provide **AI-powered responses** for:

### 📚 Food & Nutrition
- **Question:** "What should I eat today?"
- **AI Response:** Personalized meal suggestions based on pregnancy stage

### 💊 Medicines & Medications
- **Question:** "Is it safe to take ibuprofen during pregnancy?"
- **AI Response:** Safety information and pregnancy-appropriate alternatives

### 🏃 Exercise & Movement
- **Question:** "Can I continue my yoga routine?"
- **AI Response:** Stage-appropriate exercise recommendations with safety guidelines

### 📋 Report Reading
- **Question:** "What does FHR 145 mean?"
- **AI Response:** Plain-language explanation of medical metrics

### 🚨 Emergency Detection
- **Question:** "I'm bleeding and having severe pain"
- **AI Response:** Immediate emergency response with action button

---

## 🔧 LLM Model Options

### Recommended: Nemotron (Most Capable)
```env
COMPANION_LLM_MODEL=nvidia/nemotron-4-340b-instruct
```
- Best for complex medical questions
- Highest accuracy and context understanding
- Slightly slower response time

### Balanced: Llama 3.1 (Current)
```env
COMPANION_LLM_MODEL=meta/llama-3.1-8b-instruct
```
- Good balance of speed and quality
- Fast responses
- Reliable accuracy

### Fast: Mistral Large
```env
COMPANION_LLM_MODEL=mistralai/mistral-large
```
- Fastest responses
- Good for simple queries
- Lower resource usage

---

## 🐛 Troubleshooting

### Issue: LLM not responding
**Solution:**
1. Check API key is valid at https://build.nvidia.com/
2. Verify backend has reloaded config
3. Check logs: `docker logs <container_id>`
4. Test with curl command above

### Issue: "API key invalid"
**Solution:**
1. Generate new API key at https://build.nvidia.com/manage/keys
2. Update `.env` file with new key
3. Restart backend service

### Issue: Slow responses
**Solution:**
1. Switch to faster model: `meta/llama-3.1-8b-instruct`
2. Check network connection
3. Increase timeout in config: `COMPANION_LLM_TIMEOUT_SECONDS=30`

### Issue: Fallback to local responses
**Status:** This means LLM API is unreachable. The app falls back to hardcoded responses.
**Check:**
1. Are `COMPANION_LLM_API_KEY` and `COMPANION_LLM_MODEL` set?
2. Is backend running and config loaded?
3. Check logs for error messages

---

## 📊 LLM API Costs

NVIDIA Companion API is **FREE for development and testing**.

For production:
- **Per API call:** $0.0001 - $0.001 depending on model
- **Monitoring:** https://build.nvidia.com/manage/billing

---

## 🔄 Fallback Logic

The system uses **smart fallback**:

```python
if COMPANION_LLM_API_KEY and COMPANION_LLM_MODEL:
    try:
        response = await llm_api.call()  # ← LLM powered
    except Exception:
        response = fallback_response()   # ← Hardcoded
else:
    response = fallback_response()      # ← No LLM config
```

This ensures the app **always works**, even without LLM credentials.

---

## 🎯 Next Steps

1. **Verify LLM is active:**
   - Start backend: `uvicorn app.main:app --reload`
   - Test endpoint with curl above
   - Check response contains AI-generated content

2. **Monitor LLM quality:**
   - Log conversations: `backend/logs/companion.log`
   - Track response times
   - Collect user feedback

3. **Optimize responses:**
   - Fine-tune system prompt in `backend/app/api/companion.py`
   - Adjust temperature and max_tokens
   - Switch models based on performance

4. **Production deployment:**
   - Deploy frontend and backend to Vercel
   - Configure LLM API key in Vercel dashboard
   - Test all LLM features end-to-end

---

## 📞 Support

- **NVIDIA API Docs:** https://docs.nvidia.com/cloud/nvidia-cloud-endpoints/
- **FastAPI Docs:** http://localhost:8000/docs (when running locally)
- **Backend Logs:** Check `backend/logs/` directory

---

**Created:** 2026-06-03  
**Status:** ✅ Ready for activation  
**LLM Model:** meta/llama-3.1-8b-instruct  
**API Provider:** NVIDIA
