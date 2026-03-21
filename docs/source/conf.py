
import os
import sys
from datetime import datetime

project = 'UniLog Toolkit'
author = 'Harris Wang'
current_year = datetime.now().year
copyright = f"{current_year}, {author}"

# If building from repo root, add it to path so autodoc can import 'unilog'
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

autodoc_typehints = 'description'
html_theme = 'furo'

# Keep minimal warnings
nitpicky = False
