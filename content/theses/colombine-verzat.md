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
published logistic regression was first reproduced and then given something it
had lacked, an unbiased evaluation protocol separating the data used to fit the
model from the data used to judge it; on that footing the baseline reached an
area under the curve of 0.65 ± 0.04. Two non-linear models were then trained and
compared against it. Both matched the baseline and neither significantly beat it.
The reason is visible in the data rather than the models: the cohort is severely
imbalanced, with adverse events numbering in the tens against thousands of
patients, and those who suffered them do not separate from those who did not in
the recorded clinical variables.

The hypothesis was not supported: added model capacity bought nothing, because
the limitation lies in the data and not in the linearity of the baseline. The
answer to the opening question is accordingly negative — reliable advance
warning of adverse events is not achievable from this cohort — and the useful
part of that answer is its diagnosis, which tells the designers of the next
study what to change: a larger and less imbalanced cohort, described by richer
explanatory variables than routine clinical records provide. The reproducible
database interface and evaluation package built along the way mean the next
attempt starts from a verified baseline rather than a published number.
