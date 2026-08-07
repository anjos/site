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

We released the public **COHFACE** database, 40 subjects and 160 one-minute videos recorded
with a commodity webcam under two controlled lighting conditions, studio and natural. Alongside
it we re-implemented and open-sourced three state-of-the-art rPPG algorithms, CHROM, the method
of Li et al., and Spatial Subspace Rotation (2SR), so they could be run and compared under a
single common protocol on both COHFACE and the existing Manhob HCI-Tagging database. This turned
vague, incomparable claims into a like-for-like evaluation that anyone can download and reproduce.

The evaluation was deliberately unflattering, and its most important lesson was methodological.
Much prior work, including the reference method we reproduced, had tuned its parameters directly
on the test data, a severe bias that masks an algorithm's inability to generalise. When training
and test subjects were instead kept separate, performance collapsed: the strongest baseline fell
from a Pearson correlation of about 0.70 with the ground-truth heart rate when tuned in-sample to
roughly 0.45 on held-out subjects, while CHROM and 2SR dropped to near zero. Under this honest
protocol none of the three algorithms was precise enough to be trusted in a real-world scenario,
exactly the kind of sobering result a shared benchmark exists to surface. By shipping the data,
the implementations, and the evaluation protocol together, the work gave the community a fair
starting line rather than another private-data leaderboard entry.
