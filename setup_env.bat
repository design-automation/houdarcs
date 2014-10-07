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
REM Run Pthon script.
REM *********************************************************************************
:FOUND_PYTHON
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
ECHO If Python is already installed somwhere on your system, then you need to add
ECHo the location of python.exe to the Windows PATH environment variable. 
ECHO If Python is not installed, then please install Python (verion 2.6 or 2.7). 
ECHO If you are not sure how to do this, then google it!
ECHO.
ECHO Once Python is set up, run this setup file again.
ECHO.
GOTO :END

REM *********************************************************************************
REM The end.
REM *********************************************************************************
:END
ECHO Bye...
set /p dummy=Hit any key to exit.