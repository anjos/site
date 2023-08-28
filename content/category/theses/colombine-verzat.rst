Colombine Verzat: Machine Learning for Adverse Event Detection in Latent Tuberculosis Infection Treatment
---------------------------------------------------------------------------------------------------------

:date: 2020-07-15 10:00
:slug: colombine-verzat
:cover: images/covers/thesis-colombine-verzat.png
:summary: The goal of this study is to identify whether it is possible to
          predict the occurrence of adverse events in patients based on their
          clinical data.


.. figure:: {static}/images/covers/thesis-colombine-verzat.png
   :width: 90 %
   :figwidth: 100 %
   :align: center
   :alt: Illustrative comparison between active and latent TB

   Comparison between active and latent TB. Adapted from
   http://www.bccdc.ca/about/news-stories/stories/its-time-to-end-tb. Both
   latent and active TB show positive TB skin test but only active TB displays
   abnormal chest X-Ray. Latent TB is not infectious and the patients show no
   symptom since the bacterium is dormant in the lungs. On the other hand,
   patients with active TB can contaminate others and show symptoms.

One quarter of the world’s population has latent tuberculosis infection (LTBI).
In this form of the disease, the bacteria has a 10 to 15% chance to start
replicating and cause the patient to develop active tuberculosis. In those
cases, preventive therapy is thus essential to limit the spread of the disease.
Unfortunately, the treatment for LTBI can cause severe adverse events which
discourages patients. Predicting which patients are most at risk of developing
adverse events could thus improve treatment efficacy and help achieving WHO
goals of TB elimination by 2050.

The goal of this study is to identify whether it is possible to predict the
occurrence of adverse events in patients based on their clinical data.

To address this, we disposed of a clinical dataset of 6485 patients who had
LTBI and went through treatment. A small part of these patients developed
adverse events associated to the treatment. First, we reproduced `a study by
Campbell et al.`_ performed on this dataset using a logistic regression
model. We then investigated the predictive power of this model using
generalization and established a baseline from the resulting model. Finally, we
explored how non-linear machine learning models could improve the performance
compared to the baseline.

We found that multivariate logistic regression yielded a classifier with the
following performance: AUC= 0.65 ± 0.04. Although non-linear techniques matched
the baseline performance, they failed to significantly improve the prediction
further.

These findings suggest that part of the data is linearly separable, while some
isolated points in the dataset cannot be easily generalized. Patients with and
without adverse events seem to overlap in the variable space, which suggests
that an efficient detection of adverse events is difficult to achieve with this
dataset. The improvement of the model may require a larger and less imbalanced
dataset, possibly along further explanatory variables permitting a better
characterization of the patient.

.. admonition:: Available Materials
   :class: note

   :fa:`fa-file-pdf` `Thesis report`_


.. Place your references here
.. _a study by campbell et al.: https://doi.org/10.1016/s1473-3099(19)30575-4
.. _thesis report: http://publications.idiap.ch/attachments/reports/2020/Verzat_Idiap-Com-02-2020.pdf
