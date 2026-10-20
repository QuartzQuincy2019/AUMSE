@echo off
rem =====================================================================
rem  Build a minimal DLL and print its export table (the screen from the
rem  video).  Compile -> dumpbin /exports.
rem
rem  Usage: run this file from any cmd prompt, or just double-click it.
rem  vcvars64.bat is located through VCVARS below; edit it if yours differs.
rem
rem  NOTE: kept ASCII-only on purpose.  cmd.exe reads .bat as ANSI (GBK on
rem  this machine), so non-ASCII comments can split a line into garbage
rem  commands -- that actually happened the first time.
rem =====================================================================
setlocal

set "VCVARS=D:\MicrosoftVisualStudio\Community\VC\Auxiliary\Build\vcvars64.bat"

if not exist "%VCVARS%" (
    echo [ERROR] vcvars64.bat not found:
    echo         %VCVARS%
    echo         Edit the VCVARS line in this script.
    exit /b 1
)

call "%VCVARS%" >nul 2>&1
cd /d "%~dp0"
del /q demo.obj demo.dll demo.lib demo.exp >nul 2>&1

echo ============ 1/2  build ============
cl /LD /nologo /EHsc /utf-8 demo.cpp
if errorlevel 1 (
    echo.
    echo [ERROR] compile failed.
    exit /b 1
)

echo.
echo ============ 2/2  export table ============
dumpbin /exports demo.dll

echo.
echo ============ bonus: what it depends on ============
dumpbin /dependents demo.dll

endlocal
