---
title: "Towards Scalable Foundation Models for Sleep EEG and Polysomnography"
author: "Daniel Lutziger"
level: "Master"
university: "University of Zürich, Department of Informatics"
date: 2025-12-09
slug: "daniel-lutziger"
cover: "images/covers/daniel-lutziger.png"
summary: >-
  Sleep is diagnosed from all-night recordings, but models are usually built one
  task and one sensor setup at a time. This thesis built a reusable foundation
  model for sleep, pretrained on about 13,000 nights.
projects:
  - "sleep-medicine"
report: "https://seafile.ifi.uzh.ch/f/9951eb6cc9c64b0fa330/"
datasets:
  - name: "MESA, MASS, Sleep-EDF, SHHS and other public PSG cohorts (~13,000 subjects, ten cohorts)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
---

Diagnosing sleep disorders relies on polysomnography, the all-night recording of
brain, heart, breathing, and movement signals. Machine-learning models for this
data are usually trained one task at a time and for one sensor montage, which does
not scale to the variety of clinics and questions in sleep medicine. Foundation
models, large encoders pretrained once and reused across many tasks, have
reshaped vision and language, which raised the question this thesis pursued:
can scalable foundation models be built for sleep EEG and polysomnography that
transfer across tasks and montages?

Most earlier sleep models were both task-specific and montage-specific, while
self-supervised pretraining was only beginning to reach the field. The hypothesis
was that a single large encoder, pretrained without labels on diverse
polysomnography, could learn representations general enough that new tasks need
only a lightweight head rather than a model trained from scratch.

A set-then-sequence Transformer encoder was pretrained contrastively on about
13,000 subjects drawn from ten public cohorts, then frozen while lightweight
sequence heads were trained on a held-out SHHS cohort for two downstream tasks,
sleep staging and sleep-apnea detection. The frozen encoder reached 76.2 percent
balanced accuracy for sleep staging from brain-activity signals on SHHS and kept
competitive apnea detection, and a channel analysis showed that respiratory
signals are essential for apnea but of limited value for staging.

The experiments indicate that large polysomnography foundation models can indeed
be reused across tasks and montages, though how much they help depends on the
pretraining and the downstream setup. The work is a concrete step toward scalable,
general-purpose models for sleep medicine, on which later theses in the group can
build.
