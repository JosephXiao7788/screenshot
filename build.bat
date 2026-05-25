@echo off
chcp 65001 >nul
setlocal

echo === SuperShot 打包脚本 ===
echo.

cd /d "%~dp0"

if not exist icon.ico (
    echo [1/3] 生成图标...
    python make_icon.py
    if errorlevel 1 goto :error
) else (
    echo [1/3] 图标已存在，跳过。
)

echo.
echo [2/3] 清理旧构建...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo.
echo [3/3] PyInstaller 打包...
pyinstaller SuperShot.spec --clean --noconfirm
if errorlevel 1 goto :error

echo.
echo ========================================
echo  打包完成！
echo  输出: dist\SuperShot.exe
echo ========================================
echo.
explorer dist
goto :eof

:error
echo.
echo ✗ 打包失败，请检查上方错误信息。
exit /b 1
