@echo off
REM PRTG EXE/Script sensor (Windows side) — checks a systemd service INSIDE WSL with no
REM SSH (PRTG + WSL on the same machine). Param %1 = service name, e.g. klinecollect.service.
REM Output "<value>:<message>": 1 = active, 0 = down. PRTG channel: Error if value < 1.
REM GOTCHA: the PRTG service must run as the Windows user that owns the WSL distro,
REM         else wsl.exe can't see it (run PRTG's "Probe Service" as that user).
wsl.exe systemctl is-active %1 >nul 2>&1
if %errorlevel%==0 (echo 1:%1 active) else (echo 0:%1 DOWN)
