#!/usr/bin/env python
# encoding: utf-8
"""
jasper.py - pyJasper Servlet

Created by Maximillian Dornseif on 2007-09-09.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

import cgi
import json
import mimetypes
import threading
import urllib
import urllib2

import javax.servlet.http
from org.python.core.util import FileUtil

import XmlJasperInterface


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

        # Multipart-Request auseinanderpflücken:
        if request.contentType.startswith('multipart/form-data'):
            for part in request.getParts():
                fileobj = FileUtil.wrap(part.inputStream)
                if part.name in {'xpath', 'metadata'}:
                    value = fileobj.read()
                else:
                    value = fileobj
                data[part.name] = value

        # TODO: Das geht auch schöner:
        # Decode metadata
        if data['metadata']:
            metadata = {}
            for key, value in cgi.parse_qs(urllib.unquote(data['metadata'])).items():
                metadata[key] = value[0]
            data['metadata'] = metadata

        parameters = {}
        for key in request.headerNames:
            if key.startswith('X-Param-'):
                parameters[key.split('-', 2)[-1]] = request.getHeader(key)

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
            stream = self.generate_document(data['design'], data['xpath'], data['xmldata'], data, parameters)
            out = response.getOutputStream()
            stream.writeTo(out)

        out.close()

    def doGet(self, request, response):
        out = response.getWriter()
        out.println(self.__doc__)
        out.close()

    def generate_document(self, design, xpath, source, data, parameters):
        """TODO: Write doc string"""

        jaspergenerator = XmlJasperInterface.JasperInterface(design, xpath)
        return jaspergenerator.generate(
            source,
            sign_keyname=data['sign_keyname'],
            sign_reason=data['sign_reason'],
            metadata=data['metadata'],
            parameters=parameters)

