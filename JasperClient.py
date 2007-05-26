#!/usr/bin/env python
# encoding: utf-8

"""Client for generating Jasper reports using remote server.
Created by jmv, extended by md
"""

import os, socket, logging

__revision__ = '$Revision$'

HOST = 'localhost'  # The remote host
PORT = 8051         # The same port as used by the server
TIMEOUT = 150       # Timeout in seconds to wait for the server
OUTPUTDIRHIER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))

class JasperException(RuntimeError):
    """This exception indicates Jasper server problem."""
    pass

class JasperClient(object):
    """Generation of JasperReport documents either using the server or a local client."""
    
    def generate_pdf_locally(self, design_name, xpath, data_name):
        """Generates a PDF document by using Jasper-Reports."""
        # TODO: this is dublicated code
        outfilename = os.path.join(OUTPUTDIRHIER, 'pdf', 
                                   os.path.splitext(os.path.split(data_name)[-1])[0]) + '.pdf'
        logging.warning("Locally generating Report %r/%r with source %r to %r" % (design_name,
                      xpath, data_name, outfilename))
        logging.debug('calling: (cd %r; sh XmlJasperInterface.sh %r %r %r )' % (OUTPUTDIRHIER,
                       design_name, xpath, data_name))
        os.system('(cd %r; sh XmlJasperInterface.sh %r %r %r )' % (OUTPUTDIRHIER,
                    design_name, xpath, data_name))
        return outfilename

    def generate_pdf_server(self, design_name, xpath, data_name):
        """Generate report via pyJasperServer."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(TIMEOUT)
        
        logging.debug("Connecting to %s:%s" % (HOST, PORT))
        server.connect((HOST, PORT))
        server.send("%s\r\n%s\r\n%s\r\n" \
                    % (design_name, xpath, data_name))
        logging.debug("Request sent")
        data = server.recv(1024)
        logging.debug("Got Reply %r" % (data))
        data = data.strip()
        if data.startswith('500 '):
            raise JasperException, data[4:]
                
        if not data.startswith('200 '):
            raise JasperException, data

        code, filename = data.split('\r\n')[:2]
                
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            raise JasperException, 'file %r not found' % (filename,)

        return filename


    def generate_pdf(self, design_name, xpath, data_name):
        logging.debug("Request for Report %r/%r with source %r" % (design_name, xpath, data_name))
        try:
            return self.generate_pdf_server(design_name, xpath, data_name)
        except (socket.timeout, socket.error, JasperException), msg:
            logging.error('Problem with server: %r' % (msg,))
            return self.generate_pdf_locally(design_name, xpath, data_name)
