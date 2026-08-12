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
  - "vanrijn_last_2026"
  - "10.1038/s41598-026-46069-w"
  - "10.1016/j.compbiomed.2025.110327"
  - "10.1109/cbms58004.2023.00301"
  - "10.1109/isbi61048.2026.11515636"
  - "anjos_mednet_2024"
---

<small>Cover: ultra-widefield fluorescein angiography of anterior uveitis showing
peripheral vascular leakage, from [Chi et al., PLOS ONE 2015](https://doi.org/10.1371/journal.pone.0122749),
used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).</small>

Uveitis is a leading cause of preventable blindness, and treating it well depends on
grading intraocular inflammation reliably. That inflammation is read from widefield
fluorescein angiography, a task that is slow and on which experienced clinicians often
disagree. With the Jules-Gonin Eye Hospital (HOJG) and partner clinics, my group builds
models that grade retinal inflammatory signs directly from angiography, aiming at scoring
that is reproducible, interpretable, and ready for the clinic.

## Major achievements

The work advanced from grading a single inflammatory sign to scoring the retina
comprehensively. We first showed that retinal vasculitis can be graded fully
automatically from angiographic time-lapses drawn straight from hospital imaging
devices, with no manual curation of the images: on 3,205 images from 242 eyes the
pipeline reached an F1 of 0.81 and an area under the curve of 0.86, against 0.57 and
0.66 for an intensity-based baseline. Moving from detection to grading was the harder
problem, because clinical severity is recorded on ordered categories in which confusing
adjacent grades matters far less than confusing the extremes. Training transformer
models against that ordinal structure, and scoring them with a measure that respects
it, we graded four signs of the posterior pole — vascular and capillary leakage,
macular oedema, and optic disc hyperfluorescence — across 40,987 images from 1,042
eyes. The models matched expert graders sign by sign and, averaged over signs,
marginally exceeded the agreement observed between the human experts themselves.

These components were assembled into **UveAI**, an end-to-end system combining six
specialised models, four for the posterior pole and two for the periphery, into one
inflammation score aligned with the semi-quantitative scale already used in the clinic.
Trained on 3,220 images from 644 eyes and tested against three further uveitis
specialists from different hospitals, its composite score tracked the reference grader
at a correlation of 0.96, above the 0.84 observed between the human experts, with a mean
area under the curve of 0.952 across the six signs; saliency analysis confirmed the
models attend to clinically meaningful structures rather than to acquisition artefacts.
The work leaves behind the largest annotated angiography dataset in uveitis to date and
the first automated scoring to span both the posterior pole and the periphery, with the
honest caveats that validation is so far single-centre, single-device, and anchored on
one senior grader. A parallel study of foundation models tempered hopes of easy reuse:
pretraining on a related eye modality helps only when the self-supervised objective
preserves representational diversity, and can otherwise collapse the model's attention
and actively harm transfer.
