#!/usr/bin/env python
# encoding: utf-8
"""
jasper.py - pyJasper Servlet

Created by Maximillian Dornseif on 2007-09-09.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

import sys
import logging
# sys.path.append('.')

import cgi
import json
import mimetypes
import threading
import urllib
import urllib2

import javax.servlet.http
from org.apache.commons.fileupload.servlet import ServletFileUpload
from org.apache.commons.fileupload.disk import DiskFileItemFactory

try:
    import XmlJasperInterface
except ImportError:
    logging.error(u'sys.path: %s', sys.path)
    print u'sys.path: %s' % sys.path
    raise


class pyJasper(javax.servlet.http.HttpServlet):
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

    # def doGet(self, request, response):
    #     """Handle GET requests by same handler as POST"""
    #     # we use the same handler for GET and POST. I wonder:
    #     # actually GET is correct since there is no state change on the server
    #     # but POST can handle more data
    #     self.doPost(request, response)

    def doPost(self, request, response):
        """Generates a PDF with JasperReports. To be called with:

           xmldata: XML data Source for JasperReports
           xpath:   XPATH Expression for selecting rows from the datasource
           design:  JasperReports JRXML Report Design
           sign_keyname: Keyname for signing PDF files - this parameter is optional.
           sign_reason: Reason to be send w/ signature
           metadata: PDF metadata (see http://www.pdfa.org/doku.php?id=artikel:en:pdfa_metadata)
        """

        # Kack, das ist doch eh alles Multipart...
        data = {
                'xpath': request.getParameter('xpath'),
                'design': request.getParameter('design'),
                'xmldata': request.getParameter('xmldata'),
                'sign_keyname': request.getParameter('sign_keyname'),
                'sign_reason': request.getParameter('sign_reason'),
                'metadata': request.getParameter('metadata'),
               }

        if ServletFileUpload.isMultipartContent(request):
            servlet_file_upload = ServletFileUpload(DiskFileItemFactory())
            files = servlet_file_upload.parseRequest(request)
            fiterator = files.iterator()
            while fiterator.hasNext():
                file_item = fiterator.next()
                data[file_item.getFieldName()] = file_item.getString('utf-8')

        # TODO: Das geht auch schöner:
        # Decode metadata
        if data['metadata']:
            metadata = {}
            for key, value in cgi.parse_qs(urllib.unquote(data['metadata'])).items():
                metadata[key] = value[0]
            data['metadata'] = metadata

        # TODO: XPath ignorieren.
        # if not data['xpath']:
        #     out.println('No valid xpath: %r\nDocumentation:' % data['xpath'])
        #     out.println(self.__doc__)

        if not data['design']:
            out = response.getWriter()
            out.println('No valid design: %r\nDocumentation:' % data['design'])
            out.println(self.__doc__)
        elif not data['xmldata']:
            out = response.getWriter()
            out.println('No valid xmldata: %r\nDocumentation:' % data['xmldata'])
            out.println(self.__doc__)
        else:
            response.setContentType('application/pdf')
            stream = self.generate_document(data['design'], data['xpath'], data['xmldata'], data)
            out = response.getOutputStream()
            stream.writeTo(out)

        out.close()

    # TODO: doGet eher nur die __doc__
    doGet = doPost

    def generate_document(self, design, xpath, source, data):
        """TODO: Write doc string"""

        jaspergenerator = XmlJasperInterface.JasperInterface(design, xpath)
        return jaspergenerator.generate(
            source,
            sign_keyname=data['sign_keyname'],
            sign_reason=data['sign_reason'],
            metadata=data['metadata'])

