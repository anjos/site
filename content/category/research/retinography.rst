Semantical Segmentation: Retinography
-------------------------------------

:date: 2021-04-14 12:30
:slug: retinography
:cover: images/pictures/retinography-vessels-segmented.jpg
:summary: Semantical segmentation of eye fundus structures, and disease
          detection from retinography, play a key role in mass screening using
          this tecnology. Despite the incredible progress in these fields, the
          lack of annotated images (due to cost), and rigor in the comparison
          of trained models has led to the conclusion larger and more dense
          network models provide more accurate results for such tasks.  We
          present our findings on different architectures and databases in this
          context.

.. |pic1| image:: {static}/images/pictures/retinography.jpg
   :height: 220
   :align: middle
   :alt: Original image from the HRF dataset

.. |pic2| image:: {static}/images/pictures/retinography-vessels-segmented.jpg
   :height: 220
   :align: middle
   :alt: Image with vessels segmented

.. class:: center

   |pic1| |pic2|

   *Predicted vessel maps vs. ground truths for a DL model evaluated on the
   high-resolution HRF test-set. True positives, false positives and false
   negatives are displayed in green, blue and red respectively.*

.. note::

   **Reproducibility Checklist**

   * All datasets used in this study are public
   * `Software is open-source <https://gitlab.idiap.ch/bob/bob.ip.binseg>`_
   * `Complete documentation is available <https://www.idiap.ch/software/bob/docs/bob/bob.ip.binseg/master/index.html>`_

   **Partnership**

   Part of this study was conducted in partnership with the Department of
   Ophthalmology at University Hospital of Grenoble Alpes.


Since the introduction of U-Nets in 2015, the field of medical image
segmentation has seen renewed interest bringing in a variety of fully
convolutional (deep) neural network (FCN) architectures for binary and
multi-class segmentation problems promising very attractive results, with
applications in computed tomography, retinography, and histopathology to cite a
few.  Despite the incredible progress, the lack of annotated images (due to
cost), and rigor in the comparison of trained models has led to the conclusion
larger and more dense network models provide more accurate results for this
task.  This is particularly noticeable in ophtalmological images such as those
from bi-dimensional eye fundus photography (retinography).  While retinography
is not used for precision diagnostics, it remains relatively cheap and very
effective means for mass screening.  Semantical segmentation of eye fundus
structures plays a key role in this process.

We tried to address these gaps in two different ways.  The
first [@@arxiv-2019] was to conduct and publish rigorous (open source,
reproducible) benchmarks with popular retinography datasets and
state-of-the-art FCN models in which we: i) showed that simple transformation
techniques like rescaling, padding and cropping of combined lower-resolution
source datasets to the resolution and spatial composition of a
higher-resolution target dataset can be a surprisingly effective way to improve
segmentation quality in unseen conditions; ii) we proposed a set of plots and
metrics that give additional insights into model performance and demonstrated
via tables and plots how to take advantage of that information, throwing a new
light over some published benchmarks.  We argue the performance of many
contributions available in literature is actually quite comparable within
standard deviation margins of each other, in spite of huge differences in the
number of parameters for different architectures.  Finally, `we made our
findings reproducible`_, distributing code and documentation for future
researchers to build upon, in the hopes to inspire future work in the
field.

In a second contribution [@@arxiv-2020] we propose that a minimalistic version
of a standard U-Net with 3 orders of magnitude less parameters, carefully
trained and rigorously evaluated, closely approximates the state-of-the-art
performance in vessel segmentation for retinography.  In addition, we propose a
simple extension, dubbed W-Net, by concatenating two U-Nets together, which
reaches outstanding performance on several popular datasets, still using orders
of magnitude less learnable weights than any previously published approach.
This work also provide a very comprehensive intra and cross-dataset performance
analysis, involving up to 10 different databases, including artery/vein
multi-class semantic segmentation.

.. links here:
.. _we made our findings reproducible: https://gitlab.idiap.ch/bob/bob.ip.binseg
