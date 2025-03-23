#!/bin/bash

cnt=1

while :
do
	execute_date=$(date +"%Y%m%d %H:%M:%S")
	if [[ `expr $cnt % 10` -eq 0 ]]; then
		echo "[$execute_date] $cnt 회" >> output.txt
	fi
	
	python3 main.py --headless True
	exitcode=$?
	if [[ $exitcode == 0 ]]; then
		# exitcode가 0이면 신청 성공한 것이므로 종료.
		echo "[$execute_date] success" >> output.txt
		break
	fi

	cnt=$(expr $cnt + 1)
done