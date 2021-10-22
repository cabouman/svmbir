#!/bin/bash
# This script is designed to create the zip file containing python demo scripts

cd ..
zip -r demo.zip demo/*.py
zip -r demo.zip demo/*.txt
