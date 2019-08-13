# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp


#TODO: RentalRecurringFeeCommon
class RentalDetailRecurringCommon(models.AbstractModel):
    #TODO: rental.recurring_fee_common
    _name = "rental.detail_recurring_common"
    #TODO: Abstract Model for Rental Recurring Fee
    _description = "Abstract Model for Rental Recurring"

    detail_id = fields.Many2one(
        string="Details",
        comodel_name="rental.detail_common",
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
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
            ("MS", "Monthly(Calendar Month Start)"),
            ("M", "Monthly(Calendar Month End)"),
            ("BMS", "Monthly(Business Month Start)"),
            ("BM", "Monthly(Business Month End)"),
            ("YS", "Yearly(Calendar Year Start)"),
            ("Y", "Yearly(Calendar Year End)"),
            ("BYS", "Yearly(Business Year Start)"),
            ("BY", "Yearly(Business Year End)"),
        ],
        default="M",
        ondelete="restrict",
        required=True,
    )
    period_number = fields.Integer(
        string="Period Number",
        default=1,
        required=True,
        ondelete="restrict",
    )
