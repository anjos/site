---
# SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause
name: pixi
description: Comprehensive package and environment management using pixi - a fast, modern, cross-platform package manager. Use when working with pixi projects for (1) Project initialization and configuration, (2) Package management (adding, removing, updating conda/PyPI packages), (3) Environment management (creating, activating, managing multiple environments), (4) Feature management (defining and composing feature sets), (5) Task execution and management, (6) Global tool installation, (7) Dependency resolution and lock file management, or any other pixi-related operations. Supports Python, C++, R, Rust, Node.js and other languages via conda-forge ecosystem.
---

# Pixi

Pixi is a fast, modern, cross-platform package manager for reproducible environments built on conda and PyPI ecosystems.

## Documentation

Fetch these URLs when the quick reference below isn't enough:

- **Index** (topic navigation + links): https://pixi.prefix.dev/latest/llms.txt
- **Full docs** (complete reference): https://pixi.prefix.dev/latest/llms-full.txt

## Essential Commands

**Project setup:**
```bash
pixi init my-project            # new project (pixi.toml)
pixi init --format pyproject .  # use pyproject.toml instead
pixi install                    # install from manifest
pixi install --frozen           # install without updating lock
```

**Packages:**
```bash
pixi add numpy pandas           # conda packages
pixi add --pypi requests        # PyPI package
pixi add --feature dev pytest   # into a feature
pixi remove numpy
pixi update                     # update all packages
pixi upgrade numpy              # bump manifest constraint + update
```

**Run & shell:**
```bash
pixi run <task>                 # run defined task
pixi run -e <env> <task>        # in specific environment
pixi exec <cmd>                 # ad-hoc command in env
pixi shell                      # interactive shell
pixi shell -e <env>             # specific environment shell
```

**Global tools:**
```bash
pixi global install <tool>
pixi global update
pixi global list
pixi global remove <tool>
```

**Maintenance:**
```bash
pixi info                       # project status
pixi list [-e <env>]            # installed packages
pixi lock                       # update lock only (no install)
pixi clean                      # remove .pixi/
pixi clean cache                # clear package cache
```

## Manifest Patterns

**Features + environments:**
```toml
[feature.dev.dependencies]
pytest = "*"
ruff = "*"

[feature.dev.tasks]
test = "pytest tests/"
fmt  = "ruff format ."

[environments]
dev  = ["dev"]
test = { features = ["dev"], solve-group = "default" }
```

**Multiple Python versions:**
```toml
[feature.py311.dependencies]
python = "3.11.*"
[feature.py312.dependencies]
python = "3.12.*"

[environments]
py311 = ["py311"]
py312 = ["py312"]
```

**Tasks with dependencies:**
```toml
[tasks]
build = { cmd = "python build.py", depends-on = ["install"] }
ci    = { depends-on = ["fmt", "test"] }
```

**Hardware variants (e.g. CUDA vs CPU):**
```toml
[feature.cuda.dependencies]
pytorch-cuda = { version = "*", channel = "pytorch" }
[feature.cpu.dependencies]
pytorch-cpu  = { version = "*", channel = "pytorch" }

[environments]
cuda = ["cuda"]
cpu  = ["cpu"]
```
