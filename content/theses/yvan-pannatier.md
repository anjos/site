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

Four CNN-based architectures were explored for FMD detection and compared with
quantitative metrics, including precision, F1-score, and the area under the ROC
curve, alongside saliency maps for interpretability. Building on that comparison,
the thesis proposed an approach aimed at a clinically usable, interpretable
detector rather than accuracy in isolation.

The work delivers a first, interpretability-first step toward computer-aided
diagnosis of fibromuscular dysplasia, and frames how such a tool should be
evaluated for the clinic. It opens the FMD collaboration with CHUV toward models
whose decisions clinicians can inspect and trust.
