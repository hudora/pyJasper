"""Jasper Reports Python interface"""

# based on a slew of java and ruby code, originally coded by jmv, tampered with by md
# this needs JYTHON to run, CPython will not work!

import os, os.path, sys, time, md5

from net.sf.jasperreports.engine import JRException
from net.sf.jasperreports.engine import JRExporterParameter
from net.sf.jasperreports.engine import JasperExportManager
from net.sf.jasperreports.engine import JasperFillManager
from net.sf.jasperreports.engine import JasperPrint
from net.sf.jasperreports.engine.data import JRXmlDataSource
from net.sf.jasperreports.engine.export import JRCsvExporter
from net.sf.jasperreports.engine.export import JRRtfExporter
from net.sf.jasperreports.engine.export import JRXlsExporter
from net.sf.jasperreports.engine.export import JRXlsExporterParameter
from net.sf.jasperreports.engine import JasperCompileManager

TMPDIR = '/tmp/pyJasper'

# Obsolete
class XmlJasperInterface:
    def __init__(self, design, select_criteria):
        # Compile desin if compiled version doesn't exist or older than source
        source_design = os.path.join('reports', design + '.jrxml')
        compiled_design = os.path.join('compiled-reports', design + '.jasper')
        JasperCompileManager.compileReportToFile(source_design, compiled_design)
        self.compiled_design = compiled_design
        self.select_criteria = select_criteria
    
    def report(self, data_file, output_type='pdf'):
        start = time.time()
        output_name = os.path.splitext(os.path.basename(data_file))[0] + '.' + output_type
        output_filename = os.path.abspath(os.path.join(output_type, output_name))
        output_file = open(output_filename, 'w')
        print "generating report %r from datafile %r to %r with XPATH %r" % (self.compiled_design,
                      data_file, output_file, self.select_criteria)
        datasource = JRXmlDataSource(data_file, self.select_criteria)
        jasper_print = JasperFillManager.fillReport(self.compiled_design, None, datasource)
        if output_type == 'pdf':
            JasperExportManager.exportReportToPdfStream(jasper_print, output_file)
        elif output_type == 'xml':
            JasperExportManager.exportReportToXmlStream(jasper_print, output_file)
        elif output_type == 'rtf':
            rtf_exporter = JRRtfExporter()
            rtf_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
            rtf_exporter.setParameter(JRExporterParameter.OUTPUT_STREAM, output_file)
            rtf_exporter.exportReport()
        elif output_type == 'xls':
            xls_exporter = JRXlsExporter()
            xls_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
            xls_exporter.setParameter(JRExporterParameter.OUTPUT_STREAM, output_file)
            xls_exporter.setParameter(JRXlsExporterParameter.IS_ONE_PAGE_PER_SHEET, 1)
            xls_exporter.exportReport()
        elif output_type == 'csv':
            csv_exporter = JRCsvExporter()
            csv_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
            csv_exporter.setParameter(JRExporterParameter.OUTPUT_STREAM, output_file)
            csv_exporter.exportReport()
        else:
            raise RuntimeError, "Unknown output type %r" % (output_type)
        delta = time.time() - start
        print 'report %r generated in %.3f seconds' % (output_filename, delta)
        return output_filename

def ensure_dirs(dirlist):
    for thedir in dirlist:
        if not os.path.exists(thedir):
            os.makedirs(thedir)

