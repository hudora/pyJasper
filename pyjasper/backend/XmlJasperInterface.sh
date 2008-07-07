#!/bin/sh

# this directly starts jython/java and renders a report with JasperReports
# usage:
# sh XmlJasperInterface.py <design> <xpath> input.xml output.pdf
# this will read reports/<design> and compile it to compiled-reports/<design.jasper>
# It then will read xml/<input.xml> and use it with the <xpath> select expression to
# generate PDF output in pdf/<input.pdf>.

# go to script dir
BASEPATH=`dirname $0`

# generate classpath of all all JARs in lib and the fonts dir
MYCLASSPATH=`echo $BASEPATH/lib/*.jar|perl -npe 's/ /:/g;'`:$BASEPATH/fonts
PATH=$PATH:/usr/local/bin
java -cp $MYCLASSPATH "org.python.util.jython" $BASEPATH/XmlJasperInterface.py $*
