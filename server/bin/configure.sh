#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PRODROOT="$(dirname "$CURRENT_DIR")"
CONFROOT=$PRODROOT/etc

export PRODROOT CONFROOT
