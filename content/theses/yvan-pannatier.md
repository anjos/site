---
title: "Clinically Interpretable Computer-Aided Diagnostic Tool for Fibromuscular Dysplasia Detection"
author: "Yvan Pannatier"
level: "Master"
university: "University of Geneva, Faculty of Science (MSc Computer Science)"
date: 2024-12-03
slug: "yvan-pannatier"
cover: "images/covers/yvan-pannatier.png"
summary: >-
  Fibromuscular dysplasia is rare and easy to miss. This thesis explored neural
  networks that detect it in medical imaging while explaining their decisions, so a
  clinician can see why.
projects:
  - "fibromuscular-dysplasia"
report: "https://www.idiap.ch/~aanjos/pdfs/theses/yvan-pannatier.pdf"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "CHUV, Lausanne University Hospital"
    country: "Switzerland"
  - name: "University of Geneva"
    country: "Switzerland"
---

Fibromuscular dysplasia (FMD) is a rare, non-atherosclerotic vascular disease that
remains hard to diagnose because its most common symptoms are non-specific, and
because it most often involves the renal arteries where it is easy to overlook.
That diagnostic difficulty motivated the question behind this thesis: can neural
networks help detect FMD in medical imaging, and do so in a way a clinician can
actually interpret?

Convolutional networks have been strikingly successful across medical image
analysis, including segmentation, but a black-box detector is of little use in a
clinic where a diagnosis must be justified. The hypothesis was that neural networks
could detect FMD while remaining interpretable, if their decisions were exposed
through saliency maps that show which regions drove them.

Four strategies for coping with a cohort of fewer than 200 patients were tried:
patch-based training, contrastive pre-training, treating both kidneys as one
sample, and generating one sample per kidney with non-vascular structures removed
using prior anatomical knowledge. Only the last converged at all; the other three
failed outright. To make the explanations testable rather than merely decorative,
volumetric saliency mapping was paired with an extension of an established
faithfulness score to three-dimensional models. A control experiment then exposed
how narrow the margin was: a subset of control scans is never classified
correctly, and reintroducing thirteen of them dropped precision from 59 to 40
percent, accuracy from 63 to 50 percent, and the area under the curve to 0.49 —
indistinguishable from guessing.

The hypothesis survives only in weakened form. Neural networks can be made
interpretable here, and the metric extension makes the interpretation auditable,
but detection itself is not yet reliable enough for the interpretation to be worth
much. The value of the answer lies in its diagnosis: because the failure tracks
specific scans and the preprocessing applied to them rather than the choice of
architecture, the remedy is to constrain the model anatomically — isolate the
arteries and classify only those. That recommendation was taken up directly by the
group's next thesis on the disease, where it did indeed improve detection, and the
gender bias flagged here remains open. The work stands as the interpretability-first
foundation of the FMD collaboration with CHUV.
