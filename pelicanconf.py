#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Jean Lauliac'
AUTHOR_EMAIL = 'jean@lauliac.com'
SITENAME = u'les cents lignes'
SITEURL = ''

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
# LINKS =  (('Pelican', 'http://getpelican.com/'),
#           ('Python.org', 'http://python.org/'),
#           ('Jinja2', 'http://jinja.pocoo.org/'),
#           ('You can modify those links in your config file', '#'),)
LINKS = ()

# Social widget
#SOCIAL = (('Code', '#'),
#          ('Another social link', '#'),)
SOCIAL = ()

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

DISPLAY_CATEGORIES_ON_MENU = False
TYPOGRIFY = True
#GITHUB_URL = 'http://github.com/jeanlauliac'
PLUGIN_PATH = 'pelican-plugins'
PLUGINS = ['gravatar', 'related_posts']
RELATED_POSTS_MAX = 3
THEME = 'themes/cast'
AUTHOR_SAVE_AS = False
DIRECT_TEMPLATES = ('index', 'archives')
STATIC_PATHS = ['extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

from datetime import datetime as dt

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st', 2:'nd', 3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def formal_date(t):
    return custom_strftime('%B {S}, %Y', t)

JINJA_FILTERS = {'formal_date': formal_date}

