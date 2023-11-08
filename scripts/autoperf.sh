tmux new-session -d -s autoperf
tmux send-keys -t autoperf: "sudo /dev/shm/perf report --call-graph=folded,0.00000001 --no-children -i /users/edwinlim/perfdata/branches_branch-misses_perf.data" Enter
sleep 3

tmux send-keys -t autoperf: Enter
tmux send-keys -t autoperf: "E"
tmux send-keys -t autoperf: "P"
tmux send-keys -t autoperf: Tab
tmux send-keys -t autoperf: "E"
tmux send-keys -t autoperf: "P"
tmux send-keys -t autoperf: Tab
tmux send-keys -t autoperf: "E"
tmux send-keys -t autoperf: "P"
tmux send-keys -t autoperf: Tab
tmux send-keys -t autoperf: "E"
tmux send-keys -t autoperf: "P"

tmux send-keys -t autoperf: "q"
tmux kill-session -t autoperf
