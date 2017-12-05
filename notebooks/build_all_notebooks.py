import subprocess

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

# solarized dark => solarized (mpl)



themes = ['bespin',
        'chalk',
        'isotope',
        'monokai']

#        'marrakesh',
#        'solarized-dark',
#        'shapeshifter']



# make custom config directory for each theme
#
# base16-jupyter/configs/bespin
# base16-jupyter/configs/chalk
# base16-jupyter/configs/isotope
# base16-jupyter/configs/monokai
#
# then run through dir commands,
#
# JUPYTER_CONFIG_DIR="~/codes/base16/base16-jupyter/configs/bespin" jupyter notebook

from subprocess import Popen

######################
# run nb server

#config_dir="/Users/charles/codes/base16/base16-jupyter/configs/bespin"
#Popen(["jupyter notebook"], shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})

config_dir="/Users/charles/codes/base16/base16-jupyter/configs/monokai"
Popen(["jupyter notebook"], shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})




#######################
# convert to html

#config_dir="/Users/charles/codes/base16/base16-jupyter/configs/bespin"
#Popen(["jupyter nbconvert --to html bespin.ipynb"], shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})

#config_dir="/Users/charles/codes/base16/base16-jupyter/configs/monokai"
#Popen(["jupyter nbconvert --to html monokai.ipynb"], shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})








