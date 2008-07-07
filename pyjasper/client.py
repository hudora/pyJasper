#!/usr/bin/env python
# encoding: utf-8
"""
pyJasper client.py - Way to access JasperReports from Python using http.
This should be able to run under CPython, IronPython, PyPy, Jython or whatever.

Created by Maximillian Dornseif on 2007-10-12.
Consider it BSD licensed.
"""

import os.path, uuid
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from httplib2 import Http

__revision__ = '$Revision$'

class JasperException(RuntimeError):
    """This exception indicates Jasper Server problem."""
    pass


# Based on
# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
def encode_multipart_formdata(fields={}):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
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
    body = '\r\n'.join(map(str, out))
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body
    

class JasperClient(object):
    """Generation of JasperReport documents either using the server."""
    
    def find_server_url(self):
        """Return the URL of the page where the server lives.
        
        This is at the moment a static string."""
        
        return 'http://jasper.local.hudora.biz:8080/pyJasper/jasper.py'
        
    
    def generate_pdf_server(self, design, xpath, xmldata):
        """Generate report via pyJasperServer."""
        open('/tmp/pyjasperxml.xml', 'w').write(xmldata)
        url = self.find_server_url()
        content_type, content = encode_multipart_formdata(fields=dict(design=design, xpath=xpath, 
                                                                      xmldata=xmldata))
        resp, content = Http().request(url, 'POST', body=content, headers={"Content-Type": content_type})
        if not resp.get('status') == '200':
            raise JasperException("%s -- %r" % (content, resp))
        return content
        
    
    def generate_pdf(self, design, xpath, xmldata):
        """Generate report via pyJasperServer."""
        return self.generate_pdf_server(design, xpath, xmldata)
        
    

class JasperGenerator(object):
    """Abstract class for generating Documents out with Jasperreports.
    
    You have to overwrite generate_xml to make meaningfull use of this class. Then call
    YourClass.generate(yourdata). Yourdata is passes to generate_xml() and hopfully you will get
    the generated report back.
    """
    
    def __init__(self):
        super(JasperGenerator, self).__init__()
        self.reportname = None
        self.xpath = None
        self.absender = u"HUDORA GmbH\nJägerwald 13\n42897 Remscheid\nGermany\nTel. 02191-609120"
    
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


