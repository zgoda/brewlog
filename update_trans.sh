#! /bin/bash

pybabel extract -F ./babel.cfg -o ./locale/messages.pot ./
pybabel update -l pl -d ./locale/ -i ./locale/messages.pot
