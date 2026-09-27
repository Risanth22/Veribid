# Deployment Guide: AI Bid & Company Compliance Verification System

This application is ready for 24/7 cloud hosting on platforms like **Render**, **Railway**, **Fly.io**, or any cloud VM / Docker container.

---

## Architecture in Cloud Production

In production, the application runs through a unified WSGI gateway (`wsgi.py`):
- **`/`**: Main AI Audit Application (Procurement Officer Portal)
- **`/reference`**: Company Reference Data Portal (Admin View)
- **`/api/reference`**: Trusted Company Reference REST API
- **Verification Engine**: Connects to the Reference API and Google Gemini AI model for document analysis and compliance cross-checks.

---

## Option 1: Deploy to Render (Recommended — Free & Easiest)

Render provides free Python web hosting with automatic HTTPS SSL certificates.

### Step 1: Push your Code to GitHub

Open PowerShell in the project directory:

```powershell
# 1. Initialize git and commit your files
git init
git add .
git commit -m "Initial commit for cloud deployment"

# 2. Add your GitHub repository remote (replace with your repo URL)
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

*(Note: `.env` is automatically ignored by `.gitignore` so your secret API key will never be leaked).*

---

### Step 2: Create a Web Service on Render

1. Sign up / Log in to [Render.com](https://render.com/).
2. On your dashboard, click **"New +"** and select **"Web Service"**.
3. Choose **"Build and deploy from a Git repository"** and select your GitHub repository.
4. Fill in the deployment details:
   - **Name**: `veribid-compliance-audit` (or your choice)
   - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 180`
   - **Instance Type**: `Free`

---

### Step 3: Add Environment Variables

In the **Environment Variables** section on Render, add:

| Key | Value | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `your_actual_gemini_api_key` | Your Google Gemini API Key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | AI model name |
| `SECRET_KEY` | *(generate a random string)* | Flask session security |
| `PYTHON_VERSION` | `3.11.9` | Python runtime version |

5. Click **"Create Web Service"**.
6. Render will automatically build the environment, run the database seeds, and launch the service.
7. Your public URL will be live at:
   ```
   https://veribid-compliance-audit.onrender.com
   ```

---

## Option 2: Deploy to Railway

Railway detects the included `Dockerfile` or `Procfile` automatically.

1. Sign up / Log in to [Railway.app](https://railway.app/).
2. Click **"New Project"** -> **"Deploy from GitHub repo"**.
3. Select your repository.
4. Go to **Settings** -> **Variables**, and add:
   - `GEMINI_API_KEY`: `your_gemini_api_key`
   - `GEMINI_MODEL`: `gemini-2.5-flash`
5. Go to **Settings** -> **Networking** -> **Generate Domain** to get a public `*.up.railway.app` HTTPS URL.

---

## Option 3: Instant Public URL (Zero-Setup Tunnel)

If you need a public URL immediately to share or demo right now while running locally:

```powershell
npx -y localtunnel --port 5000
```
This gives you an instant public HTTPS URL (e.g., `https://cold-foxes-jump.loca.lt`) pointing directly to your local server.

---

## Verifying the Deployed Application

Once deployed, visit your public URL:
- **Officer Dashboard**: `https://<your-app-domain>/`
- **New Audit & Upload**: `https://<your-app-domain>/audit/new`
- **Reference Records Portal**: `https://<your-app-domain>/reference/companies`
- **Reference REST API**: `https://<your-app-domain>/api/reference/companies`
