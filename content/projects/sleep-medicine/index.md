---
title: "Neurophysiology — Sleep Medicine"
weight: 12
cover: "images/covers/samuel-michel.png"
summary: >-
  Generalisable, reproducible automatic sleep-stage classification from
  polysomnography, working toward foundation models for sleep medicine.
research_outputs:
  - "anjos_sleepless_2017"
---

Polysomnography is the gold standard for diagnosing sleep disorders, but staging the
recordings by hand is slow, tedious, and surprisingly inconsistent: two experts scoring the
same night often disagree, and every sleep centre uses its own sensor setup. Automating the
staging promises faster, more reliable, and fairer diagnosis. Where we would like to go is
broader still, toward foundation models for sleep medicine that hold up across clinics,
sensors, and populations.

## Major achievements

We studied stateless models for sleep-stage detection and looked closely at how they
generalise from one clinic to another. One finding stuck with us: the model that performed
best within a single database was not the one that generalised best across setups, a
reminder that peak in-domain accuracy is not the same as robust deployment.

Those methods are released through the open-source `sleepless` library, with preset
configurations that reproduce the published results, so the cross-clinic comparisons can be
rerun rather than taken on trust. The project is growing, and further supervised theses and
outputs will be attached here as they mature.

Evaluation uses public polysomnography databases (Sleep-EDF ST/SC, MASS SS3).
