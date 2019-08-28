# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class RentalPropertyDetailSchedule(models.Model):
    _name = "rental.property_detail_schedule"
    #TODO: _description
    _inherit = [
        "rental.detail_schedule_common"
    ]
    _description = "Rental Property Schedule"

    @api.multi
    def _compute_rental_state(self):
        _super = super(RentalPropertyDetailSchedule, self)
        _super._compute_rental_state()

    detail_id = fields.Many2one(
        string="Details",
        comodel_name="rental.property_detail",
    )
    invoice_id = fields.Many2one(
        related="invoice_line_id.invoice_id",
    )
