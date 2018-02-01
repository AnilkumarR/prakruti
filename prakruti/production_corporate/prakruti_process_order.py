'''
Company : EBSL
Author: Induja
Module: Process Order
Class 1: PrakrutiProcessOrder
Table 1 : prakruti_process_order 
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


class PrakrutiProcessOrder(models.Model):
    _name = 'prakruti.process_order'
    _table = 'prakruti_process_order'
    _description = 'Process Order '
    _order= "id desc"
    _rec_name="order_no"
    
  
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    order_no=fields.Char(string='Name',required="True")
    
    '''
    The order no which will be entered shoud be unique, that means same Order No must not be entered more than one 
    '''
    _sql_constraints = [
        ('uniq_order_no', 'unique(order_no)', 'This entry is already entered. Please check and retry!'),
       
    ]
    '''
     name must be in this format
    '''
    def onchange_process_order_name(self, cr, uid, ids, order_no, context=None):
        if order_no == False:
            return {
                'value': {
                    'order_no': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", order_no) != None:
            ''' to strip left and right spaces '''
            order_no = order_no.strip()
            order_no = order_no.upper()

            return {
                'value': {
                    'order_no': order_no
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'order_no': False
            }, 'warning': warning_shown}
    