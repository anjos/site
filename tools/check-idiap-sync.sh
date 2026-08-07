#!/bin/sh
# Fail if anything in idiap-public/ has not been published to the Idiap web
# server. Dry run only: it never transfers and never deletes.
#
# Push direction only. Files that exist on the server but not locally (the old
# papers/ archive, posters/, index.php) are deliberately ignored — the mirror is
# a subset, and `pixi run idiap-pull` is what fetches the rest.
#
# Needs SSH access to `idiap`, so this never runs in CI and is part of no
# composite gate: run `pixi run check-sync` by hand after `pixi run idiap-push`.
set -eu

out=$(
  rsync -avzn --out-format=%n idiap-public/ idiap:public/ |
    grep -vE '^(Transfer starting:|sending incremental|sent |total size |\./$|$)' ||
    true
)

if [ -n "$out" ]; then
  echo "! These files are not published on Idiap — run \`pixi run idiap-push\`:" >&2
  echo "$out" | sed 's/^/    /' >&2
  exit 1
fi

echo "idiap-public/ is fully published on Idiap."
