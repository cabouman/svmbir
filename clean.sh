#!/bin/bash

echo "Running clean.sh"
/bin/rm -v -r dist 2> /dev/null
/bin/rm -v -r build 2> /dev/null
/bin/rm -v -r svmbir.egg-info 2> /dev/null
/bin/rm -v svmbir/*.so 2> /dev/null
/bin/rm -v svmbir/interface_cy_c.c 2> /dev/null
