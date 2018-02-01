'''
Company : EBSL
Author: Induja
Module: Sieve Master
Class 1: PrakrutiSieveMaster
Table 1 : prakruti_sieve_master 
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


class PrakrutiSieveMaster(models.Model):
    _name = 'prakruti.sieve_master'
    _table = 'prakruti_sieve_master'
    _description = 'Sieve Master'
    _order= "id desc"
    _rec_name="sieve"
    
    
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant",required="True")
    sieve= fields.Float(string='Sieve' ,required="True",digits=(6,3))
    
    '''
     Sieve must be in this format
    '''   
    _sql_constraints = [
        ('uniq_sub_sieve','unique(subplant_id,sieve)','This entry is already entered. Please check and retry!')
        ]
    
   