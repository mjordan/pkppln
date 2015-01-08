PKP PLN Staging Software
========================

Code and example data related to the [Public Knowlege
Project](http://pkp.sfu.ca/) Private LOCKSS Network.

More info is available on this repo's
[wiki](https://github.com/mjordan/pkppln/wiki).

Testing
-------

There is a sample database schema in pkppln.sql  - load it into a MySQL database and edit config_test.cfg to point at the test database.

The automatic tests require a running WSGI instance. Luckily bottle.py
makes this easy. Start a test server from a terminal window:

 `python server.py config_test.cfg`

Then, in a second terminal window, run the unit tests with automatic discovery:

 `python -m unittest discover tests`

Configuration
-------------

This is a minimal configuration for Apache to run the server.py script as a WSGI.

```
 <VirtualHost 127.0.0.1>
  ServerName pkppln.dvh

  WSGIDaemonProcess pkppln.dvh processes=2 threads=15
  WSGIProcessGroup  pkppln.dvh
  
  WSGIScriptAlias / /path/to/pkppln/server.py
</VirtualHost>
```

This will run the server.py with configutation data from config.cfg in the same directory. You will need to update the config.cfg file with your actual configuration data.

Microservices
-------------

The server accepts SWORD deposits with a link to a BagIt file. The SWORD deposit also contains some metadata. The staging server runs each deposit through number of "microservices" to validate the data in different ways and prepare it for deposit to a [LOCKSSOMatic](https://github.com/mjordan/pkppln) instance. The services are:

<dl>
<dt>harvest</dt>
<dd>Download the deposit BagIt file.</dd>
<dt>validate_payload</dt>
<dd>Check the file size and checksum of the BagIt file against the metadata in the SWORD deposit.</dd>
<dt>validate_bag</dt>
<dd>Extract the contents of the BagIt file and validate it.</dd>
<dt>virus_check</dt>
<dd>Check the content of the deposit with ClamAV's clamd.</dd>
<dt>validate_export</dt>
<dd>Validate the OJS export XML.</dd>
<dt>reserialize_bag</dt>
<dd>Add the results of validation and virus checking to the BagIt data, and serialize it into a new BagIt file.</dd>
<dt>stage_bag</dt>
<dd>Move the new BagIt file to the staging location.</dd>
<dt>deposit_to_pln</dt>
<dd>Create a SWORD deposit on a LOCKSSOMatic instance for the staged BagIt file.</dd>
<dt>check_status</dt>
<dd>Check the status of the deposit on the LOCKSSOMatic instance.</dd>
</dl>

Services are run via pln-service.py.

```
usage: pln-service.py [-h] [-v | -q] [-n | -f] [-d DEPOSIT] service

Run a staging service

positional arguments:
  service               Name of the service to run

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -q, --quiet           Silence most output
  -n, --dry-run         Do not update the deposit states
  -f, --force           Force updates to the deposit states.
  -d DEPOSIT, --deposit DEPOSIT
                        Run the service on one or more deposits
```

Commands
--------

There are a number of convenience commands for querying the list of deposits. They are:

<dl>
<dt>journal_history</dt>
<dd>Show all deposits for a journal.</dd>
<dt>journal_info</dt>
<dd>Show metadata for a journal.</dd>
<dt>list_commands</dt>
<dd>List the available commands.</dd>
<dt>list_deposits</dt>
<dd>List all deposits.</dd>
<dt>list_journals</dt>
<dd>List all the journals that have ever made a deposit.</dd>
<dt>list_services</dt>
<dd>List all the services in the order they are applied to a deposit.</dd>
<dt>process</dt>
<dd>Process one deposit through all the services in the appropriate order</dd>
<dt>reset_deposit</dt>
<dd>Reset a deposit to a processing stage </dd>
<dt>service_log</dt>
<dd>Show all service actions against a deposit.</dd>
</dl>

```
usage: pln-command.py [-h] [-v | -q] command ...

Run a staging command

positional arguments:
  command        Name of the command to run
  subargs        Arugments to subcommand

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Increase output verbosity
  -q, --quiet    Silence most output

Use pln-command.py list_commands for a list of available commands
```

All commands accept `-h/--help` as an argument:

```
$ ./pln-command.py journal_info --help
usage: pln-command.py [global options] journal_info [command options]

Report all known journal metadata.

positional arguments:
  uuid        Journal UUID

optional arguments:
  -h, --help  show this help message and exit
```
