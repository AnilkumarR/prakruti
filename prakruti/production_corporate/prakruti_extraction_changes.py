'''
Company : EBSL
Author: Induja
Module: Extraction Changes
Class 1: PrakrutiExtractionChanges
Table 1 : prakruti_extraction_changes 
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


class PrakrutiExtractionChanges(models.Model):
    _name = 'prakruti.extraction_changes'
    _table = 'prakruti_extraction_changes'
    _description = 'Extraction Changes '
    _order= "id desc"
    _rec_name="extraction_name"
    
  
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    extraction_name=fields.Char(string='Name',required="True")
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
       
    _sql_constraints = [
        ('name_uniq', 'unique (extraction_name)', 'Extraction Name Should be Unique!')
    ]  
    '''
    Extraction name must be in this format
    '''
    def onchange_check_extraction_name(self, cr, uid, ids, extraction_name, context=None):
        if extraction_name == False:
            return {
                'value': {
                    'extraction_name': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", extraction_name) != None:
            ''' to strip left and right spaces '''
            extraction_name = extraction_name.strip()
            extraction_name = extraction_name.upper()

            return {
                'value': {
                    'extraction_name': extraction_name
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'extraction_name': False
            }, 'warning': warning_shown}