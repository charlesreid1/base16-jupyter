# base16-jupyter

forked from [base16-ipython](#)

Custom style sheets for Jupyter Notebook 

using Chris Kempson's Base16 color scheme generator

## Screenshots

see [TODO.md](/TODO.md)

----

**Monokai theme:**

<img src="/img/Monokai.png" width="300px" alt="Monokai" />

## Quick Start

### Installing Prereqs

Templates for building CSS files requires Mustache templates,
which requires `pystache`:

```
pip install pystache
```

### Use Existing Jupyter Style Configurations

The main point of the repo is to give you 
a Jupyter notebook custom configuration 
directory with custom CSS to apply base16
color themes.

These are already built and ready to go 
in the `configs` directory.

To run juyter notebook specifying a custom theme,
edit `$JUPYTER_CONFIG_DIR` before running the 
jupyter command:

```
JUPYTER_CONFIG_DIR=configs/bespin jupyter notebook
```

If you want to convert a notebook to HTML 
for including it with web content, you can
specify this directory before invoking 
nbconvert:

```
JUPYTER_CONFIG_DIR=configs/bespin jupyter nbconvert --to html mynotebook.ipynb
```

### Building Jupyter Style Configurations

**Don't edit the .css files directly.**

The CSS files are automatically created from
the templates in `templates/`.

To remake the CSS style files and the Jupyter 
custom config directories:

```
python build.py
```

This should be done if you have a new 
color scheme, or if you modify the 
template files.




## How It Works

This will use the CSS Mustache templates in `templates/` 
to generate CSS files in `colors/` for each theme.

It initializes a Jupyter configuration directory for each theem,
then copies the theme CSS files into the Jupyter config directory.

(The list of themes comes from a repo, listed in a .yml file.)




# Notes

NOTE:

There is an issue exporting to html because the styling is different.

[see this github issue](https://github.com/jupyter/nbconvert/issues/447#issuecomment-270766965)
for a useful list of tags needed for exported html.

Also see [todo](/TODO.md)
