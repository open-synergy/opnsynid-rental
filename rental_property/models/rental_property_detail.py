# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class RentalPropertyDetail(models.Model):
    _name = "rental.property_detail"
    #TODO: _description
    _inherit = [
        "rental.detail_common"
    ]
    year_period = fields.Integer(
        related="rental_id.year_period",
        store=True,
    )
    month_period = fields.Integer(
        related="rental_id.month_period",
        store=True,
    )
    day_period = fields.Integer(
        related="rental_id.day_period",
        store=True,
    )
    hour_period = fields.Integer(
        related="rental_id.hour_period",
        store=True,
    )

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

    recurring_fee_ids = fields.One2many(
        string="Recurring Fees",
        comodel_name="rental.property_recurring_fee",
        inverse_name="detail_id",
    )

    taxes_id = fields.Many2many(
        string="Taxes",
        comodel_name="account.tax",
        relation="rel_rental_property_detail_taxes",
        column1="property_detail_id",
        column2="tax_id"
    )
