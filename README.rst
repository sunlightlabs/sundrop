=========
sundeploy
=========

sundeploy is a tool used to automate deployments of Sunlight Foundation projects.

It currently takes the form of a number of [fabric](http://fabfile.org) tasks and a shell script that serves as an entry point.


Installation
============

After checking out sundeploy, symlink the file sundeploy.sh to any location on your path.

Additionally, sundeploy relies on you having Python >= 2.6 and the following packages:
* fabric
* boto

Getting Started
===============

sundeploy keeps its config in an ini-style file at ~/.sundeploy, right now the
only purpose of this file is to tell sundeploy where it should look for your
projects tree.

The projects directory is the most important part of using sundeploy, we'll
walk through a simple, single-project project tree, or see the ``projectsdir``
documentation for detailed documentation on all options available.

Creating a Project Directory
----------------------------

A project directory is required to have a ``projects.json`` and a directory
named for each project specified in ``projects.json``.

`projects.json` describes all of your projects.  It is important
to specify what server(s) you want your project to run on (`production` and
`staging`), the size of the EBS volume you wish to create (`ebs_size_gb`), and
any repositories that need to be checked out (`src`).

Example projects.json::

    {
    "labssite": {
        "production": "main",
        "ebs_size_gb": 5,
        "src": [
            {"gitrepo": "git://github.com/sunlightlabs/labssite.git",
             "dirname": "openstates"}
        ],
        "extra_packages": ["redis-server"]
    }
    }


Detailed Documentation
======================

~/.sundeploy
------------

[sundeploy]

config_dir
    path to config directory, ~ will be expanded
