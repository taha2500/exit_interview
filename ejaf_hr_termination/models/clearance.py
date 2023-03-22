from odoo import api, models, fields, _
import logging
from odoo.exceptions import UserError, ValidationError

import toolz


class ClearanceQuestion(models.Model):
  _name = "clearance.question"
  _description = "Clearance Question"

  name = fields.Char(string="Question")

  category_id = fields.Many2one("clearance.question.category")


class ClearanceQuestionCategory(models.Model):
  _name = "clearance.question.category"
  _description = "Clearance Question Category"

  name = fields.Char(string="Category")


class ClearanceAnswerQuestionLine(models.Model):
  _name = "clearance.answer.question.line"
  _description = "Clearance Answer Question Line"
  _rec_name = "question_id"
  _order = "sequence,id"

  question_id = fields.Many2one("clearance.question", string="Question", required=True)
  category_id = fields.Many2one("clearance.question.category", related='question_id.category_id')
  question_group_id = fields.Many2one("clearance.question.group", required=True)

  sequence = fields.Integer(default=10)

  answer_question = fields.Selection([("yes", "Yes"), ("no", "No"), ("na", "N/A")])
  answer_note = fields.Text("Note")

  def action_answer_question_yes(self):
    if self.question_group_id.state == "confirm":
      pass
    else:
      self.answer_question = "yes"

  def action_answer_question_no(self):
    if self.question_group_id.state == "confirm":
      pass
    else:
      self.answer_question = "no"

  def action_answer_question_na(self):
    if self.question_group_id.state == "confirm":
      pass
    else:
      self.answer_question = "na"


class ClearanceQuestionGoup(models.Model):
  _name = "clearance.question.group"
  _description = "Clearance  Question Group"

  question_line_ids = fields.One2many("clearance.answer.question.line", "question_group_id")
  category_id = fields.Many2one("clearance.question.category")
  state = fields.Selection([("draft", "Draft"), ("confirm", "Confirm")], default="draft")

  termination_id = fields.Many2one("hr.termination")

  confirm_by = fields.Many2one('hr.employee',
                               string="Name ",
                               domain=[('contract_id.state', 'not in', ['close', 'cancel'])])
  confirm_date = fields.Date(setring="Date", default=fields.Date.today(), store=True)
  position_id = fields.Many2one('hr.job', related="confirm_by.job_id", store=True)
  signature = fields.Binary(string="Signature")

  note = fields.Text(string="Note")

  def action_confirm(self):
    if not all(toolz.groupby("answer_question", self.question_line_ids)) or not self.confirm_by:
      raise ValidationError(_("Please complete the information"))
    else:
      self.confirm_date = fields.Date.today()
      self.state = "confirm"
      self.termination_id.progress += 25
      return {'type': 'ir.actions.client', 'tag': 'reload'}
