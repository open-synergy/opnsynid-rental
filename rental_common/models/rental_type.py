# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval as eval


class RentalType(models.Model):
    _name = "rental.type"
    _description = "Rental Type"

    name = fields.Char(
        string="Rental Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
    )
    rental_account_analytic_id = fields.Many2one(
        string="Parent Analytic Account",
        comodel_name="account.analytic.account",
    )
    create_analytic_ok = fields.Boolean(
        string="Auto-Create Analytic Account",
    )
    allowed_upfront_product_ids = fields.Many2many(
        string="Allowed Upfront Products",
        comodel_name="product.product",
        relation="rel_rental_type_2_upfront_product",
        column1="type_id",
        column2="product_id",
    )
    allowed_upfront_product_categ_ids = fields.Many2many(
        string="Allowed Upfront Product Categories",
        comodel_name="product.category",
        relation="rel_rental_type_2_upfront_product_categ",
        column1="type_id",
        column2="category_id",
    )
    allowed_recurring_fee_product_ids = fields.Many2many(
        string="Allowed Recurring Fee Products",
        comodel_name="product.product",
        relation="rel_rental_type_2_recurring_fee_product",
        column1="type_id",
        column2="product_id",
    )
    allowed_recurring_fee_product_categ_ids = fields.Many2many(
        string="Allowed Recurring Fee Product Categories",
        comodel_name="product.category",
        relation="rel_rental_type_2_recurring_fee_product_categ",
        column1="type_id",
        column2="category_id",
    )
    unfront_cost_journal_id = fields.Many2one(
        string="Upfront Cost Receivable Journal",
        comodel_name="account.journal",
        company_dependent=True,
    )
    unfront_cost_receivable_account_id = fields.Many2one(
        string="Upfront Cost Receivable Account",
        comodel_name="account.account",
        company_dependent=True,
    )
    upfront_invoice_name_method = fields.Selection(
        string="Upfront Invoice Description Generation Method",
        selection=[
            ("default", "Default"),
            ("code", "Python Code"),
        ],
        required=True,
        default="default",
    )
    upfront_invoice_name_code = fields.Text(
        string="Python Code for Upfront Invoice Description Generation",
        default="result = True",
    )
    rental_prepaid_receivable_journal_id = fields.Many2one(
        string="Rental Prepaid Journal",
        comodel_name="account.journal",
        company_dependent=True,
    )
    rental_prepaid_receivable_account_id = fields.Many2one(
        string="Rental Prepaid Receivable Account",
        comodel_name="account.account",
        company_dependent=True,
    )
    rental_receivable_journal_id = fields.Many2one(
        string="Rental Receivable Journal",
        comodel_name="account.journal",
        company_dependent=True,
    )
    rental_receivable_account_id = fields.Many2one(
        string="Rental Recevable Account",
        comodel_name="account.account",
        company_dependent=True,
    )
    rental_invoice_name_method = fields.Selection(
        string="Rental Invoice Description Generation Method",
        selection=[
            ("default", "Default"),
            ("code", "Python Code"),
        ],
        required=True,
        default="default",
    )
    rental_invoice_name_code = fields.Text(
        string="Python Code for Rental Invoice Description Generation",
        default="result = True",
    )
    recurring_journal_id = fields.Many2one(
        string="Recurring Journal",
        comodel_name="account.journal"
    )
    recurring_account_id = fields.Many2one(
        string="Recurring Account",
        comodel_name="account.account"
    )
    recurring_invoice_name_method = fields.Selection(
        string="Recurring Invoice Description Generation Method",
        selection=[
            ("default", "Default"),
            ("code", "Python Code"),
        ],
        required=True,
        default="default",
    )
    recurring_invoice_name_code = fields.Text(
        string="Python Code for Recurring Invoice Description Generation",
        default="result = True",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
    )
    year_pricelist_id = fields.Many2one(
        string="Yearly Pricelist",
        comodel_name="product.pricelist",
    )
    month_pricelist_id = fields.Many2one(
        string="Monthly Pricelist",
        comodel_name="product.pricelist",
    )
    day_pricelist_id = fields.Many2one(
        string="Daily Pricelist",
        comodel_name="product.pricelist",
    )
    hour_pricelist_id = fields.Many2one(
        string="Hourly Pricelist",
        comodel_name="product.pricelist",
    )
    note = fields.Text(
        string="Note",
    )
    rental_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_confirm_rental",
        column1="type_id",
        column2="group_id",
    )
    rental_approve_grp_ids = fields.Many2many(
        string="Allow To Approve Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_approve_rental",
        column1="type_id",
        column2="group_id",
    )
    rental_start_grp_ids = fields.Many2many(
        string="Allow To Confirm Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_start_rental",
        column1="type_id",
        column2="group_id",
    )
    rental_done_grp_ids = fields.Many2many(
        string="Allow To Finish Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_done_rental",
        column1="type_id",
        column2="group_id",
    )
    rental_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_cancel_rental",
        column1="type_id",
        column2="group_id",
    )
    rental_terminate_grp_ids = fields.Many2many(
        string="Allow To Terminate Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_terminate_rental",
        column1="type_id",
        column2="group_id",
    )
    rental_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Rental",
        comodel_name="res.groups",
        relation="rel_rental_type_restart_rental",
        column1="type_id",
        column2="group_id",
    )

    def _get_localdict(self, document):
        self.ensure_one()
        return {
            "env": self.env,
            "document": document,
        }

    @api.multi
    def _generate_rental_invoice_description(self, document):
        self.ensure_one()
        localdict = self._get_localdict(document)
        try:
            eval(self.rental_invoice_name_code,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = "/"
        return result

    @api.multi
    def _generate_upfront_invoice_description(self, document):
        self.ensure_one()
        localdict = self._get_localdict(document)
        try:
            eval(self.upfront_invoice_name_code,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = "/"
        return result

    @api.multi
    def _generate_recurring_invoice_description(self, document):
        self.ensure_one()
        localdict = self._get_localdict(document)
        try:
            eval(self.recurring_invoice_name_code,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = "/"
        return result
