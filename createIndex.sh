#!/bin/bash

find . -type f ! -name '.*' | grep -v '.git' | grep -v 'Icon' | grep -v 'index.txt' | grep -v '.md' | grep -v 'createIndex.sh' |sort > index.txt
