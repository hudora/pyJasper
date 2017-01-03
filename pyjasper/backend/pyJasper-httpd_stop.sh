# !/bin/sh

# Stop the jetty server by Bernhard Ströbl
java -DSTOP.PORT=8079 -DSTOP.KEY=blaat -jar start.jar --stop
