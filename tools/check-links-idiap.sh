#!/bin/sh
# Check the gitlab.idiap.ch links in the built site, which lychee.toml excludes
# from the main `check-links` run.
#
# Fatal on a workstation, where the host resolves and a dead repo link is a real
# broken link worth stopping a commit for. Only a warning under CI, where Idiap's
# GitLab does not answer cloud runners and a failure therefore says nothing about
# the link. GitHub Actions sets $CI=true; nothing else here depends on it.
set -u

if lychee --config lychee-idiap.toml \
    --root-dir "${PIXI_PROJECT_ROOT:-.}/public" public; then
  exit 0
fi

if [ -n "${CI:-}" ]; then
  echo "WARN: gitlab.idiap.ch did not answer, and this is CI, which that host" >&2
  echo "      does not serve. Not failing the build. Re-run \`pixi run" >&2
  echo "      check-links-idiap\` from Idiap to check these links for real." >&2
  exit 0
fi

echo "! Dead gitlab.idiap.ch link(s) above. If the host is simply unreachable" >&2
echo "  from here, that is not a broken link — re-run from a network that" >&2
echo "  reaches Idiap." >&2
exit 1
