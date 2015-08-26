ratelimit
=========
.. image:: https://travis-ci.org/tomasbasham/ratelimit.svg?branch=master
    :target: https://travis-ci.org/tomasbasham/ratelimit

APIs are a very common way to interact with web services. As the need to consume data grows, so does the number of API calls necessary to remain up to date with data sources. However many API providers constrain developers from making too many API calls. This is know as rate limiting and in a worst case scenario your application can be banned from making further API calls if it abuses these limits.

This packages introduces a method decorator preventing a method from being called more than once within a given time period. This should prevent API providers from banning your applications by conforming to set rate limits.

Installation
------------

PyPi
~~~~

To install ratelimit, simply:

.. code:: bash

    $ pip install ratelimit

GitHub
~~~~~~

Installing the latest version from Github:

.. code:: bash

    $ git clone https://github.com/tomasbasham/ratelimit
    $ cd ratelimit
    $ python setup.py install

Usage
-----

To use this package you simply have to declare the decorator before the method you wish to rate limit:

.. code:: python

    from ratelimit import *
    import requests

    @rate_limited(1)
    def call_api(self, url):
      response = requests.get(url)

      if response.status_code != 200:
        raise ApiError('Cannot call API: {}'.format(response.status_code))

      return response

This method makes a call to our API. Note that this method has been implemented with a decorator that dictates that this method may only be called once per second.

The argument passed into the decorator imposes the time that must elapse before a method can be called again.

Contributing
------------

1. Fork it ( https://github.com/tomasbasham/ratelimit/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
