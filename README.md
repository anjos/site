[![build](https://github.com/anjos/site/actions/workflows/deploy.yml/badge.svg)](https://github.com/anjos/site/actions/workflows/deploy.yml)

# Professional Website

Generator code using [Pelican](http://getpelican.com), for my professional web site. The
website is re-built at every commit and re-deployed as Github Pages via Github Actions.


### Local Testing

It is possible to locally test the web site before commit/pushing it back to GitHub
(which will case the site to be re-compiled and re-deployed). I advise you to install a
[Pixi](https://pixi.sh)-based environment for deployment with this command line:

```sh
$ pixi install
```

To compile a new version of the website, first make sure your CV is up-to-date
by rebuilding [its repository](https://github.com/anjos/cv), then do:

```sh
# this will fetch the latest version of the publications database
$ pixi run bib
# this will effectively create a static version of the website
$ pixi run build
```

To test the website, do:

```sh
$ pixi run serve
```


### Checking for dead links

It is possible to automatically check for dead links using the configuration
option `DEADLINKS_VALIDATION`, setting it to `True` in `pelicanconf.py`.


### Deployment

Deployment is automatic, once you push a tag to github. Deployment instructions
are stored in [deploy.yml](.github/workflows/deploy.yml).


### Publications

In order to deploy a publication, make sure to place the PDF of the publication
at Idiap, on your account, folder `~/public/papers`. The name of the PDF should
match the BibTeX publication key entry identifier.
