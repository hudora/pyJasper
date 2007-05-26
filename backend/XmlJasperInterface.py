"""Jasper Reports Python interface"""

# based on a slew of java and ruby code, originally coded by jmv, tampered with by md
# this needs JYTHON to run, CPython will not work!

import os, sys, logging, time

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

class XmlJasperInterface:
    def __init__(self, design, select_criteria):
        # Compile desin if compiled version doesn't exist or older than source
        source_design = os.path.join('reports', design + '.jrxml')
        compiled_design = os.path.join('compiled-reports', design + '.jasper')
        if not os.path.exists(compiled_design) or \
           os.path.getmtime(source_design) > os.path.getmtime(compiled_design):
            logging.warning("compiling %r to %r" % (source_design, compiled_design))
            JasperCompileManager.compileReportToFile(source_design, compiled_design)
        self.compiled_design = compiled_design
        self.select_criteria = select_criteria
    
    def report(self, data_file, output_type='pdf'):
        start = time.time()
        output_name = os.path.splitext(os.path.basename(data_file))[0] + '.' + output_type
        output_filename = os.path.abspath(os.path.join(output_type, output_name))
        output_file = open(output_filename, 'w')
        logging.debug("generating report %r from datafile %r to %r with XPATH %r" % (self.compiled_design,
                      data_file, output_file, self.select_criteria))
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
        logging.info('report %r generated in %.3f seconds' % (output_filename, delta))
        return output_filename

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

    jasper = XmlJasperInterface(design, select)
    if not jasper.report(input_file):
        sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv)
