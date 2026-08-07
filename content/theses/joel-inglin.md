---
title: "Stability and Accuracy of Radiomic Features in Medical Image Classification"
author: "Joël Inglin"
level: "Master"
university: "University of Zürich, Department of Informatics"
date: 2024-12-03
slug: "joel-inglin"
cover: "images/covers/joel-inglin.png"
summary: >-
  A radiomic biomarker is only useful if it does not change every time the scanner
  settings do. This thesis looked for image features that stay both stable and
  informative across acquisition protocols.
projects:
  - "tuberculosis-radiology"
report: "https://seafile.ifi.uzh.ch/f/4a5dbaf45523404d860d/"
research_outputs:
  - "anjos_mednet_2024"
datasets:
  - name: "Anthropomorphic phantom CT (varied scanner settings) and a patient CT set"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
---

Radiomics turns a medical image into a set of quantitative biomarkers, but the
promise fails quietly when those numbers shift as soon as the acquisition protocol
changes. Many traditional radiomic features are exactly that unstable, which
undermines reproducibility and makes results hard to move between sites. The thesis
set out to find features that are at once stable across acquisitions and genuinely
discriminative.

Two families of features were put forward as candidates to enrich the radiomic
toolbox: Gabor features and deep features from pre-trained networks. The hypothesis
was that these could match or beat traditional hand-crafted features on the two
properties that matter together, stability under changing scanner settings and
discriminative power on real disease.

Stability was quantified with the intraclass correlation coefficient on
anthropomorphic phantom CT acquired under varied scanner settings, and
discriminative power with the AUC of models trained on real patient data. The
single highest-ranked features turned out to be traditional ones, yet a substantial
number of Gabor and deep features possessed better radiomic qualities than most
traditional features, and on the external test set the deep-feature models
performed best overall.

The thesis concluded that learned features are a promising route to robust,
transferable imaging biomarkers, especially where models must hold up on data from
unseen scanners. It provides a principled, phantom-based way to weigh stability
against discriminative power when choosing which features to trust.
