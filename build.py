#!/usr/bin/env python3

import io
import os
import subprocess
from subprocess import Popen
import tempfile
import glob
import urllib.request

import pystache
import yaml


def make_context(scheme):
    context = {}
    context['scheme-name'] = scheme['scheme']
    context['scheme-author'] = scheme['author']
    for base in range(16):
        context[f'base{base:02X}-hex'] = scheme[f'base{base:02X}']
    return context

with open('templates/config.yaml') as file:
    config = yaml.safe_load(file)

templates = []
for path, details in config.items():
    with open(os.path.join('templates', path + '.mustache')) as file:
        template_source = file.read()
    parsed = pystache.parse(template_source)
    templates.append((parsed, details['extension'], details['output']))

#with urllib.request.urlopen('https://github.com/chriskempson/base16-schemes-source/raw/master/list.yaml') as fileb:
with urllib.request.urlopen('https://gist.githubusercontent.com/charlesreid1/c7137432a73c7d4dfafc4fa240a67e44/raw/f3676474918879f036609dc6546792930f60d3bb/list.yaml') as fileb:
    file = io.TextIOWrapper(fileb)
    repos = yaml.safe_load(file)

scheme_names = []
file_names = []

with tempfile.TemporaryDirectory() as tempdir:
    # repos listed in yaml at url above
    for repo, url in repos.items():
        subprocess.run(
            ['git', 'clone', '--depth=1', url, repo],
            cwd=tempdir,
            check=True)
    for schemepath in glob.iglob(os.path.join(tempdir, '**', '*.yaml')):
        # for each repo listed in the yaml file
        with open(schemepath) as schemefile:
            scheme = yaml.safe_load(schemefile)
        context = make_context(scheme)
        for parsed, extension, outdir in templates:
            filename = os.path.join(
                outdir,
                'base16-' + os.path.basename(schemepath[:-5]) + extension
            )
            scheme_names.append( os.path.basename(schemepath[:-5]) )
            print('render', filename)
            with open(filename, 'w') as file:
                file.write(
                    pystache.render(parsed, context)
                )
            file_names.append(filename)

# Now build a jupyter config dir 
# for each color scheme
import subprocess

print(file_names)

for scheme_name in scheme_names:

    # Make the custom config dir
    config_dir = 'configs/'+scheme_name
    custom_dir = config_dir+'/custom'

    print("about to make custom config dir for %s"%(scheme_name))

    subprocess.call(['mkdir','-p',config_dir])

    print("finished making custom config dir for %s"%(scheme_name))


    print("about to jupyter custom config generate config for %s at: %s"%(scheme_name, config_dir))

    # Generate config dir
    Popen(["jupyter notebook --generate-config -y"], shell=True, env={"JUPYTER_CONFIG_DIR": config_dir})

    print("finished jupyter generating config dir for %s at: %s"%(scheme_name, config_dir))


    # Make sure custom css has somewhere to go
    subprocess.call(['mkdir','-p',custom_dir])

    # Install css style
    subprocess.call(['cp','/Users/charles/codes/base16/base16-jupyter/colors/base16-'+scheme_name+'.css',custom_dir+'/custom.css'])

    print("finished installing css style at %s"%( custom_dir+'/custom.css'))



    ### ## Start a notebook
    ### #subprocess.call(['JUPYTER_CONFIG_DIR='+config_dir,'jupyter','notebook'])

    ### # Convert notebook to html
    ### # using custom configuration
    ### # jupyter nbconvert --to html mynotebook.ipynb
    ### notebook_loc = '/Users/charles/codes/base16/base16-jupyter/notebooks/'+scheme_name+'.ipynb'
    ### subprocess.call(['JUPYTER_CONFIG_DIR=/Users/charles/codes/base16/base16-jupyter/'+config_dir,'jupyter','nbconvert','--to-html',notebook_loc])



