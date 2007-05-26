import os
import unittest

from StringIO import StringIO
import JasperServer


class mock_request:
    sent_data = ''
    
    def __init__(self, test_data):
        self.test_data = test_data
    
    def makefile(self):
        data = StringIO(self.test_data)
        return data
    
    def send(self, data):
        mock_request.sent_data += data
    

class mock_xmlJasperInterface:
    constructor_calls = []
    
    def __init__(self, design, xpath, source, target):
        mock_xmlJasperInterface.constructor_calls.append((design, xpath, source, target))
    
    def generate_report(self):
        pass
    

class mock_JasperHandler(JasperServer.JasperHandler):
    def __init__(self, test_data):
        self.request = mock_request(test_data)
    

class JasperServerTest(unittest.TestCase):
    def setUp(self):
        JasperServer.XmlJasperInterface = mock_xmlJasperInterface
        mock_xmlJasperInterface.constructor_calls = []
        
        mock_request.sent_data = ''
        
    def testHandle(self):
        JasperServer.open = lambda file, mode: StringIO()
        
        h = mock_JasperHandler("design\r\nxpath\r\n/null/some_data")
        h.handle()
        
        self.assertEqual(mock_request.sent_data,
                         "500 Error: [Errno 0] couldn't rename file: /null/tmp_jasper_some_data.pdf\r\n\r\n")
        self.assertEqual(len(mock_xmlJasperInterface.constructor_calls), 1)
        self.assertEqual(mock_xmlJasperInterface.constructor_calls[0][:2],
                         ('design', 'xpath'))
        
    def testHandleError(self):
        JasperServer.open = open
        
        h = mock_JasperHandler("design\r\nxpath\r\n/random_data")
        h.handle()
        
        self.assertEqual(mock_request.sent_data,
                         "500 Error: File not found - /random_data (No such file or directory)\r\n\r\n")
        self.assertEqual(len(mock_xmlJasperInterface.constructor_calls), 0)
    

if __name__ == '__main__':
    unittest.main()
