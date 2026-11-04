#!/usr/bin/env bash
# Vercel ignoreCommand: exit 0 skips the build, exit 1 builds.
# Build only on main, and only when ops/timer changed since the last deployment.
# Vercel's shallow clone may lack the previous commit; fetch it, else build.
[ "$VERCEL_GIT_COMMIT_REF" = "main" ] || exit 0
prev="$VERCEL_GIT_PREVIOUS_SHA"
[ -n "$prev" ] || exit 1
git cat-file -e "$prev^{commit}" 2>/dev/null || git fetch -q --depth=1 origin "$prev" 2>/dev/null || exit 1
git diff --quiet "$prev" HEAD -- . 2>/dev/null && exit 0
exit 1
