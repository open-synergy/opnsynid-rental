# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero
import logging

_logger = logging.getLogger(__name__)

try:
    import numpy as np
    import pandas as pd
except (ImportError, IOError) as err:
    _logger.debug(err)


class RentalDetailCommon(models.AbstractModel):
    _name = "rental.detail_common"
    _description = "Abstract Model for Rental Details"

    year_period = fields.Integer(
        string="Year Period",
    )
    month_period = fields.Integer(
        string="Month Period",
    )
    day_period = fields.Integer(
        string="Day Period",
    )
    hour_period = fields.Integer(
        string="Hour Period",
    )

    rental_id = fields.Many2one(
        string="# Rental",
        comodel_name="rental.common",
        required=True,
    )
    object_id = fields.Many2one(
        string="Object",
        comodel_name="rental.object",
        required=True,
    )
    company_id = fields.Many2one(
        string="Company",
        related="rental_id.company_id",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        string="Partner",
        related="rental_id.partner_id",
        readonly=True,
    )
    type_id = fields.Many2one(
        string="Type",
        related="rental_id.type_id",
        readonly=True,
    )
    payment_term_id = fields.Many2one(
        string="Payment Terms",
        related="rental_id.payment_term_id",
        readonly=True,
    )
    fiscal_position_id = fields.Many2one(
        string="Fiscal Position",
        related="rental_id.fiscal_position_id",
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
    year_price_unit = fields.Float(
        string="Year Price Unit",
        required=True,
        default=0.0,
    )
    month_price_unit = fields.Float(
        string="Month Price Unit",
        required=True,
        default=0.0,
    )
    day_price_unit = fields.Float(
        string="Day Price Unit",
        required=True,
        default=0.0,
    )
    hour_price_unit = fields.Float(
        string="Hour Price Unit",
        required=True,
        default=0.0,
    )

    @api.multi
    @api.depends(
        "year_price_unit", "year_period",
        "month_price_unit", "month_period",
        "day_price_unit", "day_period",
        "hour_price_unit", "hour_period",
        "taxes_id",
    )
    def _compute_price_subtotal(self):
        for document in self:
            document.year_price_subtotal = \
                document.year_price_unit * document.year_period
            document.month_price_subtotal = \
                document.month_price_unit * document.month_period
            document.day_price_subtotal = \
                document.day_price_unit * document.day_period
            document.hour_price_subtotal = \
                document.hour_price_unit * document.hour_period
            document.price_subtotal = \
                document.year_price_subtotal + \
                document.month_price_subtotal + \
                document.day_price_subtotal + \
                document.hour_price_subtotal
            taxes = document.taxes_id.compute_all(
                document.price_subtotal,
                1.0,
                partner=document.rental_id.partner_id
            )
            document.price_tax = sum(
                t.get("amount", 0.0) for t in taxes.get("taxes", []))
            document.price_total = taxes["total_included"]

    year_price_subtotal = fields.Float(
        string="Year Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )
    month_price_subtotal = fields.Float(
        string="Month Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )
    day_price_subtotal = fields.Float(
        string="Day Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )
    hour_price_subtotal = fields.Float(
        string="Hour Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )
    price_subtotal = fields.Float(
        string="Price Subtotal",
        compute="_compute_price_subtotal",
        store=True,
    )

    taxes_id = fields.Many2many(
        string="Taxes",
        comodel_name="account.tax",
        relation="rel_rental_detail_common_taxes",
        column1="rental_detail_id",
        column2="tax_id",
    )

    price_total = fields.Float(
        string="Total",
        digits=dp.get_precision("Account"),
        store=True,
        readonly=True,
        compute="_compute_price_subtotal",
    )
    price_tax = fields.Float(
        string="Tax",
        digits=dp.get_precision("Account"),
        store=True,
        readonly=True,
        compute="_compute_price_subtotal",
    )

    date_start = fields.Date(
        string="Start Invoice",
        required=True,
        ondelete="restrict",
    )
    period = fields.Selection(
        string="Period",
        selection=[
            ("D", "Daily"),
            ("MS", "Monthly"),
            ("YS", "Yearly"),
        ],
        default="MS",
        ondelete="restrict",
        required=True,
    )
    period_number = fields.Integer(
        string="Period Number",
        default=1,
        required=True,
        ondelete="restrict",
    )

    schedule_ids = fields.One2many(
        string="Schedules",
        comodel_name="rental.detail_schedule_common",
        inverse_name="detail_id",
    )

    recurring_fee_ids = fields.One2many(
        string="Recurring Fees",
        comodel_name="rental.recurring_fee_common",
        inverse_name="detail_id",
    )

    #TODO: Untuk dianalisa lagi penempatan field yg pas
    date_handover = fields.Datetime(
        string="Date Handover",
        required=True,
        ondelete="restrict",
    )

    #TODO: Untuk dianalisa lagi penempatan field yg pas
    fitting_out = fields.Integer(
        string="Fitting Out(Days)",
        default=30,
        required=True,
        ondelete="restrict",
    )

    @api.multi
    def _compute_rental_state(self):
        for document in self:
            document.rental_state = \
                document.rental_id.state

    rental_state = fields.Selection(
        string="Rental State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Ready To Progress"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("terminate", "Terminate"),
        ],
        readonly=True,
        compute="_compute_rental_state",
        store=False,
    )

    @api.constrains("pricelist_id")
    def check_pricelist_id(self):
        if self.pricelist_id:
            if self.rental_id.pricelist_id.currency_id != \
                    self.pricelist_id.currency_id:
                raise UserError(_(
                    "Currency on Details must be equal to the "
                    "Currency on Header"))

    # @api.multi
    # @api.onchange(
    #     "object_id",
    #     "object_id.product_id",
    #     "qty",
    # )
    # def onchange_price_unit(self):
    #     obj_decimal_precision =\
    #         self.env["decimal.precision"]
    #     precision =\
    #         obj_decimal_precision.precision_get(
    #             "Product Unit of Measure")
    #     self.price_unit = 0.0
    #     test =\
    #         self.env.context.get(
    #             "rental_id", False)
    #     if self.object_id:
    #         product_id = self.object_id.product_id
    #         if product_id:
    #             if float_is_zero(self.price_unit, precision_digits=precision):
    #                 price = self.pricelist_id.price_get(
    #                     prod_id=product_id.id,
    #                     qty=self.qty or 1.0
    #                 )[self.pricelist_id.id]
    #                 self.price_unit = price

    # @api.multi
    # @api.onchange(
    #     "object_id",
    #     "object_id.product_id",
    # )
    # def onchange_product_uom(self):
    #     self.uom_id = False
    #     if self.object_id:
    #         product_id = self.object_id.product_id
    #         if product_id:
    #             if not self.uom_id:
    #                 self.uom_id = product_id.uom_id.id

    @api.multi
    def action_compute_schedule(self):
        for document in self:
            document._compute_schedule()

    @api.multi
    def _compute_schedule(self):
        self.ensure_one()
        if self.schedule_ids:
            self.schedule_ids.unlink()
        amount = self._get_period_amount()
        amount_tax = self._get_period_amount_tax()
        obj_schedule = self.env[self._get_schedule_name()]
        pd_schedule = self._get_schedule()
        offset = datetime.strptime(self.date_start, "%Y-%m-%d").day
        for period in range(0, self.period_number):
            dt_period = pd_schedule[period] + pd.DateOffset(day=offset)
            obj_schedule.create({
                "detail_id": self.id,
                "date": dt_period.strftime("%Y-%m-%d"),
                "amount": amount,
                "amount_tax": amount_tax,
            })

    @api.multi
    def _get_schedule(self):
        self.ensure_one()
        return pd.date_range(
            start=self.date_start,
            periods=self.period_number,
            freq=self.period,
        ).to_pydatetime()

    @api.multi
    def _get_schedule_name(self):
        self.ensure_one()
        model_name = str(self._model)
        obj_field = self.env["ir.model.fields"]
        criteria = [
            ("model_id.model", "=", model_name),
            ("name", "=", "schedule_ids"),
        ]
        field = obj_field.search(criteria)[0]
        return field.relation

    @api.multi
    def _get_period_amount(self):
        self.ensure_one()
        return abs(np.pmt(0.0, self.period_number, self.price_subtotal))

    @api.multi
    def _get_period_amount_tax(self):
        self.ensure_one()
        return abs(np.pmt(0.0, self.period_number, self.price_tax))
