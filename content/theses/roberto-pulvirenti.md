---
title: "Evaluating Cross-Domain Adaptation Strategies for Foundation Models: A Study on Fluorescein Angiography"
author: "Roberto Pulvirenti"
level: "Master"
university: "Politecnico di Torino, MSc in Artificial Intelligence & Data Analytics"
date: 2025-04-01
slug: "roberto-pulvirenti"
cover: "images/covers/roberto-pulvirenti.png"
summary: >-
  Fluorescein angiography reveals retinal disease but is far less annotated than
  ordinary fundus photography. This thesis tested whether AI "foundation models"
  trained on fundus images can be adapted to angiography efficiently, including
  for grading uveitis inflammation with the Jules-Gonin Eye Hospital.
projects: ["uveitis"]
report: "https://www.idiap.ch/~aanjos/pdfs/theses/roberto-pulvirenti.pdf"
research_outputs:
  - "10.1109/isbi61048.2026.11515636"   # ISBI 2026 paper from this thesis
  - "anjos_mednet_2024"                          # the mednet software library
datasets:
  - name: "3rd APTOS Competition fluorescein angiography set (public)"
  - name: "Jules-Gonin (HOJG) uveitis fluorescein angiography set (private)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "Hôpital ophtalmique Jules-Gonin (HOJG), Lausanne"
    country: "Switzerland"
---

Fluorescein angiography is a workhorse retinal modality for visualising vascular
leakage and inflammation, but labelled angiography data is scarce because its
interpretation demands expert time, unlike the abundantly annotated colour fundus
photography that dominates ophthalmic datasets. Large pre-trained "foundation"
models promise to carry knowledge from data-rich modalities into data-poor ones,
which raised the question the thesis examined: can the representations captured by
retinal foundation models trained on colour fundus photography be adapted
efficiently to fluorescein angiography tasks?

Vision Transformers pre-trained at scale had shown strong results on colour fundus
photography, with RETFound trained on roughly a million such images and its lighter
RETFound Green variant on around seventy-five thousand, while parameter-efficient
tuning and self-supervised continual pre-training had cut adaptation costs in other
settings. What remained unclear was whether a fundus-photography prior actually
helps on angiography over a generic natural-image prior. Three hypotheses were put
to the test: that a related-domain retinal prior beats an ImageNet prior on
angiography, that low-rank adaptation matches full fine-tuning at a fraction of the
trainable parameters, and that self-supervised continual pre-training on angiography
improves cross-domain transfer.

Four backbones were compared, RETFound against its ViT-Large ImageNet baseline and
RETFound Green against its ViT-Small baseline, across eleven classification tasks on
two angiography datasets: the public 3rd APTOS competition set of 1,877 unique eyes
and a private Jules-Gonin set of 752 eyes covering four uveitis-related inflammatory
signs. Each backbone was adapted by full fine-tuning, by low-rank adaptation, and by
self-supervised continual pre-training with a Masked Autoencoder or Token
Reconstruction, and scored with AU-ROC, F1 and AU-IMCP. Outcomes depended on scale:
RETFound underperformed its ViT-Large baseline, whereas RETFound Green outperformed
its ViT-Small baseline and ranked best overall. Low-rank adaptation updated only one
to four percent of parameters while costing the large model just 0.93 percent against
full fine-tuning, though smaller models proved more sensitive to it. A Masked
Autoencoder step on unlabelled angiography lifted RETFound by 8.29 percent, while
Token Reconstruction reduced RETFound Green by 6.78 percent.

The three hypotheses fare differently, which is the substance of the answer. The
first is refuted as stated: a fundus-photography prior does not universally beat a
natural-image one, and specialising a model to the source modality can actively
cost performance on the target. The second holds, with a caveat about scale —
low-rank adaptation is close to free on the large backbone and a reasonable default
under data scarcity, but smaller models tolerate it less well. The third is
conditional rather than true or false: continued self-supervised pre-training on
unlabelled angiography helps or harms depending on the objective chosen, not on
whether it is applied. Taken together these say that what transfers is not domain
proximity but the kind of representation a pre-training objective leaves behind.
The main limits are using only the final frame of each sequence, which shrank the
effective sample to the 1,877 and 752 eyes above, and a heuristic rather than
exhaustive hyperparameter search. The work informs the group's continuing uveitis
collaboration with Jules-Gonin by identifying which adaptation strategies are worth
pursuing on scarce angiography data, and its central finding was published at ISBI
2026.
