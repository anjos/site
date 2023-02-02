Geoffrey Raposo: Active tuberculosis detection from frontal chest X-ray images
------------------------------------------------------------------------------

:date: 2021-07-15 10:00
:slug: geoffrey-raposo
:cover: images/covers/geoffrey-raposo.png
:summary: In this study, we investigate the benefits of automatic Pulmonary
          Tuberculosis (PTB) detection methods based on radiological signs
          found on frontal chest X-Ray images.


.. figure:: {static}/images/covers/geoffrey-raposo.png
   :width: 90 %
   :figwidth: 100 %
   :align: center
   :alt: Comparison between direct and indirect classification of images

   Direct and indirect PTB assessment from CXR images. Machine Learning models
   found in the literature usually implement direct detection while healthcare
   professionals an indirect approach.


Tuberculosis (TB) is one of the leading causes of death from a single
infectious agent in the world.  In many high-burden regions, which often lack
specialized healthcare professionals, Chest X-Ray (CXR) exams continue to be of
vital importance in the diagnosis and follow-up of the various presentations of
the disease.  In this context, automated systems to support diagnosis from CXR
images constitute a fundamental cog as the World Health Organization (WHO)
confirmed in early 2021 that they can be used in place of human readers for the
interpretation of digital CXRs.

In this study, we investigate the benefits of automatic Pulmonary Tuberculosis
(PTB) detection methods based on radiological signs found on CXR.  Contrary to
direct scoring from images, implemented in most related work, indirect
detection offers natural interpretability of automated reasoning.  We identify
generalization difficulties for direct detection models trained exclusively on
the modest amount of publicly available CXR images from PTB patients.  We
subsequently show that a model, pre-trained on tens of thousands of CXR images
using automatically annotated radiological signs, offers a more adequate base
for development.  By relaying radiological signs through a simple linear
classifier, one is able to obtain state-of-the-art results on three publicly
available datasets (test AUC on Montgomery County-MC: 0.97, Shenzhen-CH: 0.90,
and Indian-IN: 0.93).  We further discuss limitations imposed by the limited
number of PTB-specific radiological signs available on public datasets, and
evaluate possible performance gains that could be obtained if more were
available (test AUC MC: 0.98, CH: 0.98, IN: 0.93).

We then analyze the relative importance of each of the radiological signs for
PTB prediction using two distinct methods and conclude that more than a
specific sign, it is their combination that allows a reliable detection of the
disease.

Finally, we propose a visual overview of the radiological signs predictions
over radiographs using grad-CAMs and highlight the importance of annotating PTB
datasets to study the reliability of these visualizations.

Our work is made `open source`_ and fully reproducible in the hopes it becomes
useful to further explore the application of Deep Learning to PTB screening.


:fa:`fa-file-pdf-o` `Access the full thesis text from this link`_.


:fa:`fa-brands fa-python` `Access to Python source code`_ (git repository).


.. Place your references here
.. _access the full thesis text from this link: http://publications.idiap.ch/attachments/reports/2021/Raposo_Idiap-Com-01-2021.pdf
.. _access to python source code: https://gitlab.idiap.ch/bob/bob.med.tb
.. _open source: https://pypi.org/project/bob.med.tb
