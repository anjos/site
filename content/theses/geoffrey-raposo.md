---
title: "Active Tuberculosis Detection from Frontal Chest X-ray Images"
author: "Geoffrey Raposo"
level: "Master"
university: "UniDistance, Brig (Master in AI, jointly with Idiap)"
date: 2023-02-02
slug: "geoffrey-raposo"
cover: "images/covers/geoffrey-raposo.png"
summary: >-
  Tuberculosis is often diagnosed from chest X-rays where specialists are scarce.
  This thesis built an interpretable, generalisable way to detect it by reading
  radiological signs rather than scoring the image directly.
projects:
  - "tuberculosis-radiology"
report: "http://publications.idiap.ch/attachments/reports/2021/Raposo_Idiap-Com-01-2021.pdf"
research_outputs:
  - "raposo_pulmonary_2022"
  - "anjos_mednet_2024"
datasets:
  - name: "Montgomery County, Shenzhen, Indian, and TBX11K chest X-ray sets (all public)"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
  - name: "Federal University of Rio de Janeiro"
    country: "Brazil"
---

Tuberculosis remains one of the leading causes of death from a single infectious
agent, and in the high-burden regions that suffer most, trained readers are
scarce. The chest X-ray is therefore central to diagnosis, and in 2021 the World
Health Organization accepted computer-aided detection in place of a human reader
for digital images. That endorsement raised a practical question: can pulmonary
tuberculosis be detected from a chest X-ray in a way that both generalises across
populations and remains interpretable to the clinician who has to act on it?

Most published systems score tuberculosis directly from the pixels, an approach
that tends to generalise poorly when trained on the modest amount of public
tuberculosis imagery and offers little insight into its own reasoning. The
hypothesis explored here was that routing the decision through the standard
radiological signs a radiologist looks for would recover both properties, giving
an interpretable intermediate representation that transfers better across
datasets.

A model was pre-trained on tens of thousands of chest X-rays annotated with
radiological signs, and a simple linear classifier then predicted the diagnosis
from those signs. On three public datasets the indirect approach reached
state-of-the-art performance, with test AUCs of 0.97 on Montgomery County, 0.90
on Shenzhen, and 0.93 on the Indian set, rising to 0.98, 0.98, and 0.93 when more
signs were made available. An analysis of sign importance showed that it is the
combination of signs, rather than any single one, that makes detection reliable.

The thesis established that interpretable, sign-based detection can match direct
image scoring while generalising better, and it made the case for annotating
tuberculosis datasets with radiological signs so that such reasoning, and its
visual explanations, can be studied properly. The methods were released through
the open-source `mednet` library and seeded the group's later work on trustworthy
and bias-aware tuberculosis screening.
