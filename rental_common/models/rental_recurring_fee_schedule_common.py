# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class RentalRecurringFeeScheduleCommon(models.AbstractModel):
    _name = "rental.recurring_fee_schedule_common"
    _description = "Abstract Model for Recurring Fee Schedule"

    @api.multi
    def _compute_rental_state(self):
        for document in self:
            document.rental_state = \
                document.recurring_fee_id.detail_id.rental_id.state

    recurring_fee_id = fields.Many2one(
        string="Details",
        comodel_name="rental.recurring_fee_common",
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
    def _prepare_invoice(self):
        self.ensure_one()

        # TO DO
        account_id = (
            self.recurring_fee_id.type_id.recurring_account_id.id or
            self.recurring_fee_id.partner_id.property_account_receivable.id or
            False
        )
        if not account_id:
            raise UserError(_(
                "Recurring fee receivable account is not configured. \n "
                "Please contact administrator"))
        # TO DO
        journal_id = (
            self.recurring_fee_id.type_id.recurring_journal_id.id or
            False
        )
        if not journal_id:
            raise UserError(_(
                "Recurring sale journal is not configured. \n "
                "Please contact administrator"))

        name = self._get_recurring_invoice_description()

        return {
            "origin": self.recurring_fee_id.detail_id.rental_id.name,
            "date_invoice": self.date,
            "partner_id": self.recurring_fee_id.partner_id.id,
            "account_id": account_id,
            "payment_term": self.recurring_fee_id.payment_term_id.id,
            "type": "out_invoice",
            "fiscal_position": self.recurring_fee_id.fiscal_position_id.id,
            "company_id": self.recurring_fee_id.company_id.id,
            "currency_id": self.recurring_fee_id.pricelist_id.currency_id.id,
            "journal_id": journal_id,
            "name": name,
        }

    @api.multi
    def _get_line_account(self):
        self.ensure_one()
        recurring = self.recurring_fee_id
        product = recurring.product_id

        account = product.categ_id.property_account_income_categ

        if not account:
            account = product.property_income_account

        error_msg = _("Recurring product %s income account "
                      "is not configured. \n"
                      "Please contact administrator."
                      ) % (product.display_name)
        raise UserError(error_msg)

    @api.multi
    def _prepare_invoice_line(self, inv):
        self.ensure_one()

        recurring = self.recurring_fee_id
        account_id = recurring.partner_id.\
            property_account_receivable.id

        return {
            "invoice_id": inv.id,
            "name": _("Recurring Invoice"),
            'account_id': account_id,
            'product_id': recurring.product_id.id,
            'uos_id': recurring.uom_id.id,
            'quantity': 1,
            'price_unit': self.amount,
            'invoice_line_tax_id': [(6, 0, recurring.taxes_id.ids)],
            'discount': 0.0,
            'account_analytic_id': False,
        }

    @api.multi
    def _get_recurring_invoice_description(self):
        self.ensure_one()
        type = self.recurring_fee_id.detail_id.rental_id.type_id
        if type.recurring_invoice_name_method == "default":
            return self._get_default_recurring_invoice_description()
        else:
            return type._generate_recurring_invoice_description(self)

    @api.multi
    def _get_default_recurring_invoice_description(self):
        self.ensure_one()
        recurring = self.recurring_fee_id
        rental = recurring.detail_id.rental_id
        period = dict(recurring._fields["period"].selection).get(
            recurring.period)
        result = "%s recurring invoice for # %s" % (period, rental.name)
        return result
