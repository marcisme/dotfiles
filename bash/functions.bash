function t() {
  if [ $# -lt 1 ] || ! [[ "$1" =~ ^[[:digit:]]$ ]]; then
    echo "usage: t <num executions> [command]"
    # remove execution from history if it was invalid
    history -d $((HISTCMD-1))
    return 1
  fi

  local n=$1; shift
  local cmd=$*

  # use last command in shell history if none is provided
  if [ -z "$cmd" ]; then
    cmd=$(fc -ln -1)
    # no idea why this needs to be a separate command...
    cmd=$(echo $cmd | sed 's/^ *//g')
  fi

  # reduce to base command if a previous t invocation
  if [[ "$cmd" =~ ^[[:space:]]*t[[:space:]]+[[:digit:]]+ ]]; then
    cmd=$(echo $cmd | sed 's/^\s*t\s\+[0-9]\+\s*//')
  fi

  echo "running '$cmd' $n times"
  for ((i=1; i<=n; i++)); do
    eval $cmd
  done

  # overwrite history with the expanded command
  history -s "t $n $cmd"
}
