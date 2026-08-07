---
title: "Ophthalmology — Uveitis"
weight: 10
cover: "images/covers/uveitis-fa-leakage.jpg"
summary: >-
  AI-assisted grading of intraocular inflammation in uveitis from retinal
  fluorescein angiography, developed with the Jules-Gonin Eye Hospital.
partners:
  - "Hôpital ophtalmique Jules-Gonin (HOJG), Lausanne"
  - "University Hospital of Grenoble Alpes"
  - "Luzerner Kantonsspital"
research_outputs:
  - "10.1038/s41598-026-46069-w"
  - "10.1016/j.compbiomed.2025.110327"
  - "10.1109/cbms58004.2023.00301"
  - "10.1109/isbi61048.2026.11515636"
  - "anjos_mednet_2024"
---

Uveitis is a leading cause of preventable blindness, and treating it well depends on
grading intraocular inflammation reliably. That inflammation is read from widefield
fluorescein angiography, a task that is slow and on which experienced clinicians often
disagree. With the Jules-Gonin Eye Hospital (HOJG) and partner clinics, my group builds
models that grade retinal inflammatory signs directly from angiography, aiming at scoring
that is reproducible, interpretable, and ready for the clinic.

## Major achievements

We began with a single sign, showing that retinal vasculitis can be graded fully
automatically from real-world fluorescein-angiography time-lapses: on 3,205 images from
242 eyes at Jules-Gonin, the model reached an F1 of 0.81 and an AUC of 0.86, comparable
to published state of the art and far above an intensity-based baseline. We then moved
from one sign to many, using transformer models to grade vascular leakage, capillary
leakage, macular edema, and optic disc hyperfluorescence together. Sign by sign the
models matched expert graders (F1 up to 0.87, ordinal-classification index 1-OCI up to
0.89) and, on average, met or exceeded the agreement between the human experts themselves
(model mean 1-OCI 0.87 against 0.83 between graders), with saliency maps confirming they
read clinically relevant structures rather than artefacts.

These pieces came together in **UveAI**, a modular end-to-end pipeline that combines six
transformer models into a single ASUWOG-aligned inflammation score spanning the posterior
pole and the periphery. Benchmarked on 3,220 angiograms from 644 eyes, with an independent
test set graded by three additional uveitis specialists, its total inflammation score
tracked the expert reference at a Pearson correlation of 0.96 and it reached a mean AUC of
0.952 across the six signs, approaching inter-grader agreement while staying interpretable.
Alongside this we asked how far foundation models pretrained on other eye-imaging
modalities transfer to angiography, and found that specialising a model to one modality
can help but can also quietly hurt, which tempers hopes for off-the-shelf reuse. Together
the work shows that standardised, clinic-ready angiographic scoring of uveitis is now
within reach, provided models are validated against real inter-grader variability rather
than a single reader.

*Cover: ultra-widefield fluorescein angiography of anterior uveitis showing
peripheral vascular leakage, from [Chi et al., PLOS ONE 2015](https://doi.org/10.1371/journal.pone.0122749),
used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*
