
@echo off

SET URL=https://github.com/ktkhuong/political_framing_sg/releases/download/dataset_parliament_v0.0.1/parliament.zip
SET FROM="1965-01-01"
SET TO="2022-12-31"
SET MACHINES=24
SET KRANGE="15,40"
SET DRANGE="10,30"
SET PARTY="NPAP"

call :clean
python dtm.py -u %URL% --from %FROM% --to %TO% --machines %MACHINES% --krange %KRANGE% --drange "10,30" --party "PAP" --min-count 1 --min-df "1" --max-df "1.0"
call :post_run pap
call :clean
python dtm.py -u %URL% --from %FROM% --to %TO% --machines %MACHINES% --krange %KRANGE% --drange "10,30" --party "NPAP" --min-count 1 --min-df "1" --max-df "1.0"
call :post_run opposition

:clean
IF EXIST "in" (
    RMDIR /S /Q "in"
)
IF EXIST "out" (
    RMDIR /S /Q "out"
)
IF EXIST "sgparl_tokenized.csv" (
    DEL /Q "sgparl_tokenized.csv"
)
IF EXIST "sgparl.db" (
    DEL /Q "sgparl.db"
)
IF EXIST "dtm.log" (
    DEL /Q "dtm.log"
)
IF EXIST "dtm.pkl" (
    DEL /Q "dtm.pkl"
)
EXIT /B 0

:post_run
echo D | xcopy sgparl.db e:\archive\experiments\%~1 /y
xcopy sgparl_tokenized.csv e:\archive\experiments\%~1 /y
xcopy out\w2v.model e:\archive\experiments\%~1 /y
xcopy dtm.pkl e:\archive\experiments\%~1 /y
xcopy dtm.log e:\archive\experiments\%~1 /y
xcopy in\* e:\archive\experiments\%~1 /y
EXIT /B 0