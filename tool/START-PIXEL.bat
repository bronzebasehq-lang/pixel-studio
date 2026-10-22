@echo off
chcp 65001 >nul
title PIXEL STUDIO
cd /d %~dp0
echo ============================================
echo   PIXEL STUDIO - Tool video ve bang code
echo   Phong cach khoa: PIXEL 16-BIT
echo ============================================
echo.
where python >nul 2>nul
if errorlevel 1 goto LOIPYTHON
where ffmpeg >nul 2>nul
if not errorlevel 1 goto CHAY
if exist ffmpeg.exe goto CHAY
goto LOIFFMPEG
:CHAY
echo Dang mo Pixel Studio...
echo Trinh duyet se tu mo o dia chi http://localhost:8766
echo De TAT tool: quay lai cua so nay va nhan Ctrl+C, hoac dong cua so.
echo.
python server.py
echo.
echo Pixel Studio da tat.
pause
exit /b 0
:LOIPYTHON
echo.
echo [LOI] Khong tim thay Python tren may.
echo Hay cai Python 3 roi mo lai file nay. Xem HUONG-DAN.md, Buoc 1.
echo.
pause
exit /b 1
:LOIFFMPEG
echo.
echo [LOI] Khong tim thay ffmpeg tren may.
echo Hay lam theo HUONG-DAN.md, Buoc 3, roi mo lai file nay.
echo.
pause
exit /b 1
