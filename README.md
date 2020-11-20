qpm
===

Quarks package manager and test runner for SuperCollider (https://supercollider.github.io).
Written in Python.

Author: Scott Carver (https://github.com/scztt)

Supported Python versions: 
- 3.6
- 3.7
- 3.8

Features and Usage
------------------

### Run SuperCollider code

    qpm execute '"hello world".postln' -p /path/to/sclang

### Install quarks and list names and versions

    qpm quark list
    qpm quark versions ddwCommon

### List tests available to a sclang executable

	qpm test.list

### Run tests

    qpm test.run -p /path/to/sclang -l /json/test/spec

### More info

To see available options, use:

    qpm -h

To see options available for a given subcommand:

    qpm quark checkout -h

Installing
----------

qpm is available via pip:

    pip install qpm

For developing, install via either:

    pip install -e . # install from this directory

or:

    pip install -r requirements.txt

Requirements
------------

- semantic-version==2.2.0
- nose==1.3.0
- gitpython==0.3.2
- PyDispatcher==2.0.3
- cement==2.10.2
- colorama
- appdirs
- pyyaml
