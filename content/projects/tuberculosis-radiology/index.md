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

For tuberculosis, where high-burden regions have too few trained readers and opaque models
fall apart on unfamiliar images, we route the decision through the radiological signs a
radiologist would name and predict the diagnosis from those, reaching areas under the curve
of about 0.97 on Montgomery, 0.90 on Shenzhen and 0.93 on the Indian set while keeping the
reasoning legible. We then pressed the harder question of whether a model is right for the
right reasons, and the answer was sobering: classifiers scoring a perfect area under the
curve on the standard benchmark fell to 0.79 on an unseen external cohort, and their saliency
maps concentrated outside the lungs entirely. Pre-training on a large, only loosely related
radiograph collection and balancing the classes through the loss recovered both properties at
once, lifting external performance to 0.88 while roughly quadrupling the overlap between
model attention and expert-drawn disease regions. And because much of the world still records
chest X-rays on film, we measured what photographing those films costs a lung-segmentation
model: its precision-recall area falls from 0.99 on digital images to 0.90 on digitised ones,
a gap any field deployment must budget for.

The same fragility haunts quantitative imaging. Radiomics promises to turn a scan into
biomarkers, yet many classic features change value the moment the acquisition settings do.
Imaging a 3D-printed anthropomorphic phantom containing four classes of liver tissue and
lesion under eight acquisition protocols, thirty repeat scans each, let us score stability and
discriminative power on the same footing. Three-dimensional deep features proved at least
twice as stable across scanner variation as the steadiest hand-crafted family, and some three
times as stable as hand-crafted features overall, while giving up almost nothing in their
ability to separate the tissue classes — and this from a network trained on an unrelated
anatomical task on entirely different data. Wavelet features were the most discriminative of
all but the least stable, which is exactly the trade-off a biomarker study needs to see before
committing to it. Across both strands the throughline is the same, and the tooling is shared
through the open-source `mednet` library: for computer-aided radiology to help real clinics,
what it extracts from an image has to be interpretable, fair, and robust to the scanners and
populations it will actually meet.
