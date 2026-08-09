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

Where a companion study examined stateless models that score each epoch in
isolation, this work took the opposite stance, testing the hypothesis that
modelling the temporal structure of a night improves on stateless baselines. The
reasoning is grounded in the scoring rules themselves: the lightest stage is
defined largely by transitions, and the stage that follows it depends heavily on
what preceded it, so both are cases a memoryless classifier is poorly equipped to
resolve. The emphasis throughout was on robustness to clinic setup and fairness
across patient groups rather than accuracy on a single dataset.

Recurrent architectures for sleep-phase analysis were implemented and evaluated
against the stateless baselines on the same public databases and the same
protocols, so that the two studies could be read side by side rather than compared
across differing experimental choices. Performance was assessed both within a
database and across sleep centres, keeping the cross-setup question in view
throughout rather than treating it as an afterthought.

Taken with its stateless companion, the work supports the broader claim more
firmly than either half could alone: automatic sleep staging must be judged by how
well it transfers between clinics, not by in-domain accuracy, and adding temporal
context does not by itself resolve the transfer problem. This thesis contributes
the stateful half of that picture, and its methods build on the open-source
`sleepless` library so that both halves remain directly comparable.
