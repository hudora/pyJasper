#!/bin/sh

# go to script dir
cd `dirname $0`
cd /usr/local/web/MoftS/lib/pyJasper/backend

# generate classpath of all all JARs in lib and the fonts dir
MYCLASSPATH=`echo lib/*.jar|perl -npe 's/ /:/g;'`:fonts
/usr/local/bin/java -cp $MYCLASSPATH "org.python.util.jython" XmlJasperInterface.py $*
