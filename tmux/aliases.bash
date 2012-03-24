alias tml="tmux list-sessions"
alias tma="tmux attach-session"
alias tmk="tmux kill-session"
alias tm="tmux new-session \; \
  split-window -v -l 24 \; split-window -h -l 84 \; select-pane -t 1 \; split-window -h -l 84 \; \
  select-pane -t 0 \; \
  split-window -v -l 24 \; split-window -h -l 84 \; select-pane -t 1 \; split-window -h -l 84 \; \
  select-pane -t 0 \;"
