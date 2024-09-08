#!/bin/bash
IN_DEBUG_MODE="True Not"

DATE=`date '+%Y-%m-%d %H:%M:%S'`
logfile='/home/pi/flickr/_bin/logs/system_health_monitor.log'
commands=( \
'Screen;/opt/vc/bin/tvservice -s | grep 0x12000a > /dev/null && printf on || printf off' \
'ScreenName;/opt/vc/bin/tvservice -n' \
'Temperature;/opt/vc/bin/vcgencmd measure_temp' \
'RAM;cat /proc/meminfo | grep MemFree' \
)

if [ "$IN_DEBUG_MODE" == "True" ]; then
commands+=( \
'Disk_Space;df -h' \
)
else 
commands+=( \
'Disk_Space;df / -h | tail -n 1 | awk "{print $5}" ' \
)
fi

#echo "##########  $DATE ###############################################" >> $logfile
for command in "${commands[@]}"
do
  echo "Command: $command"
  IFS=';' read -ra elements <<< "$command"
  command_result=$(eval ${elements[1]})
  lines="$lines | ${elements[0]}: $command_result"
done
echo "$DATE$lines" >> $logfile
echo Logged to: $logfile

#echo $(/opt/vc/bin/tvservice -s) >> $logfile
#echo $/opt/vc/bin/vcgencmd measure_temp
