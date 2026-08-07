---
title: "Explaining CNN-Based Active Tuberculosis Detection through Saliency Mapping"
author: "Özgür Güler"
level: "Master"
university: "University of Zürich"
date: 2023-09-01
slug: "oezguer-gueler"
cover: "images/covers/oezguer-gueler.png"
summary: >-
  Deep networks can flag active tuberculosis on chest X-rays, but can we trust the
  heatmaps that explain them? This thesis measured which explanation methods are
  actually faithful, and improved detection with more annotated data.
projects:
  - "tuberculosis-radiology"
report: "https://capuana.ifi.uzh.ch/publications/PDFs/24103_Master_Thesis_oezguer_acar_gueler.pdf"
research_outputs:
  - "10.1109/euvip61797.2024.10772829"
  - "anjos_mednet_2024"
datasets:
  - name: "TBX11K, with ground-truth bounding boxes (public)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
---

Convolutional networks can flag patients with active tuberculosis from their
chest X-rays, but in a clinical setting a prediction is only as useful as the
trust placed in it. Saliency maps, the heatmaps that claim to show where a model
looked, are the usual way to justify such decisions. This raised the question at
the centre of the thesis: for active-tuberculosis detection, which saliency
methods are genuinely faithful to the model, and does adding more annotated data
improve detection in the first place?

Saliency methods such as Grad-CAM are widely used yet rarely checked against
ground truth, because the data to check them is scarce. The TBX11K dataset,
which provides expert bounding boxes around the disease, makes that check
possible. The hypothesis was that no single saliency method would work well
across all architectures, and that a principled, ground-truth-based metric could
identify the best model-and-explanation pairing rather than leaving it to
guesswork.

Adding TBX11K data measurably improved state-of-the-art, replicable classifiers.
Faithfulness and localisation were then evaluated with the RemOve-and-Debias and
Proportional-Energy metrics, and a new combined metric, the ROAD-Normalised
PropEng Average, was proposed to rank pairings. The evaluation confirmed that no
universal saliency method exists across architectures, and singled out a
multi-label DenseNet-121 with Eigen-CAM as the best trade-off between
faithfulness and correct localisation.

The thesis concluded that the choice of explanation method must be made together
with the model, not in isolation, and recommended the DenseNet-121 with Eigen-CAM
combination for accurate and correctly localised active-tuberculosis detection.
The results were published at EuVIP 2024 and fed directly into the group's work
on refining and de-biasing tuberculosis detection.
