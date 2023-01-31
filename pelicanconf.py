#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = "André Anjos"
COPYRIGHT_NAME = AUTHOR
COPYRIGHT_YEAR = str(__import__("datetime").date.today().year)
SITENAME = "André Anjos"
SITETITLE = "André Anjos"
SITESUBTITLE = "Machine Learning, Computer Vision, Medical Imaging & Health Data Analysis, Reproducibility, Ph.D."
SITEDESCRIPTION = "Professional Website"
SITELOGO = "/images/profile_128.png"
FAVICON = "/images/favicon.ico"
APPLE_TOUCH_ICON = "/images/profile_128.png"
SITEURL = "https://anjos.ai"

# Theme setup
THEME = "theme"
BROWSER_COLOR = "#333"

# Static directories
STATIC_PATHS = (
    "images",
    "css",
)

# Extra CSS customization
EXTRA_PATH_METADATA = {
    "css/custom.css": {"path": "css/custom.css"},
}
CUSTOM_CSS = "css/custom.css"

ROBOTS = "index, follow"

PATH = "content"
DELETE_OUTPUT_DIRECTORY = True

TIMEZONE = "Europe/Zurich"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Links in the front page, aside from the static ``pages``
DIRECT_TEMPLATES = [
    "index",
    "publications",
]
LINKS = (
    ("CV", "https://anjos.ai/cv/cv.pdf"),
    ("Research", "/research/"),
    ("Publications", "/publications/"),
    ("Courses", "/courses/"),
    ("Software", "/software/"),
    ("Talks & Media", "/media/"),
    ("About", "/about/"),
    ("Short Bio", "/short-bio/"),
    ("Contact", "/contact/"),
)

# Social widget
SOCIAL = (
    ("orcid", "https://orcid.org/0000-0001-7248-4014"),
    ("google-scholar", "https://scholar.google.ch/citations?user=pAfLhMoAAAAJ"),
    ("linkedin", "https://www.linkedin.com/in/andreranjos/"),
    ("stack-overflow", "https://stackoverflow.com/users/712525/andré-anjos"),
    ("github", "https://github.com/anjos"),
    ("gitlab", "https://gitlab.idiap.ch/bob"),
)
GOOGLE_ANALYTICS = "UA-22320747-1"

# Plugins
PLUGIN_PATHS = [
    "plugins",
]
PLUGINS = [
    "deadlinks",
    "bibtex",
    "bibcite",
]

DEFAULT_PAGINATION = False
DISABLE_URL_HASH = True  # don't put hashes by the end of urls
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False
OUTPUT_RETENTION = [
    "CNAME",
]

# URL organization
ARTICLE_URL = "{category}/{slug}/"
ARTICLE_SAVE_AS = "{category}/{slug}/index.html"
CATEGORY_URL = "{slug}/"
CATEGORY_SAVE_AS = "{slug}/index.html"
PAGE_URL = "{slug}/.html"
PAGE_SAVE_AS = "{slug}/index.html"
PUBLICATIONS_SAVE_AS = "publications/index.html"

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

# Set to ``True`` the following line to enable link-checking
DEADLINK_VALIDATION = False
DEADLINK_OPTS = {
    "timeout_duration_ms": 5000,
    "archive": False,
    "classes": ["disabled"],
}

# Where is the location of your BibTeX database
PUBLICATIONS_SRC = "content/data/publications.bib"

# Theme configuration options
#USE_LESS = True #set to "True" to test theme changes
THEME_COLOR = "light"
THEME_COLOR_AUTO_DETECT_BROWSER_PREFERENCE = True
THEME_COLOR_ENABLE_USER_OVERRIDE = True
PYGMENTS_STYLE = "solarized-light"
PYGMENTS_STYLE_DARK = "solarized-dark"
