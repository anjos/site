#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'André Anjos'
SITENAME = 'André Anjos'
SITETITLE = 'André Anjos'
SITESUBTITLE = 'Signal Processing Engineer, Ph.D.'
SITEDESCRIPTION = 'Professional Website'
SITELOGO = '/images/profile_128.png'
FAVICON = '/images/favicon.ico'
SITEURL = 'https://anjos.github.io/prosite'

# Theme setup
THEME = 'theme'
BROWSER_COLOR = '#333'

# Static directories
STATIC_PATHS = (
    'images',
    'pdfs',
    'css',
    )

# Extra CSS customization
EXTRA_PATH_METADATA = {
    'css/custom.css': {'path': 'css/custom.css'},
}
CUSTOM_CSS = 'css/custom.css'

ROBOTS = 'index, follow'

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
    }

PATH = 'content'
DELETE_OUTPUT_DIRECTORY = True

TIMEZONE = 'Europe/Zurich'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Links in the front page, aside from the static ``pages``
EXTRA_TEMPLATES_PATHS = [
    'templates',
    ]
DIRECT_TEMPLATES = [
    'index',
    'publications',
    ]
LINKS = (
    ('CV', '/pdfs/cv.pdf'),
    ('Videos', '/category/videos.html'),
    ('Publications', '/publications.html'),
    )

# Social widget
SOCIAL = (
    ('linkedin', 'https://www.linkedin.com/in/andreranjos/'),
    ('stack-overflow', 'http://stackoverflow.com/users/712525/andré-anjos'),
    ('github', 'https://github.com/anjos'),
    ('gitlab', 'https://gitlab.idiap.ch/bob'),
    ('skype', 'skype:andrezito?call'),
    )
GOOGLE_ANALYTICS = 'UA-22320747-1'

# Plugins
PLUGIN_PATHS = [
    'plugins',
    ]
PLUGINS = [
    'pelican_youtube',
    'deadlinks',
    'bibtex',
    ]

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

# Set to ``True`` the following line to enable link-checking
DEADLINK_VALIDATION = False
DEADLINK_OPTS = {
    'timeout_duration_ms': 5000,
    'archive': False,
    'classes': ['disabled'],
    }

# Where is the location of your BibTeX database
PUBLICATIONS_SRC = 'content/publications.bib'
