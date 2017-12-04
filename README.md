# base16-jupyter

forked from [base16-ipython](#)

Custom style sheets for Jupyter Notebook 

using Chris Kempson's Base16 color scheme generator

## Screenshots

see [TODO.md](/TODO.md)

![Monokai](/img/Monokai.png)

## How It Works

This uses a template CSS file in templates (default.mustache) that is 
marked with Mustache template variables representing colors for 
different color schemes.

The Python build script creates a temporary folder, gets a list of repos 
containing color schemes (in .yml format), and applies them to the template.
The output winds up in `colors/` in the form of ready-to-go CSS files.

Once you decide on a color template, you copy the CSS file to the Jupyter
configuration directory.

## Using 

### Build CSS Files

To start out, you will want the CSS style files.
These are included in the repo by default, but can be 
rebuilt from the template (if templates are modified) via:

```
pip install pystache
python build.py
```

This will use the Mustache templates in `templates/` 
to generate CSS files in `colors/`.

### Using as default Jupyter configuration

To use this CSS style as the default Jupyter notebook configuration,
start by creating a custom configuration directory:

```
$ jupyter notebook --generate-config
```

Next, you will want to install the CSS file to `$HOME/.jupyter/custom/custom.css`.

This is the way `install_jupyter.sh` currently installs the Jupyter theme,
so to install the theme as the Jupyter notebook default:

```
$ ./install_jupyter
```

By default this installs the "bespin" theme. Adjust `install_jupyster.sh` as needed.

### Using as custom Jupyter configuration

To install the CSS style as a custom Jupyter notebook configuration
that is only used if specified, the `$JUPYTER_CONFIG` variable
should be set.

Change `$CONFIG_DIR` in `install_jupyter.sh` to change 
configuration directory.


# Notes

NOTE:

There is an issue exporting to html because the styling is different.

[see this github issue](https://github.com/jupyter/nbconvert/issues/447#issuecomment-270766965)
for a useful list of tags needed for exported html.

Also see [todo](/TODO.md)
