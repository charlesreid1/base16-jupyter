import glob
import os
from os.path import basename

# 3024
# bespin
# brewer
# chalk
# flat
# grreyscale
# greenscreen
# isotope
# marrakesh
# monokai
# paraiso
# pop
# railscasts
# solarized (dark-light-none)



# # mplrc themes available:
# 3024.json
# atelierdune.json
# atelierforest.json
# atelierheath.json
# atelierlakeside.json
# atelierseaside.json
# bespin.json
# bright.json
# chalk.json
# default.json
# eighties.json
# flat.json
# grayscale.json
# greenscreen.json
# isotope.json
# londontube.json
# marrakesh.json
# mocha.json
# monokai.json
# ocean.json
# paraiso.json
# pop.json
# railscasts.json
# shapeshifter.json
# solarized.json
# test.json
# tomorrow.json
# twilight.json



############################
# Get a list of themes
# that have a notebook

themes = []
for notebook_name in glob.glob('notebooks/*.ipynb'):

    # extract theme names:
    theme = os.path.splitext(notebook_name)[0]
    theme = basename(theme)
    themes.append(theme)


############################
# Convert notebooks to html
# using custom configuration,
# AND
# copy to site/dist/
# to be checked in 
# to gh-pages branch.

from subprocess import Popen

for theme in themes:

    config_dir = 'configs/'+theme

    Popen(["jupyter nbconvert --to html notebooks/%s.ipynb && mv notebooks/%s.html site/dist/%s.html"%(theme, theme, theme)], 
            shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})


### JUPYTER_CONFIG_DIR=~/jupyter_custom jupyter notebook

