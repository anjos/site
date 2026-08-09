---
title: "Angiology — Fibromuscular Dysplasia"
weight: 45
cover: "images/covers/fmd-string-of-beads.jpg"
summary: >-
  Machine learning for the characterisation and diagnosis of fibromuscular
  dysplasia, in collaboration with CHUV's angiology department.
partners:
  - "CHUV, Lausanne University Hospital"
---

<small>Cover: the diagnostic "string-of-beads" renal angiogram of medial fibromuscular
dysplasia, from Plouin et al., *Orphanet Journal of Rare Diseases* 2007;2:28
([CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)).</small>

Fibromuscular dysplasia (FMD) is an under-recognised arterial disease that is not
caused by atherosclerosis. It can lead to stenosis, aneurysm, and dissection,
most often in younger women, and because it is easy to miss, the diagnosis is
frequently delayed. Together with the angiology department at CHUV, we are
developing machine-learning methods to help characterise and diagnose it.

## Major achievements

The collaboration's first phase asked whether three-dimensional convolutional
networks can detect FMD at all from contrast-enhanced angiography, and answered
with useful caution. Working from a cohort of fewer than 200 patients, we found
that most standard remedies for scarce data — patch-based training, contrastive
pre-training, and treating both kidneys as a single sample — failed to converge
at all. Only generating one sample per kidney and stripping away non-vascular
structures using prior anatomical knowledge produced a model with genuine
signal. Because a diagnosis has to be justifiable, we paired the classifier with
volumetric saliency mapping and extended an established faithfulness measure to
three dimensions, so the explanations could themselves be tested rather than
taken on trust. A control experiment showed how thin the margin was: adding a
set of persistently misclassified control scans pushed performance back to
chance, which located the difficulty in the data and the preprocessing rather
than in the architecture.

That diagnosis pointed straight at the next step, and it proved correct.
Restricting the model to the renal arteries — segmenting the vasculature first
and classifying only what remains — raised the area under the curve from 0.849,
for a three-dimensional network trained from scratch on the whole region, to
0.900 across 126 angiography volumes under five-fold cross-validation, with
average precision improving from 0.774 to 0.875. Anatomical priors, in other
words, do work that would otherwise demand far more data. A vascular foundation
model used as a frozen feature extractor brought no improvement over training
from scratch, a useful negative result at a moment when such models are widely
assumed to help. The project remains at an early stage, and we say so plainly:
the cohorts are small enough that most of these differences fall short of
statistical significance, and lesion-level annotation is the obvious
prerequisite for the next advance.
