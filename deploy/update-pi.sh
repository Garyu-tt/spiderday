#!/usr/bin/env bash
# Deploy already-reviewed GitHub commits to the Raspberry Pi.
# No firmware flashing, DSP writes, or network exposure.
set -Eeuo pipefail
cd "$HOME/spiderday"
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Refusing update: local Spider Day changes exist" >&2
  exit 2
fi
git fetch origin main
git merge --ff-only origin/main
python3 -m compileall -q backend.py dev_proxy.py legacy_bridge.py device.py deploy
python3 -m unittest discover -q
if [[ -d "$HOME/mod-ui-spiderday/.git" ]]; then
  cd "$HOME/mod-ui-spiderday"
  if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    echo "Refusing MOD UI update: local changes exist" >&2
    exit 2
  fi
  git fetch origin master
  git merge --ff-only origin/master
else
  echo "MOD UI checkout missing: $HOME/mod-ui-spiderday" >&2
  exit 2
fi
systemctl --user restart spiderday-api.service spiderday-proxy.service
systemctl --user is-active --quiet spiderday-api.service
systemctl --user is-active --quiet spiderday-proxy.service
ready=0
for attempt in 1 2 3 4 5 6 7 8 9 10; do
  if python3 "$HOME/spiderday/deploy/healthcheck.py"; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" != 1 ]]; then
  echo "Spider Day healthcheck failed after 10 attempts" >&2
  exit 1
fi
