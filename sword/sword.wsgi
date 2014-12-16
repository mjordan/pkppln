"""
WSGI file for the PKP Private LOCKSS Network SWORD server.
For Apache configuration example, see http://bottlepy.org/docs/dev/deployment.html

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import os
os.chdir(os.path.dirname(__file__))

import sys
# Path to directory pkppln_sword_server.py is in.
sys.path.append("/opt/pkppln/sword")

import bottle
import pkppln_sword_server

application = bottle.default_app()
