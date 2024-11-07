Samuel Michel: Generalizable Automatic Classification of Sleep Stages
---------------------------------------------------------------------

:date: 2023-07-30
:slug: samuel-michel
:cover: images/covers/samuel-michel.png
:summary: This thesis develops stateless methods for sleep-phase detection from
          polysomnographs (PSG), while exploring techniques to improve
          cross-database generalisation.
:pybtex_sources: samuel-michel.bib


.. figure:: {static}/images/covers/samuel-michel.png
   :width: 90 %
   :figwidth: 100 %
   :align: center
   :alt: EEG channel configuration for the selected datasets.

   This figure illustrates the EEG channel configuration for the selected
   datasets. While EDF-ST and EDF-SC share the same channels, only three
   channels are common between MASS (SS3) and EDF (ST and SC).

The gold standard to diagnose sleep disorders is called polysomnography (PSG).
A PSG consists in sleeping one or several nights, at a hospital or a sleep
center, while wearing different sensors continuously measuring various temporal
data (e.g. electroencephalograms, electrocardiograms, electromiograms,
oxymetry, respiration rate, etc.). These data are then used by an expert to
annotate the PSG (hypnograph) into the differente sleep phases (paradoxal
summation, light, moderate and deep sleep). The hypnograph is then used for
sleep disorder diagnosis. The manual annotation process is affected by human
limitations: it is time consuming, tedious, not reliable, sensitive to the
setup of the different clinics, and to motion noise. Indeed, each sleep center
defined his own setup for the PSG. Moreover, it happens that one data is lost
due to a motion of the patient during the night (noisy data). Regarding the
reliability different studies have shown that for the same PSG two experts may
annotated differently. The aim of this work is to investigate the possibility
to automate the classification of PSG into the different sleep phases using
machine learning. The main concern will focus on the capacity of such
algorithms to be faster, and more reliable than manual scoring. To perform this
study, two follow-up questions will gravitate around the main scientific
question. We will focus on models which are robust to the setup of different
clinics, noise and are fair to different populations. One of the steps of our
work is therefore to analyse the ability of an automated classifier to manage
data coming from different sleep centers. We scoped this study to stateless
models that do not take into account temporal context. We investigated both
hand-crafted and learnable feature extractors. In terms of intra-database
performance, our best model was the CNN Chambon model proposed by Chambon et
al. in their paper [@@chambon-2018]. However, when evaluating generalization
across different setups, the random forest model with manually chosen features
described in the same paper emerged as the best model.


.. admonition:: Reproducibility Checklist
   :class: note

   :fa:`fa-file-pdf` `Thesis report`_

   :fa:`fa-brands fa-python` `Software`_ with preset configurations to
   reproduce published findings.

   :fa:`fa-database` All databases are publicly available


.. Place your references here
.. _thesis report: https://publications.idiap.ch/publications/show/5127
.. _software: {filename}../software/sleepless.rst
.. _sleepless: https://gitlab.idiap.ch/medai/software/sleepless/
