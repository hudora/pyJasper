#!/usr/bin/env python
# encoding: utf-8
"""
jasper.py - pyJasper Servlet

Created by Maximillian Dornseif on 2007-09-09.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

import sys
sys.path.extend(['.'])

import java.lang
from javax.servlet.http import HttpServlet
from org.apache.commons.fileupload.servlet import ServletFileUpload
from org.apache.commons.fileupload.disk import DiskFileItemFactory
import XmlJasperInterface

import cgi
import simplejson
import threading
import urllib
import urllib2


def respond(data):
    """Write response to a given callback"""

    headers = {"Content-type": "application/pdf"}
    stream = generate(data)

    try:
        request = urllib2.Request(data['callback'], stream, headers)
        urllib2.urlopen(request)
    except urllib2.URLError:
        pass


def generate(data):
    """Get rendered report from JasperReports"""

    jaspergenerator = XmlJasperInterface.JasperInterface(data['designs'], data['xpath'])
    return jaspergenerator.generate(data['xmldata'], 'pdf',
                                    sign_keyname=data['sign_keyname'], sign_reason=data['sign_reason'],
                                    metadata=data['metadata'])


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
           designs: JasperReports JRXML Report Design when using subreports.
           sign_keyname: Keyname for signing PDF files - this parameter is optional.
           sign_reason: Reason to be send w/ signature
           metadata: PDF metadata (see http://www.pdfa.org/doku.php?id=artikel:en:pdfa_metadata)
        """

        data = {'xpath': request.getParameter('xpath'),
                'design': request.getParameter('design'),
                'designs': request.getParameter('designs'),
                'xmldata': request.getParameter('xmldata'),
                'sign_keyname': request.getParameter('sign_keyname'),
                'sign_reason': request.getParameter('sign_reason'),
                'callback': request.getParameter('callback'),
                'metadata': request.getParameter('metadata'),
               }

        if ServletFileUpload.isMultipartContent(request):
            servlet_file_upload = ServletFileUpload(DiskFileItemFactory())
            files = servlet_file_upload.parseRequest(request)
            fiterator = files.iterator()
            while fiterator.hasNext():
                file_item = fiterator.next()
                data[file_item.getFieldName()] = str(java.lang.String(file_item.get()))

        if data['designs']:
            data['designs'] = simplejson.loads(data['designs'])

        if not data['designs']:
            data['designs'] = {'main': data['design']}

        # Decode metadata
        if data['metadata']:
            metadata = {}
            for key, value in cgi.parse_qs(urllib.unquote(data['metadata'])).items():
                metadata[key] = value[0]
            data['metadata'] = metadata

        out = response.getWriter()
        if not data['xpath']:
            out.println('No valid xpath: %r\nDocumentation:' % data['xpath'])
            out.println(self.__doc__)
        elif not data['designs']:
            out.println('No valid design: %r\nDocumentation:' % data['designs'])
            out.println(self.__doc__)
        elif not data['xmldata']:
            out.println('No valid xmldata: %r\nDocumentation:' % data['xmldata'])
            out.println(self.__doc__)
        else:
            if data.get('callback'):
                writer = self.callback_response
            else:
                writer = self.immediate_response
            writer(request, response, data)

        out.close()

    def callback_response(self, request, response, data):
        """Return data by calling a webhook"""

        response.setContentType("text/plain")
        out = response.getWriter()
        out.println('Data will be send to %s' % data['callback'])

        thread = threading.Thread(target=respond, args=(data, ))
        thread.start()

    def immediate_response(self, request, response, data):
        """Return data immediatly"""

        response.setContentType("application/pdf")
        out = response.getWriter()
        data = generate(data)
        out.write(data)
