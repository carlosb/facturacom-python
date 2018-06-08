#!/usr/bin/python

import platform
import requests

import urllib

try:
    import json
except ImportError:
    import simplejson as json


def api_version(version):
    def decorator(func):
        func.api_version = version
        return func
    return decorator


class FacturaError(Exception):
    def __init__(self, error_json):
        super(FacturaError, self).__init__(error_json)
        self.error_json = error_json


class _API:
    SANDBOX_HOST = 'http://private-anon-dab239ca03-facturacom.apiary-mock.com'
    PRODUCTION_HOST = 'https://factura.com'
    DEFAULT_VERSION = '3'
    ALLOWED_MODES = set(['SANDBOX', 'PRODUCTION'])

    DATA = {
        'lang': 'python',
        'lang_version': platform.python_version(),
        'uname': platform.uname()
    }

    HEADERS = {
        'Content-type': 'application/json',
        'X-Facturacom-Client-User-Agent': json.dumps(DATA),
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
        _API.HEADERS['F-API-KEY'] = value
        self._key = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        _API.HEADERS['F-SECRET-KEY'] = value
        self._secret_key = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in _API.ALLOWED_MODES:
            raise FacturaError({
                'message': 'Unknown API mode. Please choose between: %s' %
                ', '.join(_API.ALLOWED_MODES)
            })
        self._mode = value

    def base(self, version=None):
        if version is None:
            version = _API.DEFAULT_VERSION
        if self._mode == 'SANDBOX':
            return '%s/api/v%s' % (_API.SANDBOX_HOST, version)
        elif self._mode == 'PRODUCTION':
            return '%s/api/v%s' % (_API.PRODUCTION_HOST, version)
        else:
            raise FacturaError({
                'message': 'Unknown API mode. Please choose between: %s' %
                ', '.join(_API.ALLOWED_MODES)
            })


API = _API()  # The API singleton to be used


class _Resource(object):
    """
    A _Resource is a helper class that represents an entity (resource)
    on Factura.com's servers. Its methods and information may be accessed
    via HTTP requests.
    """

    def __init__(self, params=None):
        if params is None:
            params = {}
        self._initialize_instance(params)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self):
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
                method, url, headers=_API.HEADERS)
        else:
            if params is None:
                params = ''
            req = requests.request(
                method, path, headers=_API.HEADERS,
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
    def create(cls, params):
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

    def cancel(self, params):
        self._make_request(
            method='GET',
            path=self._cancel_url(),
            params=params)

    def send_via_email(self, params):
        self._make_request(
            method='GET',
            path=self._send_via_email_url(),
            params=params)

    def xml_url(cls):
        return '%s/xml' % (cls._instance_url())

    def pdf_url(cls):
        return '%s/pdf' % (cls._instance_url())


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
    def create(cls, params):
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
    def update(cls, params):
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
    def find(cls, params):
        """
        Creates a Customer entity on Factura.com's servers.

        See more
        --------
        https://facturacom.docs.apiary.io/#reference/cfdi-3.3/crear-cfdi
        """
        response, j = cls._make_request(
            method='GET',
            path=cls._create_url(),
            params=params)
        return Customer(j['data'])
