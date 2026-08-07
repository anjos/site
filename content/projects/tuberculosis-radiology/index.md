---
title: "Radiology — Robust Image Analysis"
weight: 30
cover: "images/covers/ptb-cxr.jpg"
summary: >-
  Interpretable, generalisable computer-aided analysis of radiological images —
  detecting tuberculosis on chest X-rays and extracting stable quantitative
  biomarkers from CT — built to hold up across scanners and populations.
partners:
  - "Federal University of Rio de Janeiro"
  - "University of Zürich"
  - "Murabei Data Science, Brazil"
  - "University Hospital Basel"
  - "Lausanne University Hospital (CHUV)"
  - "University of Geneva"
  - "ETH Zurich"
research_outputs:
  - "10.1109/euvip61797.2024.10772829"
  - "10.1109/euvip61797.2024.10772813"
  - "10.21528/cbic2021-123"
  - "raposo_pulmonary_2022"
  - "anjos_mednet_2024"
---

A radiological image, a chest X-ray or a CT slice, is only as useful as the information a
computer can reliably pull from it, and that reliability is exactly what tends to break when
the scanner, the site, or the patient population changes. This work builds computer-aided
analysis of radiological images that stays interpretable, fair, and stable enough to trust
outside the lab, from detecting disease to quantifying it.

## Major achievements

For tuberculosis, where high-burden regions have too few readers and opaque models fall apart
on unfamiliar images, we route the decision through the radiological signs a radiologist looks
for and predict the diagnosis from those, reaching state-of-the-art AUCs of around 0.97 on
Montgomery, 0.90 on Shenzhen, and 0.93 on the Indian set while keeping the reasoning legible.
We then pressed on whether a model is right for the right reasons, showing that near-perfect
AUROC can hide reliance on spurious background cues, and reduced that bias with large-scale
proxy pre-training and a class-balancing objective so the model both looks where experts look
and generalises to unseen data. And because much of the world still images chest X-rays on
analog film, we measured what photographing those films costs a lung-segmentation model, whose
precision-recall area drops from 0.99 on digital images to 0.90 on digitised ones, a gap any
field deployment must reckon with.

The same fragility haunts quantitative imaging. Radiomics promises to turn a scan into
biomarkers, yet many classic features change value the moment the CT settings change. Using a
3D-printed anthropomorphic phantom imaged under eight acquisition protocols, we showed that
three-dimensional deep features are at least twice as stable across scanner variation as any
hand-crafted family, and that even generic deep features trained on an unrelated task stay
discriminative, telling liver lesions from healthy tissue at about 93.5% accuracy. Measuring
stability and discriminative power on the same footing gives a principled way to pick
biomarkers worth trusting. Across both strands the throughline is the same, and the tools are
shared through the open-source `mednet` library: for computer-aided radiology to help real
clinics, what it extracts from an image has to be interpretable, fair, and robust to the
scanners and populations it will actually meet.
