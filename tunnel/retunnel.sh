#!/bin/bash
createTunnel() {
  /usr/bin/ssh -N -R 2400:localhost:22 root@morgen.jetzt
  if [[ $? -eq 0 ]]; then
    echo Tunnel to jumpbox created successfully
  else
    echo An error occurred creating a tunnel to jumpbox. RC was $?
  fi
}

/bin/pidof ssh
echo $?

echo create new tunnel
# kill $?
createTunnel