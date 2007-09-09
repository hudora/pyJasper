import sys
sys.path.extend(['.'])
import cgi

import java.lang
from javax.servlet.http import HttpServlet
from org.apache.commons.fileupload.servlet import ServletFileUpload
from org.apache.commons.fileupload.disk import DiskFileItemFactory
import XmlJasperInterface

class pyJasper(HttpServlet):
    def doGet(self, request, response):
        # we use the same handler for GET and POST
        # actually GET is correct since there is no state change on the server
        # but POST can handle more data
        self.doPost(request, response)
        
    def doPost(self, request, response):
        """To be called with:
        
            xmldata: XML data Source for JasperReports
            xpath:   XPATH Expression for selecting rows from the datasource
            design:  JasperReports JRXML Report Design
        """
        
        data = {'xpath': request.getParameter('xpath'),
                'design': request.getParameter('design'),
                'xmldata': request.getParameter('xmldata')}
        
        if ServletFileUpload.isMultipartContent(request):
            servletFileUpload = ServletFileUpload(DiskFileItemFactory())
            files = servletFileUpload.parseRequest(request)
            it = files.iterator()
            while it.hasNext():
                fileItem = it.next()
                data[fileItem.getFieldName()] = str(java.lang.String(fileItem.get()))
        
        w = response.getWriter()
        if not data['xpath']:
            w.println('No valid xpath: %r' % data['xpath'])
            w.println(__doc__)
            w.close()
        elif not data['design']:
            w.println('No valid design: %r' % data['design'])
            w.println(__doc__)
            w.close()
        elif not data['xmldata']:
            w.println('No valid xmldata: %r' % data['xmldata'])
            w.println(__doc__)
            w.close()
        else:
            response.setContentType ("application/pdf");
            jasper = XmlJasperInterface.JasperInterface(data['design'], data['xpath'])
            w.write(jasper.generate(data['xmldata'], 'pdf'))
            w.close()
        