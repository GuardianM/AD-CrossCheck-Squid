@echo off

::### DC NAME ###
set "DC=WRITE_NAME_HERE"


for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set DateTime=%%a

set Yr=%DateTime:~0,4%
set Mon=%DateTime:~4,2%
set Day=%DateTime:~6,2%
set Hr=%DateTime:~8,2%
set Min=%DateTime:~10,2%
set Sec=%DateTime:~12,2%


for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %ComputerName% ^| findstr [') do set IP=%%a

set "FILENAME=logout.csv"
set nmt=%time:~0,8%
echo %DATE%,%Hr%:%Min%:%Sec%,Logout,%USERNAME%,%IP%,%COMPUTERNAME%  >> \\%DC%\SharedUsersLogs$\%FILENAME%