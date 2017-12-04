#!/bin/bash
#
# Fancify. 
# - Pick a custom install location. 
# - Configure custom Jupyter config there.
# - Run Jupyter with jupyter config environment variable set.

# Or be lazy.
cp colors/base16-bespin.css ~/.jupyter/custom/custom.css

# ---------------------
# Stuff to set:

CONFIG_DIR="$HOME/.jupyter"
THEME="bespin"

# ---------------------
# Leave this alone:

CUSTOM_DIR="$CONFIG_DIR/custom"

# Create config directory
JUPYTER_CONFIG_DIR=${CONFIG_DIR} jupyter notebook --generate-config

# Make custom directory
mkdir $CUSTOM_DIR

# Install CSS style
cp colors/base16-${THEME}.css ${CUSTOM_DIR}/custom.css

# Run a notebook
JUPYTER_CONFIG_DIR=${CONFIG_DIR} jupyter notebook 
