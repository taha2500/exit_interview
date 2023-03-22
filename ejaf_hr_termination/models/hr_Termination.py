# -*-	coding:	utf-8	-*-

import datetime
import logging
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import uuid

_logger = logging.getLogger(__name__)


class Employee(models.Model):
  _inherit = "hr.employee"

  is_terminated = fields.Boolean()


class HRTermination(models.Model):
  _name = "hr.termination"
  _rec_name = 'name'
  _inherit = ['mail.thread', 'mail.activity.mixin']
  name = fields.Char(string='Reference',
                     required=True,
                     copy=False,
                     default=lambda self: self.env['ir.sequence'].next_by_code('hr.termination'))
  responsible_id = fields.Many2one('res.users',
                                   string='Requester Name',
                                   default=lambda self: self.env.user)
  employee_id = fields.Many2one('hr.employee',
                                required=True,
                                string="Employee",
                                domain=[('contract_id.state', 'not in', ['close', 'cancel'])])
  job_id = fields.Many2one('hr.job', related="employee_id.job_id", store=True)
  dept_id = fields.Many2one('hr.department', related="employee_id.department_id", store=True)
  manager_id = fields.Many2one('hr.employee', related="employee_id.parent_id", store=True)
  line_manger_job_id = fields.Many2one('hr.job', related="manager_id.job_id", store=True)

  line_manager_statement = fields.Char('Line Manager Statement', track_visibility="always")
  facility_manager_statement = fields.Char('Facility Dept Statement', track_visibility="always")
  it_manager_statement = fields.Char('IT Dept Statement', track_visibility="always")
  accounting_manager_statement = fields.Char('Accounting Dept', track_visibility="always")
  legal_manager_statement = fields.Char('Legal Dept Statement', track_visibility="always")
  hr_manager_statement = fields.Char('HR Manager Statement', track_visibility="always")

  state = fields.Selection(selection=[('draft', 'Draft'), ("exit_interview", "Exit Interview"),
                                      ('clearance', 'Clearance'), ('confirmed', 'Confirmed'),
                                      ('refused', 'Refused')],
                           default='draft',
                           tracking=True,
                           copy=False)
  progress = fields.Integer(string="Approve")

  termination_type_id = fields.Many2one(comodel_name="hr.termination.type",
                                        string="Clearance For",
                                        required=True)
  leaves_count = fields.Float(string="Leaves Balance", compute="get_leaves_balance")
  employee_loan_amount = fields.Float(compute="_get_loan_not_paid_amount")
  experience = fields.Char(string='Experience', compute="get_employee_experience")
  current_contract_id = fields.Many2one(comodel_name="hr.contract",
                                        related="employee_id.contract_id",
                                        store=True)
  contract_start_date = fields.Date(string="Start Working Date",
                                    related='current_contract_id.date_start')
  termination_date = fields.Date(string="Last Working Date",
                                 default=fields.Date.today(),
                                 required=True)
  employee_company = fields.Many2one("res.partner",
                                     string="Company",
                                     related="employee_id.address_id")
  employee_location = fields.Many2one("hr.work.location",
                                      string="Location",
                                      related="employee_id.work_location_id")

  company_id = fields.Many2one(comodel_name="res.company", default=lambda self: self.env.company)

  exit_interview_token = fields.Char(string="Exit Token",
                                     default=lambda self: str(uuid.uuid4()),
                                     readonly=True,
                                     required=True,
                                     copy=False)
  exit_interview_id = fields.Many2many("survey.user_input",
                                       compute="_compute_exit_interview_id",
                                       string="Exit Interview",
                                       ondelete='cascade')
  group_it_ids = fields.One2many("clearance.question.group",
                                 "termination_id",
                                 string="IT Clearance")

  def send_clearance_group(self):
    category_it = self.env["ir.config_parameter"].get_param("ejaf_hr_termination.category_it_id")
    category_finance = self.env["ir.config_parameter"].get_param(
        "ejaf_hr_termination.category_finance_id")
    category_reporting = self.env["ir.config_parameter"].get_param(
        "ejaf_hr_termination.category_reporting_id")
    category_hr = self.env["ir.config_parameter"].get_param("ejaf_hr_termination.category_hr_id")

    category_list = (category_it, category_finance, category_reporting, category_hr)

    for n in category_list:
      le = self.env["clearance.question.group"].create({
          "termination_id": self.id,
          "category_id": n
      })
      all_question = self.env['clearance.question'].search([("category_id.id", "=", n)])
      for rec in all_question:
        self.env["clearance.answer.question.line"].create({
            "question_id": rec.id,
            "question_group_id": le.id
        })

    self.action_clearance()

  @api.constrains('termination_date')
  def _check_termination_date(self):

    for record in self:
      if record.termination_type_id.is_termination:
        if record.termination_date and record.current_contract_id.date_start and (
            record.termination_date < record.current_contract_id.date_start):
          raise ValidationError(_("Termination date must be greater than contract start date"))

      elif record.termination_type_id.is_resignation:
        if (record.termination_date < datetime.date.today()):
          raise ValidationError(_("Resignation date must be greater than current Date"))

      elif record.termination_type_id.is_long_leave:

        if (record.termination_date < datetime.date.today()):
          raise ValidationError(_("Long Leave date must be greater than current Date"))

  @api.depends("exit_interview_token")
  def _compute_exit_interview_id(self):
    self.exit_interview_id = self.env["survey.user_input"].search([
        ("serveys_token", "=", self.exit_interview_token),
    ]) or False

  def get_employee_experience(self):
    for record in self:
      if record.current_contract_id:
        diff = relativedelta(fields.Date.today(), record.current_contract_id.date_start)
        record.experience = "{} years {} months {} days".format(diff.years, diff.months, diff.days)
      else:
        record.experience = ""

  def get_leaves_balance(self):
    for record in self:
      record.leaves_count = self.env['hr.leave'].sudo().search_count([('employee_id', '=',
                                                                       record.employee_id.id)])

  def _get_loan_not_paid_amount(self):
    for record in self:
      loan_not_paid_amount = 0.0
      loans = self.env['hr.loan'].sudo().search([('employee_id', '=', record.employee_id.id),
                                                 ('state', '=', 'approved')])
      not_paid_installments = loans.mapped('installment_ids').filtered(
          lambda i: i.state == 'not_paid')
      if not_paid_installments:
        loan_not_paid_amount = sum(not_paid_installments.mapped('amount'))
      record.employee_loan_amount = loan_not_paid_amount

  def action_confirm(self):
    # if self.termination_date > fields.Date.today():
    #     raise ValidationError(_("You can't confirm as termination date is bigger than today"))

    # if self.employee_loan_amount != 0.0:
    #     raise ValidationError(_("Loans must be paid before confirm Clearances"))

    # if self.employee_id.exit_checklist and self.employee_id.exit_progress != 100:
    #     raise ValidationError(_("Exist process must be finished before confirm termination"))
    if self.progress == 100:
      self.state = 'confirmed'
      self.employee_id.write({'is_terminated': True, 'active': False})
    else:
      raise ValidationError(_("Please continue approve clearance"))

    return True

  def action_cancel(self):
    self.state = 'draft'
    self.group_it_ids = False
    self.progress = 0

    return True

  def unlink(self):
    for record in self:
      if record.state != 'draft':
        raise UserError(_('You can only delete draft Clearance!'))
    return super(HRTermination, self).unlink()

  def action_forth_approve(self):
    for obj in self:
      obj.state = 'forth_approve'
      obj.action_confirm()

  def action_refuse(self):
    for obj in self:
      obj.state = 'refused'

  def action_clearance(self):
    for obj in self:
      obj.state = "clearance"

  def action_send_survey(self):

    survey_id = self.env["ir.config_parameter"].get_param("ejaf_hr_termination.survey_id")
    if survey_id:
      survey = self.env["survey.survey"].search([
          ("id", "=", survey_id),
      ])
      access_token = self.exit_interview_token
      if self.state == "draft":
        self.state = "exit_interview"
      return survey.with_context(default_serveys_token=access_token,
                                 default_emails=self.employee_id.work_email).action_send_survey()
    else:
      raise ValidationError(_("An empty survey cannot be sent. Please set a pattern in the settings"))

  def action_confirm_it(self):
    self.confirm_it_py = self.env.user


class SurveyUserInput(models.Model):
  _inherit = "survey.user_input"

  serveys_token = fields.Char()
