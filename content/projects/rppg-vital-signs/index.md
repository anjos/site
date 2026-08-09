---
title: "Remote Photoplethysmography and Vital Signs"
weight: 85
archived: true
period: "2016–2017"
cover: "images/covers/rppg-manhob-hci-tagging.png"
summary: >-
  Reproducible, camera-based estimation of vital signs, putting remote
  photoplethysmography on a shared, openly benchmarked footing.
research_outputs:
  - "10.48550/arxiv.1709.00962"
  - "10.34777/ff3f-ba56"
---

Remote photoplethysmography (rPPG) reconstructs a pulse signal from ordinary video, a
genuinely appealing route to contact-free vital-sign monitoring. The catch is that most
published work is evaluated on privately-owned data, so methods cannot be compared in a
standard, principled way. Our contribution was to put the field on a reproducible footing:
shared data, shared code, and one honest evaluation protocol.

## Major achievements

We released the public **COHFACE** database, 40 subjects and 160 one-minute videos recorded with
a commodity webcam under two controlled lighting conditions, studio and natural, with
synchronised physiological ground truth. Alongside it we re-implemented and open-sourced three
state-of-the-art algorithms — the method of Li et al., CHROM, and Spatial Subspace Rotation —
so they could be run and compared under a single protocol on both COHFACE and the existing
Manhob HCI-Tagging database. Reproduction alone proved instructive: we could not recover the
published correlation of 0.82 for the strongest of them, and traced the shortfall to the one
component its authors had not released. Shipping the data, the implementations, the protocol and
the scripts together turned vague, incomparable claims into a like-for-like evaluation anyone
can download and rerun.

The evaluation was deliberately unflattering, and its most important lesson was methodological.
Prior work, including the reference method we reproduced, had tuned its free parameters —
twelve of them, in that case — directly on the test data, a bias severe enough to conceal an
algorithm's inability to generalise. Once training and test subjects were kept strictly apart,
performance collapsed: the strongest baseline fell from a correlation of 0.70 with the
ground-truth heart rate to 0.45, while the other two managed 0.14 and 0.05. Changing the
acquisition conditions was worse still — moving from studio to natural lighting, or from one
database to the other, drove all three to near-zero or negative correlation. None was precise
enough to be trusted in a realistic scenario, exactly the kind of sobering result a shared
benchmark exists to surface. By shipping the data, the implementations, and the evaluation
protocol together, the work gave the community a fair starting line rather than another
private-data leaderboard entry.
