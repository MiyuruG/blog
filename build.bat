@echo off
setlocal enabledelayedexpansion

:: Set colors for output
color 0A

:: Set the Hugo blog directory
set "HUGO_DIR=D:\McBoss Blog Public\McBoss-Blog"

echo ===============================================
echo           McBoss Blog Mega Build Script
echo ===============================================
echo.

:: Change to Hugo directory
cd /d "%HUGO_DIR%"
if errorlevel 1 (
    echo ❌ ERROR: Could not change to Hugo directory: %HUGO_DIR%
    pause
    exit /b 1
)

echo 📁 Working directory: %CD%
echo.

:: Step 1: Robocopy mirror posts
echo ========================================
echo 🔄 STEP 1: Syncing posts from Obsidian
echo ========================================
robocopy "D:\Obsidian Vault - MCBOSS BLOG\McBoss Blog\posts" "D:\McBoss Blog Public\McBoss-Blog\content\posts" /mir
set robocopy_result=!errorlevel!

if !robocopy_result! leq 7 (
    echo ✅ Robocopy completed successfully
) else (
    echo ❌ Robocopy failed with exit code: !robocopy_result!
    echo Continuing anyway...
)
echo.

:: Step 2: Process images
echo ========================================
echo 🖼️  STEP 2: Processing images
echo ========================================
python3 "D:\McBoss Blog Public\McBoss-Blog\images.py"
if errorlevel 1 (
    echo ❌ ERROR: Image processing failed
    pause
    exit /b 1
)
echo ✅ Image processing completed
echo.

:: Step 3: Git add
echo ========================================
echo 📝 STEP 3: Adding files to git
echo ========================================
git add .
if errorlevel 1 (
    echo ❌ ERROR: Git add failed
    pause
    exit /b 1
)
echo ✅ Files added to git staging
echo.

:: Step 4: Git commit with dynamic message
echo ========================================
echo 💾 STEP 4: Committing changes
echo ========================================

:: Generate dynamic commit message with timestamp
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set today=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set now=%%a:%%b
set "timestamp=%today% %now%"
set "commit_msg=🚀 Blog update - %timestamp%"

git commit -m "%commit_msg%"
set commit_result=!errorlevel!

if !commit_result! equ 0 (
    echo ✅ Changes committed successfully
    echo 📝 Commit message: %commit_msg%
) else (
    echo ⚠️  No changes to commit or commit failed
    echo This might be normal if no files were changed
)
echo.

:: Step 5: Git push
echo ========================================
echo 🚀 STEP 5: Pushing to remote repository
echo ========================================
git push
if errorlevel 1 (
    echo ❌ ERROR: Git push failed
    echo Check your internet connection and git credentials
    pause
    exit /b 1
)
echo ✅ Changes pushed to remote repository
echo.

:: Success summary
echo ===============================================
echo           🎉 BUILD COMPLETE! 🎉
echo ===============================================
echo ✅ Posts synced from Obsidian
echo ✅ Images processed and references updated  
echo ✅ Changes committed to git
echo ✅ Changes pushed to remote repository
echo.
echo 🌐 Your blog should be updated shortly!
echo ===============================================

:: Optional: Open blog in browser
set /p open_blog="🌍 Open blog in browser? (y/n): "
if /i "!open_blog!"=="y" (
    start https://www.mcboss.top/
)

pause
exit /b 0