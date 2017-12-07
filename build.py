#!/usr/bin/env python3

import sys, io, os
import subprocess
from subprocess import Popen
import tempfile
import glob
import urllib.request
import pystache, yaml
import json

"""
build.py:

    This script builds the following:
    - CSS files from templates
    - Jupyter custom config directories
    - Schemes into custom config directories

    Usage:

        python build.py [command]

    all command:
    - css files
    - jupyter config
    - nbconvert

    notebooks command:
    - jupyter nbconvert with configs 

    jupyter command:
    - python build.py jupyter
    - makes css colors
    - makes/installs Jupyter config directories

    css command:
    - python build.py css
    - makes css colors
"""

def usage():
    print("""
    build.py usage:

        python build.py [command]

        commands:
            css
            jupyter
            notebooks
            all
    """)


def css_info(templates_dir):
    print("CSS files have been built from templates in %s"%(templates_dir))
    print("files: config.yaml, default.mustache")


def jupyter_info(templates_dir):
    print("jupyter config files have been built from templates %s"%(templates_dir))
    print("files: config.yaml, default.mustache, configs/")


def notebooks_info(templates_dir, notebooks_dir, deploy_dir):
    print("jupyter config files have been built from templates %s"%(templates_dir))
    print("built from notebooks in %s"%(notebooks_dir))
    print("converted to html in %s"%(deploy_dir))


def get_config(config_file):
    """Get the template configuration file
    (this controls the outupt schema for the 
    Mustache templates)
    """
    with open(config_file) as file:
        config = yaml.safe_load(file)
    return config


def make_context(scheme):
    """Create context for color scheme
    """
    context = {}
    context['scheme-name'] = scheme['scheme']
    context['scheme-author'] = scheme['author']
    for base in range(16):
        context[f'base{base:02X}-hex'] = scheme[f'base{base:02X}']
    return context


def clone_from_config(templates_dir, schemes_url):
    """Use a configuration YAML file to turn color schemes
    into output files using a Mustache template and 
    stuff.

    Returns a list of color schemes and a list of files 
    for that scheme.
    """
    config_file = templates_dir + '/' + 'config.yaml'
    config = get_config(config_file)

    # Put each .mustache template in the Mustache queue
    templates = []
    for path, details in config.items():
        # fix below 'templates'
        with open(os.path.join('templates', path + '.mustache')) as file:
            template_source = file.read()
        parsed = pystache.parse(template_source)
        templates.append((parsed, details['extension'], details['output']))

    # The URL below should contain a key-value list 
    # of scheme names and github repositories.
    with urllib.request.urlopen(schemes_url) as fileb:
        file = io.TextIOWrapper(fileb)
        repos = yaml.safe_load(file)

    # This code will check out each github repository 
    # and extract the base16 colors defined in each.

    # Name of each color scheme
    scheme_names = []
    # Location of color files
    file_names = []
    
    with tempfile.TemporaryDirectory() as tempdir:
        # repos listed in yaml at url above
        for repo, url in repos.items():
            subprocess.run(
                ['git', 'clone', '--depth=1', url, repo],
                cwd=tempdir,
                check=True)

        # Colors are contained in yaml files
        for schemepath in glob.iglob(os.path.join(tempdir, '**', '*.yaml')):

            scheme_name = os.path.basename(schemepath[:-5])

            # for each repo listed in the yaml file
            with open(schemepath) as schemefile:
                scheme = yaml.safe_load(schemefile)
            context = make_context(scheme)

            # Make matplotlibrc json files
            jsondir = 'mpljson'
            try:
                os.mkdir(jsondir)
            except FileExistsError:
                pass
            filename = os.path.join(jsondir, scheme_name+".json")
            with open (filename, 'w') as f:
                json.dump(context, f)
            # Done making matplotlib json files

            for parsed, extension, outdir in templates:
                filename = os.path.join(
                    outdir,
                    'base16-' + scheme_name + extension
                )

                # Save the name of this color scheme
                scheme_names.append( scheme_name )

                print('render', filename)
                with open(filename, 'w') as file:
                    file.write(
                        pystache.render(parsed, context)
                    )

                file_names.append(filename)

    return file_names, scheme_names


