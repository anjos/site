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

The leading foundational segmentation models, such as TotalSegmentator, Medical
SAM, and Vista3D, are trained on large medical-imaging collections and tuned to
maximise overall performance across many anatomies, while comparatively little
attention has gone to fairness, and what fairness work exists has concentrated on
classification more than on segmentation. The hypothesis was that these models
carry measurable biases, tied both to patient gender and to the size of the organ
being segmented.

The study empirically measured gender and organ-volume bias in the three
pretrained models on the liver, both kidneys, and the urinary bladder, drawing on
public datasets (CT-ORG, AbdomenCT-1K, and KiTS19). Segmentation quality was
assessed with the Dice Similarity Coefficient, the Hausdorff distance, and the
relative volume difference. The analysis found statistically significant
gender-based performance disparities, as well as biases related to organ volume,
across all three models.

The thesis concluded that leading segmentation models harbour distinct biases that
a single overall-performance number conceals, and that trustworthy medical AI
needs multifaceted, subgroup-aware fairness evaluation rather than one aggregate
score. It offers an empirical template for carrying out that kind of evaluation.
