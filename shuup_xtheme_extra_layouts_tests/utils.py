# This file is part of Shuup.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import datetime
import string
import uuid

from bs4 import BeautifulSoup
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from django.test.client import RequestFactory
from django.utils.crypto import get_random_string
from shuup.simple_cms.models import Page
from shuup.testing.factories import get_default_shop
from shuup.testing.utils import apply_request_middleware
from shuup.xtheme.editing import is_edit_mode, set_edit_mode

from .faux_users import SuperUser


CONTENT = """
<h1>Bacon ipsum dolor amet doner ham brisket</h1>

<p>Pig tenderloin hamburger sausage pork shankle.
Shoulder chicken alcatra boudin.
<a href="https://baconipsum.com">Rump short ribs porchetta shankle bacon.</a></p>
"""


def initialize_page(**kwargs):
    """
    :rtype: shuup.simple_cms.models.Page
    """
    kwargs.setdefault("_current_language", "en")
    kwargs.setdefault("title", "test")
    kwargs.setdefault("url", str(uuid.uuid4()))
    kwargs.setdefault("content", CONTENT)
    if kwargs.pop("eternal", False):
        kwargs.setdefault("available_from", datetime.datetime(1900, 1, 1))
        kwargs.setdefault("available_to", datetime.datetime(2900, 1, 1))
    page = Page(**kwargs)
    page.full_clean()
    return page


def create_page(**kwargs):
    """
    :rtype: shuup.simple_cms.models.Page
    """
    page = initialize_page(**kwargs)
    page.save()
    return page


def get_request(edit=False):
    get_default_shop()
    request = apply_request_middleware(RequestFactory().get("/"))
    request.session = {}
    if edit:
        request.user = SuperUser()
        set_edit_mode(request, True)
        assert is_edit_mode(request)
    else:
        request.user = AnonymousUser()
    return request


def printable_gibberish(length=10):
    return get_random_string(length, allowed_chars=string.ascii_lowercase)


class SmartClient(Client):
    def soup(self, path, data=None, method="get"):
        response = getattr(self, method)(path=path, data=data)
        assert 200 <= response.status_code <= 299, "Valid status"
        return BeautifulSoup(response.content)

    def response_and_soup(self, path, data=None, method="get"):
        response = getattr(self, method)(path=path, data=data)
        return (response, BeautifulSoup(response.content))
