
@echo off

IF EXIST "in" (
    RMDIR /S /Q "in"
)
IF EXIST "out" (
    RMDIR /S /Q "out"
)
IF EXIST "sgparl.db" (
    DEL /Q "sgparl.db"
)

python dtm.py -f sgparl.csv -s "2019-01-01" -e "2019-12-31"