if [ -f $(brew --prefix)/etc/bash_completion ]; then
  source $(brew --prefix)/etc/bash_completion
fi

# path for homebrew installed executables
PATH=/usr/local/bin:/usr/local/sbin:$PATH

# brew aliases
alias bru="brew update && brew outdated"
