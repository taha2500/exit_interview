from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class enviromintwizard(models.TransientModel):
  _name = "enviro.wizard"
  _description = " env Wizard"

  models = fields.Many2one("ir.model", string="Models")
  code = fields.Text(string="Code")
  result = fields.Text(string="Result")

  def execute_action(self):
    if self.models:
      model = self.models
    else:
      model = self
    self.result = f"{safe_eval(self.code.strip(),{'self':model})}"
