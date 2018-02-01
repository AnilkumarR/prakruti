'''
Company : EBSL
Author: Induja
Module: Mesh Master
Class 1: PrakrutiMeshMaster
Table 1 : prakruti_mesh_master 
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


class PrakrutiMeshMaster(models.Model):
    _name = 'prakruti.mesh_master'
    _table = 'prakruti_mesh_master'
    _description = 'Mesh Master'
    _order= "id desc"
    _rec_name="mesh_size"
    
  
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant",required="True")
    mesh_size= fields.Float(string='Mesh Size',required="True",digits=(6,3))
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    ''' 
    _sql_constraints = [
        ('uniq_mesh_size','unique(subplant_id,mesh_size)','This entry is already entered. Please check and retry!')
        ]
   