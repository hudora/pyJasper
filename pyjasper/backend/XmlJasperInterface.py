"""Jasper Reports Python interface"""
# encoding: utf-8

# based on a slew of java and ruby code, originally coded by jmv,
# tampered with and webserviced by md
# see https://cybernetics.hudora.biz/projects/wiki/pyJasper
# this needs JYTHON to run, CPython will not work!

import hashlib
import os
import sys
import tempfile
import time
#import warnings
import uuid

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.security import KeyStore
from java.util import HashMap as JMap

from com.lowagie.text import Rectangle
from com.lowagie.text.pdf import PdfReader, PdfStamper, PdfSignatureAppearance

from net.sf.jasperreports.engine import JRExporterParameter
from net.sf.jasperreports.engine import JasperExportManager
from net.sf.jasperreports.engine import JasperFillManager
from net.sf.jasperreports.engine.data import JRXmlDataSource
from net.sf.jasperreports.engine.export import JRCsvExporter
from net.sf.jasperreports.engine.export import JRRtfExporter
from net.sf.jasperreports.engine.export import JRHtmlExporter
from net.sf.jasperreports.engine.export import JRTextExporter
from net.sf.jasperreports.engine.export import JRTextExporterParameter
from net.sf.jasperreports.engine.export import JRXlsExporter
from net.sf.jasperreports.engine import JasperCompileManager

TMPDIR = os.path.join(tempfile.gettempdir(), 'pyJasper')

__revision__ = '$Revision$'


def ensure_dirs(dirlist):
    """Ensure that a dir and all its parents exist."""
    for thedir in dirlist:
        if not os.path.exists(thedir):
            os.makedirs(thedir)    


