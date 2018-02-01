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

class prakruti_bill_of_material_wizard(models.TransientModel):
    _name = 'prakruti.bill_of_material_wizard'
    _table = 'prakruti_bill_of_material_wizard'
    _description = 'Bill Of Material Wizard'
    
    extraction_bom_id=fields.Integer(string='EXTRACTION Id')
    batch_id = fields.Many2one('prakruti.batch_master',string='Batch No', readonly=1)
    subplant_id = fields.Many2one('prakruti.sub_plant', string="Sub Plant",readonly=1)
    bom_wizard_line=  fields.One2many('prakruti.bill_of_material_wizard_line','bom_wizard_id',string= 'EXTRACTION Line')       
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
            if len(temp.bom_wizard_line) > 0:
                cr.execute('''  INSERT INTO prakruti_bill_of_material_line(material_id,uom_id,description,std_qty,actual_qty,extra_qty,grn_no,grn_list,ar_no,issued_qty,extra_issued_qty,qty_returned,remarks,main_id)
                                SELECT 
                                    prakruti_bill_of_material_wizard_line.material_id,
                                    prakruti_bill_of_material_wizard_line.uom_id,
                                    prakruti_bill_of_material_wizard_line.description,
                                    prakruti_bill_of_material_wizard_line.std_qty,
                                    prakruti_bill_of_material_wizard_line.actual_qty,
                                    prakruti_bill_of_material_wizard_line.extra_qty,
                                    prakruti_bill_of_material_wizard_line.grn_no,
                                    prakruti_bill_of_material_wizard_line.grn_list,
                                    prakruti_bill_of_material_wizard_line.ar_no,
                                    prakruti_bill_of_material_wizard_line.issued_qty,
                                    prakruti_bill_of_material_wizard_line.extra_issued_qty,
                                    prakruti_bill_of_material_wizard_line.qty_returned,
                                    prakruti_bill_of_material_wizard_line.remarks,
                                    prakruti_bill_of_material_wizard.extraction_bom_id as grid_id
                                FROM
                                    prakruti_bill_of_material_wizard_line JOIN
                                    prakruti_bill_of_material_wizard ON
                                    prakruti_bill_of_material_wizard.id = prakruti_bill_of_material_wizard_line.bom_wizard_id 
                                WHERE 
                                    prakruti_bill_of_material_wizard.id = %s''',((temp.id),))
                
            else:
                raise UserError(_('Oops Something is Missing...'))
        return {}

class prakruti_bill_of_material_wizard_line(models.TransientModel):
    _name = 'prakruti.bill_of_material_wizard_line'
    _table = 'prakruti_bill_of_material_wizard_line'
    _description = 'Bill Of Material Wizard Line'

    
    
    bom_wizard_id = fields.Many2one('prakruti.bill_of_material_wizard',string="Grid", ondelete='cascade')
    material_id = fields.Many2one('product.product',string='Ingredient Name' )
    description = fields.Text(string = "Description")
    uom_id = fields.Many2one('product.uom',string="UOM")
    std_qty = fields.Float(string='Std. Qty',digits=(6,3))
    actual_qty = fields.Float(string='Actual Qty', required="True",digits=(6,3))
    extra_qty =fields.Float(string='Extra Req Qty.',digits=(6,3))
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.')
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.')
    issued_qty = fields.Float(string='Issued Qty', readonly=True,digits=(6,3))
    extra_issued_qty =fields.Float(string='Extra Qty',default=0 ,digits=(6,3))
    qty_returned = fields.Float(string='Qty Returned',digits=(6,3))
    remarks = fields.Text(string='Remarks')
    extra_flag = fields.Integer(string='Extra Flag',default=0)
    grn_list = fields.Text(string= 'GRN Nos',readonly=1,default='.')
    
    _sql_constraints = [        
        ('unique_product_id','unique(material_id, bom_wizard_id)', 'Item(s) should be Unique')
        ]
    
    
    
    def onchange_material_id(self, cr, uid, ids, material_id, context=None):
        uom_id = 0
        description = ''
        std_qty = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description,case when prakruti_standard_product.standard_value >0 then prakruti_standard_product.standard_value else 0 end as std_qty FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id LEFT JOIN prakruti_standard_product ON product_product.id = prakruti_standard_product.product_name WHERE product_product.id = cast(%s as integer)', ((material_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
            std_qty = line['std_qty']
        return {'value' :{
                'uom_id':uom_id,
                'description':description,
                'std_qty':std_qty,
                'actual_qty':std_qty
                          }}
    
   
