## Why have Translation files

netshow produces lots of terminal output. With lots of fields. Folks may feel
the need to change a name or two here and there. Instead of modifying the source
code, just change the translation file for this. So its for better managing the
terminal output code.


## Requirements

* run ``pip install -r requirements_develop.txt`` from the root of this project. This
will install distutils-extra from Ubuntu which has an awesome ``build_i18n`` command
for setup.py

* install ``intltool`` onto the system, as build_i18n depends on running
``intltools-update`` and ``xgettext``.

## Creating translation file setup


### Create POT file

In the source code, use ``_`` keyword to define a string to be translated.
Then run:
```
xgettext --language=Python --keyword=_ --output=po/netshow-linux.pot -j `find
netshow/linux/*.py`
```

Then use [PoEdit](http://poedit.net/) or another type of translation tool to clean up the POT file.
Modify the POT properties with the Language, Language Team, Charset, etc. PoEdit
will complain until you fill out everything right.


### Create English PO file

```
cp po/netshow-linux.pot po/en.po
```


### Create the POTFILES.in

This keeps track of all the files with translation strings and is required by
``intltool-update``. To create this run

```
find netshow/linux/*.py > po/POTFILES.in
```

>Note: Run this each time you create a new python module that has translation
>strings in the ``netshow/linux`` directory


### Updating translation files before an install


Before running ``python setup.py bdist_wheel`` run ``python setup.py
build_i18n -m``. This will automatically look for new translation strings and
update the .PO file and create the .MO file.

If the program says there are some untranslated strings, use
[PoEdit](http://poedit.net/) to translate the strings and run the ``build_i18n``
command again.

``build_i18n`` will install the files in the proper build location so when you
run the install command the translation files will be installed in the right location.


