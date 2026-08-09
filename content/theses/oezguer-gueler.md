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

Adding TBX11K data measurably improved state-of-the-art, replicable classifiers,
settling the second question affirmatively. The explanations were then assessed
along two axes that are easily confused: faithfulness, whether the heatmap really
reflects what the model uses, measured by removing the highlighted evidence and
observing the effect, and localisation, whether it points where the disease
actually is, measured against the expert boxes. Because a method can score well on
one and badly on the other, a combined metric was proposed to rank
model-and-explanation pairings on both at once. The ranking confirmed that no
single saliency method dominates across architectures, and identified a
multi-label DenseNet-121 paired with Eigen-CAM as the best available trade-off.

The hypothesis holds in both parts: there is no universal explanation method, and
a ground-truth-based metric can pick the right pairing rather than leaving it to
habit. The practical consequence is a change in how such systems should be built —
model and explanation must be chosen together, since a good classifier with the
conventionally chosen heatmap may be justifying itself with evidence it does not
use. The recommended pairing is offered for accurate and correctly localised
active-tuberculosis detection. The results were published at EuVIP 2024 and fed
directly into the group's work on refining and de-biasing tuberculosis detection.
