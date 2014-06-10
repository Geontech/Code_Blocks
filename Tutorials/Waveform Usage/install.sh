#!/bin/bash
# @author:      Thomas Goodwin
# @company:     Geon Technologies, LLC
# @description: Training installer template.
#               Named "install.sh", this will be executed with all environment variables
#               necessary for REDHAWK (SDRROOT, for example).  INST_DIR is the location
#               of where this install.sh script was found.
# 
#               Copy and modify this script for each module created.

INST_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Switch to base directory
pushd "$INST_DIR/Given Objects"
cp -r ./chirp_fm "$SDRROOT/dev/devices"
cp -r ./chirp_comp_passthrough "$SDRROOT/dom/components"
cp -r ./chirp_node "$SDRROOT/dev/nodes"
popd
