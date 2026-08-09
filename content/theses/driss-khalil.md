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
affected by disease, the vessels and the optic disc, and scored with the F1
measure across four experiments varying the balance and the image quality of the
disjoint training sets. It underperformed the single-task baselines on images
matching the training data, and fell further behind on images of different
quality. Two failure modes were isolated and attacked in turn. Training losses
were noisy, because alternating between tasks updated the weights many times per
epoch; accumulating gradients and updating once per epoch quietened this and
improved on the baseline multi-task setup. Convergence, however, remained poor,
and filling the missing annotations with the best epoch's own predictions made it
worse still, ending at a higher loss than doing nothing.

The hypothesis was therefore refuted, and instructively so. Because the
self-generated labels made matters worse rather than better, poor pseudo-labels
cannot be the cause; the diagnostic evidence points instead to the two tasks
interfering with one another in a network that shares almost all of its layers
between them. The answer to the opening question is thus a qualified no — one
model can be trained on disjoint datasets, but not with this degree of parameter
sharing — and the thesis names the concrete next step, keeping gradient
accumulation while giving each task more of its own layers. The segmentation
methods were built on the open-source `mednet` library, leaving reusable
foundations for later fundus-analysis work.
