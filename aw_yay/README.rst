=======
Aw-yay!
=======

The purpose of this tool is to provide a CLI interface to Trello.

Prerequisites
=============

- A Trello account with token and api key

Install
=======

The tool can be installed from the root directory of this project, using
the command::

   $ make install

Usage
=====

To use the tool a config file is expected with the API keys and the names
of lists within a board and their associated ids. These will need to be 
found from Trello.

An `example of this config`_ file is found in the root of this project.

Currently the implementation of this project, is highly specific to how _I_
use Trello, which is to keep track of:

- Monthly and weekly tasks
- Books I want to read
- Places I want to visit (locally and further afield)
- Projects to work on (coding, sewing and gardening mostly)
- Habits and long-term goals (e.g. learning German) 

To see the available CLI options, run::

  $ aw-yay -c ../example.conf

To use one of these commands, e.g. to see what's on your to-read list::

  $ aw-yay -c ../example.conf books


.. _example of this config: ../example.conf
