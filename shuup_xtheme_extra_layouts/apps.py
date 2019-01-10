# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup_xtheme_extra_layouts"
    verbose_name = "Shuup Xtheme Extra Layouts"
    label = "shuup_xtheme_extra_layouts"
    provides = {
        "xtheme_layout": [
            "shuup_xtheme_extra_layouts.layouts.PageRegisteredLayout",
            "shuup_xtheme_extra_layouts.layouts.PageAnonymousLayout",
        ],
    }
