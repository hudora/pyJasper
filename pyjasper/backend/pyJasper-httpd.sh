#!/bin/sh

# This starts the jetty based http server for pyJasper. This server can be
# used to generate Reports with JasperReport. The server keeps no state at
# all. You have to supply it with an XML datasource, an XPath expression
# for that datasource and the JRXML report design. You get back the
# generated PDF or an plain text error message.

# To try it out you can use curl. E.g.
# curl -X POST --form xpath=//lieferscheine/lieferschein \
#              --form design=@reports/Lieferschein.jrxml \
#              --form xmldata=@sample-xml/Lieferschein.xml \
#              http://localhost:8080/pyJasper/jasper.py  > test.pdf

# go to script dir
cd `dirname $0`

# generate classpath of all all JARs in lib and the fonts dir
MYCLASSPATH=`echo lib/*.jar|perl -npe 's/ /:/g;'`:fonts
PATH=$PATH:/usr/local/bin
java -cp $MYCLASSPATH  -Dpython.home=./lib -jar start.jar
