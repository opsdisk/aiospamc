#!/usr/bin/env python3

import zlib

import pytest
from conftest import *

from aiospamc.exceptions import (BadResponse,
                                 ExUsage, ExDataErr, ExNoInput, ExNoUser,
                                 ExNoHost, ExUnavailable, ExSoftware, ExOSErr,
                                 ExOSFile, ExCantCreat, ExIOErr, ExTempFail,
                                 ExProtocol, ExNoPerm, ExConfig, ExTimeout)
from aiospamc.headers import Compress
from aiospamc.responses import Response, Status



def test_response_instantiates():
    response = Response('1.5', Status.EX_OK, 'EX_OK')

    assert 'response' in locals()


@pytest.mark.parametrize('version,status,message,body,headers', [
    ('1.5', Status.EX_OK, 'EX_OK', None, []),
    ('1.5', Status.EX_OK, 'EX_OK', 'Test body\n', []),
    ('1.5', Status.EX_OK, 'EX_OK', 'Test body\n', [Compress()]),
])
def test_response_bytes(version, status, message, body, headers):
    response = Response(version, status, message, body, *headers)

    assert bytes(response).startswith(b'SPAMD/%b' % version.encode())
    assert b' %d ' % status.value in bytes(response)
    assert b' %b\r\n' % message.encode() in bytes(response)
    assert all(repr(header) in repr(response) for header in headers)
    if body:
        if any(isinstance(header, Compress) for header in headers):
            assert bytes(response).endswith(zlib.compress(body.encode()))
        else:
            assert bytes(response).endswith(body.encode())


def test_response_repr():
    response = Response('1.5', Status.EX_OK, 'EX_OK')

    assert repr(response) == ('Response(protocol_version=\'1.5\', '
                              'status_code=Status.EX_OK, '
                              'message=\'EX_OK\', '
                              'headers=(), '
                              'body=None)')


def test_response_parse_valid(response_ok):
    response = Response.parse(response_ok)

    assert 'response' in locals()


@pytest.mark.parametrize('test_input', [
    response_with_body(),
    response_empty_body()
])
def test_response_parse_has_content_length(test_input):
    response = Response.parse(test_input)

    assert response._headers['Content-length']


def test_response_parse_valid_with_body(response_with_body):
    response = Response.parse(response_with_body)

    assert hasattr(response, 'body')


def test_response_parse_invalid(response_invalid):
    with pytest.raises(BadResponse):
        response = Response.parse(response_invalid)


def test_response_parse_empty(response_empty):
    with pytest.raises(BadResponse):
        response = Response.parse(response_empty)

@pytest.mark.parametrize('test_input,expected', [
    (ex_usage(), ExUsage),
    (ex_data_err(), ExDataErr),
    (ex_no_input(), ExNoInput),
    (ex_no_user(), ExNoUser),
    (ex_no_host(), ExNoHost),
    (ex_unavailable(), ExUnavailable),
    (ex_software(), ExSoftware),
    (ex_os_err(), ExOSErr),
    (ex_os_file(), ExOSFile),
    (ex_cant_create(), ExCantCreat),
    (ex_io_err(), ExIOErr),
    (ex_temp_fail(), ExTempFail),
    (ex_protocol(), ExProtocol),
    (ex_no_perm(), ExNoPerm),
    (ex_config(), ExConfig),
    (ex_timeout(), ExTimeout),
])
def test_response_response_exceptions(test_input, expected):
    with pytest.raises(expected):
        response = Response.parse(test_input)
