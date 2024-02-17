tmux detach
tmux new-session -t spotify-1 -d
tmux send-keys -t spotify-1 "ncspot" ENTER
tmux send-keys -t spotify-1 ENTER
