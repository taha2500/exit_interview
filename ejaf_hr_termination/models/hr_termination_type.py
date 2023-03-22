# -*-	coding:	utf-8	-*-

from odoo import models, api, fields, _


class HRTerminationType(models.Model):
    _name = "hr.termination.type"
    name = fields.Char(required=True)
    is_termination = fields.Boolean("is Termination Type")
    is_resignation = fields.Boolean("is Resignation Type")
    is_long_leave = fields.Boolean("is Long Leave Type")
