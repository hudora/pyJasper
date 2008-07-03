"""Jasper pdf generation server."""
__revision__ = 1.0

import os, sys, SocketServer
#import logging # logging is not part of jython 2.1 so you have to put it 
               # yourself somewhere where Python can find it

from XmlJasperInterface import XmlJasperInterface

HOST = '127.0.0.1'       # IP this Serverr listens on
PORT = 8051              # Port this server listen on
DEBUG = 1

def log(msg):
    print msg

class JasperHandler(SocketServer.BaseRequestHandler):
    """Class handling network requests for pdf generation."""
    
    def handle(self):
        """Handle network request for pdf generation."""
        client = self.request.makefile()
        
        try:
            try:
                design = client.readline().strip()
                foo = client.readline()
                select = client.readline().strip()
                foo = client.readline()
                input_file = client.readline().strip()
                print("XXXXXXXXXX Request for %r / %r / %r" % (design, select, input_file))
                output_filename = self.generate_pdf(design, select, input_file)
                self.request.send("200 OK\r\n%s\r\n" % (output_filename,))
            except:
                #logging.error("server error: %s" % sys.exc_info()[1])
                self.request.send("500 Error: %r\r\n\r\n" % (sys.exc_info(),))
                if DEBUG:
                    raise
        finally:
            client.close()
    
    def generate_pdf(self, design, select, input_file):
        """Actually generate pdf."""
        print "ZZZZZZZZZZZZZ", design, select, input_file
        outdir, name = os.path.split(input_file)
        output_file = os.path.splitext(name)[0] + '.pdf'
        
        jasper = XmlJasperInterface(design, select)
        return jasper.report(input_file)
        
    
if __name__ == '__main__':
    serv = SocketServer.TCPServer((HOST, PORT), JasperHandler)
    serv.serve_forever()
