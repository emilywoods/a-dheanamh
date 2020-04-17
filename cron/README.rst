===========
Weekly Cron
===========

This directory contains a cron script, which is intended to be run on a weekly basis.
The purpose of this script is to generate a weekly report of things achieved
(it's nice to see what you've accomplished!), store these tasks in a CrateDB 
table, and then archive the completed ("done") tasks. The script will also bootstrap
the CrateDB tables, if they don't already exist.

Prerequisites
=============

To run the script, you will need:

- a local CrateDB instance
- a Trello account and API keys

Install
=======

To install the dependencies, run::

    $ make install

Execute
=======

In order to run the script, a config file containing the API keys, and Trello
list/column id as well as database connection. An example of this config can
be found here_.

To execute the script, run::

   $ python weekly.py -c ../cron.config

Or alternatively::

   $ make run

.. _here: ../example-cron.conf

Crontab
=======

This file is intended to be run as a weekly cron job. To set this up,
install the dependencies::

   $ pip3 install -r requirements.txt

Then, using ``crontab``, create an entry for this script::

   $ crontab -e

And add the entry::

   $ 0 0 * * 0 python3 <absolute-path>/weekly.py -c <absolute-path>/example-cron.conf >> ~/cron.log 2>&1

