'''
Created on Aug 16, 2010

@author: dexen
'''
import os
import csv
import string
import datetime
import math

from py2energyplus import idf_writer

#Find where EnergyPlus is installed
EP_FOLDER_NAME = "energyplusv"
paths = os.environ["path"].split(";")
EP_PATH = None
for path in paths:
    if EP_FOLDER_NAME in path.lower():
        EP_PATH = path
        break
if not EP_PATH:
    print "EnergyPlus was not found."
    raise Exception("EnergyPlus was not found.")


EPL_RUN_BAT_TEMPLATE = """
:  EnergyPlus Batch File for EP-Launch Program 
:  Created on: 8 Mar 2000 by J. Glazer
:  Based on:   RunE+.bat 17 AUG 99 by M.J. Witte
:  Revised:    17 Jul 2000, Linda Lawrie (beta 3 release)
:              27 Sep 2000, Witte/Glazer - add saves for EP-Macro results
:              17 Oct 2000, Lawrie - remove wthrfl option (BLAST weather)
:              09 Feb 2001, Lawrie - Add siz and mtr options, use 3dl and sln files
:              08 Aug 2001, Lawrie - add option for epinext environment variable
:              09 Oct 2001, Lawrie - put in explanation of epinext environment variable
:                                  - also add eplusout.cif for Comis Input Report
:              05 Dec 2001, Lawrie - add new eplusout.bnd (Branch/Node Details)
:              17 Dec 2001, Glazer - explain eptype for no weather case
:              19 Dec 2001, Lawrie - add eplusout.dbg, eplusout.trn, eplusmtr.csv
:                                  - also create eplusmtr.csv 
:              20 Sep 2002, Witte  - Delete all "pausing" stops except the one right
:                                    after EnergyPlus.exe
:              18 Feb 2003, Lawrie - change name of audit.out to eplusout.audit and save it
:              29 Jul 2003, Glazer - add tabular report file handling
:              21 Aug 2003, Lawrie - add "map" file handling
:              21 Aug 2003, Lawrie - change to "styled" output for sizing, map and tabular files
:              29 Aug 2003, Glazer - delete old .zsz and .ssz files if present
:               8 Sep 2003, Glazer - add ReadVars txt and tab outputs
:                                    unlimited columns option
:              09 Feb 2004, Lawrie - add DElight files
:              30 Mar 2004, Glazer - get rid of TRN file
:              30 Jul 2004, Glazer - added use of epout variable as part of groups in ep-launch
:              22 Feb 2005, Glazer - added ExpandObjects preprocessor
:              06 Jun 2006, Lawrie - remove cfp file, add shd file
:              21 Aug 2006, Lawrie - add wrl file
:              22 Aug 2006, Glazer - add convertESOMTR
:              27 Nov 2006, Lawrie - add mdd file
:              20 Feb 2007, Glazer - add csvProc
:              03 Mar 2008, Glazer - add weather stat file copying
:              04 Sep 2008, Lawrie - add sql output
:              09 Jun 2009, Griffith - add edd output (for EMS)
:              05 Feb 2010, Glazer - add basement and slab integration
:              02 Aug 2010, Lawrie - add DFS (daylighting factors) output
:              31 Aug 2010, Glazer - uses local temporary directory for use in multiple processors              
:
:  This batch file can execute EnergyPlus using either command line parameters
:  or environmental variables. The most common method is to use environmental
:  variables but for some systems that do not allow the creation of batch files
:  the parameter passing method should be used.   When not passing parameters the
:  environmental variables are set as part of RUNEP.BAT file and are shown below
: 
:  The batch file should be called from the temporary working directory location.
:
:  When passing parameters instead the first parameter (%1) should be PARAM and the other
:  parameters are shown in the list.
:
:        %epin% or %1 contains the file with full path and no extensions for input files
:
:        %epout% or %2 contains the file with full path and no extensions for output files
:
:        %epinext% or %3 contains the extension of the file selected from the EP-Launch
:          program.  Could be imf or idf -- having this parameter ensures that the
:          correct user selected file will be used in the run.
:
:        %epwthr% or %4 contains the file with full path and extension for the weather file
:         
:        %eptype% or %5 contains either "EP" or "NONE" to indicate if a weather file is used
:
:        %pausing% or %6 contains Y if pause should occur between major portions of
:          batch file
:
:        %maxcol% or %7 contains "250" if limited to 250 columns otherwise contains
:                 "nolimit" if unlimited (used when calling readVarsESO)
:
:        %convESO% or %8 contains Y if convertESOMTR program should be called
:
:        %procCSV% or %9 contains Y if csvProc program should be called
:
:        
:  This batch file is designed to be used only in the EnergyPlus directory that
:  contains the EnergyPlus.exe, Energy+.idd and Energy+.ini files.
:
:  EnergyPlus requires the following files as input:
:
:       Energy+.ini   - ini file with path to idd file (blank = current dir)
:       Energy+.idd   - input data dictionary
:       In.idf        - input data file (must be compatible with the idd version)
:
:       In.epw        - EnergyPlus format weather file
:
:  EnergyPlus will create the following files:
: 
:       Eplusout.audit-  Echo of input (Usually without echoing IDD)
:       Eplusout.end  -  A one line synopsis after the run (success/fail)
:       Eplusout.err  -  Error file
:       Eplusout.eso  -  Standard output file
:       Eplusout.eio  -  One time output file
:       Eplusout.rdd  -  Report variable data dictionary
:       Eplusout.dxf  -  DXF (from report, Surfaces, DXF;)
:       Eplusout.mtr  -  Meter output (similar to ESO format)
:       Eplusout.mtd  -  Meter Details (see what variable is on what meter)
:       Eplusout.bnd  -  Branch/Node Details Report File
:       Eplusout.dbg  -  A debugging file -- see Debug Output object for description
:       Others -- see "Clean up Working Directory for current list"
:
:  The Post Processing Program (PPP) requires the following files as input:
:
:       Eplusout.inp  -  PPP command file (specifies input and output files)
:         This file name is user specified as standard input on the command line  
:         but we will standardize on Eplusout.inp (optional)
:
:       Eplusout.eso  -  Input data (the standard output file from EnergyPlus)
:         This file name is user specified in Eplusout.inp but we will 
:         standardize on Eplusout.eso (can also accept the eplusout.mtr file)
:                        
:
:  The Post Processing Program produces the following output files:
:
:       Eplusout.csv  -  PPP output file in CSV format
:         This file name is user specified in Eplusout.inp but we will 
:         standardize on Eplusout.csv
:
:  This batch file will perform the following steps:
:
:   1.  Clean up directory by deleting old working files from prior run
:   2.  Copy %1.idf (input) into In.idf (or %1.imf to in.imf)
:   3.  Copy %2 (weather) into In.epw
:       Run the Basement preprocessor program if necessary
:       Run the Slab preprocessor program if necessary
:   4.  Execute EnergyPlus
:   5.  If available Copy %1.rvi (post processor commands) into Eplusout.inp
:       If available Copy %1.mvi (post processor commands) into eplusmtr.inp
:       or create appropriate input to get meter output from eplusout.mtr
:   6.  Execute ReadVarsESO.exe (the Post Processing Program)
:       Execute ReadVarsESO.exe (the Post Processing Program) for meter output
:   7.  Copy Eplusout.* to %1.*
:   8.  Clean up directory.
:
: The EPL-RUN.BAT file should be may be either located in the same directory 
: as EnergyPlus.exe or in the temporary directory. If the batch file is in the same
: directory as EnergyPlus.exe the program path is the same as the location 
: the batch file. If the batch file is in the temporary directory the path 
: for the location of EnergyPlus.exe will be passed as a parameter named epPath.

 SET program_path=%~dp0
 IF "%epPath%" NEQ "" SET program_path=%epPath%

: Set flag if the current directory is the same directory that EnergyPlus and the 
: batch file are located.

 SET inEPdir=FALSE
 IF "%program_path%"=="%CD%\" SET inEPdir=TRUE

: Set the variables if a command line is used
IF "%9"=="" GOTO skipSetParams
SET epin=%~1
SET epout=%~2
SET epinext=%3
SET epwthr=%~4
SET eptype=%5
SET pausing=%6
SET maxcol=%7
SET convESO=%8
SET procCSV=%9
:skipSetParams
:
:  1. Clean up working directory
IF EXIST eplusout.inp   DEL eplusout.inp
IF EXIST eplusout.end   DEL eplusout.end
IF EXIST eplusout.eso   DEL eplusout.eso
IF EXIST eplusout.rdd   DEL eplusout.rdd
IF EXIST eplusout.mdd   DEL eplusout.mdd
IF EXIST eplusout.dbg   DEL eplusout.dbg
IF EXIST eplusout.eio   DEL eplusout.eio
IF EXIST eplusout.err   DEL eplusout.err
IF EXIST eplusout.dxf   DEL eplusout.dxf
IF EXIST eplusout.csv   DEL eplusout.csv
IF EXIST eplusout.tab   DEL eplusout.tab
IF EXIST eplusout.txt   DEL eplusout.txt
IF EXIST eplusmtr.csv   DEL eplusmtr.csv
IF EXIST eplusmtr.tab   DEL eplusmtr.tab
IF EXIST eplusmtr.txt   DEL eplusmtr.txt
IF EXIST eplusout.sln   DEL eplusout.sln
IF EXIST epluszsz.csv   DEL epluszsz.csv
IF EXIST epluszsz.tab   DEL epluszsz.tab
IF EXIST epluszsz.txt   DEL epluszsz.txt
IF EXIST eplusssz.csv   DEL eplusssz.csv
IF EXIST eplusssz.tab   DEL eplusssz.tab
IF EXIST eplusssz.txt   DEL eplusssz.txt
IF EXIST eplusout.mtr   DEL eplusout.mtr
IF EXIST eplusout.mtd   DEL eplusout.mtd
IF EXIST eplusout.bnd   DEL eplusout.bnd
IF EXIST eplusout.dbg   DEL eplusout.dbg
IF EXIST eplusout.sci   DEL eplusout.sci
IF EXIST eplusmap.csv   DEL eplusmap.csv
IF EXIST eplusmap.txt   DEL eplusmap.txt
IF EXIST eplusmap.tab   DEL eplusmap.tab
IF EXIST eplustbl.csv   DEL eplustbl.csv
IF EXIST eplustbl.txt   DEL eplustbl.txt
IF EXIST eplustbl.tab   DEL eplustbl.tab
IF EXIST eplustbl.htm   DEL eplustbl.htm
IF EXIST eplusout.log   DEL eplusout.log
IF EXIST eplusout.svg   DEL eplusout.svg
IF EXIST eplusout.shd   DEL eplusout.shd
IF EXIST eplusout.wrl   DEL eplusout.wrl
IF EXIST eplusout.delightin   DEL eplusout.delightin
IF EXIST eplusout.delightout  DEL eplusout.delightout
IF EXIST eplusout.delighteldmp  DEL eplusout.delighteldmp
IF EXIST eplusout.delightdfdmp  DEL eplusout.delightdfdmp
IF EXIST eplusscreen.csv  DEL eplusscreen.csv
IF EXIST in.imf         DEL in.imf
IF EXIST in.idf         DEL in.idf
IF EXIST in.stat        DEL in.stat
IF EXIST out.idf        DEL out.idf
IF EXIST eplusout.inp   DEL eplusout.inp
IF EXIST in.epw         DEL in.epw
IF EXIST eplusout.audit DEL eplusout.audit
IF EXIST eplusmtr.inp   DEL eplusmtr.inp
IF EXIST test.mvi       DEL test.mvi
IF EXIST expanded.idf   DEL expanded.idf
IF EXIST expandedidf.err   DEL expandedidf.err
IF EXIST readvars.audit   DEL readvars.audit
IF EXIST eplusout.sql   DEL eplusout.sql
IF EXIST sqlite.err  DEL sqlite.err
IF EXIST eplusout.edd  DEL eplusout.edd
IF EXIST eplusout.dfs  DEL eplusout.dfs
IF EXIST slab.int DEL slab.int
IF EXIST BasementGHTIn.idf DEL BasementGHTIn.idf
:if %pausing%==Y pause

:  2. Copy input data file to working directory
IF EXIST "%epout%.epmidf" DEL "%epout%.epmidf"
IF EXIST "%epout%.epmdet" DEL "%epout%.epmdet"

IF NOT EXIST "Energy+.idd" copy "%program_path%Energy+.idd" "Energy+.idd"
IF NOT EXIST "Energy+.ini" copy "%program_path%Energy+.ini" "Energy+.ini"
if "%epinext%" == "" set epinext=idf
if exist "%epin%.%epinext%" copy "%epin%.%epinext%" in.%epinext%
if exist in.imf "%program_path%EPMacro"
if exist out.idf copy out.idf "%epout%.epmidf"
if exist audit.out copy audit.out "%epout%.epmdet"
if exist audit.out erase audit.out
if exist out.idf MOVE out.idf in.idf
if exist in.idf "%program_path%ExpandObjects"
if exist expandedidf.err COPY expandedidf.err eplusout.end
if exist expanded.idf COPY expanded.idf "%epout%.expidf"
if exist expanded.idf MOVE expanded.idf in.idf
if not exist in.idf copy "%epin%.idf" In.idf
:if %pausing%==Y pause

:  3. Test for weather file type and copy to working directory
if %eptype%==EP    copy "%epwthr%" In.epw
: Convert from an extension of .epw to .stat
if %eptype%==EP    SET wthrstat=%epwthr:~0,-4%.stat
if %eptype%==EP    copy "%wthrstat%" in.stat
:if %pausing%==Y pause

: Run the Basement preprocessor program if necessary
IF EXIST "%epin%.bsmt" COPY "%epin%.bsmt" EPObjects.txt
IF EXIST BasementGHTIn.idf DEL EPObjects.txt
IF NOT EXIST BasementGHTIn.idf GOTO :skipBasement
IF EXIST eplusout.end DEL eplusout.end
IF EXIST audit.out DEL audit.out
IF EXIST basementout.audit DEL basementout.audit
IF EXIST "%epout%_bsmt.csv" ERASE "%epout%_bsmt.csv"
IF EXIST "%epout%_bsmt.audit" ERASE "%epout%_bsmt.audit"
IF EXIST "%epout%_bsmt.out" ERASE "%epout%_bsmt.out"
IF EXIST "%epout%_out_bsmt.idf" ERASE "%epout%_out_bsmt.idf"
IF EXIST "%program_path%PreProcess\GrndTempCalc\BasementGHT.idd" COPY "%program_path%PreProcess\GrndTempCalc\BasementGHT.idd" BasementGHT.idd
ECHO Begin Basement Temperature Calculation processing . . . 
"%program_path%PreProcess\GrndTempCalc\Basement.exe"
IF EXIST "MonthlyResults.csv" MOVE "MonthlyResults.csv" "%epout%_bsmt.csv"
IF EXIST "RunINPUT.TXT" MOVE "RunINPUT.TXT" "%epout%_bsmt.out"
IF EXIST "RunDEBUGOUT.txt" MOVE "RunDEBUGOUT.txt" basementout.audit
IF NOT EXIST basementout.audit echo Basement Audit File > basementout.audit
IF EXIST audit.out copy basementout.audit + audit.out basementout.audit
IF EXIST "eplusout.err" copy basementout.audit + eplusout.err basementout.audit
IF EXIST basementout.audit MOVE basementout.audit "%epout%_bsmt.audit"
IF EXIST eplusout.end DEL eplusout.end
IF EXIST audit.out DEL audit.out
IF EXIST basementout.audit DEL basementout.audit
IF EXIST EPObjects.txt COPY EPObjects.txt "%epin%.bsmt"
IF EXIST BasementGHTIn.idf DEL BasementGHTIn.idf
IF EXIST BasementGHT.idd DEL BasementGHT.idd
:skipBasement
IF EXIST EPObjects.txt COPY in.idf+EPObjects.txt in.idf /B
IF EXIST EPObjects.txt COPY "%epout%.expidf"+EPObjects.txt "%epout%.expidf" /B
IF EXIST EPObjects.txt DEL EPObjects.txt

: Run the Slab preprocessor program if necessary
IF EXIST "%epin%.slab" COPY "%epin%.slab" SLABSurfaceTemps.TXT
IF EXIST GHTIn.idf DEL SLABSurfaceTemps.TXT
IF NOT EXIST GHTIn.idf GOTO :skipSlab
IF EXIST eplusout.end DEL eplusout.end
IF EXIST SLABINP.TXT DEL SLABINP.TXT
IF EXIST "SLABSplit Surface Temps.TXT" DEL "SLABSplit Surface Temps.TXT"
IF EXIST audit.out DEL audit.out
IF EXIST "%epout%_slab.ger" ERASE "%epout%_slab.ger"
IF EXIST "%program_path%PreProcess\GrndTempCalc\SlabGHT.idd" COPY "%program_path%PreProcess\GrndTempCalc\SlabGHT.idd" SlabGHT.idd
ECHO Begin Slab Temperature Calculation processing . . . 
"%program_path%PreProcess\GrndTempCalc\Slab.exe"
IF EXIST eplusout.err MOVE eplusout.err "%epout%_slab.ger"
IF EXIST SLABINP.TXT MOVE SLABINP.TXT "%epout%_slab.out"
IF EXIST eplusout.end DEL eplusout.end
IF EXIST "SLABSplit Surface Temps.TXT" DEL "SLABSplit Surface Temps.TXT"
IF EXIST audit.out DEL audit.out
IF EXIST SLABSurfaceTemps.TXT COPY SLABSurfaceTemps.TXT "%epin%.slab"
IF EXIST GHTIn.idf DEL GHTIn.idf
IF EXIST SlabGHT.idd DEL SlabGHT.idd
:skipSlab
IF EXIST SLABSurfaceTemps.TXT COPY in.idf+SLABSurfaceTemps.TXT in.idf /B
IF EXIST SLABSurfaceTemps.TXT COPY "%epout%.expidf"+SLABSurfaceTemps.TXT "%epout%.expidf" /B
IF EXIST SLABSurfaceTemps.TXT DEL SLABSurfaceTemps.TXT

:  4. Execute EnergyPlus
"%program_path%EnergyPlus"
if %pausing%==Y pause

:  5. Copy Post Processing Program command file(s) to working directory
IF EXIST "%epin%.rvi" copy "%epin%.rvi" Eplusout.inp
IF EXIST "%epin%.mvi" copy "%epin%.mvi" Eplusmtr.inp
:if %pausing%==Y pause

:  6. Run Post Processing Program(s)
if %maxcol%==250     SET rvset=
if %maxcol%==nolimit SET rvset=unlimited
: readvars creates audit in append mode.  start it off
echo %date% %time% ReadVars >readvars.audit

IF NOT EXIST "%program_path%postprocess\convertESOMTRpgm\convertESOMTR.exe" GOTO skipConv
COPY %program_path%postprocess\convertESOMTRpgm\convert.txt convert.txt
IF %convESO%==Y "%program_path%postprocess\convertESOMTRpgm\convertESOMTR"
IF EXIST ip.eso DEL eplusout.eso
IF EXIST ip.eso MOVE ip.eso eplusout.eso
IF EXIST ip.mtr DEL eplusout.mtr
IF EXIST ip.mtr MOVE ip.mtr eplusout.mtr
IF EXIST convert.txt DEL convert.txt
:skipConv

IF EXIST eplusout.inp "%program_path%postprocess\ReadVarsESO.exe" eplusout.inp %rvset%
IF NOT EXIST eplusout.inp "%program_path%postprocess\ReadVarsESO.exe" " " %rvset%
IF EXIST eplusmtr.inp "%program_path%postprocess\ReadVarsESO.exe" eplusmtr.inp %rvset%
IF NOT EXIST eplusmtr.inp echo eplusout.mtr >test.mvi
IF NOT EXIST eplusmtr.inp echo eplusmtr.csv >>test.mvi
IF NOT EXIST eplusmtr.inp "%program_path%postprocess\ReadVarsESO.exe" test.mvi %rvset%
"%program_path%postprocess\HVAC-Diagram.exe"

if %pausing%==Y pause

:  7. Copy output files to input/output path
IF EXIST "%epout%.eso" DEL "%epout%.eso"
IF EXIST "%epout%.rdd" DEL "%epout%.rdd"
IF EXIST "%epout%.mdd" DEL "%epout%.mdd"
IF EXIST "%epout%.eio" DEL "%epout%.eio"
IF EXIST "%epout%.err" DEL "%epout%.err"
IF EXIST "%epout%.dxf" DEL "%epout%.dxf"
IF EXIST "%epout%.csv" DEL "%epout%.csv"
IF EXIST "%epout%.tab" DEL "%epout%.tab"
IF EXIST "%epout%.txt" DEL "%epout%.txt"
IF EXIST "%epout%Meter.csv" DEL "%epout%Meter.csv"
IF EXIST "%epout%Meter.tab" DEL "%epout%Meter.tab"
IF EXIST "%epout%Meter.txt" DEL "%epout%Meter.txt"
IF EXIST "%epout%.sln" DEL "%epout%.sln"
IF EXIST "%epout%Zsz.csv" DEL "%epout%Zsz.csv"
IF EXIST "%epout%Zsz.tab" DEL "%epout%Zsz.tab"
IF EXIST "%epout%Zsz.txt" DEL "%epout%Zsz.txt"
IF EXIST "%epout%Ssz.csv" DEL "%epout%Ssz.csv"
IF EXIST "%epout%Ssz.tab" DEL "%epout%Ssz.tab"
IF EXIST "%epout%Ssz.txt" DEL "%epout%Ssz.txt"
IF EXIST "%epout%.mtr" DEL "%epout%.mtr"
IF EXIST "%epout%.mtd" DEL "%epout%.mtd"
IF EXIST "%epout%.bnd" DEL "%epout%.bnd"
IF EXIST "%epout%.dbg" DEL "%epout%.dbg"
IF EXIST "%epout%.sci" DEL "%epout%.sci"
IF EXIST "%epout%Map.csv" DEL "%epout%Map.csv"
IF EXIST "%epout%Map.tab" DEL "%epout%Map.tab"
IF EXIST "%epout%Map.txt" DEL "%epout%Map.txt"
IF EXIST "%epout%.audit" DEL "%epout%.audit"
IF EXIST "%epout%Table.csv" DEL "%epout%Table.csv"
IF EXIST "%epout%Table.tab" DEL "%epout%Table.tab"
IF EXIST "%epout%Table.txt" DEL "%epout%Table.txt"
IF EXIST "%epout%Table.html" DEL "%epout%Table.html"
IF EXIST "%epout%DElight.in" DEL "%epout%DElight.in"
IF EXIST "%epout%DElight.out" DEL "%epout%DElight.out"
IF EXIST "%epout%DElight.dfdmp" DEL "%epout%DElight.dfdmp"
IF EXIST "%epout%DElight.eldmp" DEL "%epout%DElight.eldmp"
IF EXIST "%epout%.svg" DEL "%epout%.svg"
IF EXIST "%epout%.shd" DEL "%epout%.shd"
IF EXIST "%epout%.wrl" DEL "%epout%.wrl"
IF EXIST "%epout%Screen.csv" DEL "%epout%Screen.csv"
IF EXIST "%epout%.rvaudit" DEL "%epout%.rvaudit"
IF EXIST "%epout%.sql" DEL "%epout%.sql"
IF EXIST "%epout%-PROC.csv" DEL "%epout%-PROC.csv"
IF EXIST "%epout%.edd" DEL "%epout%.edd"
IF EXIST "%epout%DFS.csv" DEL "%epout%DFS.csv"

IF EXIST eplusout.eso MOVE eplusout.eso "%epout%.eso"
IF EXIST eplusout.rdd MOVE eplusout.rdd "%epout%.rdd"
IF EXIST eplusout.mdd MOVE eplusout.mdd "%epout%.mdd"
IF EXIST eplusout.eio MOVE eplusout.eio "%epout%.eio"
IF EXIST eplusout.err MOVE eplusout.err "%epout%.err"
IF EXIST eplusout.dxf MOVE eplusout.dxf "%epout%.dxf"
IF EXIST eplusout.csv MOVE eplusout.csv "%epout%.csv"
IF EXIST eplusout.tab MOVE eplusout.tab "%epout%.tab"
IF EXIST eplusout.txt MOVE eplusout.txt "%epout%.txt"
IF EXIST eplusmtr.csv MOVE eplusmtr.csv "%epout%Meter.csv"
IF EXIST eplusmtr.tab MOVE eplusmtr.tab "%epout%Meter.tab"
IF EXIST eplusmtr.txt MOVE eplusmtr.txt "%epout%Meter.txt"
IF EXIST eplusout.sln MOVE eplusout.sln "%epout%.sln"
IF EXIST epluszsz.csv MOVE epluszsz.csv "%epout%Zsz.csv"
IF EXIST epluszsz.tab MOVE epluszsz.tab "%epout%Zsz.tab"
IF EXIST epluszsz.txt MOVE epluszsz.txt "%epout%Zsz.txt"
IF EXIST eplusssz.csv MOVE eplusssz.csv "%epout%Ssz.csv"
IF EXIST eplusssz.tab MOVE eplusssz.tab "%epout%Ssz.tab"
IF EXIST eplusssz.txt MOVE eplusssz.txt "%epout%Ssz.txt"
IF EXIST eplusout.mtr MOVE eplusout.mtr "%epout%.mtr"
IF EXIST eplusout.mtd MOVE eplusout.mtd "%epout%.mtd"
IF EXIST eplusout.bnd MOVE eplusout.bnd "%epout%.bnd"
IF EXIST eplusout.dbg MOVE eplusout.dbg "%epout%.dbg"
IF EXIST eplusout.sci MOVE eplusout.sci "%epout%.sci"
IF EXIST eplusmap.csv MOVE eplusmap.csv "%epout%Map.csv"
IF EXIST eplusmap.tab MOVE eplusmap.tab "%epout%Map.tab"
IF EXIST eplusmap.txt MOVE eplusmap.txt "%epout%Map.txt"
IF EXIST eplusout.audit MOVE eplusout.audit "%epout%.audit"
IF EXIST eplustbl.csv MOVE eplustbl.csv "%epout%Table.csv"
IF EXIST eplustbl.tab MOVE eplustbl.tab "%epout%Table.tab"
IF EXIST eplustbl.txt MOVE eplustbl.txt "%epout%Table.txt"
IF EXIST eplustbl.htm MOVE eplustbl.htm "%epout%Table.html"
IF EXIST eplusout.delightin MOVE eplusout.delightin "%epout%DElight.in"
IF EXIST eplusout.delightout MOVE eplusout.delightout "%epout%DElight.out"
IF EXIST eplusout.delightdfdmp MOVE eplusout.delightdfdmp "%epout%DElight.dfdmp"
IF EXIST eplusout.delighteldmp MOVE eplusout.delighteldmp "%epout%DElight.eldmp"
IF EXIST eplusout.svg MOVE eplusout.svg "%epout%.svg"
IF EXIST eplusout.shd MOVE eplusout.shd "%epout%.shd"
IF EXIST eplusout.wrl MOVE eplusout.wrl "%epout%.wrl"
IF EXIST eplusscreen.csv MOVE eplusscreen.csv "%epout%Screen.csv"
IF EXIST readvars.audit MOVE readvars.audit "%epout%.rvaudit"
IF EXIST eplusout.sql MOVE eplusout.sql "%epout%.sql"
IF EXIST eplusout.edd MOVE eplusout.edd "%epout%.edd"
IF EXIST eplusout.dfs MOVE eplusout.dfs "%epout%DFS.csv"

IF NOT EXIST "%program_path%postprocess\CSVproc.exe" GOTO skipProc
IF %procCSV%==Y "%program_path%postprocess\CSVproc.exe" %epout%.csv
:skipProc

:if %pausing%==Y pause

:  8.  Clean up directory.
IF EXIST eplusout.inp DEL eplusout.inp
IF EXIST eplusmtr.inp DEL eplusmtr.inp
IF EXIST in.idf       DEL in.idf
IF EXIST in.imf       DEL in.imf
IF EXIST in.epw       DEL in.epw
IF EXIST in.stat      DEL in.stat
IF EXIST eplusout.dbg DEL eplusout.dbg
IF EXIST test.mvi DEL test.mvi
IF EXIST expandedidf.err DEL expandedidf.err
IF EXIST readvars.audit DEL readvars.audit
IF EXIST sqlite.err  DEL sqlite.err

: Only if current directory is not the directory that EnergyPlus is located clean up
: the IDD and INI files.
IF "%inEPdir%"=="FALSE" DEL Energy+.idd
IF "%inEPdir%"=="FALSE" DEL Energy+.ini


:if %pausing%==Y pause
:  Finished

"""

