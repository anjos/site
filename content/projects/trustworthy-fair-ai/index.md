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

Fairness only becomes actionable once it can be measured and traded off honestly. Fairness
criteria conflict with one another — improving parity on one attribute routinely degrades it on
another, and no single score captures the outcome — so we built a model-agnostic evaluation
framework that treats utility and each fairness criterion as separate objectives in one
multi-objective problem, summarising how competing systems compare through a compact
radar-chart view backed by measures of convergence, capacity and diversity. It was validated on
simulations and on three real-world medical-imaging datasets, and is released as the
open-source `fairical` package. We paired it with an optimisation method that constrains loss
minimisation with several fairness metrics simultaneously, so that fairness across multiple
protected attributes at once is imposed deliberately rather than left to chance, and which
holds up on the imbalanced, modestly sized datasets where such methods usually falter. A
companion review argued that keeping medical imaging equitable as foundation models arrive
demands systematic intervention across the whole pipeline — data documentation, curation,
deployment protocols and policy — rather than the model-level fix the literature had favoured.

Looking inside the foundation models themselves produced results worth stating plainly.
Fine-tuning a retinal foundation model on a Brazilian cohort quite unlike its pre-training
population, we found that self-supervised pre-training does narrow performance gaps across
gender and age compared with supervised training, but that the label efficiency which makes
these models attractive cuts the other way: the less data the model is fine-tuned on, the wider
the demographic gap becomes. On the constructive side, we showed that a foundation model's own
backbone can substitute for demographic labels a hospital does not hold, by clustering its
embeddings into groups that stand in for protected attributes; used for both mitigation and
evaluation, this narrowed the gender gap by 4.4% in distribution and 6.2% out of it, though age
proved stubborn and remains open. None of this stays abstract: these evaluation and mitigation
methods feed straight back into our radiology and ophthalmology work, where consistent
performance across subgroups is a clinical requirement rather than a nicety.
