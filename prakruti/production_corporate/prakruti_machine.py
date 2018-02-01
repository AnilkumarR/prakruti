'''
Company : EBSL
Author: Induja
Module: Machine
Class 1: PrakrutiMachine
Table 1 : prakruti_machine 
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


class PrakrutiMachine(models.Model):
    _name = 'prakruti.machine'
    _table = 'prakruti_machine'
    _description = 'Machine '
    _order= "id desc"
    _rec_name="name"
    
    
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    name=fields.Char(string='Name',required="True")
    machine_code= fields.Char('Code',required="True")
    description=fields.Text(string='Description')
    
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('name_uniq', 'unique(name)','This entry is already entered. Please check and retry!')
        ]
    '''
     name must be in this format
    '''   
    def onchange_check_machine_name(self, cr, uid, ids, name, context=None):
        if name == False:
            return {
                'value': {
                    'name': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", name) != None:
            ''' to strip left and right spaces '''
            name = name.strip()
            name = name.upper()

            return {
                'value': {
                    'name': name
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'name': False
            }, 'warning': warning_shown}
    '''
    Machine code name must be in this format
    '''   
    def onchange_check_machine_code(self, cr, uid, ids, machine_code, context=None):
        if machine_code == False:
            return {
                'value': {
                    'machine_code': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", machine_code) != None:
            ''' to strip left and right spaces '''
            machine_code = machine_code.strip()
            machine_code = machine_code.upper()

            return {
                'value': {
                    'machine_code': machine_code
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'machine_code': False
            }, 'warning': warning_shown}