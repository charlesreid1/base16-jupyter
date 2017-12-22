#!/usr/bin/env python3

import sys, io, os
import subprocess
from subprocess import Popen
import tempfile
import glob
import urllib.request
import pystache, yaml
import json
import re
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)



BASE16_SCHEMES_LIST = 'https://gist.githubusercontent.com/charlesreid1/c7137432a73c7d4dfafc4fa240a67e44/raw/f3676474918879f036609dc6546792930f60d3bb/list.yaml'



"""
build.py:

    This script builds the following:
    - CSS files from templates
    - Jupyter custom config directories
    - Schemes into custom config directories

    Usage:

        python build.py [command]

    List of commands:

        python build.py css
        python build.py jupyter
        python build.py pyplot
        python build.py notebooks
        python build.py all

    css command:
    * Turns CSS templates into CSS output files

    jupyter command:
    * Turns CSS templates into Jupyter custom config directories

    pyplot command:
    * Installs IPython magic to load pyplot color schemes

    notebooks:
    * jupyter nbconvert with configs 

    all:
    * Turns CSS tmplates into CSS output files
    * Creates Jupyter config directory for each scheme
    * Installs IPython magic to load pyplot color schemes
    * Runs nbconvert to create example notebooks
"""

def usage():
    print("""
    build.py usage:

        python build.py [command]

        commands:
            css
            jupyter
            pyplot
            notebooks
            all
    """)


def css_info(templates_dir):
    ran("css")
    print("CSS files have been built from templates in %s"%(templates_dir))
    print("files: config.yaml, default.mustache")


def jupyter_info(templates_dir):
    ran("jupyter")
    print("jupyter config files have been built from templates %s"%(templates_dir))
    print("files: config.yaml, default.mustache, configs/")


def pyplot_info(templates_dir):
    ran("pyplot")
    print("Normally, we would do some pyplot stuff here.")
    print("However, we have no idea what we are doing.")


def notebooks_info(templates_dir, notebooks_dir, deploy_dir):
    ran("notebooks")
    print("jupyter config files have been built from templates %s"%(templates_dir))
    print("built from notebooks in %s"%(notebooks_dir))
    print("converted to html in %s"%(deploy_dir))


def ran(cmd):
    print("\nYou ran the command:\n\n")
    print("\t python build.py %s"%(cmd))
    print("\n")


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


def build_jupyter_config_directories(templates_dir, schemes_url, config_dir='configs'):
    """Initializes and builds Jupyter configuration directories
    for each color scheme.
    """
    # Start by creating CSS files
    # (returns file and schema names)
    file_names, scheme_names = clone_from_config(templates_dir, schemes_url)

    # Now build a jupyter config dir for each color scheme
    import subprocess

    # Should validate this first.
    subprocess.call(['mkdir','-p',config_dir])

    for scheme_name in scheme_names:
    
        # Make the custom config dir
        config_dir_full = config_dir+'/'+scheme_name
        custom_dir = config_dir_full+'/custom'

        # About to make custom config dir for scheme
        subprocess.call(['mkdir','-p',config_dir_full])
        # Done making custom config dir for scheme

        # Generate config dir
        Popen(["jupyter notebook --generate-config -y"], 
                shell=True, env={"JUPYTER_CONFIG_DIR": config_dir_full})
        # Done generating custom Jupyter config for scheme

        # Make sure custom css has somewhere to go
        subprocess.call(['mkdir','-p',custom_dir])
        # Install css style into Jupyter config
        ### TODO: FIX
        subprocess.call(['cp','colors/base16-'+scheme_name+'.css',custom_dir+'/custom.css'])
        # Done installing CSS style into Jupyter config.

    return file_names, scheme_names


def do_pyplot_stuff():
    """
    Install IPython notebook magic to load up
    matplotlib/pyplot color schemes. 

    The color schemes live in ~/.jupyter (?)

    The color schemes are built using (?)

    See ../cmr-base16-ipython-matplotlib



    Input arguments?
    * templates dir
    * schemes url
    * config dir
    """
    pass


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


