#!/usr/bin/env python
# encoding: utf-8
"""
pyJasper clientSubreport.py - Way to access JasperReports from Python using http when using subReports.
This should be able to run under CPython, IronPython, PyPy, Jython or whatever when (simple)json is available.
See https://cybernetics.hudora.biz/projects/wiki/pyJasper for further enligthenment.

Created by Johan Otten on 2009-09-24.
Consider it BSD licensed.
"""

import xml.etree.ElementTree as ET
from cStringIO import StringIO
import os.path

try:
    import json
except ImportError:
    import simplejson as json


from client import JasperClient

__revision__ = '$Revision: 4623 $'


class JasperGeneratorWithSubreport(object):
    """Abstract class for generating Documents with subreports out with Jasperreports with.

    You have to overwrite generate_xml to make meaningfull use of this class. Then call
    YourClass.generate(yourdata). Yourdata is passed to generate_xml() and hopfully you will get
    the generated report back.
    """

    def __init__(self):
        super(JasperGeneratorWithSubreport, self).__init__()

        self.mainreport = os.path.abspath(os.path.join(self.reportrootdir, self.reportbase + '.jrxml'))

        #self.mainreport = None
        self.subreportlist = []

        for filename in os.listdir( os.path.abspath(self.reportrootdir)):
            if filename.startswith(self.reportbase+'-subreport'):
                self.subreportlist.append(os.path.join(self.reportrootdir, filename))

        self.xpath = None

    def generate_xml(self, data=None):
        """To be overwritten by subclasses.

        E.g.
        def generate_xml(self, movement):
            ET.SubElement(self.root, 'generator').text = __revision__
            ET.SubElement(self.root, 'generated_at').text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            xml_movement  =  ET.SubElement(xmlroot, 'movement')
            ET.SubElement(xml_movement, "location_from").text = unicode(movement.location_from)
            return xmlroot
        """
        raise NotImplementedError
    
    def get_xml(self, data=None):
        """Serializes the XML in the ElementTree to be send to JasperReports."""
        root = self.generate_xml(data)
        tree = ET.ElementTree(root)
        buf = StringIO()
        tree.write(buf, encoding="utf-8")
        ret = buf.getvalue()
        buf.close()
        return ret
    
    def generate_pdf(self, data=None):
        """Generates a PDF document by using Jasper-Reports."""
        server = JasperClient()
        designs = {'main': open(self.mainreport).read()}
        for report in self.subreportlist:
            name = str(os.path.splitext(os.path.basename(report))[0])
            designs[name] = open(report).read()

        reportjson = json.dumps(designs)

        xmldata = self.get_xml(data)
        return server.generate_pdf(reportjson, self.xpath, xmldata, multi=True)
    
    def generate(self, data=None):
        """Generates a report, returns the PDF."""
        return self.generate_pdf(data)
