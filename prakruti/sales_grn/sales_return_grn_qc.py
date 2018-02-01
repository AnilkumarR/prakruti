'''
Company : EBSL
Author: Induja
Module: Sales GRN QC
Class 1: PrakrutiSalesReturnGRNQC
Class 2: PrakrutiGRNLineQC
Table 1 & Reference Id: prakruti_sales_return_grn_qc ,grn_qc_line
Table 2 & Reference Id: prakruti_sales_return_grn_qc_line,grn_qc_line_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''


# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
from openerp.tools import amount_to_text
from openerp.tools.amount_to_text import amount_to_text_in 
from openerp.tools.amount_to_text import amount_to_text_in_without_word_rupees 
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


class PrakrutiSalesReturnGRNQC(models.Model):    
    _name =  'prakruti.sales_return_grn_qc'
    _table = 'prakruti_sales_return_grn_qc'
    _description = 'Sales GRN QC'
    _rec_name = 'grn_no'    
    _order="id desc"     
        
    grn_qc_line = fields.One2many('prakruti.sales_return_grn_qc_line','grn_qc_line_id')
    grn_no = fields.Char(string='GRN No', readonly=1)
    grn_date = fields.Date('GRN Date',readonly = 1)
    qc_date = fields.Date('QC Date',default= fields.Date.today,readonly = 1)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=1)
    customer_id = fields.Many2one('res.partner',string='Customer',readonly=1)
    order_date = fields.Date(string='Order Date', readonly= 1)
    company_id = fields.Many2one('res.company',string='Company', readonly= 1 )
    remarks=fields.Text('Received Remarks')
    state = fields.Selection([('qc_check','Quality Control'),
                              ('validate','Validated'),
                              ('qc_ha','Quality Control HA'),
                              ('qc_check_done','Quality Control Done'),
                              ('done','Goods Received Note Done')],default= 'qc_check', string= 'Status')
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    quotation_no= fields.Char(string='Quotation No' ,readonly=1)
    quotation_date = fields.Date(string='Quotation Date' ,readonly=1)
    inquiry_date= fields.Date('Inquiry Date',readonly=1)
    inquiry_no = fields.Char(' Inquiry No', readonly=1)
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    remarks = fields.Text(string="Remarks")
    terms =fields.Text('Terms and conditions')
    order_type = fields.Selection([('with_tarrif','With Tarrif'),('without_tarrif','Without Tarrif')], string="Order Type")
    assessable_value=fields.Float(string='Assessable Value(%)',digits=(6,3))
    total_assessable_value= fields.Float(string='Total Assesable value',digits=(6,3))
    assessable_subtotal=fields.Float(string='Assesable  Total',digits=(6,3))
    subtotal= fields.Float(string='Sub Total',digits=(6,3))
    bed_type= fields.Selection([('percentage','%'),('quantity','Qty')], string="BED Type",default='percentage')
    bed_percentage = fields.Float(string="BED % Value",digits=(6,3))
    bed_qty = fields.Float(string="BED qty Value",digits=(6,3))
    bed_amt = fields.Float(string="BED Total",digits=(6,3))
    ed_cess_type = fields.Selection([('percentage','%'),('quantity','Qty')], string="Ed Cess Type",default='percentage')
    ed_cess_qty = fields.Float(string="Ed Cess  qty Value",digits=(6,3))
    ed_cess_percentage = fields.Float(string="Ed Cess % Value",digits=(6,3))
    ed_cess_amt = fields.Float(string="Ed Cess Total",digits=(6,3))
    sec_cess_type = fields.Selection([('percentage','%'),('quantity','Qty')], string="Sec Cess Type",default='percentage')
    sec_cess_qty = fields.Float(string="Sec Cess qty Value",digits=(6,3))
    sec_cess_percentage = fields.Float(string="Sec Cess % Value",digits=(6,3))
    sec_cess_amt = fields.Float(string="Sec Cess Total",digits=(6,3))
    tax_type = fields.Selection([('cst','CST'),('tax','Tax'),('vat','VAT')], string="Tax", default= 'tax')
    tax_value =  fields.Float(string="Tax Value",digits=(6,3))
    total_tax = fields.Float(string="Total Tax",digits=(6,3))
    cst_value =  fields.Float(string="Cst Value",digits=(6,3))
    total_cst = fields.Float(string="Total Cst",digits=(6,3))
    vat_value =  fields.Float(string="Vat Value",digits=(6,3))
    total_vat = fields.Float(string="Total Vat",digits=(6,3))
    sbc_value =  fields.Float(string="Swachh Bharat Cess Value",digits=(6,3))
    total_sbc = fields.Float(string="Total Swachh Bharat Cess",digits=(6,3))
    kkc_value =  fields.Float(string="Krushi Kalayan Cess' Value",digits=(6,3))
    total_kkc = fields.Float(string="Total Krushi Kalayan Cess",digits=(6,3))
    untaxed_amount = fields.Float(string="Untaxed Amount",digits=(6,3))
    transporatation_charges=fields.Float(string='Transportation Charges',digits=(6,3))
    final_grand_total = fields.Float(string=" Grand Total",digits=(6,3))
    flag_rejected_count = fields.Integer('Flag', default=1) 
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By') 
    checked_id =fields.Many2one('res.users','Checked By') 
    product_id = fields.Many2one('product.product', related='grn_qc_line.product_id', string='Product Name') 
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    reference_date= fields.Date(string='Ref Date')
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'checked_id': lambda s, cr, uid, c:uid,
        }
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['done','qc_check_done','qc_check','validate','qc_ha']:
                raise UserError(_('Sorry....You Can\'t Delete'))
        return super(PrakrutiSalesReturnGRNQC, self).unlink() 
    
    
    '''
    This will check the status based upon this flag will generate
    '''
    @api.one
    @api.multi 
    def validate(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        count_value= 0
        accept_value = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute(''' SELECT count(id) as status_marked FROM prakruti_sales_return_grn_qc_line WHERE (status = 'accepted' OR status = 'rejected') AND grn_qc_line_id = %s''',((temp.id),))
            for no_of_line in cr.dictfetchall():
                status_marked = int(no_of_line['status_marked'])
            if status_marked == len(temp.grn_qc_line):
                cr.execute("UPDATE prakruti_sales_return_grn_qc SET state = 'validate' WHERE id=%s",((temp.id),))
                cr.execute("SELECT count(id) as count_value FROM prakruti_sales_return_grn_qc_line WHERE status = 'rejected' AND grn_qc_line_id = %s",((temp.id),))
                for item in cr.dictfetchall():
                    count_value=int(item['count_value'])
                    print '------------------------1111111111111111111111111111-------------------',count_value
                    if count_value >= accept_value:
                        cr.execute("update prakruti_sales_return_grn_qc set flag_rejected_count =2 where id=%s",((temp.id),))
                cr.execute("SELECT count(id) as accept_value FROM prakruti_sales_return_grn_qc_line WHERE status = 'accepted' AND grn_qc_line_id = %s",((temp.id),))
                for item in cr.dictfetchall():
                    accept_value=int(item['accept_value'])    
                    print '--------------------------------00000000000000000000000000000000-------------------------------------------',accept_value
                    if count_value == accept_value:
                        print '------------------------------updateeeeeeeeeeeeee---------------------------------------------',accept_value
                        cr.execute("update prakruti_sales_return_grn_qc set flag_rejected_count =2 where id=%s",((temp.id),))
                    elif count_value == 0:
                        print '------------------------------count_value---------------------------------------------',count_value
                        cr.execute("update prakruti_sales_return_grn_qc set flag_rejected_count =4 where id=%s",((temp.id),))
                        cr.execute("update prakruti_sales_return_grn set flag_rejected_count =4 where grn_no=%s",((temp.grn_no),))
            else:
                raise UserError(_('Please Enter Accepted Qty\nPlease Check Status'))
        return {}
    '''
    Pulls the data to GRN screen
    '''
    @api.one
    @api.multi 
    def quality_to_grn(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("UPDATE prakruti_sales_return_grn_line as b set accepted_qty =a.accepted_qty,rejected_qty=a.rejected_qty,status=a.status,state=a.state  FROM( SELECT grn_qc_line_id,grn_grid_line_id,product_id,status,state,accepted_qty,rejected_qty  FROM prakruti_sales_return_grn_qc_line WHERE grn_qc_line_id= %s ) as a WHERE a.grn_grid_line_id = b.id AND a.product_id = b.product_id",((temp.id),))
            cr.execute("UPDATE prakruti_sales_return_grn_qc SET state = 'done' WHERE prakruti_sales_return_grn_qc.id = cast(%s as integer)", ((temp.id),))
            cr.execute("UPDATE prakruti_sales_return_grn set state = 'qc_check_done' where grn_no=%s",((temp.grn_no),))
        return {}
    '''
    Pulls the data to GRN HA screen
    '''
    @api.one
    @api.multi 
    def quality_to_ha(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("update prakruti_sales_return_grn_qc set state ='qc_ha' where id=%s",((temp.id),))
            ebsl_id = self.pool.get('prakruti.sales_return_grn_qc_ha').create(cr,uid, {
                    'grn_no':temp.grn_no,
                    'grn_date':temp.grn_date,
                    'order_no':temp.order_no.id,
                    'order_date':temp.order_date,
                    'customer_id':temp.customer_id.id,
                    'dispatch_id':temp.dispatch_id.id,
                    'order_id':temp.order_id.id,
                    'quotation_id':temp.quotation_id.id,
                    'requested_id':temp.requested_id.id,
                    'checked_id':temp.checked_id.id,
                    'company_id':temp.company_id.id,
                    'terms':temp.terms,
                    'remarks':temp.remarks,
                    'reference_date':temp.reference_date,
                    'reference_no':temp.reference_no,   
                    'revision_no':temp.revision_no
                    })
            for item in temp.grn_qc_line:
                erp_id = self.pool.get('prakruti.sales_return_grn_qc_ha_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'specification_id':item.specification_id.id,
                    'description': item.description,
                    'quantity': item.quantity,
                    'batch_no':item.batch_no,
                    'accepted_qty':item.accepted_qty,
                    'rejected_qty':item.rejected_qty,      
                    'status': item.status,
                    'remarks':item.remarks,
                    'grn_grid_line_id':item.grn_grid_line_id,
                    'grn_qc_ha_line_id': ebsl_id
                    })
            cr.execute("update prakruti_sales_return_grn_qc set flag_rejected_count =3 where id=%s",((temp.id),))
        return {}
    
class PrakrutiGRNLineQC(models.Model):
    _name = 'prakruti.sales_return_grn_qc_line'
    _table = 'prakruti_sales_return_grn_qc_line'
    _description = 'Sales GRN QC Line'
    
    grn_qc_line_id = fields.Many2one('prakruti.sales_return_grn_qc', ondelete='cascade')
    product_id  = fields.Many2one('product.product', string="Product Name")
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    ar_no = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")
    description = fields.Text(string="Description")
    quantity = fields.Float('Qty.',digits=(6,3))
    remarks = fields.Text(string="Remarks")
    state =fields.Selection([
        ('qc_check','QC Check'),
        ('qc_done','QC Done'),
        ('done','Done')], string= 'States',default='qc_check',invisible=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('rejected','Rejected')
        ], string= 'Status')
    accepted_qty = fields.Float(string= 'Accept. Qty.',digits=(6,3))
    rejected_qty = fields.Float(string= 'Reject. Qty.', compute='_compute_rejected_qty', store=True,digits=(6,3))
    grn_grid_line_id = fields.Integer(string= 'GRN Grid Line Id')
    batch_no = fields.Char(string="Batch No",readonly=1)
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    tarrif_id=fields.Text(string='Tarrif No')
    mrp=fields.Float(string="MRP",digits=(6,3))
    total= fields.Float(string='Total',digits=(6,3)) 
    total1= fields.Float(string='Total1',digits=(6,3)) 
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    '''
    Rejected Qty Calculation
    '''
    @api.depends('quantity','accepted_qty')
    def _compute_rejected_qty(self):
        for order in self:
            rejected_qty = 0.0            
            order.update({                
                'rejected_qty': order.quantity - order.accepted_qty 
            })
            
    
    '''
    When we select status test result will automatically display
    '''  
    @api.onchange('status')
    def onchange_status(self):
        if self.status == 'accepted':
            self.accepted_qty = self.quantity
        elif self.status == 'rejected':
            self.rejected_qty = self.quantity
            self.accepted_qty = 0.0
        else:
            self.accepted_qty = 0.0
            self.rejected_qty = 0.0