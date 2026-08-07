---
title: "Automatic Sleep-Phase Analysis via Stateful Methods"
author: "Gabriele Brunini"
level: "Master"
university: "University of Zürich, Department of Informatics"
date: 2023-07-16
slug: "gabriele-brunini"
cover: "images/covers/gabriele-brunini-lstm.png"
summary: >-
  Sleep stages unfold over time, so a good scorer should use temporal context.
  This thesis studied stateful models for automatic sleep-phase analysis, and how
  well they carry across clinics and populations.
projects:
  - "sleep-medicine"
research_outputs:
  - "anjos_sleepless_2017"
datasets:
  - name: "Sleep-EDF (ST, SC) and MASS SS3 polysomnography sets (public)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
---

Polysomnography is the gold standard for diagnosing sleep disorders, yet scoring
the recordings into sleep stages is done by hand, which is slow, subjective, and
sensitive to each clinic's setup. Because sleep stages unfold over time, a scorer
that reasons about temporal context should have an advantage. This thesis asked how
well stateful models, which carry information across time, can automate sleep-phase
analysis and how far they generalise across clinics and populations.

Where a companion study examined stateless models that classify each epoch in
isolation, this work took the opposite stance, testing the hypothesis that
modelling the temporal structure of a night improves on stateless baselines. The
emphasis throughout was on robustness to clinic setup and fairness across different
patient groups, not accuracy on a single dataset alone.

The thesis established baselines for stateful sleep-phase analysis and its own
contributions on top of them, evaluated with attention to how performance holds up
when data comes from different sleep centres. Together with the stateless study, it
maps out where temporal context helps and where the harder problem of cross-clinic
generalisation remains.

The work argues that automatic sleep staging should be judged by how well it
transfers, not just by in-domain accuracy, and it contributes the stateful half of
that picture. The methods build on the open-source `sleepless` library.
