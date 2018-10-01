# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import datetime

import pytest
from django.conf import settings
from django.core.urlresolvers import reverse

from shuup.testing import factories
from shuup.xtheme import set_current_theme
from shuup.xtheme.layout.utils import get_layout_data_key
from shuup.xtheme.view_config import ViewConfig
from .utils import create_page
from .utils import printable_gibberish, SmartClient
from .utils import get_request

from shuup_xtheme_extra_layouts.layouts import (
    PageAnonymousLayout, PageRegisteredLayout
)


@pytest.mark.django_db
def test_page_anonymous_layout():
    if "shuup.simple_cms" not in settings.INSTALLED_APPS:
        pytest.skip("Need shuup.simple_cms in INSTALLED_APPS")

    if "shuup.xtheme" not in settings.INSTALLED_APPS:
        pytest.skip("Need shuup.xtheme in INSTALLED_APPS")

    shop = factories.get_default_shop()
    theme = set_current_theme("shuup.themes.classic_gray", shop)
    view_config = ViewConfig(theme=theme, shop=shop, view_name="PageView", draft=True)
    page1_content = printable_gibberish()
    page1 = create_page(available_from=datetime.date(1917, 12, 6), content=page1_content, shop=shop, url="test1")
    page2_content = printable_gibberish()
    page2 = create_page(available_from=datetime.date(1917, 12, 6), content=page2_content, shop=shop, url="test2")

    person = factories.create_random_person(shop=shop)
    person.user = factories.create_random_user()
    password = "kisu"
    person.user.set_password(password)
    person.user.save()
    person.save()

    placeholder_name = "cms_page"
    request = get_request()
    context = {"page": page1, "request": request}
    layout = view_config.get_placeholder_layout(PageAnonymousLayout, placeholder_name, context=context)
    assert isinstance(layout, PageAnonymousLayout)
    assert layout.get_help_text({}) == ""  # Invalid context for help text
    assert page1.title in layout.get_help_text(context)

    # Make sure layout is empty
    serialized = layout.serialize()
    assert len(serialized["rows"]) == 0
    assert serialized["name"] == placeholder_name

    # Add custom plugin to page
    layout.begin_column({"md": 8})
    plugin_text = printable_gibberish()
    layout.add_plugin("text", {"text": plugin_text})
    view_config.save_placeholder_layout(get_layout_data_key(placeholder_name, layout, context), layout)
    view_config.publish()

    c = SmartClient()
    soup = c.soup(reverse("shuup:cms_page", kwargs={"url": page1.url}))
    page_content = soup.find("div", {"class": "page-content"})
    assert page1_content in page_content.text
    assert plugin_text in page_content.text

    # Make sure content not available for page2
    c = SmartClient()
    soup = c.soup(reverse("shuup:cms_page", kwargs={"url": page2.url}))
    page_content = soup.find("div", {"class": "page-content"})
    assert page2_content in page_content.text
    assert plugin_text not in page_content.text

    # Make sure content not available for logged in users
    c = SmartClient()
    c.login(username=person.user.username, password=password)
    soup = c.soup(reverse("shuup:cms_page", kwargs={"url": page1.url}))
    page_content = soup.find("div", {"class": "page-content"})
    assert page1_content in page_content.text
    assert plugin_text not in page_content.text


@pytest.mark.django_db
def test_page_registered_layout():
    if "shuup.simple_cms" not in settings.INSTALLED_APPS:
        pytest.skip("Need shuup.simple_cms in INSTALLED_APPS")

    if "shuup.xtheme" not in settings.INSTALLED_APPS:
        pytest.skip("Need shuup.xtheme in INSTALLED_APPS")

    shop = factories.get_default_shop()
    theme = set_current_theme("shuup.themes.classic_gray", shop)
    view_config = ViewConfig(theme=theme, shop=shop, view_name="PageView", draft=True)
    page1_content = printable_gibberish()
    page1 = create_page(available_from=datetime.date(1917, 12, 6), content=page1_content, shop=shop, url="test1")
    page2_content = printable_gibberish()
    page2 = create_page(available_from=datetime.date(1917, 12, 6), content=page2_content, shop=shop, url="test2")

    person = factories.create_random_person(shop=shop)
    person.user = factories.create_random_user()
    password = "kisu"
    person.user.set_password(password)
    person.user.save()
    person.save()

    placeholder_name = "cms_page"
    request = get_request()
    request.customer = person
    context = {"page": page1, "request": request}
    layout = view_config.get_placeholder_layout(PageRegisteredLayout, placeholder_name, context=context)
    assert isinstance(layout, PageRegisteredLayout)
    assert layout.get_help_text({}) == ""  # Invalid context for help text
    assert page1.title in layout.get_help_text(context)

    # Make sure layout is empty
    serialized = layout.serialize()
    assert len(serialized["rows"]) == 0
    assert serialized["name"] == placeholder_name

    # Add custom plugin to page
    layout.begin_column({"md": 8})
    plugin_text = printable_gibberish()
    layout.add_plugin("text", {"text": plugin_text})
    view_config.save_placeholder_layout(get_layout_data_key(placeholder_name, layout, context), layout)
    view_config.publish()

    # Make sure content not available for guests
    c = SmartClient()
    soup = c.soup(reverse("shuup:cms_page", kwargs={"url": page1.url}))
    page_content = soup.find("div", {"class": "page-content"})
    assert page1_content in page_content.text
    assert plugin_text not in page_content.text

    # Make sure content not available for page2
    c = SmartClient()
    soup = c.soup(reverse("shuup:cms_page", kwargs={"url": page2.url}))
    page_content = soup.find("div", {"class": "page-content"})
    assert page2_content in page_content.text
    assert plugin_text not in page_content.text

    # Now finally content should be available
    c = SmartClient()
    c.login(username=person.user.username, password=password)
    soup = c.soup(reverse("shuup:cms_page", kwargs={"url": page1.url}))
    page_content = soup.find("div", {"class": "page-content"})
    assert page1_content in page_content.text
    assert plugin_text in page_content.text
