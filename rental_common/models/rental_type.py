# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


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
    rental_journal_id = fields.Many2one(
        string="Rental Journal",
        comodel_name="account.journal"
    )
    rental_account_id = fields.Many2one(
        string="Rental Account",
        comodel_name="account.account"
    )
    recurring_journal_id = fields.Many2one(
        string="Recurring Journal",
        comodel_name="account.journal"
    )
    recurring_account_id = fields.Many2one(
        string="Recurring Account",
        comodel_name="account.account"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
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
