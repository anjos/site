---
title: "Sleep Spindle Detection from Electroencephalography via Sleep Foundation Models"
author: "Alexis Bollengier"
level: "Master"
university: "VUB, Brussels Faculty of Engineering (BRUFACE)"
date: 2026-08-13
slug: "alexis-bollengier"
cover: "images/covers/alexis-bollengier.png"
summary: >-
  Sleep spindles are second-long bursts in the EEG whose shape tracks memory and
  brain health, and counting them by hand does not scale. This thesis asked whether
  a large pretrained sleep model can be made to mark each spindle's exact start and
  end, and found that the pretrained part supplies context while a purpose-built
  frequency view supplies the precision.
projects: ["sleep-medicine"]
report: "https://www.idiap.ch/~aanjos/pdfs/theses/alexis-bollengier.pdf"
datasets:
  - name: "MASS-SS2 polysomnography with the OPA single-scorer spindle re-annotation (private)"
  - name: "MODA consensus spindle annotations over MASS (public); used for zero-shot transfer"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "Vrije Universiteit Brussel (VUB)"
    country: "Belgium"
  - name: "Assistance Publique – Hôpitaux de Paris (AP-HP)"
    country: "France"
---

Sleep spindles are the brief oscillatory bursts the thalamocortical circuit produces
during non-rapid-eye-movement sleep, and they are not merely decorative: they
coordinate with slow oscillations and hippocampal ripples to stabilise memory, and
their characteristics shift measurably in schizophrenia, in major depressive
disorder and in obstructive sleep apnoea. Turning that into a usable biomarker
requires each individual event to be found and its onset and offset placed
precisely, across enough nights to say something about a population. Expert
annotation does neither, being slow and inconsistent exactly where boundaries are
concerned. The question this thesis pursued is whether a sleep foundation model,
pretrained on large collections of polysomnography, can be adapted to locate events
at a resolution far finer than the one it was trained to represent.

Most existing spindle detectors are built for that single task and depend on expert
annotation to learn their representations at all, whereas foundation models such as
SleepFM and SleepGPT learn reusable physiology first and are specialised afterwards.
What that literature had not settled is a resolution mismatch. SleepFM compresses
several seconds of EEG into one token embedding, and raising the output resolution
after tokenisation does not recover local detail the token never preserved. Two
hypotheses followed. The first is that the pretrained temporal representation alone
does not retain enough localisation to place event boundaries. The second is that a
task-specific frequency view, computed on the same token grid, supplies the
fine-grained evidence the pretrained stream lacks.

The proposed detector poses the problem as dense prediction: a frozen SleepFM encoder
provides temporal context, a parallel branch computes a Morlet scalogram read out in a
structure that preserves spectral detail below the token scale, residual
cross-attention fuses the two, and a dense decoder reconstructs sample-resolution
estimates of the spindle mask, the boundary offsets and a three-way temporal class.
Training and evaluation used the MASS-SS2 archive, nineteen participants and 155.7
hours over three EEG channels resampled to 128 Hz, re-annotated for spindles by a
single sleep physician to yield 29,573 events, split subject-wise so no recording
crosses subsets. On the held-out test set of 5,335 events the detector reaches an
event-level F1 of 0.7950 at an overlap threshold of 0.2, with precision 0.7914 and
recall 0.7987, falling to 0.7575 under the much stricter threshold of 0.5. Matched
events overlap the reference by a median of 0.78, with the predicted onset a median
of 8 ms late and the offset 31 ms early. Under a common protocol on the same split
the architecture leads both published baselines, BLAST at 0.7811 and SUMO at 0.7675.
Two ablations qualify that result rather than support it. The frozen foundation
encoder is matched by a plain Transformer trained from scratch, 0.7950 against
0.7954, so at this scale pretraining contributes context and not accuracy. It is the
Morlet representation that carries the gain, and it pulls furthest ahead of the
short-time Fourier and learned-filterbank alternatives precisely at the strict
threshold where boundary placement decides the score.

The evidence supports both hypotheses, and the transferable lesson is that adapting a
sleep foundation model to dense event detection means preserving information below the
token scale rather than trying to recover it afterwards. That advantage does not
survive the move off home ground. Transferred without retraining to the 166-subject
MODA set, the model reaches 0.6531 while SUMO and BLAST both transfer better, so
leading in domain is not the same property as generalising. The sharpest finding
concerns labels rather than architecture: trained on the physician's annotations the
model transfers to the MODA consensus at 0.6531, whereas training on the public
MASS-SS2 scorers reaches only 0.2390, 0.2184 and 0.0964 depending on which scorer is
used, which means published detector comparisons are confounded by annotation
compatibility as much as by design. Two limits bound all of this. The test set is
three participants scored by one expert, so residual disagreements cannot be
adjudicated, and MODA is itself derived from the MASS archive, so the transfer
experiment varies population and annotation protocol rather than acquisition. The
work leaves a concrete next step for the group, namely a hierarchical time-frequency
foundation model that keeps local temporal and spectral structure during pretraining
instead of reconstructing it per task.
