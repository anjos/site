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

On vessel segmentation we deliberately stepped back from ever-larger networks. Collating
twenty published methods, we showed that a carefully trained, minimalistic U-Net of some
34,000 parameters — one to three orders of magnitude smaller than the architectures it was
competing with — closely matches the best of them, and that a simple cascaded extension,
W-Net, at roughly 68,000 parameters surpasses them on the standard benchmarks. Making that
claim safely meant first repairing how the field measures itself: we adopted a strict
protocol that computes metrics at native resolution and fixes the decision threshold from
training data alone, and a companion study showed that once scores are computed
consistently the differences between most published architectures are not statistically
meaningful, that high-resolution images need nothing more elaborate than rescaling, and
that the entire pipeline can be shipped as open code others can rerun. The same effort
produced the most comprehensive cross-dataset analysis to date, across ten databases,
which made plain that segmentation is far from solved once test images differ from the
training set; a simple self-labelling scheme recovers part of the lost generalisation.

Structure was only half the question. With the Grenoble team we contributed the vessel
segmentation behind an adaptive-optics laser-Doppler velocimeter that measures absolute
retinal blood flow non-invasively. Replacing conventional vessel detection with a learned
segmentation raised the share of the 12,320 adaptive-optics images yielding an automatic
calibre measurement from 64.9% to 99.5%, which is what made the clinical study tractable:
across fifteen healthy subjects total venous flow was 37.8 ± 6.8 µl/min, whereas in eyes
with retinal vein occlusion flow through the occluded vein fell to 3.51 ± 2.25 µl/min and
the tight relationship between vessel calibre and flow seen in healthy eyes largely broke
down. The thread across the project is restraint and reproducibility: the segmentation and
evaluation methods live on in the open-source `mednet` library, and the recurring finding,
that small models rigorously benchmarked rival heavy ones yet still generalise poorly out
of distribution, has shaped how we build and report clinically deployable retinal models
rather than chase leaderboard positions.

Experiments use public retinal benchmarks — DRIVE, STARE, CHASE-DB1, HRF, and IOSTAR.
