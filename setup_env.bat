@echo off
REM *********************************************************************************
REM Batch file for setting up Houdini libs.
REM *********************************************************************************

ECHO.
ECHO Setting up Windows environment variables for Houdini Libs.
ECHO ==========================================================
ECHO.


REM *********************************************************************************
REM Search for python.
REM *********************************************************************************
REM ECHO Searching for Python in the Windows Registry...
REM reg query "hkcu\software\pytho"
ECHO Searching for a Python executable on your system...
for /f "tokens=*" %%a in (
'where PYTHON'
) do (
set PYTHON=%%a
) 
IF DEFINED PYTHON ECHO Found python here: %PYTHON%
IF NOT DEFINED PYTHON GOTO NO_PYTHON

REM *********************************************************************************
REM Check Python version is 2
REM *********************************************************************************
:FOUND_PYTHON
ECHO Checking version of Python...
for /f "tokens=*" %%a in (
'PYTHON --version'
) do (
set PYTHON_VERSION=%%a
)
ECHO Python version = %PYTHON_VERSION%
IF NOT "%PYTHON_VERSION:~0,8%"=="Python 2" GOTO WRONG_PYTHON

REM *********************************************************************************
REM Run Pthon script.
REM *********************************************************************************
ECHO Executing Python setup script...
ECHO.
cd setenv
python setenv.py
cd ..
ECHO.
GOTO :END

REM *********************************************************************************
REM Python not found
REM *********************************************************************************
:NO_PYTHON
ECHO ERROR: The Python executable was not found on your system. Setup failed!
ECHO.
ECHO Python 2.7 is already installed as part of Houdini.
ECHo Please add the folder of python.exe to the Windows PATH environment variable. 
ECHO The location should be soometing like this (check your version of Houdini):
ECHO C:\Program Files\Side Effects Software\Houdini 18.0.287\python27
ECHO
ECHO Once Python 2.x is set up, run this setup file again.
ECHO.
GOTO :END

REM *********************************************************************************
REM Python is not version 2.x
REM *********************************************************************************
:WRONG_PYTHON
ECHO ERROR: Python is the wrong version. This installation requires verion 2.x.
ECHO.
ECHO Python 2.7 is already installed as part of Houdini.
ECHo Please add the folder of python.exe to the Windows PATH environment variable. 
ECHO The location should be soometing like this (check your version of Houdini):
ECHO C:\Program Files\Side Effects Software\Houdini 18.0.287\python27
ECHO
ECHO Once Python 2.x is set up, run this setup file again.
ECHO.
GOTO :END

REM *********************************************************************************
REM The end.
REM *********************************************************************************
:END
ECHO Bye...
set /p dummy=Hit any key to exit.