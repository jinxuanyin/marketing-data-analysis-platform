@echo off
echo ===================================================
echo        营销数据分析平台启动程序
echo ===================================================
echo.

setlocal EnableDelayedExpansion

:: 设置颜色代码
set "INFO=[92m"
set "WARN=[93m"
set "ERROR=[91m"
set "RESET=[0m"

echo %INFO%[信息]%RESET% 正在启动营销数据分析平台...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %ERROR%[错误]%RESET% 未检测到Python安装，请安装Python 3.8+后重试
    goto :error
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %ERROR%[错误]%RESET% 未检测到Node.js安装，请安装Node.js 14+后重试
    goto :error
)

:: 创建日志目录
if not exist "%~dp0logs" mkdir "%~dp0logs"
set "LOG_FILE=%~dp0logs\startup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
set "LOG_FILE=!LOG_FILE: =0!"

echo %INFO%[信息]%RESET% 日志将保存到: !LOG_FILE!
echo.

:: 启动后端服务
echo %INFO%[信息]%RESET% 正在启动后端服务...
echo %INFO%[信息]%RESET% 正在安装Python依赖，这可能需要一些时间...

:: 修复matplotlib错误 - 在安装依赖前先尝试修复
echo %INFO%[信息]%RESET% 正在修复matplotlib字体管理器问题...
python -c "import matplotlib; matplotlib.font_manager._rebuild()" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %WARN%[警告]%RESET% matplotlib字体管理器修复失败，尝试替代方法...
    python -c "import matplotlib.font_manager as fm; fm._get_fontconfig_fonts = lambda: []; fm.findSystemFonts = lambda *args, **kwargs: []" >nul 2>&1
)

:: 安装后端依赖并启动服务
start cmd /k "cd /d %~dp0backend && ^
python -m pip install --no-build-isolation -r requirements.txt && ^
echo %INFO%[信息]%RESET% Python依赖安装完成！ && ^
echo %INFO%[信息]%RESET% 正在启动后端API服务... && ^
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 || ^
echo %ERROR%[错误]%RESET% 后端启动失败，请查看错误信息"

echo %INFO%[信息]%RESET% 等待后端服务启动...
timeout /t 10 /nobreak > nul

:: 检查后端服务是否成功启动
curl -s http://localhost:8000/ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %WARN%[警告]%RESET% 后端服务可能尚未完全启动，继续等待...
    timeout /t 5 /nobreak > nul
)

:: 启动前端服务
echo %INFO%[信息]%RESET% 正在启动前端服务...
start cmd /k "cd /d %~dp0frontend && ^
echo %INFO%[信息]%RESET% 正在安装前端依赖... && ^
npm install && ^
echo %INFO%[信息]%RESET% 前端依赖安装完成！ && ^
echo %INFO%[信息]%RESET% 正在启动前端开发服务器... && ^
npm start || ^
echo %ERROR%[错误]%RESET% 前端启动失败，请查看错误信息"

echo %INFO%[信息]%RESET% 服务启动中，请稍候...
timeout /t 5 /nobreak > nul

:: 显示成功信息
echo.
echo %INFO%====================================================%RESET%
echo %INFO%          应用已启动！%RESET%
echo %INFO%====================================================%RESET%
echo.
echo %INFO%[信息]%RESET% 后端API地址: http://localhost:8000
echo %INFO%[信息]%RESET% 前端页面地址: http://localhost:3000
echo.
echo %INFO%[提示]%RESET% 关闭此窗口不会停止服务，如需停止服务请关闭对应的命令行窗口。
echo %INFO%[提示]%RESET% 如遇到问题，请查看日志文件或参考安装问题修复说明。
echo.
goto :end

:error
echo.
echo %ERROR%[错误]%RESET% 启动失败，请解决上述问题后重试。
echo %ERROR%[错误]%RESET% 您也可以参考README_启动说明.md手动启动服务。

:end
pause