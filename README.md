# netshow-cumulus-lib

# Cumulus netshow library

Abstracts network related information such as L2 info, LLDP, Network services
(ntp, dhcp, dhcrelay) into Iface Objects.
This covers, physical ports, bonds and bridges only. Designed to
work with a linux device that is configured as a switch, but can work on a
server.

pynetlinux and python-netiface doesn't quite do what I want.

## Installation

```
pip install https://github.com/skamithi/linux-netshow-lib/archive/master.tar.gz
```


## Usage

TODO: Write usage instructions

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Create a [virtualenv](https://pypi.python.org/pypi/virtualenv/) instance.
Please try and develop using the latest stable Python3. Example:
```
$ virtualenv ~/netshow_dev /usr/local/bin/python3
```
4. Run ``pip install -r requirements_develop.txt``
5. Write some cool code and _relevant nose tests too_
6. Run ``tox`` to run the tests. You can interact with the code by going to
   ``.tox/py27`` and running the relative path of ``./bin/netshow`` or use the
``./bin/python`` interpreter.
6. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D


## Main Contributors

Stanley Karunditu [@skamithi](http://github.com/skamithi)

## License

TBD
