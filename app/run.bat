@echo off
rem ============================================================
rem  UME editor: run
rem
rem   app\run.bat                                   open the editor
rem   app\run.bat file.txt                          open with a file
rem   app\run.bat --selftest file.txt --outdir out  caret/hit/selection self-test
rem   app\run.bat --render file.txt --out page.png  render one page offscreen
rem
rem  Why this wrapper: ume.exe needs Qt's DLLs. Double-clicking
rem  the exe directly fails with "Qt6Widgets.dll not found".
rem  (ASCII-only on purpose, see build.bat.)
rem ============================================================
setlocal
set "QT=D:\Qt\6.12.0\mingw_64"
set "PATH=%QT%\bin;%PATH%"
set "EXE=%~dp0build\ume.exe"

if not exist "%EXE%" goto :nobuild

"%EXE%" %*
exit /b %ERRORLEVEL%

:nobuild
echo [ERROR] not built yet: run app\build.bat first.
exit /b 1
