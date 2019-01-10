# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from shuup.xtheme.layout import Layout
from shuup.xtheme.layout.utils import get_customer_from_context


class PageAnonymousLayout(Layout):
    identifier = "simple-cms-page-anonymous-layout"
    help_text = _("Content in this placeholder is shown for guests and this page only.")

    def get_help_text(self, context):
        page = context.get("page")
        if not page:
            return ""
        return _(
            "Content in this placeholder is shown for guests and %(title)s only." % {"title": page.title})

    def is_valid_context(self, context):
        customer = get_customer_from_context(context)
        return bool(context.get("page")) and bool(customer.is_anonymous)

    def get_layout_data_suffix(self, context):
        return "%s-%s" % (self.identifier, context["page"].pk)


class PageRegisteredLayout(Layout):
    identifier = "simple-cms-page-registered-layout"
    help_text = _("Content in this placeholder is shown for registered customers and this page only.")

    def get_help_text(self, context):
        page = context.get("page")
        if not page:
            return ""
        return _(
            "Content in this placeholder is shown for registered customers and %(title)s only." % {"title": page.title})

    def is_valid_context(self, context):
        customer = get_customer_from_context(context)
        return bool(context.get("page")) and bool(not customer.is_anonymous)

    def get_layout_data_suffix(self, context):
        return "%s-%s" % (self.identifier, context["page"].pk)
