IFI/UZH Summerschool: From Scripts to Reusable Software and Reproducible Research
---------------------------------------------------------------------------------

:date: 2022-06-29 09:00
:slug: uzh
:cover: images/covers/reproducible-research.png
:summary: The course provides actionable guidelines on how to convert
          non-reproducible scripts with hard-coded parameters into reusable
          software.

.. image:: {static}/images/pictures/uzh.jpg
   :width: 90%
   :align: center
   :alt: UZH's main building


One of the key principles of proper scientific procedure is the act of
repeating an experiment or analysis and being able to reach similar
conclusions.  In the optimal case, researchers should be able to reproduce
results from papers that they read with very little effort.  The reality is,
however, often different.  Most authors do not provide any source code leading
to their findings, and even when they do, information is incomplete or does not
reproduce the results from related works.  The course provides actionable
guidelines on how to convert non-reproducible scripts with hard-coded
parameters into reusable software.  We will exercise topics such as version
control, documentation, unit testing and packaging.  While most of the concepts
are independent of the programming language, examples will be provided in
Python.

:fa:`fa-file-pdf` Access course `slides`_.

:fa:`fa-house-chimney-window` Access the `course page`_.


**Program**:

* Motivation / Introduction (20 minutes, 5 minutes Q&A)
* Workflow for code organization (extensibility) (30 minutes, provide solution,
  10 minutes Q&A):

  * Disentangling score production from analysis (tabbing and plotting)
* Command-line parameters (The Missing Semester CSAIL/MIT) (30 minutes talk, 30
  minutes of hands-on + Q&A):

  * Argument Parsing with argparse
  * Configuration files: YAML
  * Producing tables (using package "tabulate")
  * Producing plots (using package "matplotlib")
* Version control (Git/GitHub) (30 minutes of talk, 10 minutes of hands-on and Q&A)
* Deployment (python packaging, for sharing) (30 minutes of talk, 30 minutes
  hands-on + Q&A)
* Software documentation (30 minutes, 30 minutes hands-on)
* Unit testing (20 minutes talk, no hands-on)

.. Place your references here
.. _course page: https://www.ifi.uzh.ch/en/studies/phd/summer-schools/summerschool2022.html
.. _slides: http://www.idiap.ch/~aanjos/courses/uzh-summerschool-slides-2022.pdf
