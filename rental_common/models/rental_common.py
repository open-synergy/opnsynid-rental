# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import logging
_logger = logging.getLogger(__name__)

try:
    import pandas as pd
    import numpy as np
except (ImportError, IOError) as err:
    _logger.debug(err)


class RentalCommon(models.AbstractModel):
    _name = "rental.common"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "base.cancel.reason_common",
        "base.terminate.reason_common",
    ]
    _description = "Abstract Model for Rental"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_user_id(self):
        return self.env.user.id

    @api.multi
    def _compute_policy(self):
        _super = super(RentalCommon, self)
        _super._compute_policy()

    @api.multi
    @api.depends(
        "date_start", "date_end",
    )
    def _compute_rental_period(self):
        for document in self:
            year_period = month_period = day_period = hour_period = 0
            if document.date_start and document.date_end:
                dt_start = pd.to_datetime(document.date_start)
                dt_end = pd.to_datetime(document.date_end)
                year_period = int((dt_end - dt_start) / np.timedelta64(1, "Y"))
                dt_temp_year = dt_start + pd.DateOffset(years=year_period)
                month_period = int((dt_end - dt_temp_year) /
                                   np.timedelta64(1, "M"))
                dt_temp_month = dt_temp_year + \
                    pd.DateOffset(months=month_period)
                day_period = int((dt_end - dt_temp_month) /
                                 np.timedelta64(1, "D"))
                dt_temp_day = dt_temp_month + pd.DateOffset(days=day_period)
                hour_period = int((dt_end - dt_temp_day) /
                                  np.timedelta64(1, "h"))
            document.year_period = year_period
            document.month_period = month_period
            document.day_period = day_period
            document.hour_period = hour_period

    @api.multi
    def _compute_upfront_cost(self):
        for document in self:
            amount_untaxed = amount_tax = amount_total = 0.0
            for upfront in document.upfront_cost_ids:
                amount_untaxed += upfront.amount_untaxed
                amount_tax += upfront.amount_tax
                amount_total += upfront.amount_total
            document.upfront_amount_untaxed = amount_untaxed
            document.upfront_amount_tax = amount_tax
            document.upfront_amount_total = amount_total

    name = fields.Char(
        string="# Document",
        default="/",
        required=True,
        copy=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="rental.type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    contact_id = fields.Many2one(
        string="Contact",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    mailing_id = fields.Many2one(
        string="Correspondence",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    payment_term_id = fields.Many2one(
        string="Payment Terms",
        comodel_name="account.payment.term",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        readonly=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    year_pricelist_id = fields.Many2one(
        string="Yearly Pricelist",
        comodel_name="product.pricelist",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    month_pricelist_id = fields.Many2one(
        string="Monthly Pricelist",
        comodel_name="product.pricelist",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    day_pricelist_id = fields.Many2one(
        string="Daily Pricelist",
        comodel_name="product.pricelist",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    hour_pricelist_id = fields.Many2one(
        string="Hourly Pricelist",
        comodel_name="product.pricelist",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    fiscal_position_id = fields.Many2one(
        string="Fiscal Position",
        comodel_name="account.fiscal.position"
    )
    date_start = fields.Datetime(
        string="Date Start",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_end = fields.Datetime(
        string="Date End",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    year_period = fields.Integer(
        string="Year Period",
        compute="_compute_rental_period",
        store=True,
    )
    month_period = fields.Integer(
        string="Month Period",
        compute="_compute_rental_period",
        store=True,
    )
    day_period = fields.Integer(
        string="Day Period",
        compute="_compute_rental_period",
        store=True,
    )
    hour_period = fields.Integer(
        string="Hour Period",
        compute="_compute_rental_period",
        store=True,
    )
    user_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.users",
        default=lambda self: self._default_user_id(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    detail_ids = fields.One2many(
        string="Items",
        comodel_name="rental.detail_common",
        inverse_name="rental_id",
        readonly=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    # Upfront cost section
    upfront_cost_ids = fields.One2many(
        string="Upfront Cost",
        comodel_name="rental.upfront_cost_common",
        inverse_name="rental_id",
        readonly=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    upfront_amount_untaxed = fields.Float(
        string="Upfront Amount Untaxed",
        store=True,
        compute="_compute_upfront_cost",
    )
    upfront_amount_tax = fields.Float(
        string="Upfront Taxes",
        store=True,
        compute="_compute_upfront_cost",
    )
    upfront_amount_total = fields.Float(
        string="Upfront Amount Total",
        store=True,
        compute="_compute_upfront_cost",
    )
    upfront_invoice_id = fields.Many2one(
        string="Upfront Invoice",
        comodel_name="account.invoice",
        readonly=True,
        ondelete="restrict",
    )
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Ready To Progress"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("terminate", "Terminate"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )
    # Policy Field
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
    )
    start_ok = fields.Boolean(
        string="Can Start",
        compute="_compute_policy",
    )
    done_ok = fields.Boolean(
        string="Can Finish",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    terminate_ok = fields.Boolean(
        string="Can Terminate",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )
    # Log Fields
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
    )
    confirm_user_id = fields.Many2one(
        string="Confirmed By",
        comodel_name="res.users",
        readonly=True,
    )
    approve_date = fields.Datetime(
        string="Approve Date",
        readonly=True,
    )
    approve_user_id = fields.Many2one(
        string="Approve By",
        comodel_name="res.users",
        readonly=True,
    )
    start_user_id = fields.Many2one(
        string="Start By",
        comodel_name="res.users",
        readonly=True,
    )
    start_date = fields.Datetime(
        string="Start Date",
        readonly=True,
    )
    done_date = fields.Datetime(
        string="Finish Date",
        readonly=True,
    )
    done_user_id = fields.Many2one(
        string="Finished By",
        comodel_name="res.users",
        readonly=True,
    )
    cancel_date = fields.Datetime(
        string="Cancel Date",
        readonly=True,
    )
    cancel_user_id = fields.Many2one(
        string="Cancelled By",
        comodel_name="res.users",
        readonly=True,
    )
    terminate_date = fields.Datetime(
        string="Terminate Date",
        readonly=True,
    )
    terminate_user_id = fields.Many2one(
        string="Terminate By",
        comodel_name="res.users",
        readonly=True,
    )

    @api.constrains(
        "date_start",
        "date_end"
    )
    def _check_real_date(self):
        strWarning = _(
            "Date Start must be "
            "greater than Date End")
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise UserError(strWarning)

    @api.constrains(
        "date_start",
        "state",
    )
    # TODO: Rental hanya bisa dimulai ketika tanggal dan waktu saat ini sama
    # dengan atau lebih besar dari start date
    def _check_no_start_before_date(self):
        pass

    @api.multi
    @api.onchange(
        "partner_id"
    )
    def onchange_pricelist_id(self):
        if not self.partner_id:
            self.pricelist_id = False
            return
        # TODO: Jangan menggunakan field pricelist yg sudah ada
        # Data pricelist di bawah dikhususkan untuk sale.order saja
        self.pricelist_id = (
            self.partner_id.property_product_pricelist and
            self.partner_id.property_product_pricelist.id or
            False
        )

    @api.onchange(
        "currency_id",
        "type_id",
    )
    def onchange_year_pricelist_id(self):
        self.year_pricelist_id = False
        if self.currency_id and \
                self.type_id and \
                self.type_id.year_pricelist_id and \
                self.type_id.year_pricelist_id.currency_id == self.currency_id:
            self.year_pricelist_id = self.type_id.year_pricelist_id

    @api.onchange(
        "currency_id",
        "type_id",
    )
    def onchange_month_pricelist_id(self):
        self.month_pricelist_id = False
        currency = self.currency_id
        if self.currency_id and \
                self.type_id and \
                self.type_id.month_pricelist_id and \
                self.type_id.month_pricelist_id.currency_id == currency:
            self.month_pricelist_id = self.type_id.month_pricelist_id

    @api.onchange(
        "currency_id",
        "type_id",
    )
    def onchange_day_pricelist_id(self):
        self.day_pricelist_id = False
        if self.currency_id and \
                self.type_id and \
                self.type_id.day_pricelist_id and \
                self.type_id.day_pricelist_id.currency_id == self.currency_id:
            self.day_pricelist_id = self.type_id.day_pricelist_id

    @api.onchange(
        "currency_id",
        "type_id",
    )
    def onchange_hour_pricelist_id(self):
        self.hour_pricelist_id = False
        if self.currency_id and \
                self.type_id and \
                self.type_id.hour_pricelist_id and \
                self.type_id.hour_pricelist_id.currency_id == self.currency_id:
            self.hour_pricelist_id = self.type_id.hour_pricelist_id

    @api.multi
    @api.onchange(
        "partner_id"
    )
    def onchange_payment_term_id(self):
        if not self.partner_id:
            self.payment_term_id = False
            return

        obj_res_partner =\
            self.env["res.partner"]
        partner = obj_res_partner.browse(self.partner_id.id)
        addr = partner.address_get(["invoice"])
        invoice_part = obj_res_partner.browse(addr["invoice"])
        self.payment_term_id = (
            invoice_part.property_payment_term and
            invoice_part.property_payment_term.id or
            False
        )

    @api.multi
    @api.onchange(
        "partner_id",
        "company_id"
    )
    def onchange_fiscal_position_id(self):
        if not self.partner_id:
            self.fiscal_position_id = False
            return

        obj_fiscal_position =\
            self.env["account.fiscal.position"]
        self.fiscal_position_id =\
            obj_fiscal_position.get_fiscal_position(
                self.company_id.id,
                self.partner_id.id
            )

    @api.onchange(
        "partner_id",
    )
    def onchange_contact_id(self):
        self.contact_id = False

    @api.onchange(
        "partner_id",
    )
    def onchange_mailing_id(self):
        self.mailing_id = False

    @api.multi
    def action_confirm(self):
        msg = _("Warning Message")
        for document in self:
            if not document._check_availability():
                raise UserError(msg)
            for detail in document.detail_ids:
                detail._compute_schedule()
            for recurring in document.detail_ids.recurring_fee_ids:
                recurring._compute_schedule()
            document.write(document._prepare_confirm_data())

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())

    @api.multi
    def action_start(self):
        for document in self:
            document._check_upfront_invoice()
            document.write(document._prepare_start_data())

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())

    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())

    @api.multi
    def action_terminate(self):
        for document in self:
            document.write(document._prepare_terminate_data())

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def _check_availability(self):
        self.ensure_one()
        result = True
        return result

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": "confirm",
            "confirm_date": fields.Datetime.now(),
            "confirm_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        upfront_invoice = self._create_upfront_invoice()
        invoice_id = upfront_invoice and upfront_invoice.id or False
        return {
            "state": "approve",
            "approve_date": fields.Datetime.now(),
            "approve_user_id": self.env.user.id,
            "upfront_invoice_id": invoice_id,
        }

    @api.multi
    def _prepare_start_data(self):
        self.ensure_one()
        return {
            "state": "open",
            "start_date": fields.Datetime.now(),
            "start_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
            "done_date": fields.Datetime.now(),
            "done_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_terminate_data(self):
        self.ensure_one()
        return {
            "state": "terminate",
            "terminate_date": fields.Datetime.now(),
            "terminate_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "approve_date": False,
            "approve_user_id": False,
            "start_date": False,
            "start_user_id": False,
            "done_date": False,
            "done_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
        }

    @api.multi
    def _get_upfront_receivable_account(self):
        self.ensure_one()
        return self.type_id.unfront_cost_receivable_account_id

    @api.multi
    def _get_upfront_receivable_journal(self):
        self.ensure_one()
        return self.type_id.unfront_cost_journal_id

    @api.multi
    def _prepare_upfront_cost_invoice(self):
        self.ensure_one()
        line_ids = []

        account = self._get_upfront_receivable_account()
        if not account:
            raise UserError(_(
                "Account Is Empty "
                "Please Contact Administrator"))

        journal = self._get_upfront_receivable_journal()
        if not journal:
            raise UserError(_(
                "Journal Is Empty "
                "Please Contact Administrator"))

        for upfront in self.upfront_cost_ids:
            line_ids.append((0, 0, upfront._prepare_invoice_line()))

        return {
            "origin": self.name,
            "partner_id": self.partner_id.id,
            "account_id": account.id,
            "payment_term": self.payment_term_id.id,
            "type": "out_invoice",
            "company_id": self.company_id.id,
            "currency_id": self.currency_id.id,
            "journal_id": journal.id,
            "invoice_line": line_ids,
        }

    @api.multi
    def _create_upfront_invoice(self):
        self.ensure_one()
        if not self.upfront_cost_ids:
            return False

        obj_invoice = self.env["account.invoice"]
        invoice = obj_invoice.create(self._prepare_upfront_cost_invoice())
        return invoice

    @api.multi
    def _check_upfront_invoice(self):
        self.ensure_one()
        if self.upfront_invoice_id and \
                self.upfront_invoice_id.state != "paid":
            msg = _("Upfront cost unpaid!")
            raise UserError(msg)
        return True

    @api.model
    def create(self, values):
        _super = super(RentalCommon, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write({
            "name": sequence,
        })
        return result

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(RentalCommon, self)
        _super.unlink()
