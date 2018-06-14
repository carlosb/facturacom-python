#!/usr/bin/python

"""Factura.com Python Bindings
===========================

This module contains the Python helper classes to use in
conjunction with Factura.com's API.

The helper classes are based on the official documentation
specification that may be found on Factura.com's website.
Alternatively, you can follow this link to read more about it:
https://facturacom.docs.apiary.io/

Usage
-----

You will have to import the library, set the API keys and specify the operation
mode:

```python
import facturacom

facturacom.API.key = 'YOUR API KEY'
facturacom.API.secret_key = 'YOUR SECRET API KEY'
facturacom.API.mode = 'PRODUCTION'  # or SANDBOX
```

Now you can start making requests!
"""


import platform
import requests

import urllib

try:
    import json
except ImportError:
    import simplejson as json


class FacturaError(Exception):
    def __init__(self, error_json):
        super(FacturaError, self).__init__(error_json)
        self.error_json = error_json


class _API:
    """Helper class to handle and store information used by the
    resource classes when making HTTP requests.
    """
    _SANDBOX_HOST = 'http://private-anon-dab239ca03-facturacom.apiary-mock.com'
    _PRODUCTION_HOST = 'https://factura.com'
    _DEFAULT_VERSION = '3'
    _ALLOWED_MODES = set(['SANDBOX', 'PRODUCTION'])

    _DATA = {
        'lang': 'python',
        'lang_version': platform.python_version(),
        'uname': platform.uname()
    }

    _HEADERS = {
        'Content-type': 'application/json',
        'X-Facturacom-Client-User-Agent': json.dumps(_DATA),
        'F-API-KEY': '',
        'F-SECRET-KEY': ''
    }

    def __init__(self):
        self._key = None
        self._secret_key = None
        self._mode = 'PRODUCTION'

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        _API._HEADERS['F-API-KEY'] = value
        self._key = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        _API._HEADERS['F-SECRET-KEY'] = value
        self._secret_key = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in _API._ALLOWED_MODES:
            raise FacturaError({
                'message': 'Unknown API mode. Please choose between: %s' %
                ', '.join(_API._ALLOWED_MODES)
            })
        self._mode = value

    def base(self, version=None):
        if version is None:
            version = _API._DEFAULT_VERSION
        if self._mode == 'SANDBOX':
            return '%s/api/v%s' % (_API._SANDBOX_HOST, version)
        elif self._mode == 'PRODUCTION':
            return '%s/api/v%s' % (_API._PRODUCTION_HOST, version)
        else:
            raise FacturaError({
                'message': 'Unknown API mode. Please choose between: %s' %
                ', '.join(_API._ALLOWED_MODES)
            })


API = _API()  # The API singleton to be used


