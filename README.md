PKP PLN Staging Software
=====================

Code and example data related to the [Public Knowlege
Project](http://pkp.sfu.ca/) Private LOCKSS Network.

More info is available on this repo's
[wiki](https://github.com/mjordan/pkppln/wiki).

Testing
---------

There is a sample database schema in pkppln.sql  - load it into a MySQL database and edit config_test.cfg to point at the test database.

The automatic tests require a running WSGI instance. Luckily bottle.py
makes this easy. Start a test server from a terminal window:

 `python server.py config_test.cfg`

Then, in a second terminal window, run the unit tests with automatic discovery:

 `python -m unittest discover tests`

Configuration
------------------

This is a minimal configuration for Apache to run the server.py script as a WSGI.

```
 <VirtualHost 127.0.0.1>
  ServerName pkppln.dvh

  WSGIDaemonProcess pkppln.dvh processes=2 threads=15
  WSGIProcessGroup  pkppln.dvh
  
  WSGIScriptAlias / /path/to/pkppln/server.py
</VirtualHost>
```
