---
title: "Trustworthy and Fair Medical AI"
weight: 14
cover: "images/covers/fair-unfair.jpg"
summary: >-
  Making medical AI fair across patient subgroups and useful in the clinic, with
  evaluation frameworks, foundation-model bias analysis, and utility-fairness
  trade-offs.
partners:
  - "Federal University of São Paulo (UNIFESP)"
research_outputs:
  - "10.1145/3793542"
  - "10.59275/j.melba.2025-ab9a"
  - "10.1016/j.asoc.2025.113426"
  - "10.1007/978-3-031-72787-0_11"
  - "10.48550/arxiv.2408.16154"
  - "anjos_fairical_2025"
  - "anjos_credible_2023"
---

A medical model can be accurate on average and still let specific groups of patients down,
which is exactly the failure a clinic cannot afford. This line of work cuts across our medical
projects and tries to make fairness something we can measure and act on, rather than hope for,
and to understand honestly how it trades off against clinical usefulness now that large
foundation models are everywhere.

## Major achievements

Fairness only becomes actionable once you can measure it and trade it off honestly. We built a
multi-objective evaluation framework, released as the open-source `fairical` tool, that
summarises how competing models balance utility against several fairness criteria at once,
using multi-objective-optimisation measures and a compact radar-chart view, and validated it
on three real-world medical-imaging datasets. We paired it with an optimisation method that
folds multiple fairness metrics directly into the training loss, showing that accuracy and
fairness can be traded off deliberately rather than left to chance. A companion survey argued
that keeping medical imaging equitable as foundation models arrive takes systematic
intervention across the whole pipeline, from data documentation to deployment and policy, not
a single model-level fix.

Looking inside the foundation models themselves, we found results worth stating plainly:
data-efficient generalisation, the very property that makes these models attractive, can make
their bias worse, and a model can reach near-perfect accuracy while leaning on demographic
shortcuts. On the constructive side, we showed that a foundation model's own backbone can
stand in for missing demographic labels, recovering enough group structure to shrink the
gender-attribute gap by roughly 4.4% in-distribution and 6.2% out-of-distribution, though age
remained stubborn. None of this stays abstract: these evaluation and mitigation methods feed
straight back into our radiology and ophthalmology work, where fairness across subgroups is a
clinical requirement, not a nicety.
