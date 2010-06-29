
import os
import sys
import json
from optparse import OptionParser

class TemplateRenderer(object):
    """
    Renders Django templates and exports their output to
    various locations.
    """

    _ValueSeperator = '='
    _DebugTemplates = False
    _IsDjangoConfigured = False

    _Template_Name = None
    _TemplateDirectoryPaths = None
    _ValuesToRender = None


    def __init__(self):
        """
        Template can be the name of a template in the search path
        or a string containing the text of the template
        """
        self._ValuesToRender = {}
        self._TemplateDirectoryPaths = []

    def add_values(self, stream):
        """
        Parse a file like object containing json encoded data
        to be used to render the template
        """
        data = json.load(stream)
        self._ValuesToRender.update( data)

    def add_value(self, key, value):
        """
        Add a single key/value to be used to render the template.
        """
        self._ValuesToRender[key] = value
    
    def _SetupDjango(self):
        """
        Perform properly ordered import of Django modules as well as configuration
        required in order to perform said import(s)
        """
        if self._IsDjangoConfigured:
            return
        if not self._TemplateDirectoryPaths:
            self._TemplateDirectoryPaths = ('.',)
        from django.conf import settings
        settings.configure(TEMPLATE_DIRS=self._TemplateDirectoryPaths,
                           DEBUG=False,TEMPLATE_DEBUG=self._DebugTemplates)
        import django.template.loader
        self._IsDjangoConfigured = True

    def make_template(self, template):
        """
        Create a django template object from a variety of sources.
        template could be:
        1) Path to a file on disc which contains the template
        2) Name of a template resolvable by django
        """
        self._SetupDjango() # Don't remove me or nastiness happens
        from django.template import Template, loader, TemplateDoesNotExist
        if os.path.exists(template):
            with open(template, 'r') as f:
                return Template(f.read())
        else:
            try:
                return loader.get_template(template)
            except TemplateDoesNotExist as e:
                raise ValueError("Template '%s' does not appear to exist" % str(e))

    def render(self, template, stream):
        """
        Render the template with the values supplied thus far
        """
        self._SetupDjango() # Don't remove me or nastiness happens

        from django.template import Context

        t = template
        ctx=Context(self._ValuesToRender)
        stream.write(t.render(ctx))
        
   
    
def main(args):
    parser = OptionParser("usage: %prog [-o file] [-i file] [--value name1=value --value name2=value ...] template")
    parser.add_option('--search-path-template', dest='template_search_path', default='.', action = 'store',
                      help = 'Comma seperated list of directories to search for templates (defaults to ".")')
    parser.add_option('-o', '--out-file', dest='output_file', default = '', action = 'store',
                      help = 'Path to write rendered template to.  Defaults to stdout')
    parser.add_option('-i', '--in-file', dest='input_file', default = '', action = 'store',
                      help = 'Path to file containing JSON encoded values to populate the template.  Specify \'-\' to use stdin')
    parser.add_option('--value', dest='template_values', action = 'append',
                      help = 'name=value pair to be populated in the template.  This option may be specified more than once')
    options, args = parser.parse_args(args)
    if 2 != len(args):
        parser.print_usage()
        return 1
    else:
        template_spec = args[1]
    
    tr = TemplateRenderer()
    if options.output_file:
        outfile = open(options.output_file, 'w')
    else:
        outfile = sys.stdout
    if options.input_file:
        if '-' == options.input_file:
            infile = sys.stdin
        else:
            infile = open(options.input_file, 'r')
    else:
        infile = None

    try:
        template = tr.make_template(template_spec)
    except ValueError as e:
        sys.stderr.write(str(e) + '\n')
        return 1

    if infile:
        tr.add_values(infile)
    for item in options.template_values:
        name, value = item.split('=',1)
        tr.add_value(name,value)
    tr.render(template, outfile)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
