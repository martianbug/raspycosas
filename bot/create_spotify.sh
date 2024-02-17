tmux detach
tmux new-session -t spotify -d
tmux send-keys -t spotify "ncspot" ENTER
tmux send-keys -t spotify ENTER
tmux attach -t bot ENTER

