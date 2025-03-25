#!/bin/bash

if [ $# -lt 1 ]
then
	echo "usage: ${0##*/} <course name>"
	exit 1
fi

COURSE_NAME=$1
CHROMEDRIVER_PATH=/home1/irteam/.wdm/drivers/chromedriver/linux64/134.0.6998.165/chromedriver-linux64/chromedriver
LOG_FILE=log_${COURSE_NAME}.txt

cnt=1

while :
do
	execute_date=$(date +"%Y%m%d %H:%M:%S")
	if [[ `expr $cnt % 10` -eq 0 ]]; then
		echo "[$execute_date] $cnt 회" >> ${LOG_FILE}
	fi

	python3 main.py --headless True --course-name ${COURSE_NAME} --chromedriver-path ${CHROMEDRIVER_PATH}
	exitcode=$?
	if [[ $exitcode == 0 ]]; then
		# exitcode가 0이면 신청 성공한 것이므로 종료.
		echo "[$execute_date] success" >> ${LOG_FILE}
		break
	fi

	cnt=$(expr $cnt + 1)
done