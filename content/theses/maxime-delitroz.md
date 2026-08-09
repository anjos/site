---
title: "Automated Segmentation of Developing Motor Neurons in Fluorescence Microscopy"
author: "Maxime Délitroz"
level: "Master"
university: "EPFL"
date: 2022-08-30
slug: "maxime-delitroz"
cover: "images/covers/maxime-delitroz.png"
summary: >-
  The shape of a neuron carries clues to disease. This thesis automated the
  segmentation of motor neurons in microscopy so that the morphological changes of
  amyotrophic lateral sclerosis can be studied at scale.
projects: []                     # ALS project retired; thesis kept, intentionally unattached
datasets:
  - name: "High-content fluorescence microscopy of iPSC-derived motor neurons (private)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
---

The shape of a cell is a phenotypic marker closely tied to its physiological
state, and in amyotrophic lateral sclerosis, a fatal disease marked by the loss of
motor neurons, subtle morphological changes in the neurites carry information about
disease status. Studying those changes means segmenting motor neurons across large
volumes of high-content fluorescence microscopy, far more than can be traced by
hand, which raised the question of how to automate that segmentation reliably.

Digital tracing of neuronal morphology is a long-standing and still difficult
problem: the most popular tools remain semi-automatic and do not scale, while fully
supervised deep networks demand large amounts of labelled training data whose
manual creation is the real bottleneck. The hypothesis was that a two-step
strategy could sidestep that cost, first segmenting with a classical
image-processing pipeline, then training a convolutional network on the masks that
pipeline produces, so that the network generalises beyond its imperfect teacher
without any hand-drawn ground truth.

Both pipelines were built and evaluated on the high-content microscopy dataset. The
classical pipeline supplied the automatic labels, and the fully convolutional
network trained on them did not merely reproduce its teacher: it learned to correct
a substantial share of the first pipeline's errors, which is the outcome the
strategy depends on, since a network that only imitated its imperfect labels would
have no reason to exist. Both methods outperformed the segmentation tools commonly
applied to this kind of imagery, with the network ahead of the classical pipeline
that trained it.

The hypothesis is confirmed: a network bootstrapped from a classical pipeline both
removes the manual-labelling barrier and improves on the labels it was given, so
the annotation bottleneck is not the hard constraint it appears to be. The answer
to the opening question is accordingly that motor-neuron segmentation can be
automated at the volumes this research requires, without hand-drawn ground truth,
provided a classical pipeline good enough to teach from can be constructed first.
The result is a practical basis for the quantitative, morphology-based study of
motor neurons in ALS research.
