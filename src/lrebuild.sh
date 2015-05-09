# a script for re-extracting strings and updating translation files
pybabel extract -F babel.cfg -o translation.pot .
pybabel update -i translation.pot -d translations
