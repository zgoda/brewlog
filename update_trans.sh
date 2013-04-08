#! /bin/bash

pybabel extract -F ./babel.cfg -k lazy_gettext -o ./brewlog/translations/messages.pot ./
pybabel update -l pl -d ./brewlog/translations/ -i ./brewlog/translations/messages.pot
