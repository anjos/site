.. image:: https://github.com/anjos/site/actions/workflows/deploy/badge.svg
   :target: https://github.com/anjos/site/actions/workflows/deploy.yml

----------------------
 Professional Website
----------------------

Generator code using Pelican_, for my professional web site. The website is
re-built at every commit and re-deployed as Github Pages via Github Actions.


Local Testing
-------------

It is possible to locally test the web site before commit/pushing it back to
GitHub (which will case the site to be re-compiled and re-deployed). I advise
you to install a Conda_-based environment for deployment with this command
line::

  $ conda env create -f env.yml -n site
  $ source activate site


To compile a new version of the website, first make sure your CV is up-to-date
by rebuilding `its repository <https://github.com/anjos/cv>`_, then do::

  $ #this will fetch the latest version of the publications database
  $ curl --create-dirs --output content/data/publications.bib http://andreanjos.org/cv/publications.bib
  $ #this will effectively create a static version of the website
  $ pelican content

To test the website, do::

  $ pelican --listen --autoreload


Checking for dead links
=======================

It is possible to automatically check for dead links using the configuration
option ``DEADLINK_VALIDATION``, setting it to ``True`` in ``pelicanconf.py``.


Deployment
----------

Deployment is automatic, once you push a tag to github. Deployment instructions
are stored in deploy.yml_.


Publications
============

In order to deploy a publication, make sure to place the PDF of the publication
at Idiap, on your account, folder ``~/public/papers``. The name of the PDF
should match the BibTeX publication key entry identifier.


.. Place your references after this line
.. _conda: https://github.com/conda-forge/miniforge
.. _pelican: http://getpelican.com
.. _deploy.yml: .github/workflows/deploy.yml
