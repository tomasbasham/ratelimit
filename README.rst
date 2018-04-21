ratelimit |build|
=================

.. |build| image:: https://travis-ci.org/tomasbasham/ratelimit.svg?branch=master
    :target: https://travis-ci.org/tomasbasham/ratelimit

APIs are a very common way to interact with web services. As the need to
consume data grows, so does the number of API calls necessary to remain up to
date with data sources. However many API providers constrain developers from
making too many API calls. This is know as rate limiting and in a worst case
scenario your application can be banned from making further API calls if it
abuses these limits.

This packages introduces a method decorator preventing a method from being
called more than once within a given time period. This should prevent API
providers from banning your applications by conforming to set rate limits.

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

To use this package you simply have to declare the decorator before the method
you wish to rate limit:

.. code:: python

    from ratelimit import limits

    import requests

    FIFTEEN_MINUTES = 900

    @limits(calls=15, period=FIFTEEN_MINUTES)
    def call_api(url):
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception('API response: {}'.format(response.status_code))
        return response

This method makes a call to our API. Note that this method has been implemented
with a decorator enforcing that it may only be called 15 times every 15
minutes.

The arguments passed into the decorator impose the number of method invocation
allowed over a specified time period (in seconds). If no time period is
specified then it defaults to 15 minutes (the time window imposed by Twitter).

If a decorated method is called more times than that allowed within the
specified time period then a ``ratelimit.RateLimitException`` is raised. This
may be used to implement a retry strategy such as an `expoential backoff
<https://pypi.org/project/backoff/>`_

.. code:: python

    from ratelimit import limits, RateLimitException
    from backoff import on_exception, expo

    import requests

    FIFTEEN_MINUTES = 900

    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=15, period=FIFTEEN_MINUTES)
    def call_api(url):
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception('API response: {}'.format(response.status_code))
        return response

Alternatively to cause the current thread to sleep until the specified time
period has ellapsed and then retry the function use the ``sleep_and_retry``
decorator. This ensure that every function invocation is successful at the cost
of halting the thread.

.. code:: python

    from ratelimit import limits, sleep_and_retry

    import requests

    FIFTEEN_MINUTES = 900

    @sleep_and_retry
    @limits(calls=15, period=FIFTEEN_MINUTES)
    def call_api(url):
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception('API response: {}'.format(response.status_code))
        return response

Contributing
------------

1. Fork it (https://github.com/tomasbasham/ratelimit/fork)
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
