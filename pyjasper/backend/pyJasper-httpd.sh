#!/bin/sh

# This starts the jetty based http server for pyJasper. This server can be
# used to generate Reports with JasperReport. The server keeps no state at
# all. You have to supply it with an XML datasource, an XPath expression
# for that datasource and the JRXML report design. You get back the
# generated PDF or an plain text error message.

# To try it out you can use curl. E.g.
# curl -X POST --form xpath=//lieferscheine/lieferschein \
#              --form design=@reports/Lieferschein.jrxml \
#                \
#              http://localhost:8080/pyJasper/jasper.py  > test.pdf

# go to script dir
cd `dirname $0`

# This is needed to work properly with unicode on Solaris 10
LC_CTYPE=en_US.UTF-8
export LC_CTYPE

# generate classpath of all all JARs in lib and the fonts dir
MYCLASSPATH=`echo lib/*.jar|sed 's/ /:/g'`:fonts
PATH=$PATH:/usr/local/bin
mkdir -pv log

export PYJASPER_KEYSTORE_PASSWORD="aShu6xa3"
export PYJASPER_KEYSTORE_FILE="/Users/cklein/Desktop/sign/keystore.ks"

java $@ -cp $MYCLASSPATH -Dfile.encoding=utf-8 -Dpython.home=./lib -DSTOP.KEY=blaat -DSTOP.PORT=8079 -jar start.jar
