#!/usr/bin/env python
# encoding: utf-8
"""
jasper.py - pyJasper Servlet

Created by Maximillian Dornseif on 2007-09-09.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

import sys
sys.path.extend(['.'])
import cgi

import java.lang
from javax.servlet.http import HttpServlet
from org.apache.commons.fileupload.servlet import ServletFileUpload
from org.apache.commons.fileupload.disk import DiskFileItemFactory
import XmlJasperInterface

__revision__ = '$Revision$'

class jasper(HttpServlet):
    """Servlet for rendering JasperReport reports.
    
    The servlet keeps no state at all. You have to supply it with an
    XML datasource, an XPath expression for that datasource and
    the JRXML report design. You get back the generated PDF or an
    plain text error message.
    
    The respective data has to be submitted via the form variables
    'xpath', 'design' and 'xmldata'.
    
    To try it out you can use curl. E.g.
    curl -X POST --form xpath=//lieferscheine/lieferschein 
                 --form design=@reports/Lieferschein.jrxml 
                 --form xmldata=@sample-xml/Lieferschein.xml 
                 http://localhost:8080/pyJasper/jasper.py > test.pdf
    """
    
    def doGet(self, request, response):
        """Handle GET requests by just redirecting to doPost()."""
        # we use the same handler for GET and POST. I wonder:
        # actually GET is correct since there is no state change on the server
        # but POST can handle more data
        self.doPost(request, response)
    
    
    def doPost(self, request, response):
        """Generates a PDF with JasperReports. To be called with:
           
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
            w.println('No valid xpath: %r\nDocumentation:' % data['xpath'])
            w.println(self.__doc__)
            w.close()
        elif not data['design']:
            w.println('No valid design: %r\nDocumentation:' % data['design'])
            w.println(self.__doc__)
            w.close()
        elif not data['xmldata']:
            w.println('No valid xmldata: %r\nDocumentation:' % data['xmldata'])
            w.println(self.__doc__)
            w.close()
        else:
            response.setContentType ("application/pdf");
            jasper = XmlJasperInterface.JasperInterface(data['design'], data['xpath'])
            w.write(jasper.generate(data['xmldata'], 'pdf'))
            w.close()
        