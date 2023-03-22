from odoo import fields, models


class ResConfigSettings(models.TransientModel):
  _inherit = ['res.config.settings']

  cancel_days = fields.Integer(string='Cancel Days',
                               config_parameter='ejaf_hr_termination.cancel_days')

  survey_id = fields.Many2one("survey.survey",
                              string="Survey Clearance",
                              config_parameter='ejaf_hr_termination.survey_id')

  category_it_id = fields.Many2one(
      "clearance.question.category",
      string='Question Category IT',
      config_parameter='ejaf_hr_termination.category_it_id',
  )
  category_finance_id = fields.Many2one("clearance.question.category",
                                        string='Question Category finance',
                                        config_parameter='ejaf_hr_termination.category_finance_id')
  category_reporting_id = fields.Many2one(
      "clearance.question.category",
      string='Question Category reporting',
      config_parameter='ejaf_hr_termination.category_reporting_id')
  category_hr_id = fields.Many2one("clearance.question.category",
                                   string='Question Category HR',
                                   config_parameter='ejaf_hr_termination.category_hr_id')
