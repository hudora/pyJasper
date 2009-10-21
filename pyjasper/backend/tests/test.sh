#!/bin/bash

BASEPATH=$(dirname $0)

cd $BASEPATH

FAULT=0
function test_pdf {
    file $(PYTHONPATH=. python client.py $@|grep writing|awk '{ print $3 }')|grep "PDF document"	
    returnval=$?
    echo $FAULT
    if [ $returnval -ne 0 ]; then 
        FAULT=1
    fi
    echo $FAULT
    return $returnval
}


#start server:
../pyJasper-httpd.sh &
PID=$!

# high sleep is needed for jetty to process the .jar files the first time
sleep 15

test_pdf bestellanlage.jrxml bestellanlage-subreport1.jrxml bestellanlage-subreport2.jrxml bestellanlage-subreport3.jrxml 

# jetty builtin stop mechanism
java -DSTOP.KEY=blaat -DSTOP.PORT=8079 -jar ../start.jar --stop

exit $FAULT
