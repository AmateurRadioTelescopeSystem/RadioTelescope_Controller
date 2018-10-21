:: The script does the necessary configuration for the program

@ECHO OFF

FOR /F "tokens=* USEBACKQ" %%F IN (`CD`) DO (SET conf_dir=%%F)
python -m pip install -r requirements.txt

:: Compile the resources file
ECHO.
ECHO Compiling the resources file....
CHDIR C:\Qt\5.*\min*\bin\
rcc -binary %conf_dir%\Settings\resources.qrc -o %conf_dir%\Core\GUI\resources.rcc || EXIT /b
ECHO File compilation done!
