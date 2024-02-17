tmux attach -t spotify -d
tmux send-keys -t spotify C-c
tmux kill-session -t spotify

