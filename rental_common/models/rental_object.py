# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class RentalObject(models.AbstractModel):
    _name = "rental.object"
    _description = "Rental Object"

    rental_prepaid_income_account_id = fields.Many2one(
        string="Rental Prepaid Income Account",
        comodel_name="account.account",
        company_dependent=True,
    )
    rental_income_account_id = fields.Many2one(
        string="Rental Income Account",
        comodel_name="account.account",
        company_dependent=True,
    )
    rent_ok = fields.Boolean(
        string="Can Be Rent",
    )
