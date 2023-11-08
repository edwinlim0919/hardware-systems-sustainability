sudo perf record -F 250 -e $1 --call-graph lbr -p $2 sleep 10

#container_ids=()
#
#while read -r line
#do
#	id=${line%% *}
#	container_ids+=("${id}")
#done < <(sudo docker ps | grep $1)
#
#all_ps=""
#for id in ${container_ids[@]}
#do
#	out=$(sudo docker top $id | awk '{print $2}')
#	for each_pid in ${out}; do
#		if [ "$each_pid" != "PID" ]; then
#			all_ps="${each_pid},${all_ps}"
#		fi
#	done
#done
#
#echo "Running perf record for the processes $all_ps"
#
#sudo perf record -e cpu-cycles:ppp --call-graph lbr -p ${all_ps}
