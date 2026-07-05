@echo off
REM ============================================================
REM  Fraud Detection System — one-file setup
REM  Run this from the repo root (the folder containing
REM  "backend" and "frontend"), on any Windows PC with
REM  Python 3.10+ and Node.js already installed.
REM ============================================================

echo.
echo === Checking prerequisites ===
where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [ERROR] Python not found on PATH. Install Python 3.10+ first: https://python.org
  exit /b 1
)
where node >nul 2>nul
if %errorlevel% neq 0 (
  echo [ERROR] Node.js not found on PATH. Install Node 18+ first: https://nodejs.org
  exit /b 1
)
echo Prerequisites OK.

echo.
echo === Backend setup ===
cd backend
if not exist venv (
  echo Creating virtual environment...
  python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing backend dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
  echo [ERROR] Backend dependency install failed. Check the error above.
  exit /b 1
)

if not exist .env (
  if exist .env.example (
    echo No .env found — copying .env.example. YOU MUST EDIT backend\.env
    echo with the real MONGO_URI and API_KEY before running the server.
    copy .env.example .env
  )
)
cd ..

echo.
echo === Frontend setup ===
cd frontend
echo Installing frontend dependencies (this may take a minute)...
call npm install
if %errorlevel% neq 0 (
  echo [ERROR] Frontend dependency install failed. Check the error above.
  exit /b 1
)

if not exist .env (
  if exist .env.example (
    echo No .env found — copying .env.example. YOU MUST EDIT frontend\.env
    echo with the matching API key and API URL before running the app.
    copy .env.example .env
  )
)
cd ..

echo.
echo ================================================================
echo  Setup complete.
echo.
echo  Before running, confirm these two files have matching values:
echo    backend\.env   -^> API_KEY=...
echo    frontend\.env  -^> VITE_API_KEY=...   (must match backend's API_KEY)
echo.
echo  To run the system, open TWO terminals:
echo.
echo    Terminal 1 (backend):
echo      cd backend
echo      venv\Scripts\activate
echo      uvicorn app.main:app --reload --port 8000
echo.
echo    Terminal 2 (frontend):
echo      cd frontend
echo      npm run dev
echo.
echo  Then open the URL shown by the frontend terminal (usually
echo  http://localhost:5173) in a browser.
echo ================================================================
pause
