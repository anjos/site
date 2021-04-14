Remote Photoplethysmography
---------------------------

:date: 2017-09-20 08:00
:slug: rppg
:cover: images/covers/rppg-manhob-hci-tagging.png
:summary: We address the problem of reproducible research in remote
          photo-plethysmography (rPPG). Most of the work published in this
          domain is assessed on privately-owned databases, making it difficult
          to evaluate proposed algorithms in a standard and principled manner.
          As a consequence, we present a new, publicly available database
          containing a relatively large number of subjects recorded under two
          different lighting conditions.  Also, three state-of-the-art rPPG
          algorithms from the literature were selected, implemented and
          released as open source free software. After a thorough, unbiased
          experimental evaluation in various settings, it is shown that none of
          the selected algorithms is precise enough to be used in a real-world
          scenario.
:keywords: Image analysis, Remote photoplethysmography, Reproducible research, Vital signs monitoring


.. |pic1| image:: {static}/images/pictures/cohface-db-face-frontal.jpg
   :height: 200
   :align: middle
   :alt: Well lit face from (from COHFACE_)

.. |pic2| image:: {static}/images/pictures/cohface-db-face-natural.jpg
   :height: 200
   :align: middle
   :alt: Face with side lighting (from COHFACE_)

.. class:: center

   |pic1| |pic2|

   *Pictures of one of the subjects in the new COHFACE_ video dataset. On the
   left, the subject face is well-lit, without shadowed areas.  On the right,
   the subject's face is exposed to natural lighting (from the side).  Results
   vary substantially while reconstructing the PPG signal from each of these
   cases.*

.. note:: **Reproducibility Checklist**

   * All datasets used in this study are public
   * A new public dataset was released (`COHFACE Database`_)
   * `Software is open-source <https://gitlab.idiap.ch/bob/bob.rppg.base>`_
   * `Complete documentation is available <https://www.idiap.ch/software/bob/docs/bob/bob.rppg.base/master/index.html>`_


We address the problem of reproducible research in remote photo-plethysmography
(rPPG). Most of the work published in this domain is assessed
on privately-owned databases, making it difficult to evaluate proposed
algorithms in a standard and principled manner.  In our contribution
[@arxiv-2017-2], three state-of-the-art rPPG algorithms were selected and
evaluated. For this purpose, a new, publicly available database containing 40
subjects (named `COHFACE Database`_) captured under two different illumination
conditions has been introduced. A thorough experimental evaluation of the
selected approaches has been conducted using different datasets and their
associated protocols.  Our reproducible research framework allows assessing
performance in a principled and unbiased way. Obtained results show that only
one rPPG algorithm has a stable behaviour, but overall it has been noticed that
performance is highly dependent on a careful optimization of parameters.
Conducted experiments also shows that generalization across conditions (i.e.
resolution, illumination) should be of high concern when assessing rPPG
approaches. The data, the experimental protocols and the implementation of the
algorithms

.. links here:
.. _cohface database: https://idiap.ch/dataset/cohface
