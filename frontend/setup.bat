@echo off
REM Run this from inside the extracted fraud-frontend folder
echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
  echo npm install failed. Check the error above.
  exit /b 1
)
echo.
echo Setup complete. Edit .env with your real API key before running.
echo Starting dev server...
call npm run dev
