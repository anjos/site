Computer Vision and Deep Learning for Biometrics
------------------------------------------------

:date: 2018-05-01 08:00
:slug: cv
:cover: images/covers/biometrics.jpg
:summary: I have actively worked in computer vision and deep learning (mostly)
          associated to biometric recognition, with potential application to
          various other tasks.  Contributions range from the collection of
          datasets, the exploration of different methods to address and assess
          biometric recognition vulnerabilities, domain adaptation, and remote
          photoplethysmography.


.. figure:: {static}/images/pictures/wmca-database.jpg
   :align: center
   :alt: WMCA Dataset

   Sample from the `WMCA`_ Dataset of bonafide accesses for the four
   acquisition channels after alignment. The images from all channels are
   aligned with the calibration parameters and normalized to eight bits for
   better visualization.

I worked with various different themes in computer vision applied to biometric
recognition.  In here, I highlight some of the more recent contributions:

* Presentation Attack Detection (PAD): Biometric recognition systems are
  exposed to presentation attacks, and dectectors for this purpose are required
  building blocks of thrustworthy systems.  Most PAD systems work
  discriminatively, trying to separate attacks from *bona fide* presentations.
  We showed this technique does not generalize well to unseen presentation
  attacks.  We explored, for the first time, alternate approaches by
  joint-modelling client identity as a way to calibrate PAD output scores
  [@@tifs-2015], showing increased robustness to unseen attacks.  More
  recently, we also showed that solely modelling *bona fide* presentations is
  also an effective way to increased PAD robustness [@@icb-2018].  Finally, we
  showed that by adding heterogenous inputs to PAD systems can improve their
  robustness [@@tifs-2019-2] to achieve state-of-the-art performance, even to
  unseen conditions during training.

* Domain Specific Units (Adaptation): In [@@tifs-2019], we apply domain
  adaptation via dedicated Domain-Specific Units (DSU), with an application to
  Heterogeneous Face Recognition.  In this class of problems, one wants to
  recognize an individual across different spectral data,  based on the
  representation on a principal spectrum (e.g., visual).  It is a challenging
  task because multi-spectral data for covering large populations is rare,
  which in turn stymies the training of deep convolution-based architectures
  for this task.  We developed a mechanism to adapt the parameters of models
  pre-trained on large visual spectral face recognition datasets, which are
  readily available.  My contributions are directly related to core idea of
  this work.


.. admonition:: Reproducibility Checklist
   :class: note

   * All published papers are 100% reproducible
   * `Software is open-source <https://www.idiap.ch/software/bob/>`_,
     extensible and tested on a regular basis
   * `Complete documentation is available <https://www.idiap.ch/software/bob/docs/bob/docs/master/index.html>`_
   * For details on each publication, check the publication directly.

   **Datasets**

   Some of the datasets published during this period:

   * WMCA_ "Wide Multi Channel Presentation Attack" Database, DOI: `10.34777/8zdh-v182 <https://doi.org/10.34777/8zdh-v182>`_
   * `Replay Attack`_ Database, DOI: `10.34777/cwcg-7r82 <https://doi.org/10.34777/cwcg-7r82>`_
   * COHFACE_ Database, DOI: `10.34777/ff3f-ba56 <https://doi.org/10.34777/ff3f-ba56>`_

   **Partnership**

   Work in Biometrics was conducted on the context of various SNSF_, `EU FP7`_,
   IARPA_, and Innosuisse_ projects together with the `Biometrics Security &
   Privacy Group`_ at Idiap_.

The ensemble of this work `was published </publications/>`_ as book chapters,
international peer-reviewed scientific journals (including articles at very
high-impact factor journals) and in peer-reviewed conference papers totalling a
few thousand citations.


.. links here:
.. _snsf: http://www.snf.ch/
.. _eu fp7: https://ec.europa.eu/growth/sectors/space/research/fp7_en
.. _innosuisse: https://www.innosuisse.ch/inno/en/home.html
.. _iarpa: https://www.iarpa.gov
.. _biometrics security & privacy group: https://www.idiap.ch/en/scientific-research/biometrics-security-and-privacy
.. _idiap: https://idiap.ch
.. _wmca: https://doi.org/10.34777/8zdh-v182
.. _replay attack: https://doi.org/10.34777/cwcg-7r82
.. _cohface: https://doi.org/10.34777/ff3f-ba56
