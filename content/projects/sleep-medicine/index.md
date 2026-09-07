---
title: "Neurophysiology — Sleep Medicine"
weight: 12
cover: "images/covers/samuel-michel.png"
summary: >-
  Generalisable, reproducible automatic sleep-stage classification from
  polysomnography, working toward foundation models for sleep medicine.
research_outputs:
  - "anjos_sleepless_2017"
---

Polysomnography is the gold standard for diagnosing sleep disorders, but staging the
recordings by hand is slow, tedious, and surprisingly inconsistent: two experts scoring the
same night often disagree, and every sleep centre uses its own sensor setup. Automating the
staging promises faster, more reliable, and fairer diagnosis. Where we would like to go is
broader still, toward foundation models for sleep medicine that hold up across clinics,
sensors, and populations.

## Major achievements

We began with stateless models, which score each thirty-second epoch without reference to what
came before, comparing hand-crafted against learned feature extractors across databases from
different sleep centres. One finding has shaped everything since: the model that performed best
within a single database was not the one that generalised best across setups. A convolutional
network won on home ground, while a random forest over hand-designed features transferred most
reliably between centres with different sensor montages — peak in-domain accuracy is simply not
the same property as robust deployment. The ceiling deserves stating plainly too: the best model
reached a Cohen's kappa of 0.67 to 0.72 against the reference scoring, short of the 0.76
typically observed between two human experts, so staging at this level complements the scorer
rather than replacing them. A companion study carried the comparison to stateful models that
propagate temporal context across the night, on the reasoning that sleep stages are defined
partly by what precedes them.

The work has since moved from task-specific models toward reusable encoders. A set-then-sequence
transformer was pretrained contrastively on roughly 13,000 nights drawn from ten public cohorts,
then frozen while lightweight heads were trained on a held-out cohort for two different clinical
tasks. The frozen encoder reached 76.2% balanced accuracy for sleep staging from brain-activity
channels alone and remained competitive at detecting sleep apnoea, and a channel analysis showed
that respiratory signals are indispensable for apnoea yet contribute little to staging. That is
concrete evidence that a single pretrained encoder can serve several tasks and montages, with
the honest qualification that how much it helps depends on which sensors a clinic actually
records. All of it is released through the open-source `sleepless` library, with preset
configurations that reproduce the published results, so the cross-clinic comparisons can be
rerun rather than taken on trust.

The most recent step moves from labelling whole epochs to locating individual events. Sleep
spindles are second-long bursts whose count, duration and frequency carry clinical signal in
schizophrenia, depression and apnoea, and marking them demands a temporal precision that a
foundation model's token grid does not natively offer. Adapting a pretrained sleep encoder to
that task showed both that the mismatch is real and where it is solved: the pretrained stream
supplies useful context, but the precision comes from a purpose-built time-frequency branch that
keeps detail below the token scale, reaching an event-level F1 of 0.80 against a physician's
annotations and edging past the published BLAST and SUMO detectors under a common protocol. Two
results deserve to be read alongside that number. A transformer trained from scratch matched the
frozen foundation encoder at this scale, so pretraining bought context rather than accuracy. And
on transfer to another annotated corpus, which set of expert annotations the detector had been
trained on mattered far more than its architecture, F1 falling from 0.65 to as low as 0.10 across
scorers of the same recordings. That is the staging lesson arriving from a second direction: what
a model scores at home says little about what it does elsewhere, and here the labels, not the
architecture, are what travel badly.

Evaluation uses public polysomnography databases, including Sleep-EDF (ST and SC), MASS SS2 and
SS3, the MODA consensus spindle annotations, and the Sleep Heart Health Study.
