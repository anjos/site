---
title: "Machine Learning for Adverse-Event Detection in Latent Tuberculosis Treatment"
author: "Colombine Verzat"
level: "Master"
university: "UniDistance, Brig (Master in AI, jointly with Idiap)"
date: 2020-08-01
slug: "colombine-verzat"
cover: "images/covers/thesis-colombine-verzat.png"
summary: >-
  Preventive tuberculosis therapy works, but its side effects make patients stop.
  This thesis asked whether the patients most at risk of those side effects can be
  spotted in advance from routine clinical data.
projects:
  - "tuberculosis-epidemiology"
report: "https://publications.idiap.ch/attachments/reports/2020/Verzat_Idiap-Com-02-2020.pdf"
datasets:
  - name: "Clinical cohort of 6,485 latent-TB patients (private)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "Federal University of Rio de Janeiro"
    country: "Brazil"
---

About a quarter of the world's population carries a latent tuberculosis infection,
which has a 10 to 15 percent chance of progressing to active, contagious disease.
Preventive therapy is central to the World Health Organization's elimination
goals, but it can cause adverse events serious enough to make patients abandon
treatment. The thesis asked whether the patients most likely to suffer those
adverse events could be identified ahead of time from their clinical data, so that
therapy could be better targeted.

An earlier study by Campbell and colleagues had modelled this cohort with logistic
regression. The hypothesis here was that non-linear machine-learning models,
better able to capture complex interactions, might improve on that baseline and
turn adverse-event prediction into something clinically actionable.

Working from a clinical dataset of 6,485 treated latent-TB patients, the
logistic-regression baseline was first reproduced, reaching an AUC of 0.65 plus or
minus 0.04. Non-linear models were then trained and compared against it. They
matched the baseline but did not significantly beat it, and inspection showed why:
patients with and without adverse events overlap heavily in the feature space,
leaving little separable signal.

The thesis concluded that reliable adverse-event detection is not achievable from
this dataset alone, and that progress would require a larger, less imbalanced
cohort described by richer explanatory variables. The clear-eyed negative result,
with its baseline and its diagnosis of why prediction is hard, is itself a useful
guide for the design of future studies.
