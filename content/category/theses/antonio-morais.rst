Antonio Morais: A Bayesian approach to machine learning model comparison
------------------------------------------------------------------------

:date: 2022-02-28 10:00
:slug: antonio-morais
:cover: images/covers/antonio-morais.png
:summary: Performance measures are an important component of machine learning
          algorithms. They are useful when it comes to evaluate the quality of
          a model, but also to help the algorithm improve itself.  When used in
          small data sets, these measures may not properly express the
          performance of the model. That is when confidence intervals and
          credible regions can be useful. Expressing the performance measures
          in a probabilistic setting allows one to develop them as
          distributions. One can then use those distributions to establish
          credible regions.


.. figure:: {static}/images/covers/antonio-morais.png
   :width: 90 %
   :figwidth: 100 %
   :align: center
   :alt: Probabilistic F1-score distribution for 2 systems using Monte Carlo simulations.

   In this figure, we can see the distribution generation produced by the Monte
   Carlo simulation. If we only computed the F1-score using the usual formula
   we would have 0.571 for the first system and 0.315 for the second one so we
   would conclude that system 1 is way better than system 2. The probabilistic
   outlook gives another point of view. Even though the first model seems
   preferable as it is more consistent and has a better mode and average, the
   second model does not seem that far, and actually outperforms system 1 in
   43% of the cases.

Performance measures are an important component of machine learning algorithms.
They are useful when it comes to evaluate the quality of a model, but also to
help the algorithm improve itself. Every need has its own metric. However, when
we have a small data set, these measures don’t express properly the performance
of the model. That’s when confidence intervals and credible regions come in
handy. Expressing the performance measures in a probabilistic setting lets us
develop them as distributions. Then we can use those distributions to establish
credible regions. In the first instance we will address the precision, recall
and F1-score followed by the accuracy, specificity and Jaccard index. We will
study the coverage of the credible regions computed through the posterior
distributions. Then we will discuss ROC curve, precision-recall curve and
k-fold cross-validation. Finally we will conclude with a small discussion about
what we could do with dependent samples.


.. admonition:: Reproducibility Checklist
   :class: note

   :fa:`fa-file-pdf` `Thesis report`_

   :fa:`fa-brands fa-python` `Software`_ is based on the open-source bob.measure_
   library. *N.B.: Software leading to these results was only partially
   integrated into the bob.measure_ software stack.*

   :fa:`fa-database` No databases are required to reproduced results, which
   rely on Monte-Carlo simulations only.

.. Place your references here
.. _thesis report: https://publidiap.idiap.ch/attachments/reports/2022/Morais_Idiap-Com-01-2023.pdf
.. _software: https://gitlab.idiap.ch/bob/bob.measure/-/merge_requests/103
.. _bob.measure: https://gitlab.idiap.ch/bob/bob.measure/
