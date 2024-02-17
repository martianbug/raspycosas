tmux attach -t spotify-1 -d
tmux send-keys -t spotify-1 C-c
tmux kill-session -t spotify-1

