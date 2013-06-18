=========
sundrop
=========

sundrop is a tool used to automate deployments of Sunlight Foundation projects.

It currently takes the form of a number of [fabric](http://fabfile.org) tasks and a shell script that serves as an entry point.


Installation
============

After checking out sundrop, symlink the file sundrop.sh to any location on your path.

Additionally, sundrop relies on you having Python >= 2.6 and the following packages:
* fabric
* boto

Getting Started
===============

sundrop keeps its config in an ini-style file at ~/.sundrop, right now the
only purpose of this file is to tell sundrop where it should look for your
projects tree.

The projects directory is the most important part of using sundrop, we'll
walk through a simple, single-project project tree, or see the ``projectsdir``
documentation for detailed documentation on all options available.

Creating a Project Directory
----------------------------

A project directory has a directory for each project, each of which has
(at a minimum) a config.yaml file within it.

`config.yaml` describes the project.  It is important
to specify what server(s) you want your project to run on (`production` and
`staging`), the size of the EBS volume you wish to create (`ebs_size_gb`), and
any repositories that need to be checked out (`src`).

Example projects.yaml::

production: 10.0.0.1
ebs_size_gb: 5
src:
    -
        gitrepo: git://github.com/sunlightlabs/labssite.git
        dirname: labssite
extra_packages:
    - redis-server


Detailed Documentation
======================

~/.sundrop
------------

[sundrop]

config_dir
    path to config directory, ~ will be expanded


Usage
=====

If there's a new server being used, the first thing to do is

# initialize hostname to richmond, install core & python packages
sundrop -H richmond server.init:richmond,core,python
# add a 30GB mongo instance
sundrop -H richmond services.mongodb:30
# deploy a project
sundrop staging:anthropod deploy
