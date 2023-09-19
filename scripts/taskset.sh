containers=$(sudo docker ps | tail -n +2)
num_lines=$(echo "$containers" | wc -l)

if [ $num_lines -eq 1 ]; then
        echo "Node has only one container, exiting script"
        exit 1
else
        echo "Node has two containers, performing docker cpuset-cpus"
fi

i=0
while IFS= read -r line; do
        container_name=$(echo $line | awk 'BEGIN {FS=" "}; {print $NF}')
        if [ $i -eq 0 ]; then
                sudo docker container update --cpuset-cpus 0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62 "$container_name"
        else
                sudo docker container update --cpuset-cpus 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59,61,63 "$container_name"   
        fi

        i=$(($i + 1))
done <<< "$containers"
