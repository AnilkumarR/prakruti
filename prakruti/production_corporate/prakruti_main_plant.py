'''
Company : EBSL
Author: Induja
Module: Main Plant
Class 1: PrakrutiMainPlant
Table 1 : prakruti_main_plant 
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


class PrakrutiMainPlant(models.Model):
    _name = 'prakruti.main_plant'
    _table = 'prakruti_main_plant'
    _description = 'Main Plant '
    _order= "id desc"
    _rec_name="plant_name"
    
  
    plant_name=fields.Char(string='Name',required="True")
    plant_code= fields.Char(string='Code',required="True")
    description=fields.Text(string='Description')
    company_id= fields.Many2one('res.company',ondelete='cascade', string= 'Company',required="True")
    
    
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('name_uniq', 'unique (plant_code,plant_name,company_id)', 'This entry is already entered. Please check and retry!!'),
       
    ] 
    '''
     name must be in this format
    '''
    def onchange_check_name(self, cr, uid, ids, plant_name, context=None):
        if plant_name == False:
            return {
                'value': {
                    'plant_name': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", plant_name) != None:
            ''' to strip left and right spaces '''
            plant_name = plant_name.strip()
            plant_name = plant_name.upper()

            return {
                'value': {
                    'plant_name': plant_name
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'plant_name': False
            }, 'warning': warning_shown}
   #FOR CODE IN CAPS LETTER
   
   
    '''
     name must be in this format
    '''
    def onchange_check_code(self, cr, uid, ids, plant_code, context=None):
        if plant_code == False:
            return {
                'value': {
                    'plant_code': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", plant_code) != None:
            ''' to strip left and right spaces '''
            plant_code = plant_code.strip()
            plant_code = plant_code.upper()

            return {
                'value': {
                    'plant_code': plant_code
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'plant_code': False
            }, 'warning': warning_shown}
    
    