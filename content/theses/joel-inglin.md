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

Stability was quantified on anthropomorphic phantom CT acquired under varied
scanner settings, where the same physical object is imaged repeatedly so that any
change in a feature's value can only come from the acquisition; discriminative
power was measured separately as the area under the curve of models trained on
real patient data. The result splits cleanly. The single highest-ranked features
were traditional ones, so the hypothesis fails at its strongest reading. Yet a
substantial number of Gabor and deep features possessed better combined radiomic
qualities than most traditional features, and the decisive test — models applied
to the external phantom data, standing in for an unseen scanner — put the
deep-feature models ahead of every alternative.

The hypothesis is thus confirmed in the sense that matters. Learned features do
not win every individual comparison, but they hold their value when the
acquisition changes, which is the condition under which a biomarker has to
survive to be clinically useful at all. The answer to the opening question is
that features stable *and* discriminative do exist, and that they are more often
learned than hand-designed. Beyond the ranking itself, the thesis leaves a
principled, phantom-based procedure for weighing stability against discriminative
power, so that future studies can choose features on evidence rather than on
convention.
