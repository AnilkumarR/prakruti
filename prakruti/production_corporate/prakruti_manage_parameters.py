'''
Company : EBSL
Author: Induja
Module: Manage Parameters
Class 1: PrakrutiManageParameters
Table 1 : prakruti_manage_parameters 
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
'''

# -*- coding: utf-8 -*-

from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
import re
import logging


#########################################################################################################


class PrakrutiManageParameters(models.Model):
    _name = 'prakruti.manage_parameters'
    _table = 'prakruti_manage_parameters'
    _description = 'Parameters '
    _order= "id desc"
    _rec_name="parameter_name"
    
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    parameter_name= fields.Char('Parameter Name',required="True")
    parameter_code= fields.Char('Parameter Code',required="True")
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('unique_parameter_name', 'unique (parameter_name)', 'This entry is already entered. Please check and retry!'),
        ]
    
    '''
     name must be in this format
    ''' 
    def onchange_check_parameter_name(self, cr, uid, ids, parameter_name, context=None):
        if parameter_name == False:
            return {
                'value': {
                    'parameter_name': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", parameter_name) != None:
            ''' to strip left and right spaces '''
            parameter_name = parameter_name.strip()
            parameter_name = parameter_name.upper()

            return {
                'value': {
                    'parameter_name': parameter_name
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'parameter_name': False
            }, 'warning': warning_shown}
        
    '''
     name must be in this format
    ''' 
    def onchange_check_parameter_code(self, cr, uid, ids, parameter_code, context=None):
        if parameter_code == False:
            return {
                'value': {
                    'parameter_code': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", parameter_code) != None:
            ''' to strip left and right spaces '''
            parameter_code = parameter_code.strip()
            parameter_code = parameter_code.upper()

            return {
                'value': {
                    'parameter_code': parameter_code
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'parameter_code': False
            }, 'warning': warning_shown}