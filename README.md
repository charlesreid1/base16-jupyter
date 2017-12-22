# base16-jupyter

A fork of [base16-ipython](#) and [base16-ipython-matplotlibrc](#).

Uses C Kempson's Base 16 color scheme framework.



## Table of Contents

* What is it?

* For the lazy: get started using existing color schemes
    * Using Jupyter notebook color schemes
    * Using Matplotlib color schemes from Jupyter

* For the ambitious: how to modify base16-jupyter?
    * Installing dependencies
    * Building custom Jupyter CSS
    * Matplotlib configuration

* For the overachiever: how to make own color schemes?



--------------------------------------------------------



## Well... What The Hell Is It?

This repository gives you some cool dark/light color schemes 
for Jupyter notebooks, plus associated matplotlib plot styles.

How does it work? To run Jupyter with custom CSS, you can just
point Jupyter to a custom configuration directory when you run it.

To use custom matplotlib colors, you have to install
a notebook extension first.



## For The Lazy: How Do I Get Started Using Existing Color Schemes?

The main point of this repo is not just to give you the tools you need
to make your own Jupyter/Matplotlib color schemes, but to provide 
a usable bundle of Jupyter and matplotlib config files, so you can
use this package right out of the box.

### Using Jupyter Notebook Color Schemes

In the `configs` directory, there are a number of 
custom configuration directories, each with their own
CSS file to apply a base 16 color scheme to a Jupyter
notebook. 

Each color scheme has its own directory in `configs`.

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

### Using Matplotlib Color Schemes From Jupyter

TODO



## For The Ambitious: How Do I Modify base16-jupyter? 

### Installing Dependencies

Templates for building CSS files requires Mustache templates,
which requires `pystache`:

```
pip install pystache
```

### Building Custom Jupyter CSS

The base16-jupyter package uses CSS to apply style files to Jupyter notebooks.

CSS files are created from a single CSS template in the `templates/` directory.

**To edit the CSS of a base16-jupyter style,
do not edit the CSS file directly - edit the CSS template.**

Once you've modified the CSS template, you can remake
the CSS style files and custom Jupyter config directories,
via the command:

```
python build.py css
```

(Run this command from the base16-jupyter repository.)

This should be done if you have added a new color scheme to
the list of color schemes being built, or if you have 
modified the template files. 


### Matplotlib Configuration

TODO - modifying details? where are they? how copied?





## For The Overachiever: How Do I Make My Own Schemes for base16-jupyter? 

The list of color schemes actually built into Jupyter configurations
and Matplotlib styles is defined in a .yaml file.
The .yaml file is itself a list of Github repositories,
each containing the files for a particular color scheme.

To add a new color scheme to the list, simply edit the
.yaml file and add a repository for a color scheme.

Note that creating your own, brand-new color scheme is
outside the scope of this document. 



--------------------------------------------------------




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
