Özgür Güler: Explaining CNN-Based Active Tuberculosis Detection in Chest X-Rays through Saliency Mapping Techniques
-------------------------------------------------------------------------------------------------------------------

:date: 2023-09-01
:slug: oezguer-gueler
:cover: images/covers/oezguer-gueler.png
:summary: This thesis investigates CNN-based detection of active Tuberculosis (aTB) from
          chest X-rays using the TBX11K dataset, which includes ground-truth bounding
          boxes. It shows that adding more annotated data improves model performance and
          proposes a novel evaluation metric—ROAD-Normalised PropEng Average—to compare
          visual explanation methods, identifying DenseNet-121 with Eigen-CAM as the
          most faithful and accurate combination.
:pybtex_sources: oezguer-gueler.bib

.. figure:: {static}/images/covers/oezguer-gueler.png
   :width: 90 %
   :figwidth: 100 %
   :align: center
   :alt: SALIENCY MAPS

   In this figure, we show (top row) Saliency maps for the unbalanced model M_U
   featuring the five cases from the TBX11k test set with the lowest Proportional Energy
   scores; (bottom row) respective predictions of our best balanced model M_B_B.
   Human-annotated ground-truth regions including radiological signs are indicated by
   bright magenta bounding boxes. The heatmaps (ranging from red to blue) indicate the
   contribution of different regions to the models' decision-making, with non-colored
   areas having no significant contribution.

Tuberculosis (TB) is an infectious disease caused by the bacterium Mycobacterium
tuberculosis, which is one of the leading causes of death worldwide. Various Deep
Convolutional Neural Network models have gained popularity to help during the TB
screening process by detecting patients with active Tuberculosis from their Chest
X-Rays. To help with further advancing the research, a new publicly available dataset,
TBX11K, has been used to increase the number of sam- ples during training for existing
replaceable state-of-the-art models. In the first step, the model's performance was
evaluated to see if an improvement through the addition of more TB-related data was
observable. It was shown that state-of-the-art replicable binary classifier models could
further be improved through the inclusion of more data. Further, there is a lack of
focus on generating and evaluating explanations for such models. The preferred methods
currently are saliency mapping techniques such as Grad-CAM, to generate visual
explanations based on the model's decision-making process, by overlaying heatmaps over
the Chest X-Rays. The selected TBX11K dataset includes ground truth bounding box labels,
which makes it possible to evaluate if the visualisations were correct. There are
various evaluation metrics to evaluate the faithful- ness and localisation performance
of the saliency mapping techniques according to ground truth labels. Two of them have
been identified to be useful, namely RemOve and Debias, and Pro- portional Energy.
RemOve and Debias was used to observe if there is one universal saliency mapping
technique that performs well for all models for the task of active Tuberculosis
detection. Further, based on these two metrics, a new metric was proposed,
ROAD-Normalised PropEng Average, to measure the overall best-performing model and
Saliency Mapping Technique com- bination. From the evaluation with RemOve and Debias, it
was concluded that there does not seem to be a universal saliency mapping technique that
performs well on all model architectures for the detection of active Tuberculosis. Thus,
it is recommended to always consider the under- lying model before choosing the optimal
saliency mapping technique. Further, through the use of the ROAD-Normalised PropEng
Average, it was concluded that one model in combination with a saliency mapping
technique offered the best trade-off between faithfulness and correct- ness of the
visualisations. This was the multi-label DenseNet-121 model with Eigen-CAM. To obtain
accurate classifications of active Tuberculosis with explainable and correct
visualisations, it is recommended to use this model and visualisation technique
combination.

.. admonition:: Reproducibility Checklist
   :class: note

   :fa:`fa-file-pdf` `Thesis report`_

   :fa:`fa-brands fa-python` `Software`_ is based on the open-source mednet_
   library. *N.B.: Software leading to these results was integrated into the Medical AI
   Group software stack.*

   :fa:`fa-database` All databases are publicly available

   :fa:`fa-book` An article with results from this thesis was published on a conference
   [@@euvip-2024]

.. Place your references here
.. _thesis report: https://capuana.ifi.uzh.ch/publications/PDFs/24103_Master_Thesis_oezguer_acar_gueler.pdf
.. _mednet: https://gitlab.idiap.ch/medai/software/mednet
.. _software: https://gitlab.idiap.ch/medai/software/paper/euvip24-refine-cad-tb
