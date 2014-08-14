#!/bin/bash
echo "consul join \$CONSULSERVER_1_PORT_8500_TCP_ADDR ($CONSULSERVER_1_PORT_8500_TCP_ADDR)"
consul join $CONSULSERVER_1_PORT_8500_TCP_ADDR

if [ $? -eq 0 ]; then
    echo OK

    # sleep so supervisor knows that it worked
    sleep 2
else
    exit 1
fi
