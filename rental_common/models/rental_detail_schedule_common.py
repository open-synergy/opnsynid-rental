# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class RentalDetailScheduleCommon(models.AbstractModel):
    _name = "rental.detail_schedule_common"
    _description = "Abstract Model for Rental Schedule"

    @api.multi
    def _compute_rental_state(self):
        for document in self:
            document.rental_state = \
                document.detail_id.rental_id.state

    detail_id = fields.Many2one(
        string="Details",
        comodel_name="rental.detail_common",
        ondelete="cascade",
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
    )
    amount_tax = fields.Float(
        string="Tax",
        required=True,
    )
    invoice_line_id = fields.Many2one(
        string="Invoice Line",
        comodel_name="account.invoice.line",
        readonly=True,
    )
    invoice_id = fields.Many2one(
        string="# Invoice",
        comodel_name="account.invoice",
        readonly=True,
    )
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
    state = fields.Selection(
        string="Invoice State",
        selection=[
            ("draft", "Draft"),
            ("post", "Posted"),
        ],
        required=True,
        default="draft",
    )

    @api.multi
    def action_create_invoice(self):
        for document in self:
            inv = document._create_invoice()
            inv.button_reset_taxes()
            document.write({
                "state": "post",
            })
            # if document.detail_id._check_done():
            #     document.detail_id.action_done()

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        obj_inv = self.env["account.invoice"]
        obj_inv_line = self.env["account.invoice.line"]

        inv = obj_inv.create(
            self._prepare_invoice())
        self.write({"invoice_id": inv.id})

        inv_line = obj_inv_line.create(
            self._prepare_invoice_line(inv))
        self.write({"invoice_line_id": inv_line.id})

        return inv

    @api.multi
    def _get_receivable_account(self):
        self.ensure_one()
        result = False
        detail = self.detail_id
        rental_type = detail.rental_id.type_id
        if detail.invoice_schedule_method == "prepaid":
            result = rental_type.rental_prepaid_receivable_account_id
        else:
            result = rental_type.rental_receivable_account_id
        return result

    @api.multi
    def _get_invoice_detail_account(self):
        self.ensure_one()
        result = False
        detail = self.detail_id
        rental_object = detail.object_id
        if detail.invoice_schedule_method == "prepaid":
            result = rental_object.rental_prepaid_income_account_id
        else:
            result = rental_object.rental_income_account_id
        return result

    @api.multi
    def _get_receivable_journal(self):
        self.ensure_one()
        result = False
        detail = self.detail_id
        rental_type = detail.rental_id.type_id
        if detail.invoice_schedule_method == "prepaid":
            result = rental_type.rental_prepaid_receivable_journal_id
        else:
            result = rental_type.rental_receivable_journal_id
        return result

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()

        account = self._get_receivable_account()
        if not account:
            raise UserError(_(
                "Receivable account is not configured. \n"
                "Please contact administrator"))

        journal = self._get_receivable_journal()
        if not journal:
            raise UserError(_(
                "Rental sale journal is not configured. \n"
                "Please contact administrator"))

        name = self._get_invoice_description()

        rental = self.detail_id.rental_id

        return {
            "origin": self.detail_id.rental_id.name,
            "date_invoice": self.date,
            "partner_id": self.detail_id.partner_id.id,
            "account_id": account.id,
            "payment_term": self.detail_id.payment_term_id.id,
            "type": "out_invoice",
            "fiscal_position": self.detail_id.fiscal_position_id.id,
            "company_id": self.detail_id.company_id.id,
            "currency_id": rental.currency_id.id,
            "journal_id": journal.id,
            "name": name,
        }

    @api.multi
    def _get_invoice_description(self):
        self.ensure_one()
        type = self.detail_id.rental_id.type_id
        if type.rental_invoice_name_method == "default":
            return self._get_default_invoice_description()
        else:
            return type._generate_rental_invoice_description(self)

    @api.multi
    def _get_default_invoice_description(self):
        self.ensure_one()
        detail = self.detail_id
        rental = detail.rental_id
        period = dict(detail._fields["period"].selection).get(detail.period)
        result = "%s invoice for # %s" % (period, rental.name)
        return result

    @api.multi
    def _prepare_invoice_line(self, inv):
        self.ensure_one()

        rental = self.detail_id.rental_id
        account = self._get_invoice_detail_account()
        analytic = rental.account_analytic_id
        return {
            "invoice_id": inv.id,
            "name": _("Rental"),
            "account_analytic_id": analytic and analytic.id or False,
            'account_id': account.id,
            'product_id': self.detail_id.object_id.product_id.id,
            'uos_id': self.detail_id.uom_id.id,
            'quantity': 1,
            'price_unit': self.amount,
            'invoice_line_tax_id': [(6, 0, self.detail_id.taxes_id.ids)],
            'discount': 0.0,
        }
