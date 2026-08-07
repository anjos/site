---
title: "Ophthalmology — Retinal Image Analysis"
weight: 20
cover: "images/covers/xiao-tan.png"
summary: >-
  Segmentation and analysis of retinal fundus images (vessels, optic disc, blood
  flow) with minimalistic, reproducible, and clinically deployable models.
partners:
  - "University Hospital of Grenoble Alpes"
  - "Idiap Research Institute"
research_outputs:
  - "10.1038/s41598-022-09675-y"
  - "10.1016/j.mvr.2023.104648"
  - "10.48550/arxiv.1909.03856"
  - "anjos_mednet_2024"
---

Retinal fundus imaging is a cheap, non-invasive window onto vascular and neurological
health, and many sight-threatening diseases develop before symptoms appear. Analysing the
retinal vasculature automatically therefore supports earlier and more interpretable
diagnosis. A recurring principle in this work is that the models should stay small and
rigorously reproducible: state of the art, but light enough to train honestly and to run
in a clinic.

## Major achievements

On vessel segmentation we deliberately stepped back from ever-larger networks. Reviewing
twenty published methods, we showed that a carefully trained, minimalistic U-Net with
orders of magnitude fewer parameters closely matches the best techniques, and that a small
cascaded extension (W-Net) reaches outstanding accuracy on the standard benchmarks while
still using a fraction of the weights of prior work. The same effort produced the most
comprehensive cross-dataset study to date, spanning up to ten databases, which made clear
that segmentation is far from solved once test images differ from the training set, and
that a simple self-labeling strategy recovers part of that lost generalisation. A companion
study took aim at the field's evaluation habits: it showed that high-resolution images can
be handled by plain rescaling, that widely reported F1 scores are mostly statistically
indistinguishable once computed consistently, and it released a fully reproducible
framework so those comparisons can actually be repeated.

Beyond structure we also looked at function. Working with the Grenoble team on an
adaptive-optics laser-Doppler velocimeter, we helped quantify absolute retinal blood flow
in a cohort of healthy eyes and eyes with retinal vein occlusion, where flow is markedly
reduced and the usual relationship between vein calibre and flow no longer holds. The
thread tying these results together is reproducibility and restraint: the segmentation and
evaluation methods live on in the open-source `mednet` library, and the recurring finding,
that small models rigorously benchmarked can rival heavy ones yet still generalise poorly
out of distribution, has shaped how we build and report clinically deployable retinal
models rather than chase leaderboard numbers.

Experiments use public retinal benchmarks — DRIVE, STARE, CHASE-DB1, HRF, and IOSTAR.
