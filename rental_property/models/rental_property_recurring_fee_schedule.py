# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class RentalPropertyRecurringFeeSchedule(models.Model):
    _name = "rental.property_recurring_fee_schedule"
    _inherit = [
        "rental.recurring_fee_schedule_common"
    ]
    _description = "Rental Property Reccuring Fee Schedule"

    @api.multi
    def _compute_rental_state(self):
        _super = super(RentalPropertyRecurringFeeSchedule, self)
        _super._compute_rental_state()

    recurring_fee_id = fields.Many2one(
        string="Details",
        comodel_name="rental.property_recurring_fee",
    )
    invoice_id = fields.Many2one(
        related="invoice_line_id.invoice_id",
    )
