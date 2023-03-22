# -*- coding: utf-8 -*-
{
    'name': 'HR Clearance',
    'category': 'Human Resources',
    'summary': 'HR Clearance',
    'description': """
        This module calculate end of service for employee.
    """,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'hr_payroll',
        'hr_holidays',
        # 'ejaf_employee_check_list',
        'ejaf_hr_loan_management',
    ],
    'data': [
        "security/groups.xml",
        "data/data.xml",
        "data/question_clearance.xml",
        "security/ir.model.access.csv",
        "views/termination_type_views.xml",
        "views/termination_views.xml",
        "views/clearance_question.xml",
        "views/question_category.xml",
        "views/res_config_settings_views.xml",
        "views/clearance_approve.xml",
        # "views/payslip_views.xml",
        "reports/employee_termination.xml",
    ],
    'application': False,
    'installable': True,
}
