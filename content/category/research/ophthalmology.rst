AI for Ophthalmology
--------------------

:date: 2024-09-25 19:26
:slug: ophtalmology
:cover: images/pictures/retinography-vessels-segmented.jpg
:summary: The application of Artificial Intelligence (AI) in ophthalmology enhances
          diagnostic accuracy, reduces false positives, and enables personalized
          treatment plans by analyzing retinal images and identifying subtle changes
          indicative of various eye conditions.

The application of Artificial Intelligence (AI) in ophthalmology has revolutionized the
field by providing valuable support for medical decision-making. By leveraging machine
learning algorithms and image analysis techniques, AI can aid clinicians in diagnosing
and managing various eye conditions more accurately and efficiently. For instance,
AI-powered systems can analyze retinal images from fundus photography, automated
refraction, or optical coherence tomography (OCT) scans to detect subtle changes
indicative of diseases such as diabetic retinopathy, age-related macular degeneration,
or glaucoma. By identifying patterns and anomalies that may be missed by human
observers, AI can enhance diagnostic accuracy, reduce false positives, and enable
earlier interventions. Additionally, AI-driven predictive models can help identify
patients at high risk of disease progression or complications, enabling personalized
treatment plans and improved patient outcomes. Overall, the integration of AI in
ophthalmology has the potential to transform clinical practice, improve patient care,
and enhance the overall efficiency of eye care services.

.. |pic1| image:: {static}/images/pictures/retinography.jpg
   :height: 220
   :align: middle
   :alt: Original image from the HRF dataset

.. |pic2| image:: {static}/images/pictures/retinography-vessels-segmented.jpg
   :height: 220
   :align: middle
   :alt: Image with vessels segmented

.. class:: figure center

   |pic1| |pic2|

   .. class:: caption

      **Example Application**: *Evaluation of a semantic segmentation techniques on
      color fundus imaging (CFI).  True positives, false positives and false negatives
      are displayed in green, blue and red respectively.*

.. admonition:: Partnerships
   :class: note

   * Dr. Mattia Tommasoni, M.D. Florence Hoogewoud, Hôpital Ophthalmique Jules Gonin,
     Lausanne, Switzerland
   * Dr. Med. Christophe Chiquet, Department of Ophthalmology at University Hospital of
     Grenoble Alpes, France
   * Dr. Med. Christoph Amstutz, Augenklinik Luzerner Kantonsspital, Switzerland


**Uveitis**: Our recent work have made significant strides in developing automated
grading systems for retinal inflammation. In [@@cbms-2023], we presented a novel
pipeline capable of fully automating the grading of retinal vasculitis from fundus
angiographies, achieving a high area-under-the-curve (AUC) score of 0.81, comparable to
state-of-the-art approaches. Building on this work, in [@@ssrn-2024], we developed an
automatic Transformer-based grading system for multiple retinal inflammatory signs,
utilizing a larger dataset of fluorescein angiography images. The model was trained on a
dataset with 543 patients (1042 eyes, 40'987 images). The new approach demonstrated
excellent performance in detecting vascular leakage, capillary leakage, macular edema,
and optic disc hyperfluorescence. These advancements have the potential to streamline
clinical evaluations, improve diagnostic accuracy, and enable more efficient patient
care for this class of diseases.

**Retinal vein occlusions**: In [@@mvr-2024] I contributed to the developement of a
novel non-invasive tool, named AO-LDV, which combines adaptive optics with laser Doppler
velocimetry to measure retinal venous blood flow in humans. This device enables accurate
measurements of absolute blood flow rates and red blood cell velocities across various
retinal vessel diameters. The study demonstrates that the AO-LDV can be used to quantify
total retinal blood flow in healthy individuals (approximately 38 μl/min), which was
found to correlate significantly with retinal vessel diameter and maximal velocity. The
study's findings are also accompanied by a thorough evaluation of two software suites
for automated retinal vessel measurement, one of which (based on deep neural networks)
demonstrated higher accuracy and wider measurements.

**Semantic segmentation**: Our study [@@nsr-2022] presents significant advancements in
retinal vessel segmentation from color fundus images, challenging the notion that
increasingly complex deep learning models are necessary for high performance. By
revisiting fundamental techniques and carefully training a minimalistic U-Net
architecture, we demonstrated that it can closely approximate the performance of current
state-of-the-art methods using orders of magnitude fewer parameters. Furthermore, they
introduce a cascaded extension (W-Net) that achieves outstanding results on several
popular datasets with even lower model complexity. The study also provides the most
comprehensive cross-dataset performance analysis to date, highlighting the limitations
of existing approaches and the potential for domain adaptation techniques. Overall, this
work showcases efficient and effective solutions for retinal vessel segmentation tasks
that align with current state-of-the-art results while reducing model complexity.

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

