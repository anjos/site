---
title: "Generalizable Automatic Classification of Sleep Stages"
author: "Samuel Michel"
level: "Master"
university: "UniDistance, Brig (Master in AI, jointly with Idiap)"
date: 2023-06-18
slug: "samuel-michel"
cover: "images/covers/samuel-michel.png"
summary: >-
  Scoring a night of sleep by hand is slow and two experts often disagree. This
  thesis studied automatic sleep-stage classification with a focus on holding up
  across different clinics.
projects:
  - "sleep-medicine"
report: "https://publications.idiap.ch/attachments/reports/2023/Michel_Idiap-Com-02-2023.pdf"
research_outputs:
  - "anjos_sleepless_2017"
datasets:
  - name: "Sleep-EDF (ST, SC) and MASS SS3 polysomnography sets (public)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
---

Polysomnography is the gold standard for diagnosing sleep disorders, but turning a
night of recordings into a sleep-stage score is done by hand, and that process is
slow, tedious, and surprisingly unreliable: two experts scoring the same night
often disagree, and every sleep centre uses its own sensor setup. The thesis asked
whether machine learning could stage sleep faster and more reliably than manual
scoring, while staying robust to the clinic setup and fair across populations.

Manual annotation is subjective, and prior automated work had shown that models
can learn the task in principle. The study was deliberately scoped to stateless
models, which classify each epoch without temporal context, to test the hypothesis
that even without modelling time such models can generalise across the differing
setups of different sleep centres.

Hand-crafted and learnable feature extractors were compared across the Sleep-EDF
and MASS databases, with performance read through balanced accuracy and Cohen's
kappa. Within a single database the best model was a convolutional network, but
the ranking inverted under cross-setup evaluation, where a random forest over
manually chosen features combining electroencephalogram and eye-movement channels
generalised best between clinics. The absolute level was equally informative: the
best model reached a kappa of 0.67 to 0.72 on the intra-database test sets,
against the 0.76 reported between two human scorers, so it did not reach expert
agreement.

The hypothesis is only partly borne out. Stateless models do generalise across
setups well enough to be useful, but not by the route expected — the learnable
extractor that ought to have won lost to hand-crafted features once the clinic
changed. The answer to the opening question is therefore that automatic staging
is faster and more consistent than manual scoring but not yet more accurate than
a human expert, and that peak in-domain accuracy is no guide to how a model will
behave elsewhere: cross-clinic generalisation must be measured directly rather
than assumed. The fairness question the thesis set out with remains open, the
tooling for it built but the experiments not run. The methods were released
through the open-source `sleepless` library, and the work is complemented by a
companion thesis on stateful methods that add temporal context.
