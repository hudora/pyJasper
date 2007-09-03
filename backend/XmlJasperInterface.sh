#!/bin/sh

cd /usr/local/web/MoftS/lib/pyJasper/backend

export CLASSPATH=$CLASSPATH:/usr/local/jython21/jython.jar
export CLASSPATH=$CLASSPATH:lib/iReport.jar:lib/barbecue-1.1.jar
export CLASSPATH=$CLASSPATH:lib/commons-beanutils-1.5.jar:lib/commons-digester-1.7.jar
export CLASSPATH=$CLASSPATH:lib/commons-collections-2.1.jar:lib/commons-logging-1.0.2.jar
export CLASSPATH=$CLASSPATH:lib/itext-1.3.1.jar:lib/jasperreports-1.2.6.jar:lib/jcommon-1.0.0.jar
export CLASSPATH=$CLASSPATH:lib/jdt-compiler.jar:lib/jfreechart-1.0.0.jar:lib/log4j-1.2.13.jar
export CLASSPATH=$CLASSPATH:lib/poi-2.0-final-20040126.jar:lib/xalan.jar:fonts

export INTERFACE_CLASSPATH=$CLASSPATH
java -cp $INTERFACE_CLASSPATH "org.python.util.jython" XmlJasperInterface.py $*
