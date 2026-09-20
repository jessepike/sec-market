#!/bin/bash
# THROWAWAY script — runs inside OrbStack dev VM. Copy of baseline/measure/run-lighthouse.sh
# with the target URL changed to preview and the output path changed to evidence/after/measure.
set -e
cd /mnt/mac/Users/jessepike/code/projects/sec-market/web
export CHROME_PATH=/home/jessepike/.cache/ms-playwright/chromium-1234/chrome-linux/chrome
OUT=/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/after/measure
URL=https://security-market-pulse-git-preview-pikeholdings.vercel.app/

for i in 1 2 3; do
  echo "mobile run $i..."
  npx --yes lighthouse "$URL" \
    --output=json --output-path="$OUT/lh-mobile-$i.json" \
    --chrome-flags='--headless=new --no-sandbox' \
    --quiet --form-factor=mobile --screenEmulation.mobile=true \
    2>"$OUT/lh-mobile-$i.log" || echo "mobile run $i FAILED"
done

for i in 1 2 3; do
  echo "desktop run $i..."
  npx --yes lighthouse "$URL" \
    --output=json --output-path="$OUT/lh-desktop-$i.json" \
    --chrome-flags='--headless=new --no-sandbox' \
    --quiet --preset=desktop \
    2>"$OUT/lh-desktop-$i.log" || echo "desktop run $i FAILED"
done

echo "done"
