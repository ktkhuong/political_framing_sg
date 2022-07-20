
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

python dtm.py -u https://github.com/ktkhuong/political_framing_sg/releases/download/dataset_parliament_v0.0.1/parliament.zip -s "2015-01-01" -e "2019-12-31" -m 24
rem python dtm.py -s "2015-01-01" -e "2019-12-31" -m 5