@echo off
REM ===========================================================================
REM IntelliTransit: OpenTripPlanner 2 Startup Script for Windows
REM ===========================================================================

set OTP_DIR=%~dp0
set DATA_DIR=%OTP_DIR%data
set CONFIG_DIR=%OTP_DIR%config

echo Starting OpenTripPlanner 2 for Pune Metropolitan Region...
echo OTP Base URL: http://localhost:8080
echo Data Directory: %DATA_DIR%

java -Xmx4G -jar "%OTP_DIR%otp-shaded.jar" --build --serve "%DATA_DIR%"
