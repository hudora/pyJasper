"""Jasper Reports Python interface"""
# encoding: utf-8

# based on a slew of java and ruby code, originally coded by jmv,
# tampered with and webserviced by md
# see https://cybernetics.hudora.biz/projects/wiki/pyJasper
# this needs JYTHON to run, CPython will not work!

import codecs
import hashlib
import os
import sys
import tempfile
import uuid

from com.lowagie.text.pdf import PdfReader, PdfStamper, PdfSignatureAppearance
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.security import KeyStore
from net.sf.jasperreports.engine import JasperCompileManager
from net.sf.jasperreports.engine import JasperExportManager
from net.sf.jasperreports.engine import JasperFillManager
from net.sf.jasperreports.engine import JRExporterParameter
from net.sf.jasperreports.engine.data import JRXmlDataSource
from net.sf.jasperreports.engine.export import JRCsvExporter
from net.sf.jasperreports.engine.export import JRHtmlExporter
from net.sf.jasperreports.engine.export import JRRtfExporter
from net.sf.jasperreports.engine.export import JRTextExporter
from net.sf.jasperreports.engine.export import JRTextExporterParameter
from net.sf.jasperreports.engine.export import JRXlsExporter


def concat_filename(dirname, filename):
    """Create filename in subdirectory of pyJasper temporary directory"""

    tmpdir = os.path.join(tempfile.gettempdir(), 'pyJasper')
    path = os.path.join(tmpdir, dirname)
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, filename)


def make_hash(unicodeobj):
    return hashlib.new('md5', unicodeobj.encode('utf-8')).hexdigest()


def _update_report(data):
    """Compile the report design if needed."""

    report_hash = make_hash(data)
    compiled_report = concat_filename('compiled-reports', report_hash + '.jasper')
    if not os.path.exists(compiled_report):
        sourcefile = concat_filename('reports', report_hash + '.jrxml')
        with codecs.open(sourcefile, 'w', 'utf-8') as fileobj:
            fileobj.write(data)

        uid = str(uuid.uuid1())
        JasperCompileManager.compileReportToFile(sourcefile, compiled_report + uid)
        os.rename(compiled_report + uid, compiled_report)

    return compiled_report


class JasperInterface(object):
    """This is the new style pyJasper Interface"""

    def __init__(self, report, xpath=None):
        """
        Constructor

        Parameters:
        report: XML-Data of JasperReport document
        xpath: The xpath expression passed to the report.
        """

        # Compile design if compiled version doesn't exist
        self.compiled_report = _update_report(report)
        self.xpath = xpath

    def generate(self, source, sign_keyname=None, sign_reason=None, metadata=None):
        """Generate Output with JasperReports."""

        oid = '{}-{}'.format(make_hash(source), uuid.uuid1())

        xmlfile = concat_filename('xml', oid + '.xml')
        with codecs.open(xmlfile, 'w', 'utf-8') as fileobj:
            fileobj.write(source)

        datasource = JRXmlDataSource(xmlfile, self.xpath)
        # Fill Report without parameters
        jasper_print = JasperFillManager.fillReport(self.compiled_report, None, datasource)

        stream = self._generate_pdf(jasper_print, metadata, sign_keyname, sign_reason)

        # # Warum eigentlich?
        # output_filename = concat_filename('output', oid + '.pdf')
        # with open(output_filename, 'wb') as output_file:
        #     stream.writeTo(output_file)

        return stream

    def _generate_pdf(self, jasper_print, metadata=None, sign_keyname=None, sign_reason=''):
        """Generate and sign PDF document"""

        stream = ByteArrayOutputStream()
        JasperExportManager.exportReportToPdfStream(jasper_print, stream)

        # Add metadata and sign document
        if metadata or sign_keyname:
            stream = addMetadataAndSign(stream, metadata, sign_keyname, sign_reason)

        # Write PDF to output file
        return stream


def getKeychain(sign_keyname):
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


def addMetadataAndSign(inputstream, metadata, sign_keyname, sign_reason):
    """Add meta data and sign PDF"""

    reader = PdfReader(ByteArrayInputStream(inputstream.toByteArray()))
    outputstream = ByteArrayOutputStream()
    stamper = PdfStamper.createSignature(reader, outputstream, '\0')

    if metadata:
        info = reader.getInfo()
        for key in 'Subject', 'Author', 'Keywords', 'Title', 'Creator', 'CreationDate':
            if key in metadata:
                info.put(key, metadata[key])
        stamper.setMoreInfo(info)

    if sign_keyname:
        # This might raise a ValueError which will be catched one stack above
        key, chain = getKeychain(sign_keyname)

        sap = stamper.getSignatureAppearance()
        sap.setCrypto(key, chain, None, PdfSignatureAppearance.WINCER_SIGNED)
        sap.setCertificationLevel(PdfSignatureAppearance.CERTIFIED_NO_CHANGES_ALLOWED)
        sap.setReason(sign_reason)
        # Kann man evtl. Metadaten an den Key hängen?
        sap.setLocation("Remscheid, Germany")  # TODO: Configure

    stamper.close()
    return outputstream
