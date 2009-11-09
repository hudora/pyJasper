#!/bin/sh

PYTHON="python2.6"
BASEPATH=$(dirname $0)

cd $BASEPATH

PYJASPER_SERVLET_URL="http://localhost:4580/pyJasper/jasper.py"

FAULT=0
test_pdf() {
    file $(PYTHONPATH=. $PYTHON client.py --url="$PYJASPER_SERVLET_URL" $@ | grep writing | awk '{ print $3 }') | grep "PDF document"	
    returnval=$?
    echo $FAULT
    if [ $returnval -ne 0 ]; then 
        FAULT=1
    fi
    echo $FAULT
    return $returnval
}


#start server:
../pyJasper-httpd.sh -Djetty.port=4580 -DSTOP.PORT=8079 &

# high sleep is needed for jetty to process the .jar files the first time
sleep 45

test_pdf bestellanlage.jrxml bestellanlage-subreport1.jrxml bestellanlage-subreport2.jrxml bestellanlage-subreport3.jrxml 

# give it some more time
sleep 5

# jetty builtin stop mechanism
java -DSTOP.KEY=blaat -DSTOP.PORT=8079 -jar ../start.jar --stop


exit $FAULT
