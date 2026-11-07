@echo off
rem kabayan.cmd - alias dari kp.cmd (perintah global, sama persis).
call "%~dp0kp.cmd" %*
exit /b %errorlevel%