class JasperInterface:
    """This is ne new style pyJasper Interface"""
    
    def __init__(self, designdata, xpath):
        # Compile desin if compiled version doesn't exist or older than source
        self.compiled_design = self._update_design(designdata)
        self.xpath = xpath
    
    def _update_design(self, designdata):
        md5hash = md5.new(designdata).hexdigest()
        sourcepath = os.path.join(TMPDIR, 'reports')
        destinationpath = os.path.join(TMPDIR, 'compiled-reports')
        ensure_dirs([sourcepath, destinationpath])
        source_design = os.path.join(sourcepath, md5hash + '.jrxml')
        compiled_design = os.path.join(destinationpath, md5hash + '.jasper')
        
        if not os.path.exists(source_design):
            # TODO: fix race conditions
            fd = open(source_design, 'w')
            fd.write(designdata) #.encode('utf-8'))
            fd.close()
            JasperCompileManager.compileReportToFile(source_design, compiled_design)
        
        return compiled_design
    
    def generate(self, xmldata, output_type='pdf'):
        start = time.time()
        xmlpath = os.path.join(TMPDIR, 'xml')
        outputpath = os.path.join(TMPDIR, 'output')
        oid =  "%s-%d" % (md5.new(xmldata).hexdigest(), id(xmldata))
        ensure_dirs([xmlpath, outputpath])
        xmlfile = os.path.join(xmlpath, oid + '.xml')
        fd = open(xmlfile, 'w')
        fd.write(xmldata)
        fd.close()
        
        output_filename = os.path.abspath(os.path.join(outputpath, oid + '.' + output_type))
        output_file = open(output_filename, 'w')
        datasource = JRXmlDataSource(xmlfile, self.xpath)
        jasper_print = JasperFillManager.fillReport(self.compiled_design, None, datasource)
        if output_type == 'pdf':
            JasperExportManager.exportReportToPdfStream(jasper_print, output_file)
        elif output_type == 'xml':
            JasperExportManager.exportReportToXmlStream(jasper_print, output_file)
        # TODO: find out what is needed to make this work
        # elif output_type == 'rtf':
        #     self.generate_rtf(jasper_print, output_file)
        # elif output_type == 'xls':
        #     self._generate_xls(jasper_print, output_file)
        # elif output_type == 'csv':
        #     self._generate_csv(jasper_print, output_file)
        else:
            raise RuntimeError, "Unknown output type %r" % (output_type)
        output_file.close()
        delta = time.time() - start
        # print 'report %r generated in %.3f seconds' % (output_filename, delta)
        return open(output_filename, 'rb').read()

    def generate_rtf(self, jasper_print, output_file):
        rtf_exporter = JRRtfExporter()
        rtf_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        rtf_exporter.setParameter(JRExporterParameter.OUTPUT_STREAM, output_file)
        rtf_exporter.exportReport()

    def _generate_xls(self, jasper_print, output_file):
        xls_exporter = JRXlsExporter()
        xls_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        xls_exporter.setParameter(JRExporterParameter.OUTPUT_STREAM, output_file)
        xls_exporter.setParameter(JRXlsExporterParameter.IS_ONE_PAGE_PER_SHEET, 1)
        xls_exporter.exportReport()

    def _generate_csv(self, jasper_print, output_file):
        csv_exporter = JRCsvExporter()
        csv_exporter.setParameter(JRExporterParameter.JASPER_PRINT, jasper_print)
        csv_exporter.setParameter(JRExporterParameter.OUTPUT_STREAM, output_file)
        csv_exporter.exportReport()


def usage():
    print """XmlJasperInterface usage:
jython XmlJasperInterface.py <design> <xpath> input.xml
this will read reports/<design> and compile it to compiled-reports/<design.jasper>
It then woll read xml/<input.xml> and use it with the <xpath> select expression to
generate PDF output in pdf/<input.pdf>.
See net.sf.jasperreports.engine.data.JRXmlDataSource for further information)
"""    

def main(args):
    if len(args) != 4:
        usage()
        sys.exit(1)
    
    design    = args[1]
    select    = args[2]
    input_file = args[3]

    #jasper = XmlJasperInterface(design, select)
    #if not jasper.report(input_file):
    #    sys.exit(1)
    
    jasper = JasperInterface(open(design).read(), select)
    fd = open('output.pdf', 'w')
    fd.write(jasper.generate(open(input_file, 'r').read(), 'pdf'))
    
if __name__ == '__main__':
    main(sys.argv)