def convert_notebooks_to_html(templates_dir, schemes_url, config_dir, 
                              notebooks_dir, deploy_dir, deploy=True):

    """Convert notebooks to html using custom configurations,
    and optionally (b/c nbconvert is asynchronous)
    copy to deployment directory to be checked into the
    gh-pages branch.

    config_dir should be destination for jupyter configuration files:
        configs/

    notebooks_dir should be where notebooks are located, by default:
        notebooks/

    deploy_dir should be where the gh-pages branch is deployed, by default:
        site/htdocs

    """
    from subprocess import Popen

    # Start by building the Jupyter notebook configuration files to config
    file_names, scheme_names = build_jupyter_config_directories(templates_dir, schemes_url, config_dir)

    #for scheme_name in scheme_names:
    for scheme_name in get_notebook_schemes():
    
        config_dir_full = config_dir + '/' + scheme_name

        # verify notebooks_dir is a path homie
        nbcmd = "jupyter nbconvert --to html"
        nbcmd += " %s/%s.ipynb"%(notebooks_dir, scheme_name)

        mvcmd = "mv"
        mvcmd += " %s/%s.html %s/%s.html"%(notebooks_dir, scheme_name, deploy_dir, scheme_name)
        
        combined_cmd = nbcmd + " && " + mvcmd

        if(deploy):
            # Convert notebook to html and copy to deploy dir
            Popen([combined_cmd],shell=True,
                env={"JUPYTER_CONFIG_DIR": config_dir_full})
    
        else:
            # Convert notebook to html only
            Popen([nbcmd],shell=True,
                env={"JUPYTER_CONFIG_DIR": config_dir_full})
    



    ### ## Start a notebook
    ### #subprocess.call(['JUPYTER_CONFIG_DIR='+config_dir,'jupyter','notebook'])

    ### # Convert notebook to html
    ### # using custom configuration
    ### # jupyter nbconvert --to html mynotebook.ipynb
    ### notebook_loc = '/Users/charles/codes/base16/base16-jupyter/notebooks/'+scheme_name+'.ipynb'
    ### subprocess.call(['JUPYTER_CONFIG_DIR=/Users/charles/codes/base16/base16-jupyter/'+config_dir,'jupyter','nbconvert','--to-html',notebook_loc])





