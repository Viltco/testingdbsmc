# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResBranchInh(models.Model):
    _inherit = 'res.branch'

    # branch_code = fields.Char('Branch Code')
    active = fields.Boolean(default=True)


class BranchReportInh(models.TransientModel):
    _inherit = 'branch.wizard'

    branches = fields.Many2many('res.branch', default=lambda self: self.env.user.branch_id.ids)
