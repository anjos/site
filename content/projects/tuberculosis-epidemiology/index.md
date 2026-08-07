---
title: "Epidemiology — Anticipating Risk"
weight: 35
cover: "images/covers/diabetic-foot-thermogram.jpg"
summary: >-
  Machine learning on routine clinical records, chest radiographs, and
  patient-contact networks to flag who is most at risk — from diabetic-foot
  complications to drug-resistant infection to tuberculosis.
partners:
  - "University of Geneva"
  - "Polytechnic University of Leiria"
  - "Federal University of Rio de Janeiro"
  - "State University of Campinas (UNICAMP)"
  - "Federal University of Lavras"
research_outputs:
  - "10.1007/978-3-031-95838-0_16"
  - "10.5588/ijtld.22.0687"
  - "10.1016/j.compbiomed.2020.103744"
---

Epidemiology is ultimately about anticipating where the next case, or the next complication,
will come from. This strand applies machine learning to the everyday data of clinical care —
routine measurements, chest radiographs, and evolving patient-contact networks — to flag who
is most at risk and to detect disease earlier, so that prevention can be targeted before harm
is done. The common thread is a shift from reacting to cases toward getting ahead of them.

## Major achievements

Much of the work is about spotting high-risk patients in data a clinic already collects. From
250 people with diabetes, each described by 54 routine clinical risk factors, an unsupervised
competitive-neuron-layer method separated patients into risk groups with no labelled outcomes;
on a nurse-annotated validation cohort of 73 it reached 90% accuracy at 100% specificity,
singling out those who most need priority follow-up to prevent diabetic-foot complications. The
same instinct, anticipate rather than react, drove **STM-GNN**, a space-time-and-memory graph
neural network that predicts which patients are at risk of multidrug-resistant hospital-acquired
infection as contact networks evolve. By coupling a graph over patient-and-environment
interactions with a recurrent memory of each patient's colonisation history, it reached 0.84
AUROC on a real infection-control dataset and gave the most balanced performance of any method
tried, ahead of both classical baselines and other temporal graph networks.

The other side of the work is earlier detection. We contributed a critical synthesis of how
artificial intelligence now reads chest X-rays for tuberculosis: computer-aided detection has
reached accuracy comparable to human radiologists, with areas under the curve of 0.85 to 0.94
in triage studies, which led the World Health Organization to conditionally recommend it in
place of a human reader, and used this way it can cut diagnostic costs by roughly a fifth to a
third. Our review weighed that promise against its conditions — performance drifting between
populations, thresholds needing local recalibration, and unequal access threatening to widen
rather than close global gaps. The conclusion for elimination is a measured one: automated
screening can genuinely expand access to fast, consistent diagnosis, but only with local
calibration, external validation, and attention to equity will it help end tuberculosis rather
than entrench its disparities.

<small>Cover: infrared plantar thermography of both feet, the kind of routine signal used to
flag diabetic-foot risk before ulceration, from Renero-C, *Diabetic Foot & Ankle*
2017;8:1361298 ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).</small>
