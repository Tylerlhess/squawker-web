#!/bin/bash

LASTBLOCK=$BESTBLOCK
THISBLOCK=$(raven-cli getbestblockhash)

if [ "$LASTBLOCK" != "$THISBLOCK" ];
then 
	export BESTBLOCK=$THISBLOCK
	python cache.py $THISBLOCK
fi

