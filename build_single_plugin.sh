#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

cd $SCRIPTPATH/clang-examples/FloatGuard-plugin
if [ $1 == "clean" ]; then
    make clean
else
    make $1
fi

cd $SCRIPTPATH/inst_pass
if [ $1 == "clean" ]; then
    make cleanall
else
    make
fi