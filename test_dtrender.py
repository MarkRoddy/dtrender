
import json
from StringIO import StringIO
from unittest import TestCase, main

from dtrender import TemplateRenderer

class TestTemplateRenderer(TestCase):

    def testAddValues_DataDecoded(self):
        data = dict(foo = 'bar', biz = 'baz', bling = 'hova')
        buff = StringIO(json.dumps(data))
        tr = TemplateRenderer()
        tr.add_values(buff)
        self.assertEqual(data, tr._ValuesToRender)

    def testAddValues_ErrorOnNonDictDataStructure(self):
        data = [1,2,3,4]
        buff = StringIO(json.dumps(data))
        tr = TemplateRenderer()
        self.assertRaises(TypeError, tr.add_values, buff)

    def testRenderedTemplate(self):
        template_text = """
        foo bar
        {{ foo }}
        baz
        {{ biz }}
        """
        data = dict(foo = '1', biz = '2')
        inbuff = StringIO(json.dumps(data))
        tr = TemplateRenderer()
        tr.add_values(inbuff)
        expected_output = """
        foo bar
        1
        baz
        2
        """
        outbuff = StringIO()

        tr._SetupDjango()
        from django.template import Template

        template = Template(template_text)
        tr.render(template, outbuff)
        self.assertEqual(expected_output, outbuff.getvalue())


if __name__ == '__main__':
    main()