class Idf(object):
    
    def __init__(self):
        self.zones = []
        self.runperiods = []
        self.outputvars = []
        self.outputmeter = []
        self.buildingshades = []
        self.daylight_controls = []
        self.version = None
        self.time_step = None
        self.shadow_calc = None
        self.building_data = None
        self.result_file_path = None
        self.terrain = None
        self.solar_dist = None
        self.max_warmup_days = None
        self.ground_temp = None
        self.return_air_fracs = None #lights
        self.controller_num_steps = None
        self.controller_setpoints = None
        self.controller_glare_azimuth = None
        self.controller_glare_index = None
        self.controller_glare_azimuth = None
        self.create_pv_walls = None
        self.create_pv_roofs = None
        self.create_pv_shades = None
        self.pv_frac_srf = None
        self.pv_efficiency = None
        self.output_control_table_style = None
        self.output_surfaces_drawings = []
        self.output_table_summary_reports = []
        
    def set_version(self, version):
        self.version = version
        
    def set_time_step(self, time_step):
        self.time_step = time_step
        
    def set_shadow_calc(self, calc_frequency, max_figures):
        self.shadow_calc = (calc_frequency, max_figures)
        
    def set_terrain(self, terrain):
        self.terrain = terrain
        
    def set_solar_dist(self, solar_dist):
        self.solar_dist = solar_dist
        
    def set_max_warmup_days(self, max_warmup_days):
        self.max_warmup_days = max_warmup_days
        
    def set_ground_temp(self, ground_temp):
        self.ground_temp = ground_temp
        
    def set_create_pv_walls(self, create_pv_walls):
        self.create_pv_walls = create_pv_walls
    
    def set_create_pv_roofs(self, create_pv_roofs):
        self.create_pv_roofs = create_pv_roofs

    def set_create_pv_shades(self, create_pv_shades):
        self.create_pv_shades = create_pv_shades
        
    def set_pv_frac_srf(self, pv_frac_srf):
        self.pv_frac_srf = pv_frac_srf
    
    def set_pv_efficiency(self, pv_efficiency):
        self.pv_efficiency = pv_efficiency
    
    def set_return_air_fracs(self, return_air_fracs):
        self.return_air_fracs = return_air_fracs
        
    def set_controller_num_steps(self, controller_num_steps):
        self.controller_num_steps = controller_num_steps
        
    def set_controller_setpoints(self, controller_setpoints):
        self.controller_setpoints = controller_setpoints
        
    def set_controller_glare_azimuth(self, controller_glare_azimuth):
        self.controller_glare_azimuth = controller_glare_azimuth
        
    def set_controller_glare_index(self, controller_glare_index):
        self.controller_glare_index = controller_glare_index
    
    def set_output_control_table_style(self, column_sep, unit_conversion):
        self.output_control_table_style = (column_sep, unit_conversion)
        
    def add_output_surfaces_drawing(self, drawing_type):
        self.output_surfaces_drawings.append(drawing_type)
        
    def add_output_table_summary_report(self, report_type):
        self.output_table_summary_reports.append(report_type)

    def execute_idf(self, base_file_path, weather_file_path, data_folder_path):
        
        #check the number days the simulation will run for
        run_period_days = []
        for period in self.runperiods:
            s_mth = int(period.s_mth)
            s_day = int(period.s_day)
            e_mth = int(period.e_mth)
            e_day = int(period.e_day)
            start = datetime.date(2010, s_mth, s_day)
            end =  datetime.date(2010, e_mth, e_day)
            diff = end - start
            run_period_days.append(diff.days + 1)
        self.simdays = sum(run_period_days)
        
        #CREATE LISTS OF SRFS AND SUBS
        total_srfs= []
        total_subs = []
        for zone in self.zones:
            for srf in zone.surfaces:
                total_srfs.append(srf)
                for subsrf in srf.subsurfaces:
                    total_subs.append(subsrf)
            
        #GET ALL THE DATA FROM THE OBJECTS AND APPEND IT INTO THE TEXT FILE 
        building_data = ""

        if self.version:
            building_data = building_data + idf_writer.write_version(self.version)
        if self.time_step:
            building_data = building_data + idf_writer.write_time_step(self.time_step)
        if self.shadow_calc:
            calc_frequency = self.shadow_calc[0]
            max_figures = self.shadow_calc[1]
            building_data = building_data + idf_writer.write_shadow_calc(calc_frequency, max_figures)
        if self.terrain and self.solar_dist and self.max_warmup_days:
            building_data = building_data + idf_writer.write_building(self.terrain,self.solar_dist,self.max_warmup_days)
        if self.ground_temp:
            building_data = building_data + idf_writer.write_ground_temp_bldg_srf(self.ground_temp)
        
        building_data = building_data + idf_writer.write_schedule_type_limits("Fraction", "0", "1", "CONTINUOUS", "DIMENSIONLESS")
        building_data = building_data + idf_writer.write_schedule_type_limits("Temperature", "-60", "200", "CONTINUOUS", "TEMPERATURE")
        building_data = building_data + idf_writer.write_schedule_type_limits("Any Number", "", "", "", "")
        
        for period in self.runperiods:
            building_data = building_data + period.idf()
        for outputvar in self.outputvars:
            building_data = building_data + outputvar.idf()
        for outputmeter in self.outputmeter:
            building_data = building_data + outputmeter.idf()
        for buildingshade in self.buildingshades:
            building_data = building_data + buildingshade.idf()
        for zone in self.zones:
            building_data = building_data + zone.write_idf()
        for srf in total_srfs:
            building_data = building_data + srf.idf()
        for subsrfs in total_subs:
            building_data = building_data + subsrfs.idf()
        for daylight_control in self.daylight_controls:
            building_data = building_data + daylight_control.idf()
        
        if self.create_pv_walls or self.create_pv_roofs or self.create_pv_shades:
            building_data = building_data + idf_writer.write_schedule_type_limits("Simple_Sch_Limits", "0.0", "1.0", "CONTINUOUS", "")
            building_data = building_data + idf_writer.write_constant_schedule("Always_On_Sch", "Simple_Sch_Limits", "1.0")
            building_data = building_data + idf_writer.write_electric_load_centre_distribution(
                "Simple_Load_Centre", "Simple_Generator", "Baseload", "0", "", "", "DirectCurrentWithInverter","Simple_Inverter", "", "")
            building_data = building_data + idf_writer.write_electric_load_centre_inverter_simple("Simple_Inverter", "Always_On_Sch", "", "0", "1")
            building_data = building_data + idf_writer.write_photovoltaic_performance_simple("Simple_Performance", self.pv_frac_srf, "Fixed", self.pv_efficiency, "")
            generators_data = []
            for srf in total_srfs:
                if self.create_pv_walls and srf.type == "WALL" and srf.sun_exp == "SunExposed": 
                    building_data = building_data + idf_writer.write_generator_photovoltaic(
                        "PV_"+srf.name, srf.name, "PhotovoltaicPerformance:Simple", "Simple_Performance", "Decoupled", "1", "1")
                    generators_data.append(["PV_"+srf.name, "Generator:Photovoltaic", "20000", "Always_On_Sch", ""])
                if self.create_pv_roofs and srf.type == "ROOF" and srf.sun_exp == "SunExposed": 
                    building_data = building_data + idf_writer.write_generator_photovoltaic(
                        "PV_"+srf.name, srf.name, "PhotovoltaicPerformance:Simple", "Simple_Performance", "Decoupled", "1", "1")
                    generators_data.append(["PV_"+srf.name, "Generator:Photovoltaic", "20000", "Always_On_Sch", ""])
            for srf in total_subs:
                if self.create_pv_shades and isinstance(srf, IdfShade): 
                    building_data = building_data + idf_writer.write_generator_photovoltaic(
                        "PV_"+srf.name, srf.name, "PhotovoltaicPerformance:Simple", "Simple_Performance", "Decoupled", "1", "1")
                    generators_data.append(["PV_"+srf.name, "Generator:Photovoltaic", "20000", "Always_On_Sch", ""])
            building_data = building_data + idf_writer.write_electrical_load_centre_generators("Simple_Generator", generators_data)
        
        if self.output_control_table_style:
            column_sep = self.output_control_table_style[0]
            unit_conversion = self.output_control_table_style[1]
            building_data = building_data + idf_writer.write_output_control_table_style(column_sep, unit_conversion)
        for drawing_type in self.output_surfaces_drawings:
            building_data = building_data + idf_writer.write_output_surfaces_drawing(drawing_type)
        if self.output_table_summary_reports:
            building_data = building_data + idf_writer.write_output_table_summary_reports(self.output_table_summary_reports)
        
        #CREATE THE TEXT FILE 
        if not os.path.isdir(data_folder_path):
            os.mkdir(data_folder_path)
        idf_file_path_no_ext = os.path.join(data_folder_path, "in")
        idf_file_path = idf_file_path_no_ext + ".idf"
        
        #read all the stuff in the base idf file 
        base_file = open(base_file_path,  "r")
        base_stuff = base_file.read()
        base_file.close()
        
        #create the new idf file and write to it
        idf_file = open(idf_file_path,  "w")
        idf_file.write(base_stuff)
        for _ in range(10):
            idf_file.write("! ======================================== \n")
        idf_file.write(building_data)
        idf_file.close()
        
        #EXECUTE ENERGYPLUS 
        result_file_path_no_ext = os.path.join(data_folder_path, "output")
        result_file_path = result_file_path_no_ext + ".csv"
        self.result_file_path = result_file_path
        
        operating_sys = os.name
        if operating_sys == "posix":
            command = "runenergyplus " +  idf_file_path_no_ext + " " + weather_file_path +  " > ep_out.txt"
            os.system(command)
            f = open("ep_out.txt", "r")
            print f.read()
            f.close()

        elif operating_sys == "nt":

            #fix path problem
            ep_path = os.path.normpath(EP_PATH)
            idf_file_path_no_ext = os.path.normpath(idf_file_path_no_ext)
            result_file_path_no_ext = os.path.normpath(result_file_path_no_ext)
            weather_file_path = os.path.normpath(weather_file_path)
            
            #generate bat files
            ep_temp_path = os.path.join(data_folder_path, "ep_temp")
            ep_temp_path = os.path.normpath(ep_temp_path)
            if not os.path.isdir(ep_temp_path):
                os.mkdir(ep_temp_path)
            
            bat_file_1_path = os.path.join(ep_temp_path, "Epl-run.bat")
            bat_file_1 = open(bat_file_1_path, "w")
            bat_file_1.write(EPL_RUN_BAT_TEMPLATE)
            bat_file_1.close()
            
            bat_file_2_path = os.path.join(data_folder_path, "run_ep.bat")
            bat_2_file = open(bat_file_2_path, "w")
            bat_2_file.write(data_folder_path[0:2] + "\n")
            bat_2_file.write("cd " + ep_temp_path + "\n")
            bat_2_file.write("SET epPath=" + ep_path + "\\\n")
            bat_2_file.write('Epl-run.bat "' + idf_file_path_no_ext + '" ' + ' "' + result_file_path_no_ext + '" ' + 'idf' +\
                     ' "' + weather_file_path + '" ' + 'EP N nolimit N N \n')
            bat_2_file.close()
            os.system(bat_file_2_path)
        
    def read_results_file(self):
        if self.result_file_path == None:#TODO: check file exists
            raise Exception
        
        #read the csv file 
        f = open(self.result_file_path, "r")
        reader = csv.reader(f, delimiter=",", quotechar='"')
        
        #append the csv file into a row list 
        content_rows = []
        for row in reader:
            s_row = []
            for r in row:
                s_row.append(r.strip())
            content_rows.append(s_row)
        f.close
        
        #from the row list append it to become the column list 
        content_cols = []
        cols = len(content_rows[0])
        rows = len(content_rows)
        for col in range(cols):
            col_data = []
            for row in range(rows):
                try:
                    col_data.append(content_rows[row][col])
                except:
                    col_data.append(None)
            content_cols.append(col_data)
        
        self.content = content_cols
            
    def get_results(self, result_category, display):
        if self.content == None:
            raise Exception
        content = self.content
        #======================================================================
        #==BUILINGS============================================================
        #======================================================================
        #BUILDING TOTAL ENERGY 
        if result_category == "b_total_energy":
            counter = 0
            res_list = []
            l_energy_list = []
            e_energy_list = []
            for c in content:
                if counter != 0:
                    if c[0] == "Cooling:EnergyTransfer [J](Hourly)":
                        c_energy = c[1:]
                    elif c[0] == "Heating:EnergyTransfer [J](Hourly)":
                        h_energy = c[1:]
                    elif c[0].split(":")[1] == "Zone Lights Electric Consumption [J](Hourly)":
                        l_energy_list.extend(c[1:])
                    elif c[0].split(":")[1] == "Zone Electric Equipment Electric Consumption [J](Hourly)":
                        e_energy_list.extend(c[1:])
                counter =+1
                    
            c_energy = sum(map(float,c_energy))
            h_energy = sum(map(float,h_energy))
            l_energy_list = sum(map(float,l_energy_list))
            e_energy_list = sum(map(float,e_energy_list))
            t_energy = c_energy + h_energy + l_energy_list + e_energy_list
            
            if display == "daily":
                total = t_energy / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh

            else:
                total = t_energy * 2.777777777777787E-07 # convert from J to KWh
                
            res_list.append(total)
            return res_list
            
        #======================================================================
        #BUILDING COOLING AND HEATING
        if result_category == "b_cooling_heating":
            res_list = []
            for c in content:
                if c[0] == "Cooling:EnergyTransfer [J](Hourly)":
                    c_energy = c[1:]
                elif c[0] == "Heating:EnergyTransfer [J](Hourly)":
                    h_energy = c[1:]
                    
            c_energy = sum(map(float,c_energy))
            h_energy = sum(map(float,h_energy))
            t_energy = c_energy + h_energy
            
            if display == "daily":
                total = t_energy / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh

            else:
                total = t_energy * 2.777777777777787E-07 # convert from J to KWh
                
            res_list.append(total)
            return res_list
        #======================================================================
        #BUIDLING COOLING
        if result_category == "b_cooling":
            res_list = []
            for c in content:
                if c[0] == "Cooling:EnergyTransfer [J](Hourly)":
                    c_energy = c[1:]
                    
            c_energy = sum(map(float,c_energy))
            
            if display == "daily":
                total = c_energy / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh

            else:
                total = c_energy * 2.777777777777787E-07 # convert from J to KWh
                
            res_list.append(total)
            return res_list
        #======================================================================
        #BUILDING HEATING 
        if result_category == "b_heating":
            res_list = []
            for c in content:
                if c[0] == "Heating:EnergyTransfer [J](Hourly)":
                    h_energy = c[1:]
                    
            h_energy = sum(map(float,h_energy))
            
            if display == "daily":
                total = h_energy / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh

            else:
                total = h_energy * 2.777777777777787E-07 # convert from J to KWh
                
            res_list.append(total)
            return res_list
        #======================================================================
        #BUILDING LIGHTING 
        if result_category == "b_lighting":
            counter = 0
            res_list = []
            energy_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Lights Electric Consumption [J](Hourly)":
                        energy_list.extend(c[1:])
                counter =+1
            total = sum(map(float, energy_list))
            if display == "daily":
                total = total / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh
            else:
                total = total * 2.777777777777787E-07 # convert from J to KWh
            res_list.append(total)
            return res_list
        #======================================================================
        #BUILDING EQUIPMENT 
        if result_category == "b_equipment":
            counter = 0
            res_list = []
            energy_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Electric Equipment Electric Consumption [J](Hourly)":
                        energy_list.extend(c[1:])
                counter =+1
            total = sum(map(float, energy_list))
            if display == "daily":
                total = total / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh
            else:
                total = total * 2.777777777777787E-07 # convert from J to KWh
            res_list.append(total)
            return res_list
        #======================================================================
        #BUILDING PV 
        if result_category == "b_pv":
            counter = 0
            res_list = []
            energy_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "PV Generator DC Energy [J](Hourly)":
                        energy_list.extend(c[1:])
                counter =+1
            total = sum(map(float, energy_list))
            if display == "daily":
                total = total / self.simdays
                total = total * 2.77777777777778E-07 # convert from J to KWh
            else:
                total = total * 2.777777777777787E-07 # convert from J to KWh
            res_list.append(total)
            return res_list
        #======================================================================
        #BUILDING AIR TEMPERATURE
        if result_category == "b_air_temp":
            counter = 0
            values_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Mean Air Temperature [C](Hourly)":
                        values_list.extend(map(float,c[1:]))
                counter =+1
            n = len(values_list)
            mean = sum(values_list) / n
            stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),values_list))/n)
            if n%2 == 1:
                median = values_list[(n-1)/2]
            else:
                median = (values_list[(n/2)-1] + values_list[n/2])/2
            return [mean, stdev, median]
        #======================================================================
        #BUILDING RADIANT TEMPERATURE
        if result_category == "b_radiant_temp":
            counter = 0
            values_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Mean Radiant Temperature [C](Hourly)":
                        values_list.extend(map(float,c[1:]))
                counter =+1
            n = len(values_list)
            mean = sum(values_list) / n
            stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),values_list))/n)
            if n%2 == 1:
                median = values_list[(n-1)/2]
            else:
                median = (values_list[(n/2)-1] + values_list[n/2])/2
            return [mean, stdev, median]
        #======================================================================
        #BUILDING PMV
        if result_category == "b_pmv":
            counter = 0
            values_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "FangerPMV(Hourly)":
                        values_list.extend(map(float,c[1:]))
                counter =+1
            n = len(values_list)
            mean = sum(values_list) / n
            stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),values_list))/n)
            if n%2 == 1:
                median = values_list[(n-1)/2]
            else:
                median = (values_list[(n/2)-1] + values_list[n/2])/2
            return [mean, stdev, median]
        #======================================================================
        #BUILDING PPD
        if result_category == "b_ppd":
            counter = 0
            values_list = []
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "FangerPPD(Hourly)":
                        values_list.extend(map(float,c[1:]))
                counter =+1
            n = len(values_list)
            mean = sum(values_list) / n
            stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),values_list))/n)
            if n%2 == 1:
                median = values_list[(n-1)/2]
            else:
                median = (values_list[(n/2)-1] + values_list[n/2])/2
            return [mean, stdev, median]
        #======================================================================
        #==ZONES===============================================================
        #======================================================================
        #ZONE TOTAL ENERGY
        if result_category == "z_total_energy":
            counter = 0
            res_list = {}
            for c in content:
                if counter != 0:
                    if c[0].split(":")[1] == "Zone/Sys Sensible Cooling Energy [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if zone_name in res_list.keys():
                            res_list[zone_name].extend(c[1:])
                        else:
                            res_list[zone_name] = c[1:]
                    elif c[0].split(":")[1] == "Zone/Sys Sensible Heating Energy [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if zone_name in res_list.keys():
                            res_list[zone_name].extend(c[1:])
                        else:
                            res_list[zone_name] = c[1:]
                    elif c[0].split(":")[1] == "Zone Lights Electric Consumption [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if zone_name in res_list.keys():
                            res_list[zone_name].extend(c[1:])
                        else:
                            res_list[zone_name] = c[1:]
                    elif c[0].split(":")[1] == "Zone Electric Equipment Electric Consumption [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if zone_name in res_list.keys():
                            res_list[zone_name].extend(c[1:])
                        else:
                            res_list[zone_name] = c[1:]
                counter =+1
            for key in res_list.keys():
                total = sum(map(float,res_list[key]))
                if display == "daily":
                    total = total / self.simdays
                    total = total * 2.77777777777778E-07 # convert from J to KWh
                else:
                    total = total * 2.777777777777787E-07 # convert from J to KWh
                res_list[key] = total
            return res_list
        #======================================================================
        #ZONE COOLING AND HEATING
        if result_category == "z_cooling_heating":
            counter = 0
            res_list = {}
            for c in content:
                if counter != 0:
                    if c[0].split(":")[1] == "Zone/Sys Sensible Cooling Energy [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if zone_name in res_list.keys():
                            res_list[zone_name].extend(c[1:])
                        else:
                            res_list[zone_name] = c[1:]
                    elif c[0].split(":")[1] == "Zone/Sys Sensible Heating Energy [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if zone_name in res_list.keys():
                            res_list[zone_name].extend(c[1:])
                        else:
                            res_list[zone_name] = c[1:]
                counter =+1
            for key in res_list.keys():
                total = sum(map(float,res_list[key]))
                if display == "daily":
                    total = total / self.simdays
                    total = total * 2.77777777777778E-07 # convert from J to KWh
                else:
                    total = total * 2.777777777777787E-07 # convert from J to KWh
                res_list[key] = total
            return res_list
        #======================================================================
        #ZONE COOLING 
        if result_category == "z_cooling":
            counter = 0
            res_list = {}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone/Sys Sensible Cooling Energy [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        else:
                            value = sum(map(float,c[1:]))
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        res_list[zone_name] = value
            
                counter =+1
            return res_list
        #======================================================================
        #ZONE HEATING
        if result_category == "z_heating":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone/Sys Sensible Heating Energy [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        else:
                            value = sum(map(float,c[1:]))
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        res_list[zone_name] = value
                        
                counter =+1
            return res_list
        #======================================================================
        #ZONE EQUIPMENT
        if result_category == "z_equipment":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Electric Equipment Electric Consumption [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        else:
                            value = sum(map(float,c[1:]))
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        res_list[zone_name] = value
                        
                counter =+1
            return res_list
        #======================================================================
        #ZONE LIGHTING
        if result_category == "z_lighting":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Lights Electric Consumption [J](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        else:
                            value = sum(map(float,c[1:]))
                            value = value*2.77777777777778E-07 # convert from J to KWh
                        res_list[zone_name] = value
                        
                counter =+1
            return res_list
        #======================================================================
        #ZONE AIR TEMPERATURE
        if result_category == "z_air_temp":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Mean Air Temperature [C](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        results_list = map(float,c[1:])
                        n = len(c[1:])
                        mean = sum(results_list) / n
                        stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),results_list))/n)
                        if n%2 == 1:
                            median = results_list[(n-1)/2]
                        else:
                            median = (results_list[(n/2)-1] + results_list[n/2])/2
                        value = [mean, stdev, median]
                        res_list[zone_name] = value
                counter =+1
            return res_list
        #======================================================================
        #ZONE RADIANT TEMPERATURE
        if result_category == "z_radiant_temp":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Zone Mean Radiant Temperature [C](Hourly)":
                        zone_name  = string.lower(c[0].split(":")[0])
                        results_list = map(float,c[1:])
                        n = len(c[1:])
                        mean = sum(results_list) / n
                        stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),results_list))/n)
                        if n%2 == 1:
                            median = results_list[(n-1)/2]
                        else:
                            median = (results_list[(n/2)-1] + results_list[n/2])/2
                        value = [mean, stdev, median]
                        res_list[zone_name] = value
                counter =+1
            return res_list
        #======================================================================
        #ZONE PMV
        if result_category == "z_pmv":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "FangerPMV(Hourly)":
                        # We assume that the name ends in "_PEOPLE_BY_AREA".
                        # So 15 characters need to be chopped to get the zone name.
                        zone_name  = string.lower(c[0].split(":")[0][:-15])
                        results_list = map(float,c[1:])
                        n = len(c[1:])
                        mean = sum(results_list) / n
                        stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),results_list))/n)
                        if n%2 == 1:
                            median = results_list[(n-1)/2]
                        else:
                            median = (results_list[(n/2)-1] + results_list[n/2])/2
                        value = [mean, stdev, median]
                        res_list[zone_name] = value
                        
                counter =+1
            return res_list
        #======================================================================
        #ZONE PPD
        if result_category == "z_ppd":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "FangerPPD(Hourly)":
                        # We assume that the name ends in "_PEOPLE_BY_AREA".
                        # So 15 characters need to be chopped to get the zone name.
                        zone_name  = string.lower(c[0].split(":")[0][:-15])
                        results_list = map(float,c[1:])
                        n = len(c[1:])
                        mean = sum(results_list) / n
                        stdev = math.sqrt(sum(map(lambda i: pow(i - mean,2),results_list))/n)
                        if n%2 == 1:
                            median = results_list[(n-1)/2]
                        else:
                            median = (results_list[(n/2)-1] + results_list[n/2])/2
                        value = [mean, stdev, median]
                        res_list[zone_name] = value
                        
                counter =+1
            return res_list
        #======================================================================
        #==SURFACES============================================================
        #======================================================================
        #FOR SRF EXT CATEGORY 
        if result_category == "sol_incident":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Solar Incident[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                        else:
                            value = sum(map(float,c[1:]))
                        res_list[srf_name] = value
            
                counter =+1
            return res_list
        #======================================================================
        if result_category == "sol_beam":
            counter = 0
            res_list ={}
            res_list["att_name"] ="Surface_Ext_Solar_Beam_Incident"
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Solar Beam Incident[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                        else:
                            value = sum(map(float,c[1:]))
                            
                        res_list[srf_name] = value
            
                counter =+1
            return res_list
        #======================================================================
        if result_category == "sol_sky_diff":
            counter = 0
            res_list ={}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Solar Sky Diffuse Incident[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                        else:
                            value = sum(map(float,c[1:]))
                        res_list[srf_name] = value
            
                counter =+1
            return res_list
        #======================================================================
        if result_category == "sol_refl_obs":
            
            counter = 0
            res_list1 =[]
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Solar Ground Diffuse Incident[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        att_name = c[0].split(":")[1].replace("(RunPeriod)", "")
                        value = sum(map(float,c[1:]))
                        result = {"srf_name":srf_name, "att_name":att_name, "value":value}
                        res_list1.append(result)
            
                counter =+1
                
            counter = 0
            res_list2 =[]
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Solar From Sky Diffuse Refl From Obstructions[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        att_name = c[0].split(":")[1].replace("(RunPeriod)", "")
                        value = sum(map(float,c[1:]))
                        result = {"srf_name":srf_name, "att_name":att_name, "value":value}
                        res_list2.append(result)
            
                counter =+1
                
            counter = 0
            res_list3 =[]
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Beam Sol From Bm-To-Bm Refl From Obstructions[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        att_name = c[0].split(":")[1].replace("(RunPeriod)", "")
                        value = sum(map(float,c[1:]))
                        result = {"srf_name":srf_name, "att_name":att_name, "value":value}
                        res_list3.append(result)
            
                counter =+1
                
            counter = 0
            res_list4 =[]
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "Surface Ext Diff Sol From Bm-To-Diff Refl From Obstructions[W/m2](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])
                        att_name = c[0].split(":")[1].replace("(RunPeriod)", "")
                        value = sum(map(float,c[1:]))
                        result = {"srf_name":srf_name, "att_name":att_name, "value":value}
                        res_list4.append(result)
            
                counter =+1
                
            num_srf = len(res_list1)
            res_list = {}
            res_list["att_name"] ="Surface_Ext_Solar_Reflected_From_Obstruction"
            for cnt in range(num_srf):
                srf_name = res_list1[cnt]["srf_name"]
                value1 = res_list1[cnt]["value"]
                value2 = res_list2[cnt]["value"]
                value3 = res_list3[cnt]["value"]
                value4 = res_list4[cnt]["value"]
                value = value1 + value2 + value3 + value4 
                if display == "daily":
                    value = value/self.simdays
                res_list[srf_name] = value
                
            return res_list
        #======================================================================
        #FOR PV SURFACE LEVEL 
        if result_category == "s_pv":
            counter = 0
            res_list = {}
            for c in content:
                if counter !=0:
                    if c[0].split(":")[1] == "PV Generator DC Energy [J](Hourly)":
                        srf_name  = string.lower(c[0].split(":")[0])[3:]
                        if display == "daily":
                            value = sum(map(float,c[1:]))/self.simdays
                        else:
                            value = sum(map(float,c[1:]))
                        if display == "daily":
                            value = value / self.simdays
                            value = value * 2.77777777777778E-07 # convert from J to KWh

                        else:
                            value = value * 2.777777777777787E-07 # convert from J to KWh
                        res_list[srf_name] = value
                        
                counter =+1
            return res_list
        #======================================================================
        #======================================================================
        #======================================================================
class RunPeriod(object):
    def __init__(self, start_month, start_day, end_month, end_day, idf):
        self.s_mth = start_month
        self.s_day = start_day
        self.e_mth = end_month
        self.e_day = end_day
        idf.runperiods.append(self)
        
    def idf(self):
        runperiod = idf_writer.write_runperiod(self.s_mth, self.s_day, 
                                                      self.e_mth, self.e_day)
        return runperiod
    
class OutputMeter(object):
    def __init__(self, variable_name, report_frequency, idf):
        self.variable = variable_name
        self.frequency = report_frequency
        idf.outputmeter.append(self)
        
    def idf(self):
        output_meter = idf_writer.write_outputmeter(self.variable, self.frequency)
        
        return output_meter
    
class OutputVariables(object):
    def __init__(self, variable_name, report_frequency, idf):
        self.variable = variable_name
        self.frequency = report_frequency
        idf.outputvars.append(self)
        
    def idf(self):
        output_var = idf_writer.write_outputvar(self.variable, self.frequency)
        
        return output_var
    
class IdfZone(object):
    def __init__(self, name, model):
        self.name = name
        self.surfaces = []
        #cooling
        self.cstart = None
        self.cend = None
        self.ctemp = None
        #heating
        self.hstart = None
        self.hend = None
        self.htemp = None
        #infiltration
        self.ai_start = None
        self.ai_end = None
        self.ai_ach = None
        #lighting
        self.l_start = None
        self.l_end = None 
        self.l_watts = None
        #internal gains
        self.ig_start = None
        self.ig_end = None 
        self.ig_watts = None
        #people by area
        self.pp_start = None
        self.pp_end = None 
        self.pp_area_per_person = None
        self.pp_activity_level = None
        self.pp_work_efficiency = None
        self.pp_clothing_insulation = None
        self.pp_air_velocity = None
        #electric equipment
        self.ee_start = None
        self.ee_end = None 
        self.ee_watts = None
        #controllers
        self.controller_point_1 = None
        self.controller_point_2 = None
        #lights
        self.l_start = None
        self.l_end = None 
        self.l_watts = None
        #add this zone to the list
        self.model = model
        model.zones.append(self)
        
    def add_surface(self,  surface):
        surface.zone = self.name
        self.surfaces.append(surface)
        
    def set_cool_schedule(self, start, end, temp):
        self.cstart = start
        self.cend = end
        self.ctemp = temp
        
    def set_heat_schedule(self, start, end, temp):
        self.hstart = start
        self.hend = end
        self.htemp = temp
        
    def set_infiltration_schedule(self, start, end, ach):
        self.ai_start = start
        self.ai_end = end
        self.ai_ach = ach
        
    def set_internal_gains_schedule(self, start, end, watts):
        self.ig_start = start
        self.ig_end = end 
        self.ig_watts = watts
        
    def set_people_schedule(self, start, end, area_per_person, activity_level, work_efficiency, clothing_insulation, air_velocity):
        self.pp_start = start
        self.pp_end = end 
        self.pp_area_per_person = area_per_person
        self.pp_activity_level = activity_level
        self.pp_work_efficiency = work_efficiency
        self.pp_clothing_insulation = clothing_insulation
        self.pp_air_velocity = air_velocity
        
    def set_electric_equipment_schedule(self, start, end, watts):
        self.ee_start = start
        self.ee_end = end 
        self.ee_watts = watts
        
    def set_light_schedule(self, start, end, watts):
        self.l_start = start
        self.l_end = end 
        self.l_watts = watts

    def set_controller_points(self, point_1, point_2):
        self.controller_point_1 = point_1
        self.controller_point_2 = point_2
        
    def write_idf(self):
        name = self.name 
        zone_data = idf_writer.write_zone(name)
        #cooling and heating
        if self.cstart and self.cend and self.ctemp and self.hstart and self.hend and self.htemp:
            c_sch_name = name+"_cool"
            h_sch_name = name+"_heat"
            t_name = name+"_thermo"
            c_sch = idf_writer.write_hvacschedule(c_sch_name, "Temperature", self.cstart, self.cend, self.ctemp, "50.0")
            h_sch = idf_writer.write_hvacschedule(h_sch_name, "Temperature", self.hstart, self.hend, self.htemp, "-50.0")
            thermostat = idf_writer.write_thermostat(t_name, h_sch_name,c_sch_name)
            hvac = idf_writer.write_hvac_ideal_load_air_system(name, t_name)
            zone_data = zone_data + c_sch + h_sch + thermostat + hvac
        #infiltration
        if self.ai_start and self.ai_end and self.ai_ach:
            ai_sch_name = name + "_infiltration"
            ai_sch = idf_writer.write_alldays_schedule(ai_sch_name, "Fraction", self.ai_start, self.ai_end)
            zone_infiltration = idf_writer.write_zone_infiltration(name, ai_sch_name, self.ai_ach)
            zone_data = zone_data + ai_sch + zone_infiltration
        #internal gains
        if self.ig_start and self.ig_end and self.ig_watts:
            ig_sch_name = name + "_internal_gains"
            ig_sch = idf_writer.write_alldays_schedule(ig_sch_name, "Fraction", self.ig_start, self.ig_end)
            internal_gains = idf_writer.write_internal_gains_other_equipment(name, ig_sch_name, self.ig_watts)
            zone_data = zone_data + ig_sch + internal_gains
        #electric equipment
        if self.ee_start and self.ee_end and self.ee_watts:
            ee_sch_name = name + "_electric_equipment"
            ee_sch = idf_writer.write_alldays_schedule(ee_sch_name, "Fraction", self.ee_start, self.ee_end)
            electric_equipment = idf_writer.write_internal_gains_electric_equipment(name, ee_sch_name, self.ee_watts)
            zone_data = zone_data + ee_sch + electric_equipment
        #controls
        if self.controller_point_1:
            if self.controller_point_2:
                num_points = 2
            else:
                num_points = 1
            controllers = idf_writer.write_daylight_control(
                    name,
                    num_points,
                    [self.controller_point_1, self.controller_point_2],
                    ["1", "0"],
                    self.model.controller_setpoints,
                    "2",
                    self.model.controller_glare_azimuth,
                    self.model.controller_glare_index,
                    ["0","0"], 
                    self.model.controller_num_steps,
                    "1")
            #append
            zone_data = zone_data + controllers
        #lighting
        if self.l_start and self.l_end and self.l_watts:
            l_sch_name = name + "_lights"
            l_sch = idf_writer.write_alldays_schedule(l_sch_name, "Fraction", self.l_start,self.l_end)
            lights = idf_writer.write_light(
                    name + "_light",
                    name,
                    l_sch_name,
                    "Watts/Area",
                    "",
                    self.l_watts,
                    "",
                    self.model.return_air_fracs,
                    "General", "No")
            #append
            zone_data = zone_data + l_sch + lights
        #people by area
        if self.pp_start and self.pp_end and self.pp_area_per_person and self.pp_activity_level and self.pp_work_efficiency and self.pp_clothing_insulation and self.pp_air_velocity:
            #schedules
            pp_area_sch_name = name + "_people_area"
            pp_activity_sch_name = name + "_people_activity"
            pp_work_sch_name = name + "_people_work"
            pp_clothing_sch_name = name + "_people_clothing"
            pp_air_sch_name = name + "_people_air"
            pp_area_sch = idf_writer.write_alldays_schedule(pp_area_sch_name, "Fraction", self.pp_start,self.pp_end)
            pp_activity_sch = idf_writer.write_constant_schedule(pp_activity_sch_name, "Any Number", self.pp_activity_level)
            pp_work_sch = idf_writer.write_constant_schedule(pp_work_sch_name, "Any Number", self.pp_work_efficiency)
            pp_clothing_sch = idf_writer.write_constant_schedule(pp_clothing_sch_name, "Any Number", self.pp_clothing_insulation)
            pp_air_sch = idf_writer.write_constant_schedule(pp_air_sch_name, "Any Number", self.pp_air_velocity)
            #people
            pp_people = idf_writer.write_people_by_area(name, self.pp_area_per_person, pp_area_sch_name, pp_activity_sch_name, pp_work_sch_name, pp_clothing_sch_name, pp_air_sch_name)
            #append
            zone_data = zone_data + pp_area_sch + pp_activity_sch + pp_work_sch + pp_clothing_sch + pp_air_sch + pp_people
        
        return zone_data
        
class IdfSurface(object):
    def __init__(self, name, points, construction):
        self.name = name
        self.points = points
        self.construction = construction
        
class IdfZoneSurface(IdfSurface):
    def __init__(self, name, points, construction, type, boundary_srf_name):
        if not type in ("WALL", "FLOOR", "CEILING", "ROOF"):
            return
        super(IdfZoneSurface, self).__init__(name,  points, construction)
        self.zone = None 
        self.type = type
        self.subsurfaces = []
        if boundary_srf_name == "OUTDOORS":
            self.boundary = "OUTDOORS" 
            self.boundary_obj = "" 
            self.sun_exp = "SunExposed" 
            self.win_exp = "WindExposed"
        elif boundary_srf_name == "ADIABATIC":
            self.boundary = "ADIABATIC" 
            self.boundary_obj = name
            self.sun_exp =  "NoSun"
            self.win_exp = "NoWind"
        elif boundary_srf_name == "GROUND":
            self.boundary = "GROUND"
            self.boundary_obj = "" 
            self.sun_exp =  "NoSun"
            self.win_exp = "NoWind"
        else:
            self.boundary = "SURFACE" 
            self.boundary_obj = boundary_srf_name
            self.sun_exp = "NoSun" 
            self.win_exp = "NoWind"
            
    def add_window(self,  window):
        self.subsurfaces.append(window)
        
    def add_shade(self,  shade):
        self.subsurfaces.append(shade)
        
    def idf(self):
        return idf_writer.write_surface(
            self.name, 
            self.type,
            self.construction,
            self.zone, 
            self.boundary,
            self.boundary_obj, 
            self.sun_exp, 
            self.win_exp, 
            self.points)
                                              
class IdfSubSurface(IdfSurface):
    def __init__(self, name, points, construction, host_srf):
        if host_srf == None:
            raise Exception
        super(IdfSubSurface,self).__init__(name, points, construction)
        self.host_srf = host_srf
        self.transmittance = "" 

class IdfWindow(IdfSubSurface):
    def idf(self):
        return idf_writer.write_window(self.name, self.construction, self.host_srf, "", "", self.points)   


class IdfShade(IdfSubSurface):
    def idf(self):
        return idf_writer.write_zone_shade(self.name, self.host_srf, self.transmittance, self.points)

#for shadings that are not attached to the buildings which includes trees and surrounding site
class IdfBuildingShade(object):
    def __init__(self, name, points, idf):
        self.name = name 
        self.points = points
        idf.buildingshades.append(self)
        
    def idf(self):
        return idf_writer.write_building_shade(self.name, "", self.points)

            
