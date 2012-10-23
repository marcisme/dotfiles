if [ "$(uname)" == "Darwin" ]; then
  if [ -f $(brew --prefix)/etc/autojump ]; then
    source $(brew --prefix)/etc/autojump
  fi
fi
