WIP: Vital Sign Analysis: Decompensation
----------------------------------------

:date: 2019-09-20 08:00
:slug: vital-sign
:cover: images/covers/vital-sign.png
:summary: Early and accurate prediction of decompensation (functional
          deterioration) in patients in domestic settings may help prevent
          deaths.  Based on values that can be measured from portable devices
          such as heart rate, blood oxygen saturation, systolic blood pressure,
          temperature, and age, we study the prediction capability of machine
          learning algorithms to determine patient decompensation (death) in
          the next 24 hours.

Early and accurate prediction of decompensation (functional deterioration) in
patients in domestic settings may help prevent deaths.  Based on values that
can be measured from portable devices such as heart rate, blood oxygen
saturation, systolic blood pressure, temperature, and age, we study the
prediction capability of machine learning algorithms to determine patient
decompensation (death) in the next 24 hours.  Two sources of variability
influencing the performance of predictions are investigated during training and
inference: (i) the effect of reducing the number of input signals from those
available in our source data set (about 17 different vital signs; source:
MIMIC-III_) to a subset that can be collected by portable devices; (ii) the
effect of the sampling frequency (how many measurements per unit of time are
necessary for training a reliable prediction system).  We conclude our analysis
with a inference-only study on the effect of the number of measurements
preceding the prediction (does having more measurements improve prediction?).

.. admonition:: Reproducibility Checklist
   :class: note

   * All datasets used in this study are public
   * A software package will be made available when work is published.

   **Partnership**

   Part of this study was conducted in partnership with VTULS_.


.. figure:: {static}/images/pictures/vital-sign-roc-all.png
   :align: center
   :alt: ROC with all methods

   **Preview Results**: ROC comparison for various systems. The best results
   are achieved with the original 17 features.  The threshold one day baseline,
   denoted by a green dot, represents the performance with a portable device
   with only the last vital signs measurement of a given sample.

.. links here:
.. _mimic-iii: https://mimic.physionet.org
.. _vtuls: https://www.vtuls.com
