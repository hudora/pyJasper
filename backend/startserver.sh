#!/bin/sh
#
# $Id$
#

# PROVIDE: pyJasperServer
# REQUIRE: DAEMON NETWORKING SERVERS
# BEFORE:  LOGIN
# KEYWORD: FreeBSD

export CLASSPATH=/usr/local/jython21/jython.jar:$CLASSPATH
export CLASSPATH=$CLASSPATH:lib/iReport.jar:lib/barbecue-1.1.jar
export CLASSPATH=$CLASSPATH:lib/commons-beanutils-1.5.jar:lib/commons-digester-1.7.jar
export CLASSPATH=$CLASSPATH:lib/commons-collections-2.1.jar:lib/commons-logging-1.0.2.jar
export CLASSPATH=$CLASSPATH:lib/itext-1.3.1.jar:lib/jasperreports-1.2.6.jar:lib/jcommon-1.0.0.jar
export CLASSPATH=$CLASSPATH:lib/jdt-compiler.jar:lib/jfreechart-1.0.0.jar:lib/log4j-1.2.13.jar
export CLASSPATH=$CLASSPATH:lib/poi-2.0-final-20040126.jar:lib/xalan.jar
export INTERFACE_CLASSPATH=$CLASSPATH

. /etc/rc.subr

name=pyJasperServer
pidfile=/var/run/pyJasperServer.pid
rcvar=`set_rcvar`

load_rc_config $name

command="/bin/sh"
command_args="/usr/local/web/diamond/lib/public/pyJasper/backend/JasperServer.sh"

pyJasperServer_enable=${pyJasperServer_enable:-"NO"}

run_rc_command "$1"
