function t() {
  if [ $# -lt 1 ]; then
    echo "usage: t <num executions> [command]"
    return 1
  fi

  n=$1; shift
  cmd=$*

  # use last command in shell history if none is provided
  if [ -z "$cmd" ]; then
    cmd=$(history 2 | head -1 | sed 's/\s*[0-9]\+\s*//')
  fi

  echo "running '$cmd' $n times"
  for ((i=1; i<=n; i++)); do
    eval $cmd
  done
}
