#!/usr/bin/env bash
# Lets git reach the private evidence repository (jessepike/sec-market-private)
# over SSH with its write deploy key. The key can touch that one repository only.
# The host key is GitHub's published ed25519 key, so no first-use trust.
set -euo pipefail
: "${SMP_EVIDENCE_DEPLOY_KEY:?EVIDENCE_DEPLOY_KEY_MISSING}"
: "${RUNNER_TEMP:?RUNNER_TEMP_MISSING}"
dir="$RUNNER_TEMP/smp-evidence-ssh"
install -d -m 700 "$dir"
umask 077
printf '%s\n' "$SMP_EVIDENCE_DEPLOY_KEY" > "$dir/key"
printf '%s\n' 'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' > "$dir/known_hosts"
git config --global core.sshCommand \
  "ssh -i $dir/key -o IdentitiesOnly=yes -o UserKnownHostsFile=$dir/known_hosts -o StrictHostKeyChecking=yes"
