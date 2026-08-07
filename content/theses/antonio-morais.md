---
title: "Is System A Statistically Better Than System B?"
author: "Antonio Morais"
level: "Master"
university: "EPFL, Electrical Engineering"
date: 2022-02-01
slug: "antonio-morais"
cover: "images/covers/antonio-morais.png"
summary: >-
  On a small test set, is model A really better than model B, or did it just get
  lucky? This thesis expresses common performance measures as probability
  distributions so that comparisons come with honest uncertainty.
projects: []
report: "https://publidiap.idiap.ch/attachments/reports/2022/Morais_Idiap-Com-01-2023.pdf"
research_outputs:
  - "anjos_credible_2023"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
---

Performance measures decide which model is judged best and often guide how a model
is improved. Yet when the test set is small, a single number can be misleading:
the apparent winner may simply have been lucky on the particular examples it was
scored on. The thesis took up the deceptively simple question this poses, namely
when system A can be said to be statistically better than system B.

Comparisons in machine learning are usually reported as point estimates, with
confidence or credible intervals used far less often than in classical statistics.
The hypothesis was that expressing a performance measure in a probabilistic
setting, as a distribution rather than a single value, would let credible regions
carry the uncertainty around any reported score.

Credible regions were derived for precision, recall, F1-score, accuracy,
specificity, and the Jaccard index from their posterior distributions, and their
coverage was studied through Monte-Carlo simulation. A worked example makes the
point vividly: two systems with F1-scores of 0.571 and 0.315 by the usual formula
look decisively different, yet in the probabilistic view the second system
actually outperforms the first in 43 percent of simulated cases. The analysis also
covered ROC and precision-recall curves, k-fold cross-validation, and the
treatment of dependent samples.

The thesis showed that probabilistic performance measures give a statistically
sound basis for comparing models on small datasets, where point estimates quietly
mislead. The methods live on in the open-source `credible` package,
so the uncertainty around a score can be reported as a matter of routine.
