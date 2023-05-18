#!/bin/sh

# RUN IT FROM ROOT OF PROJECT
# on windows you can use 'python -m black *.py' (--check)

source_dir=src
if [ -d "$source_dir" ]; then
  black `find ./$source_dir -name '*.py'`
else
  echo "Run the script from the root folder of the project !!!"
fi