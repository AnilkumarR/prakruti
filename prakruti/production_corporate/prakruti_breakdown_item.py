'''
Company : EBSL
Author: Induja
Module: Breakdown Item
Class 1: PrakrutiBreakdownItem
Table 1 & Reference Id: prakruti_breakdown_item 
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


class PrakrutiBreakdownItem(models.Model):
    _name = 'prakruti.breakdown_item'
    _table = 'prakruti_breakdown_item'
    _description = 'Breakdown Item '
    _order= "id desc"
    
  
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    name=fields.Char(string=' Name',required="True")
    
    '''
    Name must be in this format
    '''
    _sql_constraints = [
        ('name_name', 'unique (name)', '  Name Should be Unique!')
        ]
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