class _DictHelper:
    """This class may acquire an existing dictionary and perform
    operations over it. I.e. changes to this dictionary will be
    reflected in the original dictionary. Furthermore, this class
    allows the use of the dot accessor: `d['x']` is the same as `d.x`.

    Example
    -------

    ```python
    >>> d = {'x': 2}
    >>> d
    {'x': 2}
    >>> other = _DictHelper(d)
    >>> other.x = 3
    >>> other
    {'x': 3}
    >>> d
    {'x': 3}
    ```
    """
    def __init__(self, d={}):
        self.__dict__ = d

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return str(self.__dict__)

    def __any__(self):
        return any(self.__dict__)

    def __all__(self):
        return all(self.__dict__)

    def __ascii__(self):
        return ascii(self.__dict__)

    def __bool__(self):
        return bool(self.__dict__)

    def __enumerate__(self):
        return enumerate(self.__dict__)

    def __filter__(self):
        return filter(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __max__(self):
        return max(self.__dict__)

    def __min__(self):
        return min(self.__dict__)

    def __map__(self):
        return map(self.__dict__)

    def __sorted__(self):
        return sorted(self.__dict__)

    def __sum__(self):
        return sum(self.__dict__)

    def __zip__(self):
        return zip(self.__dict__)

    def clear(self, *args, **kwargs):
        return self.__dict__.clear(*args, **kwargs)

    def copy(self, *args, **kwargs):
        return self.__dict__.copy(*args, **kwargs)

    def fromkeys(self, *args, **kwargs):
        return self.__dict__.fromkeys(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.__dict__.get(*args, **kwargs)

    def items(self, *args, **kwargs):
        return self.__dict__.items(*args, **kwargs)

    def keys(self, *args, **kwargs):
        return self.__dict__.keys(*args, **kwargs)

    def popitem(self, *args, **kwargs):
        return self.__dict__.popitem(*args, **kwargs)

    def setdefault(self, *args, **kwargs):
        return self.__dict__.setdefault(*args, **kwargs)

    def pop(self, *args, **kwargs):
        return self.__dict__.pop(*args, **kwargs)

    def values(self, *args, **kwargs):
        return self.__dict__.values(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)


class _Resource(object):
    """
    A _Resource is a helper class that represents an entity (resource)
    on Factura.com's servers. Its methods and information may be accessed
    via HTTP requests.

    **All attributes names are converted to lowercase.**
    """

    def __init__(self, params=None):
        if params is None:
            params = {}
        self._initialize_instance(params)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return str(self.__dict__)

    # --- Static methods ------------------------------------------------------
    @classmethod
    def _make_request(cls, method, path, params, _raise=True):
        """
        Makes an HTTP request to Factura.com's servers.

        Parameters
        ----------
        method : string
            The method to use for the request. i.e. `GET`, `POST`, etc.
        path : string
            The path to where the request will be made.
        params : dictionary
            Parameters used for the request. i.e. the body of the request
            which will be converted to JSON.
        _raise : bool
            Whether to raise an exception on an unsuccesful response. If
            `_raise == False`, this function will fail silently.

        Return Type
        -----------
        `requests.Response`

        Raises
        ------
        `FacturaError` - If `req.ok == False`.
        """
        if method == 'GET':
            if params is None or params == {}:
                url = path
            else:
                try:
                    url = '%s?%s' % (
                        path, urllib.parse.urlencode(params, True))
                except AttributeError:
                    url = '%s?%s' % (
                        path, urllib.urlencode(params, True))
            req = requests.request(
                method, url, headers=_API._HEADERS)
        else:
            if params is None:
                params = ''
            req = requests.request(
                method, path, headers=_API._HEADERS,
                data=json.dumps(params))

        j = json.loads(req.text)

        if req.ok:
            try:
                status = j.pop('status')
            except KeyError:
                status = j.pop('response')
            if status == 'success':
                return req, j
            elif _raise:
                raise FacturaError(j)

    @classmethod
    def _class_name(cls):
        """
        Returns the class name as it appears in URI requests.
        """
        try:
            return '%s' % urllib.parse.quote_plus(cls.__name__.lower())
        except AttributeError:
            return '%s' % urllib.quote_plus(cls.__name__.lower())

    @classmethod
    def _class_url(cls, api_version=None):
        """
        Returns the URL to where the resource's operations reside.
        """
        return '%s/%s' % (API.base(api_version), cls._class_name())

    # --- Private methods -----------------------------------------------------
    def _initialize_instance(self, params):
        """
        Initializes the instance with the passed keyword arguments.
        """
        if 'id' in params.keys():
            self.id = params['id']

        existing_keys = self.__dict__.keys()
        new_keys = params.keys()

        old_keys = (set(existing_keys) - set(['parent'])) - set(new_keys)
        for key in old_keys:
            self.__dict__[key] = None

        for key in new_keys:
            self.__dict__[key] = params[key]

        # converts the keys to lower case of
        # all the nested dictionaries
        stack = [self.__dict__]
        while stack:
            d = stack.pop()
            lowercase = {k.lower(): v for k, v in d.items()}
            d.clear()
            d.update(lowercase)
            for k, v in d.items():
                if isinstance(v, dict):
                    d[k] = _DictHelper(d[k])
                    stack.append(d[k])

    def _instance_url(self):
        """
        Gets the URL pointing to the instance on Factura.com's servers.
        """
        return '%s/%s' % (self._class_url(), self.uid)


class CFDI33(_Resource):
    API_VERSION = 3

    @classmethod
    def _list_url(cls):
        return '%s/list' % (cls._class_url(CFDI33.API_VERSION))

    @classmethod
    def _create_url(cls):
        return '%s/create' % (cls._class_url(CFDI33.API_VERSION))

    def _instance_url(self):
        """
        Gets the URL pointing to the instance on Factura.com's servers.
        """
        return '%s/%s' % (self._class_url(CFDI33.API_VERSION), self.uid)

    def _cancel_url(cls):
        return '%s/cancel' % (cls._instance_url())

    def _send_via_email_url(cls):
        return '%s/email' % (cls._instance_url())

    @classmethod
    def list(cls, params={}):
        """
        Lists the CFDIs that match the passed params.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/listar-cfdis/listar-clientes
        """
        response, j = cls._make_request(
            method='GET',
            path=cls._list_url(),
            params=params)
        return [CFDI33(cfdi) for cfdi in j['data']]

    @classmethod
    def create(cls, params={}):
        """
        Creates a CFDI entity on Factura.com's servers.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/crear-cfdi
        """
        response, j = cls._make_request(
            method='POST',
            path=cls._create_url(),
            params=params)
        j.pop('message')
        return CFDI33(j)

    def cancel(self, params={}):
        self._make_request(
            method='GET',
            path=self._cancel_url(),
            params=params)

    def send_via_email(self, params={}):
        self._make_request(
            method='GET',
            path=self._send_via_email_url(),
            params=params)

    @property
    def xml_url(self):
        return '%s/xml' % (self._instance_url())

    @property
    def pdf_url(self):
        return '%s/pdf' % (self._instance_url())


class Customer(_Resource):
    API_VERSION = 1

    @classmethod
    def _class_url(cls, api_version=None):
        """
        Returns the URL to where the resource's operations reside.
        """
        return '%s/%s' % (API.base(cls.API_VERSION), 'clients')

    def _instance_url(self):
        """
        Gets the URL pointing to the instance on Factura.com's servers.
        """
        return '%s/%s' % (self._class_url(Customer.API_VERSION), self.uid)

    @classmethod
    def _list_url(cls):
        return cls._class_url()

    @classmethod
    def _create_url(cls):
        return '%s/create' % (cls._class_url(cls.API_VERSION))

    @classmethod
    def _find_url(cls):
        return cls._class_url()

    def _update_url(cls):
        return '%s/update' % (cls._instance_url())

    @classmethod
    def list(cls, params={}):
        """
        Lists the Customers that match the passed params.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/listar-cfdis/listar-clientes
        """
        response, j = cls._make_request(
            method='GET',
            path=cls._list_url(),
            params=params)
        return [Customer(cus) for cus in j['data']]

    @classmethod
    def create(cls, params={}):
        """
        Creates a Customer entity on Factura.com's servers.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/crear-cfdi
        """
        response, j = cls._make_request(
            method='POST',
            path=cls._create_url(),
            params=params)
        return Customer(j['data'])

    @classmethod
    def update(cls, params={}):
        """
        Creates a Customer entity on Factura.com's servers.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/crear-cfdi
        """
        response, j = cls._make_request(
            method='POST',
            path=cls._create_url(),
            params=params)
        return Customer(j['data'])

    @classmethod
    def find(cls, params={}):
        """
        Creates a Customer entity on Factura.com's servers.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/crear-cfdi
        """
        response, j = cls._make_request(
            method='GET',
            path=cls._find_url(),
            params=params)
        return Customer(j['data'])
