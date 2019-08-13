# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class RentalPropertyDetail(models.Model):
    _name = "rental.property_detail"
    _inherit = [
        "rental.detail_common"
    ]

    rental_id = fields.Many2one(
        comodel_name="rental.property",
        required=True,
        ondelete="cascade",
    )

    object_id = fields.Many2one(
        string="Property",
        comodel_name="property.object",
        required=True,
    )

    schedule_ids = fields.One2many(
        string="Schedule",
        comodel_name="rental.property_detail_schedule",
        inverse_name="detail_id",
    )

    recurring_ids = fields.One2many(
        string="Recurrings",
        comodel_name="rental.property_detail_recurring",
        inverse_name="detail_id",
    )

    taxes_id = fields.Many2many(
        string="Taxes",
        comodel_name="account.tax",
        relation="rel_rental_property_detail_taxes",
        column1="property_detail_id",
        column2="tax_id"
    )
