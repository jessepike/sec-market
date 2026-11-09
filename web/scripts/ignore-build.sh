#!/usr/bin/env bash
# Vercel ignoreCommand for Git deployments: exit 0 skips the build, exit 1 builds.
# Only preview builds from Git. main and data/archive never do: production is
# the publisher's prebuilt upload (D-110). Short-lived work branches merge into
# preview, which owns the review URL. preview builds only when the site's
# inputs, web/ or contracts/, changed since its last successful deployment, so
# docs-only and ops-only pushes spend no build minutes.
# Vercel's shallow clone may lack the previous commit; fetch it, else build.
[ "$VERCEL_GIT_COMMIT_REF" = "preview" ] || exit 0
prev="$VERCEL_GIT_PREVIOUS_SHA"
[ -n "$prev" ] || exit 1
git cat-file -e "$prev^{commit}" 2>/dev/null || git fetch -q --depth=1 origin "$prev" 2>/dev/null || exit 1
git diff --quiet "$prev" HEAD -- . ../contracts 2>/dev/null && exit 0
exit 1
