Deepdraw: Semantic segmentation library for medical imaging
-----------------------------------------------------------

:date: 2023-01-01 15:30
:slug: deepdraw
:cover: images/logos/biosignal-black.png
:summary: Deepdraw is semantic segmentation library for medical imaging based
          on PyTorch_.

Deepdraw_ is an open-source software package to train and evaluate a range of
neural network architectures for semantic `image segmentation`_ tasks. It is
built using PyTorch_.  It used to be called ``bob.ip.binseg`` when it was part
of the Signal Processing and Machine Learning Library bob_.

.. figure:: {static}/images/pictures/fundus-image-segmented.jpg
   :width: 90 %
   :figwidth: 100 %
   :align: center
   :alt: Example 1: semantic segmentation output, where the model was trained to delineate vessels on a color fundus image (ophthalmological data).

   Example 1: Semantic segmentation output of deepdraw_, where a
   fully-convolutional model was trained to delineate vessels on a color fundus
   image (ophthalmological data).


.. admonition:: :fa:`fa-solid fa-book` Associated Publications
   :class: information

   If you use this work, cite at least use the BibTeX references below:

   .. code-block:: bibtex

      @inproceedings{renzo-2021,
          title     = {Development of a lung segmentation algorithm for analog imaged chest X-Ray: preliminary results},
          author    = {Matheus A. Renzo and Nat\'{a}lia Fernandez and Andr\'e Baceti and Natanael Nunes de Moura Junior and Andr\'e Anjos},
          month     = {10},
          booktitle = {XV Brazilian Congress on Computational Intelligence},
          year      = {2021},
          doi       = {10.21528/CBIC2021-123},
      }

      @misc{laibacher-2019,
          title         = {On the Evaluation and Real-World Usage Scenarios of Deep Vessel Segmentation for Retinography},
          author        = {Tim Laibacher and Andr\'e Anjos},
          year          = {2019},
          eprint        = {1909.03856},
          archivePrefix = {arXiv},
          primaryClass  = {cs.CV},
          url           = {https://arxiv.org/abs/1909.03856},
      }


.. admonition:: Links
   :class: note

   :fa:`fa-brands fa-gitlab` `GitLab project page`_

   :fa:`fa-solid fa-book` `Documentation`_

   :fa:`fa-brands fa-python` Installable Python package `PyPI`_


.. Place your references here
.. _pytorch: https://pytorch.org
.. _deepdraw: https://gitlab.idiap.ch/medai/software/deepdraw
.. _gitlab project page: https://gitlab.idiap.ch/medai/software/deepdraw
.. _documentation: https://www.idiap.ch/software/bob/docs/medai/software/deepdraw/main/sphinx/index.html
.. _pypi: https://pypi.org/project/bob.ip.binseg/
.. _image segmentation: https://en.wikipedia.org/wiki/Image_segmentation
.. _bob: {filename}bob.rst
