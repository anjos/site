---
title: "Semantic Segmentation of Weakly Labeled Retinal Images"
author: "Xiao Tan"
level: "Master"
university: "University of Zürich, Department of Informatics"
date: 2023-02-27
slug: "xiao-tan"
cover: "images/covers/xiao-tan.png"
summary: >-
  Labelling retinal images pixel by pixel is slow and expensive. This thesis
  learned to segment retinal vessels while leaning on unlabelled images, so good
  results need far fewer annotations.
projects:
  - "retinal-image-analysis"
report: "https://capuana.ifi.uzh.ch/publications/PDFs/23611_Xiao%20Tan_thesis.pdf"
research_outputs:
  - "anjos_mednet_2024"
datasets:
  - name: "DRIVE, STARE, CHASE-DB1, HRF, IOSTAR (public retinal benchmarks)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
---

Segmenting the vessels in a retinal image means giving every pixel a label, a far
more demanding task than classifying the whole image, and one whose progress is
capped by how scarce and expensive pixel-level annotations are. This thesis asked
whether reliable vessel segmentation can be learned when labelled data is limited,
by putting the abundant unlabelled images to work.

Fully supervised networks are bounded by the amount of labelled data, whereas
semi-supervised consistency learning promises to exploit unlabelled images as
well. The catch is that vessels are thin and sparse, so the data augmentations
that consistency methods rely on must be chosen with care. The hypothesis was that
extending the Mean Teacher model to retinal images, with augmentations suited to
their structure, would let unlabelled data improve segmentation and generalisation.

The Mean Teacher model was adapted to retinal vessel segmentation and the
augmentations were searched systematically, with performance measured by the F1
(Dice) score because vessel pixels are so heavily outnumbered by background.
Greyscale conversion and additive Gaussian noise proved the effective pair:
strong enough to make the two branches disagree usefully, mild enough to leave
thin vessels intact, where more aggressive transformations prevented the model
from converging at all. Across four public datasets the gains were concentrated
exactly where they matter, on the labelled-and-unlabelled pairs that generalise
poorly under ordinary supervised training, and were negligible where supervised
learning already transferred well. On a genuinely unseen dataset the choice of
labelled training set dominated the outcome, and only once that choice was sound
did adding further unlabelled data help.

The hypothesis holds, but conditionally. Consistency learning does transfer to
retinal vessels and does turn unlabelled images into a real asset, provided the
augmentations respect the sparse structure of the target — which answers the
opening question affirmatively while naming the constraint that makes it work.
The more useful finding is the one that was not anticipated: under weak
supervision, choosing the labelled set well matters at least as much as adding
unlabelled data, so annotation effort is better spent on which images to label
than on how many. The methods live on in the open-source `mednet` library.
