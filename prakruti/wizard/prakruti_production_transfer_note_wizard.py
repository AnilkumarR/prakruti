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

class prakruti_production_transfer_note_wizard(models.TransientModel):
    _name = 'prakruti.production_transfer_note_wizard'
    _table = 'prakruti_production_transfer_note_wizard'
    _description = 'Production Transfer Note Wizard'
    
    ptn_id=fields.Integer(string='PTN Id')
    batch_no = fields.Many2one('prakruti.batch_master',string='Batch No', readonly=1)
    ptn_no = fields.Char(string='PTN No',readonly=1)
    ptn_wizard_line=  fields.One2many('prakruti.production_transfer_note_wizard_line','ptn_wizard_id',string= 'PTN Line')       
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
            if len(temp.ptn_wizard_line) > 0:
                cr.execute('''  INSERT INTO prakruti_production_transfer_note_line(product_id,uom_id,description,specification_id,packing_style,packing_qty,total_output_qty,remarks,main_id)
                                SELECT 
                                    prakruti_production_transfer_note_wizard_line.product_id,
                                    prakruti_production_transfer_note_wizard_line.uom_id,
                                    prakruti_production_transfer_note_wizard_line.description,
                                    prakruti_production_transfer_note_wizard_line.specification_id,
                                    prakruti_production_transfer_note_wizard_line.packing_style,
                                    prakruti_production_transfer_note_wizard_line.packing_qty,
                                    prakruti_production_transfer_note_wizard_line.total_output_qty,
                                    prakruti_production_transfer_note_wizard_line.remarks,
                                    prakruti_production_transfer_note_wizard.ptn_id as grid_id
                                FROM
                                    prakruti_production_transfer_note_wizard_line JOIN
                                    prakruti_production_transfer_note_wizard ON
                                    prakruti_production_transfer_note_wizard.id = prakruti_production_transfer_note_wizard_line.ptn_wizard_id 
                                WHERE 
                                    prakruti_production_transfer_note_wizard_line.ptn_wizard_id = %s''',((temp.id),))
                
            else:
                raise UserError(_('Oops Something is Missing...'))
        return {}

class prakruti_production_transfer_note_wizard_line(models.TransientModel):
    _name = 'prakruti.production_transfer_note_wizard_line'
    _table = 'prakruti_production_transfer_note_wizard_line'
    _description = 'Production Transfer Note Wizard Line'

    
    
    ptn_wizard_id = fields.Many2one('prakruti.production_transfer_note_wizard',string="Grid", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product Name")
    uom_id = fields.Many2one('product.uom',string="UOM")
    description = fields.Text(string="Description")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    packing_style=fields.Float(string='Packing Style',digits=(6,3))
    packing_qty=fields.Float(string='Packing Qty',digits=(6,3))
    total_output_qty=fields.Float(string='Total Output Qty',digits=(6,3))
    accepted_qty = fields.Float(string = "Accepted.Qty",digits=(6,3))
    rejected_qty = fields.Float(string = "Reject Qty" ,digits=(6,3))
    test_result=fields.Char(string='Test Result')
    qc_status=fields.Selection([('approved','Approved'),('rejected','Rejected')],string='QC status')
    remarks=fields.Char(string='Remarks')
    
    _sql_constraints = [        
        ('unique_product_id','unique(product_id, ptn_wizard_id)', 'Item(s) should be Unique')
        ]
    
    
    
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        cr.execute('SELECT  product_uom.id AS uom_id,product_uom.name,product_template.name as description FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id=cast(%s as integer)', ((product_id),))
        for values in cr.dictfetchall():
            uom_id = values['uom_id']
            description = values['description']
            return {'value' :{ 'uom_id': uom_id,'description':description }}
    
   
