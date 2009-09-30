#!/usr/bin/env python
import unittest
import os.path

from pyjasper.client_subreport import JasperGeneratorWithSubreport

class TestReport(JasperGeneratorWithSubreport):

    def __init__(self):
        self.reportrootdir = os.path.join(os.path.dirname(__file__), 'backend', 'tests')
        self.reportbase = "bestellanlage"

        super(TestReport, self).__init__()

        #self.mainreport = os.path.abspath(os.path.join(self.reportrootdir, 'bestellanlage.jrxml'))
        #self.subreportlist = []
        self.xpath = open(os.path.join(self.reportrootdir, 'bestellanlage.xpath')).read()

        #for item in ['bestellanlage-subreport1.jrxml', 'bestellanlage-subreport2.jrxml',
        #                'bestellanlage-subreport3.jrxml']:
        #    self.subreportlist.append(os.path.join(self.reportrootdir, item))

    def get_xml(self, data=None):
        return open(os.path.join(self.reportrootdir, 'bestellanlage.xml')).read()


class TestSequenceFunctions(unittest.TestCase):
    """Test the pyJasper client python interface with subreports."""

    def test_subreports(self):
        """Test a subreport generation."""
        generator = TestReport()

        generator.generate()


if __name__ == '__main__':
    unittest.main()
