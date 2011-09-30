# pyJasper

pyJasper is a set of python based tools to handle JasperReports.
Since jasper reports is a Java application you need Java installed.

Jython (bundled with pyJasper) is used to access the JasperReports
library via HTTP. Your pure Python clients can transparently generate
JasperReport Documents.

See [StackOverflow](http://stackoverflow.com/questions/458340/is-there-a-better-layout-language-than-html-for-printing/459352#459352) and [this Blogposting](http://blogs.23.nu/c0re/2008/07/antville-18473/) to understand what problem pyJasper is trying to solve.

## Usage

### Servlet Interface

The servlet keeps no state at all. You have to supply it with an XML datasource, an XPath expression for that datasource and the JRXML report design. You get back the generated PDF or an plain text error message. The respective data has to be submitted via the form variables 'xpath', 'design' and 'xmldata'.

To try it out you can use curl. E.g. do to pyjasper/backend and start the jetty servlet container (`sh pyJasper-httpd.sh`). Then use  `curl` in another window to request rendering of a PDF.

    curl -X POST --form xpath=//lieferscheine/lieferschein 
                 --form design=@reports/Lieferschein.jrxml 
                 --form xmldata=@sample-xml/Lieferschein.xml 
                 --form sign_keyname={{ alias of the certificate in the KeyStore }} #optional
                 --form sign_reason={{ reason to be send w/ certificate }} #optional
                 --form callback={{ callback_URL }} #optional
                 http://localhost:8080/pyJasper/jasper.py > test.pdf

test.pdf should now contain a rendered PDF document.
If you provided sign_keyname and sign_reason AND your backend installation knows this keyname, you get a signed pdf.

With parameter callback you tell the server to generate the pdf and send it to the given URL instead of immediate return. 

### Python interface

You are expected to subclass `pyjasper.JasperGenerator` and call it's `generate_pdf()` function. Usually you only have to overwrite the `__init__()` and `generate_xml(self, ...)` functions and use the the Python [ElementTree](http://docs.python.org/lib/module-xml.etree.ElementTree.html) API to generate an xml-tree. E.g.

    class MyPDFGenerator(JasperGenerator):
        """Jasper-Generator for Greetingcards"""
        def __init__(self):
            super(MovementGenerator, self).__init__()
            self.reportname = 'reports/Greeting.jrxml'
            self.xpath = '/greetings/greeting'
            self.root = ET.Element('gretings') 
    
        def generate_xml(self, tobegreeted):
            """Generates the XML File used by Jasperreports"""
            
            ET.SubElement(self.root, 'generator').text = __revision__
            for name in tobegreeted:
                xml_greeting  =  ET.SubElement(self.root, 'greeting')
                ET.SubElement(xml_greeting, "greeting_to").text = unicode(name)
                ET.SubElement(xml_greeting, "greeting_from").text = u"Max"
            return xmlroot

Now you can use `MyPDFGenerator` like this:

    generator = MyPDFGenerator()
    pdf = generator.generate(['nik', 'tobias', 'chris', 'daniel'])
    open('/tmp/greetingcard.pdf', 'w').write(pdf)

The Python client finds the URL of the Jasper Servlet by checking the @PYJASPER_SERVLET_URL@ environment variable. It this Variable is not set, a default value of `http://localhost:8080/pyJasper/jasper.py` is used.

### Installation

Get it at the [Python Cheeseshop](http://pypi.python.org/pypi/pyJasper) or at [GitHub](http://github.com/hudora/pyJasper)
To install the Python client interface  just execute `python setup.py install` as administrator. This should install the requred dependency [httplib2](http://code.google.com/p/httplib2/) automatically. For the Server part there exist no automatic setup script. Just copy `pyjasper/backend/`  to a suitable location and start `pyJasper-httpd.sh` I use Dan Bernsteins [supervise](http://cr.yp.to/daemontools/supervise.html) tool for running the Jetty server.

#### exampledeployment on Amazon EC2

##### Create an new instance via AWS Management console

* Launch instance
  * Choose an AMI
    * Community AMI
    * e.g. ubuntu-images-eu/ubuntu-lucid-10.04-i386-server-20100923.manifest.xml
* Instance details
* Create Keypair
  * Create a new keypair or choose one of your existing
* Firewall
  * Custom: TCP Port 5555 - 5555
  * This custom option is not choosable in this setup-wizard but you can change the firewall settings later

##### Install and configure pyJasper

    ssh -A ubuntu@dns-name-of-instance.com
    sudo aptitude update
    sudo aptitude safe-upgrade
    sudo aptitude install openjdk-6-jre daemontools daemontools-run git-core
    cd /usr/local
    sudo git clone https://github.com/hudora/pyJasper.git
    cd /usr/local/pyJasper

Now you have to add a command to `/etc/crontab` to delete old files from `/tmp/pyJasper/` to keep the temporary files small. For example you can use this line to delete all files older than 7 days in `/tmp/pyJasper/`.

    0  1    * * *   root    /usr/bin/find /tmp/pyJasper/ -mtime +7 -type f -exec /bin/rm {} \;

Optional: Now you have to upload a keystore file for signing your documents and set it in `/usr/local/pyJasper/pyjasper/backend/pyJasper-httpd.sh`

    export PYJASPER_KEYSTORE_PASSWORD="thesecretpassphrase"
    export PYJASPER_KEYSTORE_FILE="/usr/local/pyJasper/signature-keystore-file.ks"

Finally configure daemontools to run the following command as a service:

    /usr/local/pyJasper/pyjasper/backend/pyJasper-httpd.sh -Xms128m -Xmx1G


## History

* **0.2.1*** public release (Summer 2008)
* **0.2*** release based on Jetty/Servlets (late 2007)
* **0.1.1*** public release on hosted-projects.com
* **0.1*** release based on long running Java Process (late 2006)
* **.01** one Java process per document (2006)

## Files

* client.py                      - contains high-level Python functions for report generation. Should theoretically be able to work with report generators other than JasperReports. So far builds on JasperClient.py.
* backend/                       - contains tools to drive JasperReports and actually build reports. The backend was once based on XmlJasperInterface by Jonas Schwertfeger but hase benn moving away from it for some time.
* backend/lib                    - JasperReports and Jython Java Libraries
* reports                        - report source files (*.jrxml)
* sample-xml                     - sample XML files to work with reports
* sample-pdf                     - sample PDFs generated by using reports with sample XML

## Links

* [JasperReports](http://en.wikipedia.org/wiki/JasperReports)
* [How to Integrate JasperReports with Ruby on Rails](http://wiki.rubyonrails.org/rails/pages/howtointegratejasperreports)
* [jasapp](http://www.vmware.com/appliances/directory/311) a VMWare Virtuall Appliance providing a JasperReports Interface
* [Geraldo](http://geraldo.sourceforge.net/)
