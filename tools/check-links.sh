#!/bin/sh
# SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause
# Check ordinary links strictly, then report the temporary IMAGIN-AIR exception.
set -eu

lychee --config lychee.toml \
  --root-dir "${PIXI_PROJECT_ROOT:-.}/public" public

if ! lychee --config lychee-warnings.toml \
    --root-dir "${PIXI_PROJECT_ROOT:-.}/public" public; then
  echo "WARN: The IMAGIN-AIR project page is temporarily unavailable:" >&2
  echo "      https://www.idiap.ch/en/projects/imagin-air" >&2
fi
