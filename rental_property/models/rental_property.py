# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class RentalProperty(models.Model):
    _name = "rental.property"
    #TODO: _description
    _inherit = [
        "rental.common"
    ]

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_policy(self):
        _super = super(RentalProperty, self)
        _super._compute_policy()

    @api.model
    def _default_type_id(self):
        return self.env.ref(
            "rental_property."
            "rental_property_type").id

    type_id = fields.Many2one(
        default=lambda self: self._default_type_id(),
    )
    detail_ids = fields.One2many(
        comodel_name="rental.property_detail",
    )
