#!/usr/bin/env python
# encoding: utf-8
"""
pyJasper frontend.py

Created by Maximillian Dornseif on 2006-11-02.
Consider it BSD licensed.
"""

import sys, os, os.path, re, copy, time, logging
import unittest
from huTools import luids
from JasperClient import JasperClient, OUTPUTDIRHIER

try:
    import cElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

class JasperError(RuntimeError):
    pass

class JasperGenerator(object):
    """Abstract class for generating Documents out with Jasperreports"""
    def __init__(self):
        super(JasperGenerator, self).__init__()
        self.absender = u"HUDORA GmbH\nJägerwald 13\n42897 Remscheid\nGermany\nTel. 02191-609120"
    
    def generate_xml(self, data):
        raise NotImplementedError
    
    def write_xml(self, filename, data):
        outfilename = os.path.join(OUTPUTDIRHIER, 'xml', filename + '.xml')
        logging.debug("generating %r" % (outfilename,))
        outfile = open(outfilename, 'w')
        self.generate_xml(data)
        tree = ET.ElementTree(self.root)
        tree.write(outfile, encoding="utf-8")
        outfile.close()
        return outfilename
    
    def generate_pdf(self, filename, data):
        """Generates a PDF document by using Jasper-Reports."""
        start = time.time()
        # TODO: fixme - this is code dublication - outfilename shoulb be handled by pyJasper
        outfilename = os.path.join(OUTPUTDIRHIER, 'pdf', filename) + '.pdf'
        xmlfilename = self.write_xml(filename, data)
        logging.debug("generating %r" % (outfilename,))
        server = JasperClient()
        ret = server.generate_pdf(self.reportname, self.xpath, xmlfilename)
        if ret != outfilename:
           raise ProgrammingError, 'name difference: %r %r' % (ret, outfilename)
        logging.info('generated %r in %.3fs' % (outfilename, time.time() - start))
        if not os.path.exists(outfilename) or os.path.getsize(outfilename) == 0:
            raise JasperError, "PDF generation failed for %r" % (outfilename, )
        return outfilename

    def generate(self, data, repid=None):
        if not repid:
            # TODO: use hutools.luids
            repid = luids.unique_hostname()
        # filename based on class name
        filename = re.sub('[^0-9a-zA-Z_-]', '', str(self.__class__).split('.')[-1] + '-' + str(repid))
        return self.generate_pdf(filename, data)


class myjasperTests(unittest.TestCase):
    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()
