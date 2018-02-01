# -*- coding: utf-8 -*-
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
import time
from openerp.tools import image_resize_image_big

class PrakrutiMaterialOutwardNote(models.Model):
    _name = 'prakruti.material_outward_note'
    _table = "prakruti_material_outward_note"
    _description = 'Prakruti Material Outward Note'
    _rec_name = "mon_no"
    _order = 'id desc'
    
    mon_no = fields.Char(string= 'MON No')
    mon_date = fields.Date(string= 'MON Date', default=fields.Date.today)
    gc_no = fields.Char(string= 'GC No')
    gc_date = fields.Date(string= 'GC Date')    
    vendor_id = fields.Many2one('res.partner',string= 'Vendor')
    address_line_1 = fields.Char(string= 'Address', related='vendor_id.street')
    address_line_2 = fields.Char(related='vendor_id.street2')
    address_line_3 = fields.Char(related='vendor_id.city')
    address_line_3_1 = fields.Many2one(related='vendor_id.state_id')
    address_line_3_2 = fields.Char(related='vendor_id.zip')
    address_line_4 = fields.Many2one(related='vendor_id.country_id')    
    party_vat_no = fields.Char(string= 'Party VAT No', related='vendor_id.vat_no')
    party_cst_no = fields.Char(string= 'Party CST No', related='vendor_id.cst_no')    
    transporter_name = fields.Char(string= 'Transporter Name', size=16)
    t_pay_det = fields.Char(string= 'Transporter Payment Details', size=16)    
    company_id = fields.Many2one('res.company',string= 'Company',default=lambda self: self.env.user.company_id,readonly=1)
    c_tin_vat = fields.Char(string= 'TIN/VAT No', related='company_id.tin')
    gst = fields.Char(string= 'GST', related='company_id.gstin')      
    remarks = fields.Text(string= 'Remarks',size=28)    
    s_ing = fields.Many2one('res.users', string= 'Stores Incharge')    
    doc_no = fields.Char(string= 'Doc No')
    rev_no = fields.Char(string= 'Rev No')
    doc_date = fields.Char(string= 'Date')    
    order_line = fields.One2many('prakruti.material_outward_note_line','line_id')
    total_no_of_pack = fields.Float(string= 'Total No of Packing',compute= '_compute_total_pack')
    total_no_of_qty = fields.Float(string= 'Total No of Qty',compute= '_compute_total_qty')
    total_amount = fields.Float(string= 'Total Amount',compute= '_compute_total_amount')
    material_no = fields.Char(compute= '_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)    
    sent_to_gate_pass_flag = fields.Integer(default=0)
    
    '''
    Pushing the data to material_outward
    '''
    @api.one
    @api.multi 
    def material_outward_to_gate_pass(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            gate_pass_id = self.pool.get('prakruti.gate_pass').create(cr,uid, {
                'company_id':temp.company_id.id,
                'vendor_id':temp.vendor_id.id,
                'coming_from':'purchase_return',
                'document_type':'purchase_outward',
                })
            for line in temp.order_line:
                gate_pass_line_id = self.pool.get('prakruti.gate_pass_line').create(cr,uid, {
                    'product_id': line.product_id.id,
                    'description': line.description,
                    'remarks': line.remarks,
                    'quantity': line.qty,
                    'uom_id': line.uom_id.id,
                    'no_of_packings':line.no_of_pack,
                    'pack_per_qty':line.pack_size,
                    'main_id': gate_pass_id
                    })
            cr.execute('''UPDATE prakruti_material_outward_note SET sent_to_gate_pass_flag = 1 WHERE id = %s''',((temp.id),))
        return {}
    
    
    @api.one
    @api.multi
    def _get_auto(self):
        x = {}
        month_value=0
        year_value=0
        next_year=0
        display_year=''
        display_present_year=''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self :
            cr.execute('''select cast(extract (month from mon_date) as integer) as month ,cast(extract (year from mon_date) as integer) as year ,id from prakruti_material_outward_note where id=%s''',((temp.id),))            
            for item in cr.dictfetchall():
                month_value=int(item['month'])
                year_value=int(item['year'])
            if month_value<=3:
                year_value=year_value-1
            else:
                year_value=year_value
            next_year=year_value+1
            display_year=str(next_year)[-2:]
            display_present_year=str(year_value)[-2:]
            cr.execute('''select autogenerate_material_outward(%s)''', ((temp.id),)  ) 
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_material_outward'];
            auto_gen = int(parent_invoice_id)
            if len(str(auto_gen)) < 2:
                auto_gen = '000'+ str(auto_gen)
            elif len(str(auto_gen)) < 3:
                auto_gen = '00' + str(auto_gen)
            elif len(str(auto_gen)) == 3:
                auto_gen = '0'+str(auto_gen)
            else:
                auto_gen = str(auto_gen)
            for record in self :
                x[record.id] = 'MO-'+str(auto_gen) +'/'+str(display_present_year)+'-'+str(display_year)
                cr.execute('''update prakruti_material_outward_note set mon_no =%s where id=%s ''', ((x[record.id]),(temp.id),)  )
        return x   
    
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')   
    
    _defaults = {
        's_ing': lambda s, cr, uid, c:uid,
        'company_id': _default_company,
        'mon_no': 'New'
        }
    
    
    def _check_the_grid(self, cr, uid, ids, context=None, * args):
        for line in self.browse(cr, uid, ids, context=context):
            if len(line.order_line) == 0:
                return False
        return True   
    _constraints = [
         (_check_the_grid, 'Sorry !!!, Your Order Line is empty, Please enter some products to procced further, Thank You !', ['order_line']),
    ]
    
    @api.depends('order_line.qty','order_line.amount')
    def _compute_total_amount(self):
        total = 0.0
        for order in self:
            for line in order.order_line:
                total += line.qty * line.amount                
                print 'totaltotaltotaltotaltotaltotaltotaltotaltotaltotal --',total
                order.update({
                    'total_amount': total 
                    })
    @api.depends('order_line.qty')
    def _compute_total_qty(self):
        total_qty = 0.0
        for order in self:
            for line in order.order_line:
                total_qty += line.qty                
                print 'total_qtytotal_qtytotal_qtytotal_qtytotal_qtytotal_qty --',total_qty
                order.update({
                    'total_no_of_qty': total_qty 
                    })
    @api.depends('order_line.no_of_pack')
    def _compute_total_pack(self):
        total_packing = 0.0
        for order in self:
            for line in order.order_line:
                total_packing += line.no_of_pack                
                print 'total_packingtotal_packingtotal_packingtotal_packing --',total_packing
                order.update({
                    'total_no_of_pack': total_packing 
                    })
    
    

class PrakrutiMaterialOutwardNoteLine(models.Model):
    _name = 'prakruti.material_outward_note_line'
    _table = "prakruti_material_outward_note_line"
    _description = 'Prakruti Material Outward Note Line'
    
    line_id = fields.Many2one('prakruti.material_outward_note')    
    product_id = fields.Many2one('product.product',string= 'Product',required=1,readonly=1)
    description = fields.Char(string="Description", readonly= 1)
    uom_id = fields.Many2one('product.uom',string= 'UOM')
    no_of_pack = fields.Float(string= 'No of Packing',default=0.000,digits=(6,3))
    pack_size = fields.Float(string= 'Packing Size',default=0.000,digits=(6,3))
    qty = fields.Float(string= 'Qty')
    amount = fields.Float(string= 'Amount')
    remarks = fields.Text(string= 'Remarks')
    
    
    
    
    
    
    
    
    