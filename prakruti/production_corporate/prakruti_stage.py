'''
Company : EBSL
Author: Induja
Module: Stage
Class 1: PrakrutiStage
Table 1 : prakruti_stage 
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


class PrakrutiStage(models.Model):
    _name = 'prakruti.stage'
    _table = 'prakruti_stage'
    _description = 'Stage '
    _order= "id desc"
    _rec_name="stage_name"
    
  
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    stage_name=fields.Char(string='Name',required="True")
    stage_code=fields.Char(string='Code',required="True")
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('uniq_stage_name', 'unique(stage_name)', 'This entry is already entered. Please check and retry!'),
       
    ]
    '''
     name must be in this format
    ''' 
    def onchange_check_stage_name(self, cr, uid, ids, stage_name, context=None):
        if stage_name == False:
            return {
                'value': {
                    'stage_name': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", stage_name) != None:
            ''' to strip left and right spaces '''
            stage_name = stage_name.strip()
            stage_name = stage_name.upper()

            return {
                'value': {
                    'stage_name': stage_name
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'stage_name': False
            }, 'warning': warning_shown}
        
    '''
     Code must be in this format
    ''' 
    def onchange_check_stage_code(self, cr, uid, ids, stage_code, context=None):
        if stage_code == False:
            return {
                'value': {
                    'stage_code': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", stage_code) != None:
            ''' to strip left and right spaces '''
            stage_code = stage_code.strip()
            stage_code = stage_code.upper()

            return {
                'value': {
                    'stage_code': stage_code
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'stage_code': False
            }, 'warning': warning_shown}