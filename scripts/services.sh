out=$(sudo docker service ls | tail -n +2)
output=""
while IFS= read -r line; do
	first=$(echo "$line" | cut -d " " -f1)
	output+=$(sudo docker service ps --format "{{.CurrentState}}\t{{.DesiredState}}\t{{.Name}}\t{{.Node}}" $first)
	output+=$'\n'
done <<< "$out"
echo "$output" | sort -Vk 7 | column -t