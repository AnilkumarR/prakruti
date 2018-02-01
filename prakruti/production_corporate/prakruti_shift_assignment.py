'''
Company : EBSL
Author: Induja
Module: Shift Assignment
Class 1: PrakrutiShiftAssignment
Table 1 : prakruti_shift_assignment 
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


class PrakrutiShiftAssignment(models.Model):
    _name = 'prakruti.shift_assignment'
    _table = 'prakruti_shift_assignment'
    _description = 'Shift Assignment '
    _order= "id desc"
    _rec_name="name"
    
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id)
    effective_date= fields.Date('Effective Date', default=fields.Date.today,required="True")
    name= fields.Many2one('prakruti.shift_master',string="Shift Name",required="True")
    
    