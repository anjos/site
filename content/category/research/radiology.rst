AI for Radiology
----------------

:date: 2024-09-25 20:30
:slug: radiology
:cover: images/covers/ptb-cxr.jpg
:summary: The application of Artificial Intelligence (AI) in radiology improves
          diagnostic accuracy and efficiency by automating routine tasks, detecting
          subtle patterns, and analyzing large datasets from various types of medical
          images, including X-rays, CT scans, MRIs, and mammograms.

The application of Artificial Intelligence (AI) in radiology has numerous benefits,
including improved diagnostic accuracy for X-ray and CT scans, enhanced image analysis
of MRI and PET scans, and increased efficiency in reviewing ultrasound and mammography
images. AI-powered systems can automate routine tasks related to chest X-rays, abdominal
CTs, and bone density scans, freeing up radiologists to focus on complex cases like
brain MRIs, cardiac CTA scans, and breast cancer screening mammograms. For example, AI
can be used to detect active pulmonary tuberculosis (TB) by analyzing X-ray images for
signs of disease progression, such as cavitation or fibrosis. By automating the
detection of these changes, AI-powered systems can help healthcare professionals
diagnose TB, ultimately improving patient outcomes.

.. figure:: {static}/images/pictures/ptb-healthy-cxr.jpg
   :align: center
   :alt: Radiological signs

   **Example Application**: Radiological signs on healthy (left) and active Pulmonary
   TB-affected lungs (right). AI models can be used to detect TB from CXR images.

.. admonition:: Partnerships

   * Prof. Dr. Med. Anete Trajman, Dr. José Manoel de Seixas, Dr. Natanael Moura Jr., from the
     Federal University of Rio de Janeiro
   * Prof. Dr. Med. Lucia Mazzolai, from CHUV (Lausanne university hospital), Switzerland
   * Prof. Manuel Günther, University of Zürich, Switzerland
   * Dr. Eugenio Canes and André Baceti, Murabei Data Science, Brazil

**Radiomics**: In [@@euvip-2024-2] We've developed an evaluation framework for
extracting 3D deep radiomics features using pre-trained neural networks on real computed
tomography (CT) scans, allowing comprehensive quantification of tissue characteristics.
We compared these new features with standard hand-crafted radiomic features,
demonstrating that our proposed 3D deep learning radiomics are at least twice more
stable across different CT parameter variations than any category of traditional
features. Notably, even when trained on an external dataset and task, our generic deep
radiomics showed excellent stability and discriminative power for tissue
characterization between different classes of liver lesions and normal tissue, with an
average accuracy of 93.5%.

**Chest X-ray CAD for Tuberculosis**: In [@@ijtld-2023], We conducted a review of
computer-aided detection (CAD) software for TB detection, highlighting its potential as
a valuable tool but also several implementation challenges. Our assessment emphasizes
the need for further research to address issues related to diagnostic heterogeneity,
regulatory frameworks, and technology adaptation to meet the needs of high-burden
settings and vulnerable populations. In [@@union-2022] we proposed an new approach to
develop more generalizable computer-aided detection (CAD) systems for pulmonary
tuberculosis (PT) screening from Chest X-Ray images. Our method used radiological signs
as intermediary proxies to detect PT, rather than relying on direct image-to-probability
detection techniques that often fail to generalize across different datasets. We
developed a multi-class deep learning model that maps images to 14 key radiological
signs, followed by a second model that predicts PT diagnosis from these signs. Our
approach demonstrated superior generalization capabilities compared to traditional CAD
models, achieving higher area under the specificity vs. sensitivity curve (AUC) values
on cross-dataset evaluation scenarios. Building on this, in [@@euvip-2024-1] we
developed reliable techniques to train deep learning models for PT detection. By
pre-training a neural network on a proxy task and using a technique called Mixed
Objective Optimization Network (MOON) to balance classes during training, we demonstrate
that our approach can improve alignment with human experts' decision-making processes
while maintaining perfect classification accuracy. Notably, this method also enhances
generalization on unseen datasets, making it more suitable for real-world applications.
We made `our source code publicly available <euvip24_tb_>`_ online for reproducibility
purposes.

**Semanatic Segmentation**: In [@@cbic-2021] we investigated the impact of digitization
on X-Ray images and their effect on deep neural networks trained for lung segmentation,
highlighting the need to adapt these models to accurately analyze digitized data. Our
results show that while our model performs exceptionally well (AUPRC: 0.99) at
identifying lung regions in digital X-Rays, its performance drops significantly (AUPRC:
0.90) when applied to digitized images. We also found that traditional performance
metrics, such as maximum F1 score and area under the precision-recall curve (AUPRC), may
not be sufficient to characterize segmentation problems in test images, particularly due
to the natural connectivity of lungs in X-Ray images.

**Demographic Fairness**: In [@@miccai-2024] we tackled the challenge of ensuring
consistent performance and fairness in machine learning models for medical image
diagnostics, with a focus on chest X-ray images. We proposed using Foundation Models as
an embedding extractor to create groups representing protected attributes, such as
gender and age. This approach can effectively group individuals by gender in both in-
and out-of-distribution scenarios, reducing bias by up to 6.2%. However, the model's
robustness in handling age attributes is limited, highlighting a need for more
fundamentally fair and robust Foundation models. These findings contribute to the
development of more equitable medical diagnostics, particularly where protected
attribute information is lacking.

.. links here:

.. _euvip24_tb: https://biosignal.pages.idiap.ch/software/paper/euvip24-refine-cad-tb/
