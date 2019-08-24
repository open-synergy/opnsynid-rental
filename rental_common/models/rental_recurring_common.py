# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero


class RentalRecurringFeeCommon(models.AbstractModel):
    _name = "rental.recurring_fee_common"
    _description = "Abstract Model for Rental Recurring Fee"

    detail_id = fields.Many2one(
        string="Details",
        comodel_name="rental.detail_common",
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
    )
    company_id = fields.Many2one(
        string="Company",
        related="detail_id.rental_id.company_id",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        string="Partner",
        related="detail_id.rental_id.partner_id",
        readonly=True,
    )
    type_id = fields.Many2one(
        string="Type",
        related="detail_id.rental_id.type_id",
        readonly=True,
    )

    @api.model
    def _default_pricelist_id(self):
        pricelist_id =\
            self.env.context.get(
                "pricelist_id", False)
        if pricelist_id:
            return pricelist_id

    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=True,
        default=lambda self: self._default_pricelist_id(),
    )
    payment_term_id = fields.Many2one(
        string="Payment Terms",
        comodel_name="account.payment.term",
    )
    price_unit = fields.Float(
        string="Price",
        required=True,
        digits=(16,2),
    )
    qty = fields.Float(
        string="Quantity",
        required=True,
        default=1,
        digits=(16,2),
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
    )

    @api.multi
    @api.depends(
        "qty",
        "price_unit",
        "taxes_id",
    )
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * line.qty
            taxes = line.taxes_id.compute_all(
                price,
                line.qty,
                product=line.product_id,
                partner=line.partner_id
            )
            line.update({
                "price_tax": sum(
                    t.get("amount", 0.0) for t in taxes.get("taxes", [])),
                "price_total": taxes["total_included"],
                "price_subtotal": taxes["total"],
            })

    taxes_id = fields.Many2many(
        string="Taxes",
        comodel_name="account.tax",
        relation="rel_rental_recurring_common_taxes",
        column1="rental_recurring_id",
        column2="tax_id",
    )

    price_subtotal = fields.Float(
        string="Subtotal",
        digits=dp.get_precision("Account"),
        store=True,
        readonly=True,
        compute="_compute_amount",
    )

    price_total = fields.Float(
        string="Total",
        digits=dp.get_precision("Account"),
        store=True,
        readonly=True,
        compute="_compute_amount",
    )
    price_tax = fields.Float(
        string="Tax",
        digits=dp.get_precision("Account"),
        store=True,
        readonly=True,
        compute="_compute_amount",
    )
    date_start = fields.Date(
        string="Start Invoice",
        required=True,
        ondelete="restrict",
    )
    period = fields.Selection(
        string="Period",
        selection=[
            ("B", "Daily(Business Day)"),
            ("D", "Daily(Calendar Day)"),
        ],
        default="B",
        ondelete="restrict",
        required=True,
    )
    period_number = fields.Integer(
        string="Period Number",
        default=1,
        required=True,
        ondelete="restrict",
    )

    recurring_fee_schedule_ids = fields.One2many(
        string="Schedules",
        comodel_name="rental.recurring_fee_schedule_common",
        inverse_name="recurring_fee_id",
    )

    @api.multi
    @api.onchange(
        "product_id",
        "qty",
    )
    def onchange_price_unit(self):
        obj_decimal_precision =\
            self.env["decimal.precision"]
        precision =\
            obj_decimal_precision.precision_get(
                "Product Unit of Measure")
        self.price_unit = 0.0
        product_id = self.product_id
        if product_id:
            if float_is_zero(self.price_unit, precision_digits=precision):
                price = self.pricelist_id.price_get(
                    prod_id=product_id.id,
                    qty=self.qty or 1.0
                )[self.pricelist_id.id]
                self.price_unit = price

    @api.multi
    @api.onchange(
        "product_id",
    )
    def onchange_product_uom(self):
        self.uom_id = False
        if self.product_id:
            product_id = self.product_id
            if product_id:
                if not self.uom_id:
                    self.uom_id = product_id.uom_id.id
