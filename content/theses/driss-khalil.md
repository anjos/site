---
title: "Computer-Aided Screening for Eye Diseases from 2-D Retinography"
author: "Driss Khalil"
level: "Master"
university: "UniDistance, Brig (Master in AI, jointly with Idiap)"
date: 2022-06-19
slug: "driss-khalil"
cover: "images/covers/driss-khalil.png"
summary: >-
  Many blinding eye diseases show no early symptoms. This thesis worked toward
  interpretable screening from ordinary retinal photographs by teaching a single
  model to segment the fundus structures that disease affects most.
projects:
  - "retinal-image-analysis"
report: "https://www.idiap.ch/~aanjos/pdfs/theses/driss-khalil.pdf"
research_outputs:
  - "anjos_mednet_2024"
datasets:
  - name: "Public retinal-fundus benchmarks (DRIVE, DRIONS-DB, and others)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
---

Several blinding eye diseases develop without any visual symptoms, so a late
diagnosis can mean irreversible loss of sight. Screening from two-dimensional
retinal photographs offers a cheap way to catch them early, but for a clinician
to trust an automated screen, the model should also show its reasoning. That
motivated the question behind this thesis: can a single model segment the key
fundus structures well enough to support interpretable disease screening?

Automated fundus analysis had largely relied on separate, single-task models,
each trained to segment one structure, while the available public datasets were
each annotated for only one task. The difficulty, and the hypothesis under test,
was that a multi-task model could learn from these disjoint datasets at once by
alternating between tasks and filling in the missing annotations with its own
predictions from a previous training stage.

A U-Net-based multi-task model was built to segment the two structures most
affected by disease, the vessels and the optic disc, and evaluated with the
F1-score. Two failure modes appeared, noisy training losses and poor convergence,
and two remedies were tested against them. Gradient accumulation, updating the
weights once per epoch, calmed the loss noise, whereas generating the missing
labels from the best-epoch predictor proved counter-productive and produced an
even higher loss than the single-task baseline.

The thesis mapped out what does and does not work when training multi-task
segmentation on disjoint datasets, a practical prerequisite for interpretable
retinal screening. The segmentation methods were built on the open-source
`mednet` library, leaving reusable foundations for later fundus-analysis work.
