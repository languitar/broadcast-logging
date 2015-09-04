# broadcast-logging

A [Python logging system](https://docs.python.org/3/library/logging.html) handler which broadcasts log messages via UDP.
Additionally, a receiver is provided which can be used to display or further process the received log records on another host.

Broadcasting log messages, apart from the obvious advantage that multiple receivers can exist and do not need to be know by the sending process, is also handy in situations where you want to prevent explicit TCP connections on the sending side.

## Installation

From source:

```sh
python setup.py install
```

or from [PyPI](https://pypi.python.org/pypi) using [pip](https://pip.pypa.io):

```sh
pip install broadcast-logging
```

## Usage

### Sender

[Configure](https://docs.python.org/3/library/logging.config.html) the Python logging system using the standard mechanisms so that the provided `BroadcastHandler` is used.
When using a file-based configuration, a config file might look like this:

```ini
[loggers]
keys=root

[handlers]
keys=broadcastHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=broadcastHandler

[handler_broadcastHandler]
class=broadcastlogging.BroadcastHandler
level=DEBUG
args=('192.168.0.255',55555)
```

In case you want complete freedom on the receiving side on how to display which messages, it is advisable to set the level of the `BroadcastHandler` to `DEBUG` so that all logging messages are sent out.
Filtering can then be performed on the receiver side.
It is important to configure the correct broadcast address for your network.

### Receiver

The receiver can be invoked using:

```sh
python -m broadcastlogging
```

The following options are supported:

```
usage: broadcastlogging.py [-h] (-c | -f FILE) [-d] [-b ADDRESS] PORT

Receiver for python logging messages sent via UDP broadcasts using the
BroadcastHandler. Received logging messages are fed back into Python's logging
system on this receiver's side. Therefore you can use the usual configuration
mechanisms to determine how to handle the received messages.

positional arguments:
  PORT                  Port on which the logging messages are broadcasted

optional arguments:
  -h, --help            show this help message and exit
  -c, --basic           Use a basic logging system config printing everything
                        (default: False)
  -f FILE, --file FILE  Python logging system config file to configure how
                        received messages are handled. (default: None)
  -d, --debug           Include this receiver's logging in the logging system
                        by setting the own logger (broadcastlogging.receiver)
                        level to DEBUG. (default: False)
  -b ADDRESS, --bind ADDRESS
                        Bind address to use (default: <broadcast>)
```

In order to launch a receiver which is able to display all logging messages for a sender as configured above, use:

```sh
python -m broadcastlogging -h -c -b '192.168.0.255' 55555
```

## License

This library is [free software](https://en.wikipedia.org/wiki/Free_software); you can redistribute it and/or modify it under the terms of the [GNU Lesser General Public License](https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License) as published by the [Free Software Foundation](https://en.wikipedia.org/wiki/Free_Software_Foundation); either version 3 of the License, or any later version. This work is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU Lesser General Public License](https://www.gnu.org/copyleft/lgpl.html) for more details.
