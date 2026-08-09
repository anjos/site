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

<small>Cover: infrared plantar thermography of both feet, the kind of routine signal used to
flag diabetic-foot risk before ulceration, from Renero-C, *Diabetic Foot & Ankle*
2017;8:1361298 ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).</small>

Epidemiology is ultimately about anticipating where the next case, or the next complication,
will come from. This strand applies machine learning to the everyday data of clinical care —
routine measurements, chest radiographs, and evolving patient-contact networks — to flag who
is most at risk and to detect disease earlier, so that prevention can be targeted before harm
is done. The common thread is a shift from reacting to cases toward getting ahead of them.

## Major achievements

Much of the work is about spotting high-risk patients in data a clinic already collects. From
250 people with diabetes described by 54 routine risk factors — the kind an attendant or the
patient can record on a questionnaire, with no clinical examination required — an unsupervised
competitive-neuron-layer method separated the cohort into risk groups without any labelled
outcomes; against a nurse-annotated validation cohort of 73 it reached 90% accuracy at 100%
specificity and 71% sensitivity, so that those it does flag for priority follow-up to prevent
diabetic-foot complications can be acted on with confidence. The same instinct, anticipate
rather than react, drove **STM-GNN**, a space-time-and-memory graph neural network predicting
which patients are at risk of multidrug-resistant hospital-acquired infection as contact
networks evolve. Coupling a heterogeneous graph over patients, beds and rooms with a recurrent
memory of each patient's colonisation history, and feeding the two back into one another, it
reached 0.84 area under the curve on a real and deliberately sparse infection-control cohort,
the most balanced performance of any method tried, classical baselines and other temporal graph
networks alike.

The other strand is earlier detection, and a critical synthesis of how artificial intelligence
now reads chest X-rays for tuberculosis. Computer-aided detection has reached accuracy on a par
with human radiologists, with areas under the curve of roughly 0.83 to 0.94 in triage studies,
which led the World Health Organization to conditionally recommend it in place of a human reader
for those aged fifteen and over; used this way it is projected to cut diagnostic costs by
roughly a fifth to a third. Our review weighed that promise against its conditions: accuracy
drifts with age, body mass, HIV status and smear-negative disease, decision thresholds must be
recalibrated locally rather than taken from the vendor, evidence in children is absent, and
rapid version churn means a product's published accuracy may not describe the version actually
deployed. The conclusion for elimination is a measured one: automated screening can genuinely
widen access to fast, consistent diagnosis, but only with local calibration, independent
external validation, and deliberate attention to equity will it help end tuberculosis rather
than entrench its disparities.
