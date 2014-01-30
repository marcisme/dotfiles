alias g="git"
alias gs="g status"
alias ga="g add"
alias grm="g rm"
alias gc="g commit"
alias gca="gc --amend"
alias gcA="gc --amend -C HEAD"
alias gl="g log"
alias glo="gl --oneline"
alias glg="gl --graph"
alias gln="glo --name-status"
alias gb="g branch"
alias gt="g tag"
alias gco="git checkout"
alias gd="g diff"
alias gdc="gd --cached"
alias gf="g fetch"
alias gpr="g pull --rebase"
alias gtfo="g reset --hard && g clean -fd"

# make completion work for g
# http://askubuntu.com/questions/62095/how-to-alias-git-to-g-so-that-bash-completion-rules-are-preserved
complete -o bashdefault -o default -o nospace -F _git g 2>/dev/null \
    || complete -o default -o nospace -F _git g
