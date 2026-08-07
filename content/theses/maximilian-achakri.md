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

Working from a cohort of 126 contrast-enhanced CTA volumes focused on the renal
arteries, three complementary approaches were evaluated, ranging from a baseline
3D convolutional network trained from scratch for binary abnormality
classification to variants that presegment the vasculature before classifying it.
The convolutional architectures detected arterial abnormalities reliably despite
the limited data, and focusing the model on the presegmented arteries improved
its performance.

The thesis showed that deep learning can flag FMD-related renal-artery
abnormalities from CTA even with small cohorts, and that concentrating the model
on the segmented arteries rather than the whole scan is what makes that possible.
It carries the FMD collaboration a step further toward a usable diagnostic aid,
complementing the group's earlier, interpretability-focused work on the disease.