def do_matplotlib_stuff(templates_dir, schemes_url):
    """Theme the inline backend of matplotlib using base16 schemes.
    Inline magic will look like this:

    %base16-mplrc <theme>

    The extension defines magic configuring 
    InlineBackend.rc to match active base16
    custom.css file, if present.
    """
    # Start by building the Jupyter notebook configuration files to config
    build_jupyter_config_directories(config_file)


    #
    # how should this be handled?
    # install all themes?
    # then when config passed, loads the theme too?
    # still specify magic in notebook?
    #
    # in spirit of original, 
    # keep notebook markup,
    # to mix and match styles.
    #
    # install all themes, user specifies 
    # using notebook magic.


    # TODO: fix scope
    @magics_class
    class MPLRCMagics(Magics):
        def __init__(self,shell): 
            super(MPLRCMagics,self).__init__(shell)
    
        # Decorators make this magic accept arguments
        @line_magic
        @magic_arguments()
        @argument('theme', nargs='?', default=None, help='base16 theme')
        def base16_mplrc(self,args):
            """base16_mplrc defines magic invoked with %base16_mplrc.

                args:
                    theme : base16 theme to use
            """
            # Parse the magic arguments
            # https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.magic_arguments.html
            args = parse_argstring(self.base16_mplrc, args)
            theme = args.theme

            # Detect the base16 ipython notebook theme, 
            # setup the matplotlib rc
            css_theme = None
            custom_css_fname = self.shell.profile_dir.location+'/custom/custom.css'
            if os.path.exists(custom_css_fname):
                with open(custom_css_fname) as css_file:
                    for line in css_file:
                        if(re.match('^\s*Name: ',line)):
                            css_theme = line.split()[2].lower()
    
            # Fall back on sensible defaults
            if theme is None:
                theme = css_theme
            if theme is None:
                print('''
                         Could not detect base-16 ipython notebook theme. Download base16 theme notebook theme
                         from https://github.com/nsonnad/base16-ipython-notebook . Using \'default\' theme.''')
                theme='default'
    
            # TODO: fixme
            #### old:
            ###jsondir = '/Users/charles/codes/base16/base16-jupyter/mpljson'
            # new:
            jsondir = 'mpljson'
            avail_themes = [os.path.split(f)[-1].split('.')[0] for f in glob.glob(jsondir + '/*.json')]
            #validate input
            if theme not in avail_themes:
                print("theme must be present in base16-mplrc-themes dir, defaulting to 'default'")
                print("Available themes:")
                for t in avail_themes:
                    print("\t{}".format(t))
                theme = 'default'
    
            print("Setting plotting theme to {}. Palette available in b16_colors".format(theme))
    
            theme_colors = json.load(open(jsondir+'/'+theme+'.json'))
    
            #snag the matplotlibrc configuration from the ipython config
            #### old IPython:
            ###from IPython.kernel.zmq.pylab.backend_inline import InlineBackend
            # new ipykernel:
            from ipykernel.pylab.config import InlineBackend

            cfg = InlineBackend.instance(parent=self.shell)
            cfg.shell=self.shell
            if cfg not in self.shell.configurables:
                self.shell.configurables.append(cfg)
            if True:
                 cfg.rc = {'figure.facecolor':theme_colors['base00'],
                            'savefig.facecolor':theme_colors['base00'],
                            'text.color':theme_colors['base07'],
                            'axes.color_cycle':[theme_colors['base{:02X}'.format(i)] for i in [13,8,11,9,12,14,10,15]],
                            'axes.facecolor': theme_colors['base01'],
                            'axes.edgecolor': theme_colors['base01'],
                            'axes.labelcolor': theme_colors['base07'],
                            'lines.color': theme_colors['base09'],
                            'lines.markeredgewidth': 0,
                            'patch.facecolor': theme_colors['base09'],
                            'patch.edgecolor': theme_colors['base02'],
                            'xtick.color': theme_colors['base07'],
                            'ytick.color': theme_colors['base07'],
                            'grid.color': theme_colors['base02']}

            #If pyplot is already using the InlineBackend, this will force an update to the rcParams
    
            from matplotlib import pyplot, cm
            from matplotlib.colors import ColorConverter, ListedColormap
            import numpy as np
    
            conv = ColorConverter()
            if pyplot.rcParams['backend'] == 'module://ipykernel.pylab.backend_inline':
    
                #push the color pallete into scope for the user
                full=['red','orange','yellow','green','cyan','blue','magenta','brown']
                abbr=['r','o','y','g','c','b','m','n']
                #create a color palette class
                class Palette(object): pass
                b16_colors=Palette()
                for f,a,i in zip(full,abbr,range(8,16)):
                    setattr(b16_colors,f,conv.to_rgb(theme_colors['base{:02X}'.format(i)]))
                    setattr(b16_colors,a,conv.to_rgb(theme_colors['base{:02X}'.format(i)]))
    
                setattr(b16_colors,'white',conv.to_rgb(theme_colors['base07']))
                setattr(b16_colors,'w',conv.to_rgb(theme_colors['base07']))
                setattr(b16_colors,'black',conv.to_rgb(theme_colors['base00']))
                setattr(b16_colors,'k',conv.to_rgb(theme_colors['base00']))
    
                #----------------- Color maps ---------------------#
                def make_gradient(cols):
                    N=255
                    M=int(np.ceil(N/len(cols)))
                    reds = np.empty((0),dtype=np.float)
                    blues = np.empty((0),dtype=np.float)
                    greens = np.empty((0),dtype=np.float)
                    for c0,c1 in zip(cols[:-1],cols[1:]):
                        reds = np.concatenate((reds,np.linspace(c0[0],c1[0],M-1)))
                        greens = np.concatenate((greens,np.linspace(c0[1],c1[1],M-1)))
                        blues = np.concatenate((blues,np.linspace(c0[2],c1[2],M-1)))
                    return np.array((reds,greens,blues)).transpose()
    
                #Make a "jet" colormap
                cols =[b16_colors.b,
                       b16_colors.c,
                       b16_colors.g,
                       b16_colors.y,
                       b16_colors.o,
                       b16_colors.r]
                b16_colors.jet = ListedColormap(make_gradient(cols),name='b16_jet')
                cm.register_cmap('b16_jet',b16_colors.jet)
    
                #Make a "grayscale" colormap
                cols = [conv.to_rgb(theme_colors['base{:02X}'.format(i)]) for i in range(8)]
                b16_colors.gray = ListedColormap(make_gradient(cols),name='b16_gray')
                cm.register_cmap('b16_gray',b16_colors.gray)
    
                #Make a "blues" colormap
                cols = [b16_colors.w,b16_colors.c,b16_colors.b]
                b16_colors.blues = ListedColormap(make_gradient(cols),name='b16_blues')
                cm.register_cmap('b16_blues',b16_colors.blues)
    
                #Make a "greens" colormap
                cols = [b16_colors.w,b16_colors.c,b16_colors.g]
                b16_colors.greens = ListedColormap(make_gradient(cols),name='b16_greens')
                cm.register_cmap('b16_greens',b16_colors.greens)
    
                #Make a "oranges" colormap
                cols = [b16_colors.w,b16_colors.y,b16_colors.o]
                b16_colors.oranges = ListedColormap(make_gradient(cols),name='b16_oranges')
                cm.register_cmap('b16_oranges',b16_colors.oranges)
    
                #Make a "reds" colormap
                cols = [b16_colors.w,b16_colors.y,b16_colors.o,b16_colors.r]
                b16_colors.reds = ListedColormap(make_gradient(cols),name='b16_reds')
                cm.register_cmap('b16_reds',b16_colors.reds)
    
                #Make a "flame" colormap
                cols = [conv.to_rgb(theme_colors['base{:02X}'.format(i)]) for i in range(0,3,2)]+\
                       [b16_colors.y,b16_colors.o,b16_colors.r]
                b16_colors.flame = ListedColormap(make_gradient(cols),name='b16_flame')
                cm.register_cmap('b16_flame',b16_colors.flame)
    
                #Make a "brbg" colormap
                cols = [b16_colors.n,b16_colors.w,b16_colors.b,b16_colors.g]
                b16_colors.brbg = ListedColormap(make_gradient(cols),name='b16_brbg')
                cm.register_cmap('b16_brbg',b16_colors.brbg)
    
                self.shell.push({"b16_colors":b16_colors})
                cfg.rc.update({'image.cmap':'b16_flame'})
    
                pyplot.rcParams.update(cfg.rc)


