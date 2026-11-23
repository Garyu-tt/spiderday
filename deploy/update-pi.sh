#!/usr/bin/env bash
# Deploy already-reviewed GitHub commits to the Raspberry Pi.
# No firmware flashing, DSP writes, or network exposure.
set -Eeuo pipefail
cd "$HOME/spiderday"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing update: local Spider Day changes exist" >&2
  exit 2
fi
git fetch --ff-only origin main
git merge --ff-only origin/main
python3 -m compileall -q backend.py dev_proxy.py legacy_bridge.py device.py deploy
python3 -m unittest discover -q
if [[ -d "$HOME/mod-ui-spiderday/.git" ]]; then
  cd "$HOME/mod-ui-spiderday"
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Refusing MOD UI update: local changes exist" >&2
    exit 2
  fi
  git fetch origin master
  git merge --ff-only origin/master
fi
systemctl --user restart spiderday-api.service spiderday-proxy.service
systemctl --user is-active --quiet spiderday-api.service
systemctl --user is-active --quiet spiderday-proxy.service
python3 "$HOME/spiderday/deploy/healthcheck.py"
