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

The Mean Teacher model was adapted to retinal vessel segmentation and the most
effective augmentations identified, with performance measured by the F1 (Dice)
score because vessel pixels are so heavily outnumbered. Across four public datasets
the method significantly improved the labelled-and-unlabelled dataset pairs that
generalise poorly under ordinary supervised learning. For a genuinely unseen
dataset the choice of labelled training set mattered a great deal, and once that
choice was good, adding more unlabelled data improved results further.

The thesis showed that consistency learning transfers to retinal vessels when the
augmentations respect their sparse structure, turning unlabelled images into a
real asset. Its lasting practical lesson is that, under weak supervision, choosing
the labelled set well matters as much as adding unlabelled data. The methods live
on in the open-source `mednet` library.
