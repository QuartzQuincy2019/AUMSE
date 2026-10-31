@echo off
rem ============================================================
rem  UME editor: configure + build (Windows)
rem
rem  Usage:  app\build.bat
rem
rem  Toolchain (same as tools\qt\a02):
rem      Qt 6.12.0 mingw_64    D:\Qt\6.12.0\mingw_64
rem      MinGW 13.1            D:\Qt\Tools\mingw1310_64
rem      CMake / Ninja         D:\Qt\Tools\...
rem  Installed elsewhere? Edit the three paths below.
rem  (Kept ASCII-only on purpose: cmd.exe reads .bat in the OEM
rem   code page, and UTF-8 Chinese comments break it.)
rem ============================================================
setlocal
set "QT=D:\Qt\6.12.0\mingw_64"
set "MINGW=D:\Qt\Tools\mingw1310_64"
set "CMAKE=D:\Qt\Tools\CMake_64\bin\cmake.exe"
set "NINJA=D:\Qt\Tools\Ninja\ninja.exe"

set "PATH=%QT%\bin;%MINGW%\bin;%PATH%"
set "HERE=%~dp0"
set "BUILD=%HERE%build"

if not exist "%QT%\bin\Qt6Widgets.dll" goto :noqt
if not exist "%BUILD%\build.ninja" goto :configure
goto :build

:configure
echo === configuring (cmake) ===
"%CMAKE%" -S "%HERE%." -B "%BUILD%" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="%QT%" -DCMAKE_CXX_COMPILER="%MINGW%\bin\g++.exe" -DCMAKE_MAKE_PROGRAM="%NINJA%"
if errorlevel 1 goto :fail

:build
echo === building (ninja) ===
"%NINJA%" -C "%BUILD%"
if errorlevel 1 goto :fail

echo.
echo Done: %BUILD%\ume.exe
echo Run : app\run.bat        (or: app\run.bat yourfile.txt)
exit /b 0

:noqt
echo [ERROR] %QT%\bin\Qt6Widgets.dll not found.
echo         Edit the QT path at the top of this file.
exit /b 1

:fail
echo.
echo [FAILED] build did not finish.
exit /b 1