def build_jupyter_config_directories(templates_dir, schemes_url):
    """Initializes and builds Jupyter configuration directories
    for each color scheme.
    """
    # Start by creating CSS files
    # (returns file and schema names)
    file_names, scheme_names = clone_from_config(templates_dir, schemes_url)

    # Now build a jupyter config dir for each color scheme
    import subprocess

    for scheme_name in scheme_names:
    
        # Make the custom config dir
        config_dir = 'configs/'+scheme_name
        custom_dir = config_dir+'/custom'

        # About to make custom config dir for scheme
        subprocess.call(['mkdir','-p',config_dir])
        # Done making custom config dir for scheme

        # Generate config dir
        Popen(["jupyter notebook --generate-config -y"], 
                shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})
        # Done generating custom Jupyter config for scheme

        # Make sure custom css has somewhere to go
        subprocess.call(['mkdir','-p',custom_dir])
        # Install css style into Jupyter config
        ### TODO: FIX
        subprocess.call(['cp','colors/base16-'+scheme_name+'.css',custom_dir+'/custom.css'])
        # Done installing CSS style into Jupyter config.

    return file_names, scheme_names


def get_notebook_schemes(notebooks_dir):
    """Get a list of schemes 
    that have a notebook
    """
    schemes = []
    for notebook_name in glob.glob(notebooks_dir+'/*.ipynb'):
    
        # extract theme names:
        theme = os.path.splitext(notebook_name)[0]
        theme = basename(theme)
        schemes.append(theme)

    return schemes


def convert_notebooks_to_html(config_dir, notebooks_dir, deploy_dir, deploy=True):
    """Convert notebooks to html using custom configurations,
    and optionally (b/c nbconvert is asynchronous)
    copy to deployment directory to be checked into the
    gh-pages branch.
    """
    from subprocess import Popen

    build_jupyter_config_directories(config_file)

    for scheme in get_notebook_schemes():
    
        config_dir = 'configs/'+scheme

        # verify notebooks_dir is a path homie
        nbcmd = "jupyter nbconvert --to html"
        nbcmd += " %s/%s.ipynb"%(notebooks_dir, scheme)

        mvcmd = "mv"
        mvcmd += " %s/%s.html %s/%s.html"%(notebooks_dir, scheme, deploy_dir, scheme)
        
        combined_cmd = nbcmd + " && " + mvcmd

        if(deploy):
            # Convert notebook to html and copy to deploy dir
            Popen([combined_cmd],shell=True,
                env={"JUPYTER_CONFIG_DIR": config_dir})
    
        else:
            # Convert notebook to html only
            Popen([nbcmd],shell=True,
                env={"JUPYTER_CONFIG_DIR": config_dir})
    



    ### ## Start a notebook
    ### #subprocess.call(['JUPYTER_CONFIG_DIR='+config_dir,'jupyter','notebook'])

    ### # Convert notebook to html
    ### # using custom configuration
    ### # jupyter nbconvert --to html mynotebook.ipynb
    ### notebook_loc = '/Users/charles/codes/base16/base16-jupyter/notebooks/'+scheme_name+'.ipynb'
    ### subprocess.call(['JUPYTER_CONFIG_DIR=/Users/charles/codes/base16/base16-jupyter/'+config_dir,'jupyter','nbconvert','--to-html',notebook_loc])


def main():

    templates_dir ='templates'

    schemes ='https://gist.githubusercontent.com/charlesreid1/c7137432a73c7d4dfafc4fa240a67e44/raw/f3676474918879f036609dc6546792930f60d3bb/list.yaml'

    notebooks_dir = 'notebooks'

    deploy_dir = 'site/htdocs'

    # longer list of schemes:
    # https://github.com/chriskempson/base16-schemes-source/raw/master/list.yaml

    # Eventually this will use argparse and set default values 
    # for config/schemes config

    # Parse input:
    if(len(sys.argv)==1):
        task='all'

    elif(len(sys.argv)>2):
        usage()
    
    else:
        task = sys.argv[1]

    print(task)

    if(task=='css'):
        print("About to build CSS files")
        ## Build CSS files for schemes
        f, s = clone_from_config(templates_dir, schemes)
        css_info(templates_dir)

    elif(task=='jupyter'):
        print("About to build Jupyter config directories")
        # Build Jupyter config directories
        f, s = build_jupyter_config_directories(templates_dir, schemes)
        jupyter_info(templates_dir)

    elif(task=='notebooks'):
        print("About to convert Jupyter notebooks to HTML")
        #convert_notebooks_to_html(templates_dir, notebooks_dir, deploy_dir, 
        #        deploy=True)
        notebooks_info(templates_dir, notebooks_dir, deploy_dir)

    elif(task=='all'):
        print("About to perform all tasks")

    else:
        usage()


if __name__=="__main__":
    main()

