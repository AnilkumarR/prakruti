'''
Company : EBSL
Author: Induja
Module: Shift Master
Class 1: PrakrutiShiftMaster
Table 1 : prakruti_shift_master 
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


class PrakrutiShiftMaster(models.Model):
    _name = 'prakruti.shift_master'
    _table = 'prakruti_shift_master'
    _description = 'Shift Master '
    _order= "id desc"
    _rec_name="name"
    
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    name= fields.Char('Name',required="True")
    shift_starttime =fields.Datetime(string='Start Time ',required="True")
    shift_endtime =fields.Datetime(string='End Time',required="True")
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('name_code', 'unique (name)', ' This entry is already entered. Please check and retry!'),
        ]
    '''
     name must be in this format
    '''
    def onchange_check_name(self, cr, uid, ids, name, context=None):
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