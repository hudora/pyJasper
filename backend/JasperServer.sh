#!/bin/sh

# go to script dir
cd `dirname $0`

# generate classpath of all all JARs in lib and the fonts dir
MYCLASSPATH=`echo lib/*.jar|perl -npe 's/ /:/g;'`:fonts
java -Xrs -cp $MYCLASSPATH org.python.util.jython JasperServer.py $* 
