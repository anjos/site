---
title: "Towards Computer-Aided Diagnosis of Fibromuscular Dysplasia: Abnormality Detection in the Renal Artery Using Deep Learning"
author: "Maximilian Achakri"
level: "Master"
university: "University of Zürich, Department of Informatics"
date: 2025-12-02
slug: "maximilian-achakri"
cover: "images/covers/maximilian-achakri.png"
summary: >-
  Fibromuscular dysplasia shows up as subtle abnormalities in the arteries and is
  easily missed. This thesis trained deep-learning models to detect them in
  renal-artery CT angiography, from a cohort of 126 scans.
projects:
  - "fibromuscular-dysplasia"
report: "https://www.idiap.ch/~aanjos/pdfs/theses/maximilian-achakri.pdf"
datasets:
  - name: "126 contrast-enhanced renal-artery CTA volumes (clinical, not public)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "University of Zürich"
    country: "Switzerland"
  - name: "CHUV, Lausanne University Hospital"
    country: "Switzerland"
---

Fibromuscular dysplasia (FMD) is an under-recognised, non-atherosclerotic disease
of the arteries that manifests as subtle abnormalities, from the tell-tale
string-of-beads to stenosis, aneurysm, dissection, and tortuosity. Many patients
stay asymptomatic until a serious event, and the signs are easy to overlook on
imaging. Computed tomography angiography (CTA) is a standard way to look for them,
which raised the question this thesis pursued: can deep learning detect
FMD-related abnormalities in the renal arteries from CTA, to support
computer-aided diagnosis?

Because the abnormalities are subtle and the disease is uncommon, automated
detection is hard, and it is made harder still by the small annotated cohorts that
such a rare condition affords. Earlier computer-aided work rarely targeted FMD
specifically. The hypothesis was that three-dimensional convolutional networks,
helped by first isolating the arteries, could flag abnormalities reliably even
from a modest dataset.

Working from a cohort of 126 contrast-enhanced CTA volumes cropped to the renal
region, three progressively more informed pipelines were compared under five-fold
cross-validation: a baseline 3D convolutional network trained from scratch, the
same network fed only presegmented vessels, and a frozen vascular foundation model
used as a feature extractor. The baseline reached an area under the curve of
0.849 ± 0.018. Presegmenting the vasculature raised this to 0.900, with average
precision improving from 0.774 to 0.875 and accuracy from 0.746 to 0.831. The
foundation model, by contrast, matched the baseline at 0.851 and did not approach
the segmentation-based pipeline. Consistent mild overfitting was observed
throughout, and with only five folds most differences fall short of statistical
significance.

The hypothesis is supported in direction but not yet in strength. Deep learning
does detect FMD-related abnormalities from modest cohorts, and isolating the
arteries first is what makes the difference — the gain is best explained as
anatomical inductive bias, since restricting the field of view removes the
contextual confounders a small dataset invites a model to exploit. The negative
half of the answer is equally useful: a pretrained vascular foundation model
brought no benefit over training from scratch, so supplying vessel information
directly beat inheriting it. The honest verdict is a promising direction on
evidence too thin to be conclusive, with lesion-level annotation identified as
the prerequisite for the next step.
