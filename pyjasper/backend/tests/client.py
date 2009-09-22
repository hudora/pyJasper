#!/usr/bin/env python
# encoding: utf-8

import os
import os.path
import tempfile
import simplejson
from optparse import OptionParser

command = "curl -X POST --form xpath=%s --form designs=@%s --form xmldata=@%s.xml %s > %s"

def get_report(files, url):
    """
    """

    main_report = files[0]

    if len(files) > 1:
        files = files[1:]

    cachefile = tempfile.mkstemp(prefix=main_report, suffix=".json")[1]

    # add the contents 
    designs = {'main': open(main_report).read().replace("\t", '')}
    for i in files:
        designs[str(os.path.splitext(i)[0])] = open(i).read().replace("\t", '')

    json = simplejson.dumps(designs)

    handle = open(cachefile, 'w')
    handle.write(json)
    handle.close()

    print "trying %s" % files
    tfile = tempfile.mkstemp(prefix=main_report, suffix=".pdf")[1]
    filename = os.path.splitext(main_report)[0]
    xpath = open("%s.xpath" % filename).read().strip()

    print "writing to: %s" % tfile
    execcommand = command % (xpath, cachefile, filename, url, tfile)
    os.system(execcommand)

    #os.system("open %s" % tfile)

if __name__ == "__main__":
    usage = "usage: %prog [options] file1 [file2 ...]"
    parser = OptionParser(usage=usage)
    parser.add_option("-u", "--url",
                  dest="url", default="http://localhost:8080/pyJasper/jasper.py",
                  help="set the url to the pyjasper server")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("incorrect number of arguments")

    get_report(args, options.url)
