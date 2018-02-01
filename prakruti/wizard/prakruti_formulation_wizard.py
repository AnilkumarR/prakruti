# -*- coding: utf-8 -*-
from openerp.tools import image_resize_image_big
from openerp.exceptions import ValidationError
import openerp
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize, image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
from openerp import tools
from datetime import timedelta
from openerp.osv import osv,fields
from openerp import models, fields, api, _
from openerp.tools.translate import _
import sys, os, urllib2, urlparse
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import email, re
from datetime import datetime
from datetime import date, timedelta
from lxml import etree
import cgi
import logging
import lxml.html
import lxml.html.clean as clean
import openerp.pooler as pooler
import random
import re
import socket
import threading

class prakruti_formulation_wizard(models.TransientModel):
    _name = 'prakruti.formulation_wizard'
    _table = 'prakruti_formulation_wizard'
    _description = 'Formulation Wizard'
    
    formulation_bom_id=fields.Integer(string='Formulation Id')
    batch_no = fields.Many2one('prakruti.batch_master',string='Batch No', readonly=1)
    subplant_id = fields.Many2one('prakruti.sub_plant', string="Sub Plant",readonly=1)
    formulation_bom_wizard_line=  fields.One2many('prakruti.formulation_wizard_line','formulation_bom_wizard_id',string= 'Formulation Line')       
    @api.one
    @api.multi
    def action_approve(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        total_line = 0        
        packing_enter_line = 0
        total_issued_qty = 0
        for temp in self:
            if len(temp.formulation_bom_wizard_line) > 0:
                cr.execute('''  INSERT INTO prakruti_powder_line(product_id,uom_id,description,std_wgt,composition,material_weight,actual_weight,extra_qty,grn_no,grn_list,ar_no,issued_weight,extra_issued_qty,weight_return,weighed_by,checked_by,main_id)
                                SELECT 
                                    prakruti_formulation_wizard_line.product_id,
                                    prakruti_formulation_wizard_line.uom_id,
                                    prakruti_formulation_wizard_line.description,
                                    prakruti_formulation_wizard_line.std_wgt,
                                    prakruti_formulation_wizard_line.composition,
                                    prakruti_formulation_wizard_line.material_weight,
                                    prakruti_formulation_wizard_line.actual_weight,
                                    prakruti_formulation_wizard_line.extra_qty,
                                    prakruti_formulation_wizard_line.grn_no,
                                    prakruti_formulation_wizard_line.grn_list,
                                    prakruti_formulation_wizard_line.ar_no,
                                    prakruti_formulation_wizard_line.issued_weight,
                                    prakruti_formulation_wizard_line.extra_issued_qty,
                                    prakruti_formulation_wizard_line.weight_return,
                                    prakruti_formulation_wizard_line.weighed_by,
                                    prakruti_formulation_wizard_line.checked_by,
                                    prakruti_formulation_wizard.formulation_bom_id as grid_id
                                FROM
                                    prakruti_formulation_wizard_line JOIN
                                    prakruti_formulation_wizard ON
                                    prakruti_formulation_wizard.id = prakruti_formulation_wizard_line.formulation_bom_wizard_id 
                                WHERE 
                                    prakruti_formulation_wizard.id = %s''',((temp.id),))
                
            else:
                raise UserError(_('Oops Something is Missing...'))
        return {}

class prakruti_formulation_wizard_line(models.TransientModel):
    _name = 'prakruti.formulation_wizard_line'
    _table = 'prakruti_formulation_wizard_line'
    _description = 'Formulation Wizard Line'

    
    
    formulation_bom_wizard_id = fields.Many2one('prakruti.formulation_wizard',string="Grid", ondelete='cascade')
    product_id=fields.Many2one('product.product', string="Ingredient Name")
    description = fields.Text(string = "Description")
    uom_id = fields.Many2one('product.uom',string="UOM")
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.',readonly=True)
    std_wgt = fields.Float(string='Std. Weight',digits=(6,3))
    composition = fields.Float(string='Composition per 10ml',digits=(6,3))
    material_weight = fields.Float(string='Material Weight',digits=(6,3))
    actual_weight = fields.Float(string='Actual Weight',digits=(6,3))
    weighed_by=fields.Many2one('res.users','Weighed By')
    checked_by=fields.Many2one('res.users','Checked By')
    issued_weight = fields.Float(string='Issued Weight',digits=(6,3))
    extra_qty =fields.Float(string='Extra Req Weight',digits=(6,3))
    extra_issued_qty =fields.Float(string='Extra Weight',digits=(6,3))
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.',readonly=True)
    extra_flag = fields.Integer(string='Extra Flag',default=0)
    readonly_grid = fields.Integer(string='Grid Readonly',default=0)
    weight_return = fields.Float(string='Weight Returned',digits=(6,3))
    grn_list = fields.Text(string= 'GRN Nos',readonly=1,default='.')
    
    _sql_constraints = [        
        ('unique_product_id','unique(material_id, bom_wizard_id)', 'Item(s) should be Unique')
        ]
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = 0
        description = ''
        std_wgt = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description,case when prakruti_standard_product.standard_value >0 then prakruti_standard_product.standard_value else 0 end as std_wgt FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id LEFT JOIN prakruti_standard_product ON product_product.id = prakruti_standard_product.product_name WHERE product_product.id = cast(%s as integer)', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
            std_wgt = line['std_wgt']
        return {'value' :{
                'uom_id':uom_id,
                'description':description,
                'std_wgt':std_wgt,
                'actual_weight':std_wgt
                          }}
  
    
   
