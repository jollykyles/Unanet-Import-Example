REM script to run ant and execute the unanet_imu export process
set ant_home=bin/ant
bin/ant/bin/ant.bat -Dlog4j2.formatMsgNoLookups="true" -f imu_export_build.xml export