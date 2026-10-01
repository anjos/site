#!/bin/sh
# SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause
# Temporary: check idiap.ch and its subdomains without failing the gate.
set -u

if ! lychee --config lychee-idiap.toml \
    --root-dir "${PIXI_PROJECT_ROOT:-.}/public" public; then
  echo "WARN: idiap.ch link checks failed; the domain is temporarily unstable." >&2
  echo "      Reporting warnings locally and in CI. Other domains remain fatal." >&2
fi
