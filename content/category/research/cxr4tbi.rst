WIP: Intepretable Classification: Chest X-Rays
----------------------------------------------

:date: 2021-04-14 17:30
:slug: cxr4tb
:cover: images/covers/ptb-cxr.jpg
:summary: Tuberculosis (TB) is one of the leading causes of death from a single
          infectious agent.  In many high-burden regions around the world,
          which often lack specialized healthcare professionals, Chest X-Ray
          (CXR) exams continue to be of vital importance in the diagnosis and
          follow-up of the various presentations of the disease.  In this
          context, we investigate the benefits of automatic Pulmonary
          Tuberculosis (PTB) detection methods from these images.

.. figure:: {static}/images/pictures/ptb-healthy-cxr.jpg
   :align: center
   :alt: Radiological signs

   Radiological signs on healthy (left) and Activte Pulmonary TB-affected lungs
   (right).

.. note::

   **Reproducibility Checklist**

   * All datasets used in this study are public
   * `Software will be open-sourced soon <https://gitlab.idiap.ch/bob/bob.med.tb>`_. It is extensible and tested on a regular basis
   * `Complete documentation will be availabe available <https://www.idiap.ch/software/bob/docs/bob/bob.med.tb/master/index.html>`_


   **Partnership**

   This study was conducted in partnership with TB specialists from the Federal
   University of Rio de Janeiro and Rede TB in Brazil.

.. Abstract
.. Tuberculosis (TB) is one of the leading causes of death from a single
.. infectious agent.  In many high-burden regions around the world, which often
.. lack specialized healthcare professionals, Chest X-Ray (CXR) exams continue to
.. be of vital importance in the diagnosis and follow-up of the various
.. presentations of the disease.  In this context, we investigate the benefits of
.. automatic Pulmonary Tuberculosis (PTB) detection methods based on radiological
.. signs found on CXR.  Contrary to direct scoring from images, implemented in
.. most related work, indirect detection offers natural interpretability of
.. automated reasoning.  We identify generalization difficulties for direct
.. detection models trained exclusively on the modest amount of publicly available
.. CXR images from PTB patients.  We subsequently show that a model, pre-trained
.. on tens of thousands of CXR images using automatically annotated radiological
.. signs, offers a more adequate base for development.  By relaying radiological
.. signs through a simple linear classifier, one is able to obtain
.. state-of-the-art results on all three publicly available datasets (test AUC on
.. Montgomery County-MC: 0.98, Shenzhen-CH: 0.90, and Indian-IN: 0.94).  We
.. further discuss limitations imposed by the limited number of PTB-specific
.. radiological signs available on public datasets, and evaluate possible
.. performance gains that could be obtained if more were available (test AUC MC:
.. 1.00, CH: 0.98, IN: 0.99).  Our work is made open-source and fully reproducible
.. in the hopes it becomes useful to further explore the application of Deep
.. Learning to PTB screening.

.. Conclusions
.. Our study suggests that radiological signs extracted from CXR images constitute
.. a sufficient canvas, close to clinical requirements, to build more
.. interpretable and generalizable CAD for active PTB detection.  We obtained
.. state-of-the-art results (test AUC on MC: 0.98, CH: 0.90, IN: 0.94) by simply
.. plugging a linear classifier to a DL-based framework detecting radiological
.. signs on CXR images.  Our indirect detection algorithm provides better
.. generalization, more interpretable diagnosis and state-of-the-art performance
.. while using a training set with only 8 TB-related radiological signs.  By
.. fine-tuning, on PTB datasets, a direct detection model pretrained on thousands
.. of CXR images, it is possible to obtain new state-of-the-art results (test AUC
.. MC: 1.00, CH: 0.98, IN: 0.99), in exchange for interpretability.   These
.. results offer a glimpse of the possible performance gains that an adapted PTB
.. dataset with more specific radiological signs could bring.
..
.. While new state-of-the-art results could be extracted in the proposed workflow,
.. it is adequate to highlight limitations of this work.  First and foremost,
.. public PTB datasets are relatively small in size, and may not be representative
.. of realistic deployment conditions.  A study considering confidence intervals
.. may throw some light on this matter.  Secondly, the use of known markers for a
.. disease may limit the discovery of new ones.  The combination of both direct
.. and indirect techniques into a single CAD solution could offer both
.. interpretability and the required robustness in realistic deployments.
.. Finally, the proposed workflow could be applicable to other diseases and
.. medical imaging techniques, but this remains untested at this moment.  To
.. bridge this gap, we make our findings fully reproducible, distributing code and
.. documentation so these limitations may be eventually addressed.

Tuberculosis (TB) is one of the leading causes of death from a single
infectious agent.  In many high-burden regions around the world, which often
lack specialized healthcare professionals, Chest X-Ray (CXR) exams continue to
be of vital importance in the diagnosis and follow-up of the various
presentations of the disease.  In this context, we investigate the benefits of
automatic Pulmonary Tuberculosis (PTB) detection methods based on Deep
Learning.  Our work will be made open-source and fully reproducible in the
hopes it becomes useful to further explore the application of Deep Learning to
PTB screening.

.. links here:
