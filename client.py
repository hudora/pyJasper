#!/usr/bin/env python
# encoding: utf-8
"""
pyJasper client.py - Way  to access JasperReports from Python. This should be able to run under CPython,
IronPython, PyPy, Jython or whatever.

Created by Maximillian Dornseif on 2007-10-12.
Consider it BSD licensed.
"""

import sys, os, os.path, re, copy, time, logging, uuid, httplib
import unittest
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from urllib import urlencode
from httplib2 import Http

class JasperException(RuntimeError):
    """This exception indicates Jasper server problem."""
    pass


# Based on
# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
def encode_multipart_formdata(fields=[], files=[]):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$%s' % (uuid.uuid4())
    CRLF = '\r\n'
    L = []
    # if it's dict like then use the items method to get the fields
    if hasattr(fields, "items"):
        fields = fields.items()
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(map(str,L))
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


class JasperClient(object):
    """Generation of JasperReport documents either using the server or a local client."""
    
    
    # def generate_pdf_locally(self, design_name, xpath, data_name):
    #     """Generates a PDF document by using Jasper-Reports."""
    #     # TODO: this is dublicated code
    #     outfilename = os.path.join(OUTPUTDIRHIER, 'pdf', 
    #                                os.path.splitext(os.path.split(data_name)[-1])[0]) + '.pdf'
    #     os.system('(cd %r; sh XmlJasperInterface.sh %r %r %r )' % (OUTPUTDIRHIER,
    #                 design_name, xpath, data_name))
    #     return outfilename
    
    
    def findServerUrl(self):
        return 'http://jasper.local.hudora.biz:8080/pyJasper/jasper.py'
    
    
    def generate_pdf_server(self, design, xpath, xmldata):
        """Generate report via pyJasperServer."""
        open('/tmp/pyjasperxml.xml', 'w').write(xmldata)
        url = self.findServerUrl()
        content_type, content = encode_multipart_formdata(fields=dict(design=design, xpath=xpath, 
                                                                      xmldata=xmldata))
        resp, content = Http().request(url, 'POST', body=content, headers={"Content-Type": content_type})
        if not resp.get('status') == '200':
            raise JasperException, "%s -- %r" % (content, resp)
        return content
    
    
    def generate_pdf(self, design, xpath, xmldata):
        try:
            return self.generate_pdf_server(design, xpath, xmldata)
        except JasperException, msg:
            logging.error('Problem with server: %s' % (msg,))
            return self.generate_pdf_locally(design, xpath, xmldata)


class JasperGenerator(object):
    """Abstract class for generating Documents out with Jasperreports.
    
    You have to overwrite generate_xml to make meaningfull use of this class. Then call
    YourClass.generate(yourdata). Yourdata is passes to generate_xml() and hopfully you will get
    the generated report back.
    """
    
    def __init__(self):
        super(JasperGenerator, self).__init__()
        self.absender = u"HUDORA GmbH\nJägerwald 13\n42897 Remscheid\nGermany\nTel. 02191-609120"
    
    def generate_xml(self, data=None):
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
        return self.generate_pdf(data)


class myjasperTests(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()