class JasperInterface(object):
    """This is the new style pyJasper Interface"""
    
    def __init__(self, designdatalist, xpath):
        """
        Constructor
        
        Parameters:
        designdatalist: A dictionary of {"template_var_name": "JRXML data"}
        xpath:          The xpath expression passed to the report
        """
        
        # deprecation check
        if isinstance(designdatalist, basestring):
            designdatalist = {'main': designdatalist}

        # Compile design if compiled version doesn't exist
        self.compiled_design = {}
        for design_name in designdatalist:
            self.compiled_design[design_name] = self._update_design(designdatalist[design_name])

        self.xpath = xpath

    def _update_design(self, designdata):
        """Compile the report design if needed."""
        
        designdata_hash = hashlib.md5(designdata.encode('utf-8')).hexdigest()
        sourcepath = os.path.join(TMPDIR, 'reports')
        destinationpath = os.path.join(TMPDIR, 'compiled-reports')
        ensure_dirs([sourcepath, destinationpath])
        source_design = os.path.join(sourcepath, designdata_hash + '.jrxml')
        compiled_design = os.path.join(destinationpath, designdata_hash + '.jasper')
        
        if not os.path.exists(compiled_design):
            fdesc = open(source_design, 'w')
            fdesc.write(designdata.encode('utf-8'))
            fdesc.close()
            
            uid = str(uuid.uuid1())
            JasperCompileManager.compileReportToFile(source_design, compiled_design + uid)
            os.rename(compiled_design + uid, compiled_design)

        return compiled_design
    
    def generate(self, xmldata, output_type='pdf', sign_keyname=None, sign_reason=None, metadata=None):
        """Generate Output with JasperReports."""
        start = time.time()
        xmldata_utf8 = xmldata.encode('utf-8')
        xmlpath = os.path.join(TMPDIR, 'xml')
        outputpath = os.path.join(TMPDIR, 'output')
        oid = "%s-%s" % (hashlib.md5(xmldata_utf8).hexdigest(), uuid.uuid1())
        ensure_dirs([xmlpath, outputpath])
        xmlfile = os.path.join(xmlpath, oid + '.xml')
        fdesc = open(xmlfile, 'w')
        fdesc.write(xmldata_utf8)
        fdesc.close()
        
        output_filename = os.path.abspath(os.path.join(outputpath, oid + '.' + output_type))
        datasource = JRXmlDataSource(xmlfile, self.xpath)

        # convert to a java.util.Map so it can be passed as parameters
        map = JMap()
        for i in self.compiled_design:
            map[i] = self.compiled_design[i]

        # add the original xml document source so subreports can make a new datasource.
        map['XML_FILE'] = xmlfile

        jasper_print = JasperFillManager.fillReport(self.compiled_design['main'], map, datasource)

        if output_type == 'pdf':
            # Get PDF content from JasperReports
            stream = ByteArrayOutputStream()
            JasperExportManager.exportReportToPdfStream(jasper_print, stream)
            
            # Add metadata
            if metadata:
                try:
                    inputstream = ByteArrayInputStream(stream.toByteArray())
                    stream = self.addMetadata(inputstream, metadata)
                except:
                    raise
            
            # Try to sign the PDF file if a keyname is given
            if sign_keyname:
                try:
                    inputstream = ByteArrayInputStream(stream.toByteArray())
                    stream = self.sign(inputstream, sign_keyname, sign_reason)
                except ValueError:
                    raise
            
            # Write PDF to output file
            output_file = open(output_filename, 'wb')
            stream.writeTo(output_file)
            output_file.close()
            
        elif output_type == 'xml':
            output_file = open(output_filename, 'w')
            JasperExportManager.exportReportToXmlStream(jasper_print, output_file)
            output_file.close()
        elif output_type == 'rtf':
            self.generate_rtf(jasper_print, output_filename)
        elif output_type == 'xls':
            self._generate_xls(jasper_print, output_filename)
        elif output_type == 'csv':
            self._generate_csv(jasper_print, output_filename)
        elif output_type == 'text':
            self._generate_text(jasper_print, output_filename)
        elif output_type == 'html':
            self._generate_html(jasper_print, output_filename)
        else:
            raise RuntimeError("Unknown output type %r" % (output_type))
        delta = time.time() - start
        sys.stderr.write('report %r generated in %.3f seconds\n' % (output_filename, delta))
        return open(output_filename, 'rb').read()
    
    def generate_rtf(self, jasper_print, output_filename):
        """Generate RTF output."""
        rtf_exporter = JRRtfExporter()
        rtf_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        rtf_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        rtf_exporter.exportReport()

    def _generate_xls(self, jasper_print, output_filename):
        """Generate XLS output."""
        xls_exporter = JRXlsExporter()
        xls_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        xls_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        xls_exporter.exportReport()

    def _generate_csv(self, jasper_print, output_filename):
        """Generate CSV output."""
        csv_exporter = JRCsvExporter()
        csv_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        csv_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        csv_exporter.exportReport()

    def _generate_text(self, jasper_print, output_filename):
        """Generate Text output."""
        text_exporter = JRTextExporter()
        text_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        text_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        text_exporter.setParameter(JRTextExporterParameter.PAGE_WIDTH, 80)
        text_exporter.setParameter(JRTextExporterParameter.PAGE_HEIGHT, 60)
        text_exporter.exportReport()

    def _generate_html(self, jasper_print, output_filename):
        """Generate HTML output."""
        html_exporter = JRHtmlExporter()
        html_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        html_exporter.setParameter(JRExporterParameter.OUTPUT_FILE_NAME, output_filename)
        html_exporter.exportReport()

    def getKeychain(self, sign_keyname):
        """Get key and chain from a Keystore"""
        
        if not 'PYJASPER_KEYSTORE_FILE' in os.environ:
            raise ValueError('No keychain defined')
        
        password = list(os.environ.get('PYJASPER_KEYSTORE_PASSWORD', ''))
        keystore = KeyStore.getInstance(KeyStore.getDefaultType())
        keystore.load(open(os.environ['PYJASPER_KEYSTORE_FILE']), password)
        if not keystore.containsAlias(sign_keyname):
            raise ValueError('No key named %s' % sign_keyname)
        
        key = keystore.getKey(sign_keyname, password)
        chain = keystore.getCertificateChain(sign_keyname)
        return key, chain

    def sign(self, inputstream, sign_keyname, sign_reason, visible=False):
        """Sign a PDF"""
        
        # This might raise a ValueError which will be catched one stack above
        key, chain = self.getKeychain(sign_keyname)
        
        reader = PdfReader(inputstream)
        outputstream = ByteArrayOutputStream()
        stp = PdfStamper.createSignature(reader, outputstream, "\0")
        sap = stp.getSignatureAppearance()
        sap.setCrypto(key, chain, None, PdfSignatureAppearance.WINCER_SIGNED)
        sap.setCertificationLevel(PdfSignatureAppearance.CERTIFIED_NO_CHANGES_ALLOWED)
        sap.setReason(sign_reason)
        sap.setLocation("Remscheid, Germany")  # TODO: Configure
        if visible:
            sap.setVisibleSignature(Rectangle(100, 100, 200, 200), 1, None)
        stp.close()
        return outputstream

    def addMetadata(self, inputstream, metadata):
        """Adds metadata to a PDF document"""

        reader = PdfReader(inputstream)
        outputstream = ByteArrayOutputStream()
        stp = PdfStamper(reader, outputstream, "\0")
        meta = reader.getInfo()
        for key in ('Subject', 'Author', 'Keywords', 'Title', 'Creator', 'CreationDate'):
            if key in metadata:
                meta.put(key, metadata[key])
        stp.setMoreInfo(meta)
        stp.close()
        return outputstream


def usage():
    """Display usage information."""
    print """XmlJasperInterface usage:
jython XmlJasperInterface.py <design> <xpath> input.xml output.pdf
this will read design.jrxml and compile it to design.jasper
It then will read input.xml and use it with the <xpath> select expression to
generate PDF output to output.pdf.
See net.sf.jasperreports.engine.data.JRXmlDataSource for further information)
"""    


def main(args):
    """command line interface"""
    
    if len(args) != 5:
        usage()
        sys.exit(1)
    
    design = args[1]
    select = args[2]
    input_file = args[3]
    output_file = args[4]
    
    jasper = JasperInterface(open(design).read(), select)
    open(output_file, 'wb').write(jasper.generate(open(input_file, 'r').read(), 'pdf'))
    

if __name__ == '__main__':
    main(sys.argv)
