# olliv
A Villo! bike management project for the city of Brussels

# Requirements

    sudo pip install flask
    sudo pip install python-dateutil
    sudo pip install Flask-Babel

# Setup

    cd src/
    python buildModel.py    # create the database
    python importData.py    # import all data from /data in the database
    ./lrebuild.sh           # rebuild the .pot translation file, update all translations
    ./lcompile.sh           # compile all translations

# Run

    python main.py

# Maintenance

## Add new strings to translate
In the jinja2 templates, replace strings such as `<p>Hello</p>` with 
`<p>{{ _('Hello') }}</p>` and execute the following command:

    ./lrebuild.sh

This script will re-extract all strings from the project and update all translation
files. Just go in src/translations and update accordingly all .po files.

Then, compile the .po files :

    ./lcompile.sh   # in /src

## Add new languages
Run the following in `/src`, change `de` to the language you wish to add

    pybabel init -i translations.pot -d translations -l de

Be sure to add the corresponding language in `LANGUAGES` in main.py.