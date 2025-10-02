REM script to run ant and execute the unanet_imu process
set ant_home=bin/ant
bin/ant/bin/ant.bat -Dlog4j2.formatMsgNoLookups="true" -f imu_build.xml import