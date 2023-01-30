[![build](https://github.com/anjos/site/actions/workflows/deploy.yml/badge.svg)](https://github.com/anjos/site/actions/workflows/deploy.yml)

# Professional Website

Generator code using [Pelican](http://getpelican.com), for my professional web
site. The website is re-built at every commit and re-deployed as Github Pages
via Github Actions.


### Local Testing

It is possible to locally test the web site before commit/pushing it back to
GitHub (which will case the site to be re-compiled and re-deployed). I advise
you to install a [Conda](https://github.com/conda-forge/miniforge)-based
environment for deployment with this command line:

```sh
$ conda env create -f env.yml -n site
$ source activate site
```

To compile a new version of the website, first make sure your CV is up-to-date
by rebuilding [its repository](https://github.com/anjos/cv), then do:

```sh
$ #this will fetch the latest version of the publications database
$ curl --create-dirs --output content/data/publications.bib https://raw.githubusercontent.com/anjos/cv/main/publications.bib
$ #this will effectively create a static version of the website
$ pelican
```

To test the website, do:

```sh
$ pelican --listen --autoreload
```


### Checking for dead links

It is possible to automatically check for dead links using the configuration
option `DEADLINK_VALIDATION`, setting it to `True` in `pelicanconf.py`.


### Deployment

Deployment is automatic, once you push a tag to github. Deployment instructions
are stored in [deploy.yml](.github/workflows/deploy.yml).


### Publications

In order to deploy a publication, make sure to place the PDF of the publication
at Idiap, on your account, folder `~/public/papers`. The name of the PDF should
match the BibTeX publication key entry identifier.
