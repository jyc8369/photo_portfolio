@echo off
echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Auto commit %date% %time%"

echo Pushing to GitHub...
git push origin main

echo Done!
pause