---
title: "Measuring Bias in AI Anatomical Structure Segmentation Models"
author: "Reto Odoni"
level: "Master"
university: "University of Zürich, Department of Informatics"
date: 2025-05-29
slug: "reto-odoni"
cover: "images/covers/reto-odoni.png"
summary: >-
  AI models that outline organs in medical scans can quietly work better for some
  patients than others. This thesis measured gender and organ-size bias in three
  widely used segmentation models.
projects:
  - "trustworthy-fair-ai"
report: "https://seafile.ifi.uzh.ch/f/da14adc2a0a14e70964d/"
datasets:
  - name: "CT-ORG, AbdomenCT-1K, and KiTS19 (public abdominal CT)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
---

AI segmentation models are increasingly woven into medical-imaging workflows,
where they outline anatomical structures automatically. A model that is accurate
on average, however, can still be less accurate for some patients than for others.
Because evaluation usually reports only overall segmentation quality, this thesis
asked whether widely used pretrained models are biased across patient subgroups
and organ characteristics.

The leading foundational segmentation models — TotalSegmentator, SAM-Med3D and
Vista3D — are trained on large medical-imaging collections and tuned to maximise
overall performance across many anatomies, while comparatively little attention
has gone to fairness, and what fairness work exists has concentrated on
classification rather than segmentation. The hypothesis was that these models
carry measurable biases tied both to patient gender and to the size of the organ
being segmented, and further that the two are entangled, organ size acting as a
confounder for any apparent gender effect.

The three pretrained models were evaluated on the liver, both kidneys and the
urinary bladder across three public collections, CT-ORG, AbdomenCT-1K and KiTS19,
with quality read through the Dice similarity coefficient, the Hausdorff distance
and the relative volume difference. Statistically significant gender disparities
appeared in 24 to 33 percent of all organ-and-metric combinations, and organ size
mattered more still: grouping organs into small, medium and large produced
significant differences in 52 to 70 percent of combinations. The confounding was
demonstrated rather than assumed, showing that part of what presents as a gender
effect is the downstream consequence of systematically different organ volumes.

Both parts of the hypothesis are confirmed, and the answer to the opening
question is that yes, widely deployed segmentation models are measurably biased —
across every model examined, not merely the weakest. The practical consequence is
that an aggregate Dice score conceals precisely the disparities a clinic would
care about, so trustworthy medical AI requires subgroup-aware evaluation as a
matter of routine. The thesis leaves behind an empirical template for conducting
it, including the reminder that subgroup differences must be tested against
anatomical confounders before being attributed to demographics.
