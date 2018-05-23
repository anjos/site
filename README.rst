.. image:: https://travis-ci.org/anjos/site.svg?branch=master
   :target: https://travis-ci.org/anjos/site

----------------------
 Professional Website
----------------------

Generator code using Pelican_, for my professional web site. The website is
re-built at every commit and re-deployed as Github Pages via Travis_.


Local Testing
-------------

It is possible to locally test the web site before commit/pushing it back to
GitHub (which will case the site to be re-compiled and re-deployed). I advise
you to install a Conda_-based environment for deployment with this command
line::

  $ conda env create -f env.yml
  $ source activate site


To compile a new version of the website, do::

  $ #this will fetch the latest version of the publications database
  $ curl --create-dirs --output content/pages/publications/index.bib http://andreanjos.org/cv/publications.bib
  $ #this will effectively create a static version of the website
  $ pelican

To test the website, do::

  $ ./develop_server.sh start 8000

Use the application ``develop_server.sh`` to restart the server or stop it if
necessary.

.. note::

   The application ``develop_server.sh`` is provided by ``pelican-quickstart``.
   You should regenerate it in case of problems.


Checking for dead links
=======================

It is possible to automatically check for dead links using the configuration
option ``DEADLINK_VALIDATION``, setting it to ``True`` in ``pelicanconf.py``.


Deployment
----------

Deployment is automatic, once you push a tag to github. Deployment instructions
are stored in ``.travis.yml``.


Publications
============

In order to deploy a publication, make sure to place the PDF of the publication
at Idiap, on your account, folder ``~/public/papers``. The name of the PDF
should match the BibTeX publication key entry identifier.


.. Place your references after this line
.. _conda: http://conda.pydata.org/miniconda.html
.. _pelican: http://getpelican.com
.. _travis: https://docs.travis-ci.com
