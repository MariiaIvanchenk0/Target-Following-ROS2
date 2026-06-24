# 1. Project Information
project = 'Target Following ROS2'
copyright = '2026, Lab Team'
author = 'Mariia and Daniel'
release = '1.0.0'

# 2. Plugins / Extensions
extensions = [
    'myst_parser', #  lets Sphinx read Markdown (.md) files
    'sphinx_rtd_theme',  # gives us the classic Read the Docs sidebar layout
]

# 3. Visual Layout Configuration
html_theme = 'sphinx_rtd_theme'

# 4. Cleanup & Behavior Rules
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
myst_heading_anchors = 3
