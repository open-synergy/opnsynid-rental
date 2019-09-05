# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class RentalUpfrontCostCommon(models.AbstractModel):
    _name = "rental.upfront_cost_common"
    _description = "Abstract Model for Rental Upfront Cost"
    _order = "sequence, id"

    @api.multi
    @api.depends(
        "price_unit",
        "qty",
        "tax_ids",
    )
    def _compute_amount(self):
        for document in self:
            amount_untaxed = amount_tax = amount_total = 0.0
            taxes = document.tax_ids.compute_all(
                document.price_unit * document.qty,
                1.0,
                partner=document.rental_id.partner_id
            )
            amount_untaxed = taxes["total"]
            amount_total = taxes["total_included"]
            amount_tax = amount_total - amount_untaxed
            document.amount_untaxed = amount_untaxed
            document.amount_tax = amount_tax
            document.amount_total = amount_total

    @api.multi
    def _compute_allowed_product(self):
        for document in self:
            document.allowed_product_ids = \
                document.type_id.allowed_upfront_product_ids.ids
            document.allowed_product_categ_ids = \
                document.type_id.allowed_upfront_product_categ_ids.ids

    rental_id = fields.Many2one(
        string="# Rental",
        comodel_name="rental.common",
        required=True,
    )
    type_id = fields.Many2one(
        string="Type",
        related="rental_id.type_id",
        comodel_name="rental.type",
        store=False,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
        required=True,
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Upfront Products",
        comodel_name="product.product",
        compute="_compute_allowed_product",
        store=False,
    )
    allowed_product_categ_ids = fields.Many2many(
        string="Allowed Upfront Product Categories",
        comodel_name="product.category",
        compute="_compute_allowed_product",
        store=False,
    )
    product_id = fields.Many2one(
        string="Upfront Cost",
        comodel_name="product.product",
        required=True,
    )
    price_unit = fields.Float(
        string="Price",
        required=True,
    )
    qty = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
    )
    product_uom_categ_id = fields.Many2one(
        string="Product UoM Category",
        comodel_name="product.uom.categ",
        related="product_id.uom_id.category_id",
        store=False,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
        required=True,
    )
    tax_ids = fields.Many2many(
        string="Taxes",
        comodel_name="account.tax",
    )
    amount_untaxed = fields.Float(
        string="Amount Untaxed",
        store=True,
        compute="_compute_amount",
    )
    amount_tax = fields.Float(
        string="Taxes",
        store=True,
        compute="_compute_amount",
    )
    amount_total = fields.Float(
        string="Amount Total",
        store=True,
        compute="_compute_amount",
    )

    @api.onchange(
        "product_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.multi
    def _get_invoice_line_account(self):
        self.ensure_one()
        return self.product_id.prepaid_income_account_id

    @api.multi
    def _prepare_invoice_line(self):
        self.ensure_one()

        account = self._get_invoice_line_account()
        if not account:
            raise UserError(_(
                "Account Is Empty "
                "Please Contact Administrator"))

        return {
            "name": self.product_id.description_sale or self.product_id.name,
            "account_id": account.id,
            "product_id": self.product_id.id,
            "uos_id": self.uom_id.id,
            "quantity": self.qty,
            "price_unit": self.price_unit,
            "invoice_line_tax_id": [(6, 0, self.tax_ids.ids)],
            "discount": 0.0,
            "account_analytic_id": False,
        }
