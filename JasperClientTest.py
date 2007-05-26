import os
import unittest
from pmock import *

import JasperClient

# this needs pmock - see http://pmock.sourceforge.net/

class mock_socket(object):
    @staticmethod
    def socket(family, type):
        return mock_socket.mock
    
    timeout = None
    error = None
    AF_INET = 0
    SOCK_STREAM = 0

class mock_os(object):
    @staticmethod
    def system(command):
        mock_os.commands.append(command)
    
    commands = []
    path = os.path
    
class JasperClientTest(unittest.TestCase):
    def setUp(self):
        mock_socket.mock = Mock()
        JasperClient.socket = mock_socket
        JasperClient.os = mock_os
        mock_os.commands = []
    
    def testGeneratePdf(self):
        mock_socket.mock.expects(once()).socket().will(return_value(mock_socket.mock))
        mock_socket.mock.expects(once()).settimeout(eq(1)).will(return_value(None))
        mock_socket.mock.expects(once()).connect(eq((JasperClient.HOST, JasperClient.PORT))).will(return_value(None))
        mock_socket.mock.expects(once()).send(eq('design\r\n.\r\ndata\r\n')).will(return_value(None))
        mock_socket.mock.expects(once()).recv(eq(1024)).will(return_value('200 OK'))
        mock_socket.mock.expects(once()).close().will(return_value(None))
        
        client = JasperClient.JasperClient()
        client.generate_pdf('design', '.', 'data')
        self.assertEqual(len(mock_os.commands), 0)
    
    def testGeneratePdfError(self):
        """Emulate server returning error."""
        mock_socket.mock.expects(once()).socket().will(return_value(mock_socket.mock))
        mock_socket.mock.expects(once()).settimeout(eq(1)).will(return_value(None))
        mock_socket.mock.expects(once()).connect(eq((JasperClient.HOST, JasperClient.PORT))).will(return_value(None))
        mock_socket.mock.expects(once()).send(eq('fb_design\r\nxpath\r\nfb_data\r\n')).will(return_value(None))
        mock_socket.mock.expects(once()).recv(eq(1024)).will(return_value('500 Error'))
        mock_socket.mock.expects(once()).close().will(return_value(None))
        
        client = JasperClient.JasperClient()
        client.generate_pdf('fb_design', 'xpath', 'fb_data')
        # Verify that client generated report using os.system after receiving error from server
        self.assertEqual(len(mock_os.commands), 1)
        self.assertEqual(mock_os.commands[0],
                         'jython XmlJasperInterface.py -ffb_design -xxpath < fb_data > fb_data.pdf')
        
if __name__ == '__main__':
    unittest.main()