def load_ipython_extension(ipython):
    ipython.register_magics(MPLRCMagics)



def main():

    templates_dir ='templates'

    schemes = BASE16_SCHEMES_LIST

    jupyter_config_dir = 'configs'

    notebooks_dir = 'notebooks'

    deploy_dir = 'site/htdocs'

    # longer list of schemes:
    # https://github.com/chriskempson/base16-schemes-source/raw/master/list.yaml

    # Eventually this will use argparse and set default values 
    # for config/schemes config

    # Parse input:
    if(len(sys.argv)==1):
        usage()
        exit()

    elif(len(sys.argv)>2):
        usage()
        exit()
    
    else:
        task = sys.argv[1]

    if(task=='css'):
        print("About to build CSS files")
        # Build CSS files for schemes
        f, s = clone_from_config(templates_dir, schemes)
        css_info(templates_dir)

    elif(task=='jupyter'):
        print("About to build Jupyter config directories")
        # Build Jupyter config directories
        f, s = build_jupyter_config_directories(templates_dir, schemes, jupyter_config_dir)
        jupyter_info(templates_dir)

    elif(task=='pyplot'):
        print("About to install nb magic and pyplot color schemes")
        # notebook magic and pyplot
        pyplot_info(templates_dir)

    elif(task=='notebooks'):
        print("About to convert Jupyter notebooks to HTML")
        convert_notebooks_to_html(templates_dir, schemes, jupyter_config_dir, 
                notebooks_dir, deploy_dir, 
                deploy=True)
        notebooks_info(templates_dir, schemes, notebooks_dir, deploy_dir)

    elif(task=='all'):
        print("About to perform all tasks")

    else:
        usage()


if __name__=="__main__":
    main()

