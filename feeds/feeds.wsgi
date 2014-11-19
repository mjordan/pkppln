"""
WSGI file for the PKP Private LOCKSS Network CRUD tool for terms of use.
For Apache configuration example, see http://bottlepy.org/docs/dev/deployment.html

Copyright (c) 2014 Simon Fraser University Library
Copyright (c) 2014 John Willinsky
Distributed under the GNU GPL v3. For full terms see the file COPYING.
"""

import os
import sys
import bottle
os.chdir(os.path.dirname(__file__))

sys.path.append("/opt/pkppln/feeds")
import feed_server

application = bottle.default_app()
