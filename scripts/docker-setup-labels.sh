all_nodes=$(sudo docker node ls)

while IFS= read -r line; do
	node_name=$(echo "$line" | awk 'BEGIN {FS=" "}; {print $2}')
 	node_label=$(echo "$node_name" | awk 'BEGIN {FS="."}; {print $1}')
	sudo docker node update --label-add "$node_label"=true "$node_name"
done <<< "$all_nodes"
