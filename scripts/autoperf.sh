tmux new-session -d -s autoperf
#tmux send-keys -t autoperf: "sudo /dev/shm/perf report --call-graph=folded,0.00000001 --no-children -i /users/edwinlim/perfdata/branches_branch-misses_perf.data" Enter
tmux send-keys -t autoperf: "sudo /dev/shm/perf report -f --call-graph=folded,0.00000001 --no-children -i ${1}" Enter
sleep 30

tmux send-keys -t autoperf: Enter
sleep 20
tmux send-keys -t autoperf: "E"
sleep 20
tmux send-keys -t autoperf: "P"
sleep 20
tmux send-keys -t autoperf: Tab
sleep 20
tmux send-keys -t autoperf: "E"
sleep 20
tmux send-keys -t autoperf: "P"
sleep 20
tmux send-keys -t autoperf: Tab
sleep 20
tmux send-keys -t autoperf: "E"
sleep 20
tmux send-keys -t autoperf: "P"
sleep 20
tmux send-keys -t autoperf: Tab
sleep 20
tmux send-keys -t autoperf: "E"
sleep 20
tmux send-keys -t autoperf: "P"
sleep 20

tmux send-keys -t autoperf: "q"
sleep 20
tmux kill-session -t autoperf
