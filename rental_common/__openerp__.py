# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Common Rental Feature",
    "version": "8.0.2.0.0",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_cancel_reason",
        "base_terminate_reason",
        "base_print_policy",
        "mail",
        "product_prepaid_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_pricelist_type_data.xml",
        "menu.xml",
        "views/rental_type_views.xml",
        "views/rental_common_views.xml",
        "views/rental_detail_common_views.xml",
        "views/rental_detail_schedule_common_views.xml",
    ],
}
