Reproducible Research and Computing Platforms
---------------------------------------------

:date: 2024-09-25 17:54
:slug: reproducibility
:cover: images/covers/reproducible-research.png
:summary: Reproducible research not only leads to proper scientific conduct but
          also provides other researchers the access to build upon previous
          work. Most importantly, the person setting up a reproducible research
          project will quickly realize the immediate personal benefits: an
          organized and structured way of working. The person that most often
          has to reproduce your own analysis is your future self!

One of the key principles of proper scientific procedure is the act of
repeating an experiment or analysis and being able to reach similar
conclusions. Published research based on computational analysis, e.g.
bioinformatics or computational biology, have often suffered from incomplete
method descriptions (e.g. list of used software versions); unavailable raw
data; and incomplete, undocumented and/or unavailable code. This essentially
prevents any possibility of attempting to reproduce the results of such
studies. The term "reproducible research" has been used to describe the idea
that a scientific publication based on computational analysis should be
distributed along with all the raw data and metadata used in the study, all the
code and/or computational notebooks needed to produce results from the raw
data, and the computational environment or a complete description thereof.

.. figure:: {static}/images/pictures/reproducibility-nature.jpg
   :align: center
   :height: 350px
   :alt: Is there a reproducibility crisis?

   From: *M. Baker*, **1,500 scientists lift the lid on reproducibility**,
   Nature, vol. 533, no. 7604, pp. 452–454, May 2016, https://doi.org/10.1038/533452a.

Reproducible research not only leads to proper scientific conduct but also
provides other researchers the access to build upon previous work. Most
importantly, the person setting up a reproducible research project will quickly
realize the immediate personal benefits: an organized and structured way of
working. The person that most often has to reproduce your own analysis is your
future self!

All our work is driven by a fully reproducible framework. As such, I'm always active in
evaluating the reproducibility of published research and seeking ways to lower the
barriers for contributions. In most cases, it's insufficient simply to publish software
that leads to results without making original data accessible. A truly reproducible
workflow should possess characteristics such as repeatability, shareability,
extensibility, and stability – features that are not consistently guaranteed by most
published work [@@icml-2017-2].

We typically propose software suites (e.g., mednet_, Bob_) that embody these desirable
traits. The diverse applications of these suites demonstrate the flexibility of our
approach to various tasks, including medical image classification, segmentation, and
object detection; biometric person recognition; presentation attack detection; and
remote photoplethysmography.

From another perspective, there are legitimate cases in which raw data leading to
research conclusions cannot be published. Furthermore, in a growing number of use-cases,
the availability of both software does not translate into an accessible reproducibility
scenario. To bridge this gap, we built a prototype open platform for research called
BEAT_ [@@icml-2017-1]. This platform provided a computing infrastructure for open
science, proposing solutions for open access to scientific information, sharing, and
re-use – including data and source code while protecting privacy and confidentiality.
After nearly 10 years of usage and development, the BEAT_ platform is now retired.

Our recently granted project, CollabCloud_, further investigates how web-accessible
computing platforms can enhance reproducibility in data sciences, while also increasing
collaboration potential for computing infrastructures. Researchers conducting Artificial
Intelligence (AI) breakthrough research often face significant barriers due to limited
access to resources, including well-tuned systems, large datasets, and computing power.
This slows down complementary research as teams spend a substantial amount of time
setting up and transferring systems between institutions. To address this issue, the
Idiap Research Institute is developing "CollabCloud_", a cloud-based research
infrastructure designed to boost collaborative work in AI research. The platform aims to
provide easy exportability of research workflows, controlled access to shared storage
and computing power, and the ability for both computational and non-computational
experts to explore AI models together.  CollabCloud_ uses the Renku_ platform from the
`Swiss Data Science Center <sdsc_>`_.


.. links here:
.. _mednet: https://mednet.readthedocs.io/en/stable/
.. _bob: https://www.idiap.ch/software/bob
.. _beat: https://www.idiap.ch/software/beat
.. _collabcloud: https://data.snf.ch/grants/grant/220409
.. _renku: https://renkulab.io
.. _sdsc: https://www.datascience.ch
