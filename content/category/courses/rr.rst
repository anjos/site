Reproducible Research for Pattern Recognition
---------------------------------------------

:date: 2015-07-22 10:00
:slug: reproducible-research
:cover: images/covers/reproducible-research.png
:summary: This is a course on Reproducible Research (RR) for research engineers
          working with software applications in Pattern Recognition (PR) and
          Machine Learning (ML). It motivates and explains concepts behind
          RR, an increasing trend in scientific publications in this niche, its
          implications and tools for implementing it on an individual or group
          levels. It is a hands-on course in the sense students will be
          required to create their own workflows for selected problems in ML
          and PR. By the end of this course, students should understand the
          basic concepts of reproducibility, its importance on their daily
          practice and how to achieve it with freely available tools and
          environments.

One of the key aspects of modern technological research lies on the use of
personal computers (PCs) either for the simulation of known phenomena or for
the evaluation of data collected from natural observations. Mashups of these
data, organized in tables and figures are attached to textual descriptions
leading to scientific publications. In the current practice, data sets, code
and actionable software leading to those results are excluded upon recording
and preservation of articles. This panorama slows down potential scientific
development in at least two major aspects: (1) re-using ideas from different
sources normally implies on the re-development of software leading to original
results and (2) the reviewing process of candidate ideas is based on trust
rather than on hard, verifiable evidence that can be thoroughly analyzed.

In this course, I introduce the concept of `Reproducible Research`_ (RR), a
term that labels scientific work that provides not only a description of the
effort leading to stated conclusions, but points to data, software and
instructions that allows readers to reproduce author results locally, with all
required details and in a very short time. The promised gains of RR are
incredible, but it does not come without a cost: in order to boost
reproducibility, researchers now need to (re-)organize themselves so as to
always be doing RR. This course will walk students through tools and practical
exercises in order to implement RR on their daily activities.

Finally, I introduce students to the `BEAT Platform`: a web-based system for
Reproducible Research. BEAT provides an all-in-one experience in RR: tools to
graphically create workflows, write algorithms, run, log and search for results
in a socially interactive way. All complexity of RR and computation is hidden
behind an easy-to-use graphical web interface.  Experimentation designed inside
the platform can be easily transmitted and reproduced in a matter of seconds.


Topics and Outline
==================

The length of each topic will depend on student motivation and discussions. The
minimum course time is ~10 hours. If required, the course can be given in two
days (each with, at least, 5 hours of course time).

* Introduction and Some Programming Background

  * The need for reproducibility
  * Database and protocols: how to do it
  * Tools for RR in the wild

* Python and Bob_

  * Building database packages (encoding protocols)
  * Using Python and Bob for basic Machine Learning
  * Putting all together

* Going social (`BEAT platform`_):

  * The requirement for a web-based RR tool
  * The BEAT platform
  * Adapting your workflow to the platform
  * From running experiments to publication preparation using only a
    web-browser


Course Requirements
===================

Participants shall understand the basics of Pattern Recognition, Machine
Learning and programming. Knowing the Python programming language is a plus.
Here is a list of resources which can be interesting:

* Theoretical:

  * Machine Learning Basics (e.g. use Bishop's book)

* Practical:

  * `Dive into Python`_ (free tutorial)
  * Numerical and Scientific Programming in Python (numpy_, scipy_)
  * Bob_ framework for Signal Processing, Machine Learning and Biometrics


Material
========

* `Syllabus`_: essentially, a copy of the above in LaTeX
* Slides_: from the last iteration of the course


.. Place your references here
.. _reproducible research: http://reproducibleresearch.net/
.. _beat platform: https://www.beat-eu.org/
.. _bob: https://www.idiap.ch/software/bob/
.. _dive into python: http://www.diveintopython.net/toc/index.html
.. _numpy: http://www.numpy.org/
.. _scipy: http://www.scipy.org/
.. _syllabus: http://www.idiap.ch/~aanjos/courses/reproducible-research/syllabus.pdf
.. _slides: http://www.idiap.ch/~aanjos/courses/reproducible-research/slides.pdf
