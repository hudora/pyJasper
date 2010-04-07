#!/usr/bin/env python
# encoding: utf-8

"""
pyJasper client.py - Way to access JasperReports from Python using http.
This should be able to run under CPython, IronPython, PyPy, Jython or whatever.
See https://cybernetics.hudora.biz/projects/wiki/pyJasper for further enligthenment.

Created by Maximillian Dornseif on 2007-10-12.
Consider it BSD licensed.
"""

import os
import os.path
import uuid
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from httplib2 import Http


__revision__ = '$Revision$'


class JasperException(RuntimeError):
    """This exception indicates Jasper Server problem."""
    pass


def encode_multipart_formdata(fields):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    # Based on From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$%s' % (uuid.uuid4())
    out = []
    # if it's dict like then use the items method to get the fields
    if hasattr(fields, "items"):
        fields = fields.items()
    for (key, value) in fields:
        out.append('--' + boundary)
        out.append('Content-Disposition: form-data; name="%s"' % key)
        out.append('')
        out.append(value)
    out.append('--' + boundary + '--')
    out.append('')
    body = '\r\n'.join([str(x) for x in out])
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body


def get_reportname(base, *args):
    """
    Construct path for report file relative to base
    
    In most cases, this will be JasperGenerator.__file__
    """
    path = os.path.join(os.path.dirname(base), 'reports', *args)
    return os.path.abspath(path)


class JasperClient(object):
    """Generation of JasperReport documents using the Jetty/Jython Servelet."""
    
    def find_server_url(self):
        """Return the URL of the page where the server lives.
        
        Checks the PYJASPER_SERVLET_URL default variable."""
        
        return os.getenv('PYJASPER_SERVLET_URL', default='http://localhost:8080/pyJasper/jasper.py')
    
    def generate_pdf_server(self, design, xpath, xmldata, multi=False):
        """Generate report via pyJasperServer."""

        url = self.find_server_url()
        if multi:
            content_type, content = encode_multipart_formdata(fields=dict(designs=design, xpath=xpath, 
                                                                      xmldata=xmldata))
        else:
            content_type, content = encode_multipart_formdata(fields=dict(design=design, xpath=xpath, 
                                                                      xmldata=xmldata))

        resp, content = Http().request(url, 'POST', body=content, headers={"Content-Type": content_type})
        if not resp.get('status') == '200':
            raise JasperException("%s -- %r" % (content, resp))
        return content
    
    def generate_pdf(self, design, xpath, xmldata, multi=False):
        """Generate report via pyJasperServer."""
        return self.generate_pdf_server(design, xpath, xmldata, multi)
    

class JasperGenerator(object):
    """Abstract class for generating Documents out with Jasperreports.
    
    You have to overwrite generate_xml to make meaningfull use of this class. Then call
    YourClass.generate(yourdata). Yourdata is passed to generate_xml() and hopfully you will get
    the generated report back.
    """
    
    def __init__(self):
        super(JasperGenerator, self).__init__()
        self.reportname = None
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
        design = open(self.reportname).read()
        xmldata = self.get_xml(data)
        return server.generate_pdf(design, self.xpath, xmldata)
    
    def generate(self, data=None):
        """Generates a report, returns the PDF."""
        return self.generate_pdf(data)
