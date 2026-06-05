# Deployment Plan

This document outlines the steps to deploy the application, with the backend hosted on **Railway** and the frontend hosted on **Vercel**.

## 1. Backend Deployment (Railway)

Railway provides a simple, Git-based deployment workflow for backend applications and databases.

### Build Command

pip install -r requirements.txt

### Start Command

uvicorn src.app:app --host 0.0.0.0 --port $PORT

### Environment Variables

ENABLE_SCHEDULER=1

CHROMA_COLLECTION=mutual_fund_chunks

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

### Prerequisites
- Ensure your backend code has a defined start script (e.g., `npm start`, `python app.py`, or a `Procfile`).
- Ensure all necessary dependencies are listed in your package manager file (e.g., `package.json`, `requirements.txt`).
- The backend should be configured to listen on the `PORT` environment variable (Railway assigns this automatically).

### Deployment Steps
1. **Login to Railway:** Go to [railway.app](https://railway.app) and log in with your GitHub account.
2. **Create a New Project:** Click "New Project" and select "Deploy from GitHub repo".
3. **Select Repository:** Choose the repository containing your backend code. (If it's a monorepo, specify the root directory for the backend).
4. **Add Variables:** Go to the "Variables" tab of your service and add all necessary environment variables (e.g., `DATABASE_URL`, API keys).
5. **Provision Database (Optional):** If your app requires a database, you can easily provision PostgreSQL, MySQL, or Redis within the same Railway project by clicking "New" -> "Database".
6. **Deploy:** Railway will automatically build and deploy your application. Monitor the "Deployments" tab for progress.
7. **Generate Domain:** Once deployed, go to the "Settings" tab and click "Generate Domain" under the Networking section to get your public API URL.

---

## 2. Frontend Deployment (Vercel)

Vercel is optimized for frontend frameworks and provides excellent developer experience with automatic preview deployments.


### Prerequisites
- The frontend codebase should be ready for a production build (e.g., `npm run build`).
- Any API calls should be configured to use an environment variable for the base URL so it can be updated to the Railway backend URL in production.

### Deployment Steps
1. **Login to Vercel:** Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. **Add New Project:** Click "Add New..." and select "Project".
3. **Import Repository:** Import the repository containing your frontend code. (If it's a monorepo, select the frontend folder as the Root Directory).
4. **Configure Project:**
   - **Framework Preset:** Vercel usually auto-detects the framework (e.g., Next.js, React, Vite). Confirm it's correct.
   - **Build and Output Settings:** Ensure the build command and output directory are correct for your framework.
5. **Environment Variables:** Expand the "Environment Variables" section. Add necessary variables, particularly the one pointing to your backend API.
   - Example: `VITE_API_URL` or `NEXT_PUBLIC_API_URL` = `<your-railway-generated-domain>`
6. **Deploy:** Click the "Deploy" button. Vercel will build and deploy the frontend.
7. **Verify:** Once finished, Vercel will provide a production URL. Visit the site to verify everything is working and successfully communicating with the Railway backend.

## 3. Scheduler Verification
1. Verify GitHub Actions workflow exists.
2. Verify Refresh Corpus workflow runs successfully.
3. Verify /refresh-status endpoint returns valid refresh data.
4. Confirm daily refresh schedule is configured for 10:00 AM IST.

## 4. Post-Deployment Verification
- Ensure CORS on the backend is configured to accept requests from the Vercel frontend domain.
- Test the core functionality of the application in the production environment.
- Monitor logs on both Railway and Vercel for any runtime errors.
