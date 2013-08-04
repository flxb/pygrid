# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.abspath('..'))
import pygrid

extensions = ['sphinx.ext.autodoc', 'numpydoc']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'PyGrid'
copyright = u'2013, Felix Brockherde'

version = pygrid.__version__
release = pygrid.__version__

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'default'
#html_theme_options = {'nosidebar': True}

html_static_path = ['_static']

htmlhelp_basename = 'PyGriddoc'

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

latex_documents = [
  ('index', 'PyGrid.tex', u'PyGrid Documentation',
   u'Felix Brockherde', 'manual'),
]
