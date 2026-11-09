#!/usr/bin/env bash
# Vercel ignoreCommand for Git deployments: exit 0 skips the build, exit 1 builds.
# main and data/archive never build from Git; production is the publisher's
# prebuilt upload (D-110). Other branches build only when the site's inputs,
# web/ or contracts/, changed since the branch's last successful deployment,
# so docs-only and ops-only pushes spend no build minutes.
# Vercel's shallow clone may lack the previous commit; fetch it, else build.
case "$VERCEL_GIT_COMMIT_REF" in main|data/archive) exit 0 ;; esac
prev="$VERCEL_GIT_PREVIOUS_SHA"
[ -n "$prev" ] || exit 1
git cat-file -e "$prev^{commit}" 2>/dev/null || git fetch -q --depth=1 origin "$prev" 2>/dev/null || exit 1
git diff --quiet "$prev" HEAD -- . ../contracts 2>/dev/null && exit 0
exit 1
