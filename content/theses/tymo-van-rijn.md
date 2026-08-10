---
title: "Beyond the Last Frame: Temporal Deep Learning for Automated Grading of Retinal Inflammation in Fluorescein Angiography"
author: "Tymo van Rijn"
level: "Bachelor"
university: "Hogeschool Rotterdam"
date: 2026-06-21
slug: "tymo-van-rijn"
cover: "images/covers/tymo-van-rijn.png"
summary: >-
  Fluorescein angiography films the eye for several minutes, yet the group's
  grading model was reading only the final photograph. This thesis taught it to
  watch the whole sequence, lifting grading accuracy where the disease is defined
  by how it changes over time.
projects: ["uveitis"]
report: "https://www.idiap.ch/~aanjos/pdfs/theses/tymo-van-rijn.pdf"
research_outputs:
  - "anjos_mednet_2024"                    # the mednet library, extended here
datasets:
  - name: "3rd APTOS Competition fluorescein angiography set (public)"
  - name: "Jules-Gonin (HOJG) uveitis fluorescein angiography set (private); prepared for external validation, not run"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "Hogeschool Rotterdam"
    country: "Netherlands"
  - name: "Hôpital ophtalmique Jules-Gonin (HOJG), Lausanne"
    country: "Switzerland"
---

Fluorescein angiography is not a photograph but a film: a fluorescent dye is
injected into the bloodstream and the camera keeps shooting for several minutes
while the dye transits the retina. Clinicians separate the hyperfluorescence
patterns precisely by how they behave over that interval, since leakage spreads
and blurs, pooling fills a cavity with a sharp border, staining brightens without
expanding, and a window defect appears early and stays geographically fixed. The
group's existing grading pipeline nonetheless collapsed each examination to a
single late frame, reaching a macro ROC-AUC of 0.82 on multiclass
hyperfluorescence typing while discarding the very evolution that defines several
of the classes it was asked to name. The question the thesis pursued is whether
reading the whole sequence recovers that discarded signal.

Earlier work in the group had established the single-frame reference this thesis
had to beat, adapting retinal foundation models to angiography and settling on a
compact RETFound Green Vision Transformer. What that line of work had not
attempted was sequence modelling over an entire examination, and the wider
literature offered temporal encoding strategies whose cost and interpretability
were untested on shared research infrastructure. Two hypotheses followed. The
first is that the temporal ordering of frames carries diagnostic information the
last frame throws away, recoverable by passing per-frame embeddings through a
lightweight recurrent model. The second, sharper hypothesis is that this only
works if the image backbone is allowed to adapt to the sequence task, so that
sequencing embeddings from a frozen backbone would not be enough.

Work was carried out on the public 3rd APTOS angiography benchmark, deliberately
chosen over clinical data so the method would remain reproducible and publishable.
The dataset carries no structured timing, so elapsed time was recovered by an
OCR pipeline benchmarked against 150 hand-checked frames, reaching 96 percent
accuracy and yielding 32,834 validated timestamps together with a frame
eligibility filter. Phase boundaries were then calibrated from the data itself
with a linear discriminant probe, landing at 103 and 518 seconds and outperforming
the textbook clinical convention on every separability metric. Twelve frames, four
per phase, were passed through the RETFound Green backbone into a two-layer GRU,
with the existing classification head left untouched so that any gain would be
attributable to the temporal block alone. With the backbone frozen, no temporal
aggregation reliably beat a single well-chosen frame, a genuine negative result.
Fine-tuning backbone and GRU jointly improved every graded task, raising macro
ROC-AUC from 0.82 to 0.87, with the largest gains exactly where behaviour over
time is diagnostic: pooling from 0.76 to 0.83 and window defect from 0.78 to 0.85.
A separate controlled study found that reducing embedding dimensionality by
principal component analysis before the sequence model helped nowhere, and that
branch was dropped.

The evidence supports both hypotheses, and the second is the transferable one:
temporal information is real, but it is only reachable by co-adapting the image
backbone and the sequence model together, so bolting a recurrent layer onto frozen
features buys nothing. Two limits bound the claim. The results rest on one public
benchmark, and external validation on the Jules-Gonin clinical set of 543 patients
was prepared and scoped but could not be run inside the internship window, because
clearance for identifiable patient data takes longer than six months. Timing itself
was reconstructed rather than measured, a weakness that disappears on hospital data
where native timing metadata is recorded. The work left the group more than a
number: the temporal pipeline was integrated into the MedNet research framework
with tests and continuous integration rather than kept as a private script, its
findings were accepted as an abstract at the Swiss AI in Medicine Initiative
meeting in June 2026, and the clinical validation and an explicit time-embedding
variant were handed over as the two next steps.
