@echo off
REM TYF helper launcher (Windows).
REM Add this bin\ directory to PATH so %~dp0 resolves to the repo. If you copy
REM this file elsewhere instead, set TYF_PACK_ROOT to the repo so `tyf check`
REM can find skills\ (workspace commands are CWD-relative and need no pack root).
setlocal
where python >nul 2>nul && (set "PY=python") || (set "PY=py")
"%PY%" "%~dp0\..\scripts\tyf.py" %*
