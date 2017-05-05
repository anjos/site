.. image:: https://travis-ci.org/anjos/site.svg?branch=master
   :target: https://travis-ci.org/anjos/site

----------------------
 Professional Website
----------------------

Generator code using Pelican_, for my professional web site. The website is
re-built at every commit (in Travis) and re-deployed as Github Pages via
Fabric_.


Local Testing
-------------

It is possible to locally test the web site before commit/pushing it back to
GitHub (which will case the site to be re-compiled and re-deployed). I advise
you to install a Conda_-based environment for deployment with this command
line::

  $ conda env create -f env.yml
  $ source activate site


To compile a new version of the website, do::

  $ pelican

To test the website, do::

  $ ./develop_server.sh start 8000

Use the application ``develop_server.sh`` to restart the server or stop it if
necessary.

.. note::

   The application ``develop_server.sh`` is provided by ``pelican-quickstart``.
   You should regenerate it in case of problems.


Deployment
----------

To deploy the website, do...



.. Place your references after this line
.. _conda: http://conda.pydata.org/miniconda.html
.. _pelican: http://getpelican.com
.. _fabric: http://www.fabfile.org
