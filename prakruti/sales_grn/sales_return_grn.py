'''
Company : EBSL
Author: Induja
Module: Sales GRN
Class 1: PrakrutiSalesReturnGRN
Class 2: PrakrutiGRNLine 
Table 1 & Reference Id: prakruti_sales_return_grn ,grn_line
Table 2 & Reference Id: prakruti_sales_return_grn_line,grn_line_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''


# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
import time
from openerp.tools import image_resize_image_big
from openerp.exceptions import ValidationError
from openerp import api, fields, models, _
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
from openerp.tools import amount_to_text
from openerp.tools.amount_to_text import amount_to_text_in 
from openerp.tools.amount_to_text import amount_to_text_in_without_word_rupees 




class PrakrutiSalesReturnGRN(models.Model):    
    _name =  'prakruti.sales_return_grn'
    _table = 'prakruti_sales_return_grn'
    _description = 'Sales GRN'
    _rec_name = 'grn_no'    
    _order="id desc"   
    
    
  
    '''Auto genereation function
    'Format: SR\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SR\MISC\0455\17-18
    Updated By : Induja
    Updated On : 20170823
    Version :0.1
    '''
    
    @api.one
    @api.multi
    def _get_auto_grn_no(self):
        style_format = {}
        month_value=0
        year_value=0
        next_year=0
        display_year=''
        display_present_year=''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self :
            cr.execute('''SELECT 
                                CAST(EXTRACT (month FROM grn_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM grn_date) AS integer) AS year,
                                id
                          FROM 
                                prakruti_sales_return_grn 
                          WHERE 
                                id=%s''',((temp.id),))
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
            cr.execute('''SELECT autogenerate_sales_grn_no(%s)''', ((temp.id),)  ) # DATABASE FUNCTION:  autogenerate_sales_grn_no
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_sales_grn_no'];
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
                    if temp.product_type_id.group_code:
                        style_format[record.id] = 'SR\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(display_year)
                    else:                        
                        style_format[record.id] = 'SR\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(display_year)
            cr.execute('''UPDATE 
                                prakruti_sales_return_grn 
                          SET 
                                grn_no =%s 
                          WHERE 
                                id=%s ''', ((style_format[record.id]),(temp.id),)  )
        return style_format
    
    
    
    grn_line = fields.One2many('prakruti.sales_return_grn_line','grn_line_id')
    return_type =fields.Selection([
        ('from_dispatch','FROM DISPATCH'),
        ('return_by_customer','RETURN BY CUSTOMER')
       ],default='from_dispatch', string= 'Type')
    grn_no= fields.Char(string='GRN No', readonly=True)
    grn_date=fields.Date('Date',default= fields.Date.today)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=True)
    customer_id = fields.Many2one('res.partner',string='Customer',readonly=True)
    order_date = fields.Date(string='Order Date')
    company_id = fields.Many2one('res.company',string='Company')
    remarks=fields.Text('Received Remarks')
    state = fields.Selection([('grn','Goods Received Note'),
                              ('to_scrap','Scrap'),
                              ('qc_check','Quality Control '),
                              ('qc_check_done','Quality Control Done'),
                              ('done','Goods Received Note Done')],default= 'grn', string= 'Status')
    prakruti_stock_id = fields.Integer('SCREEN COMMON ID')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)    
    good_received_note_no= fields.Char(string='GRN No',compute= '_get_auto_grn_no')
    scrap_count = fields.Integer('Scrap Count',default= 0)
    flag_rejected_count = fields.Integer('Flag Reject Count',default= 1)
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    quotation_no= fields.Char(string='Quotation No' ,readonly=True)
    quotation_date = fields.Date(string='Quotation Date' ,readonly=True)
    inquiry_date= fields.Date('Inquiry Date',readonly=True)
    inquiry_no = fields.Char(' Inquiry No', readonly=True)
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
    sec_cess_qty = fields.Float(string="Sec Cess qty Value")
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
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By') 
    product_id = fields.Many2one('product.product', related='grn_line.product_id', string='Product Name') 
    location_id = fields.Many2one('prakruti.stock_location',string = 'Location')
    
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    reference_date= fields.Date(string='Ref Date')

    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'grn_no':'New',
        'company_id': _default_company
        }
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['done','qc_check_done','qc_check','to_scrap','grn']:
                raise UserError(_('Sorry....You Can\'t Delete'))
        return super(PrakrutiSalesReturnGRN, self).unlink() 
    
    
    '''
    UPDATE THE STOCK
    '''
    @api.one
    @api.multi 
    def grn_to_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("SELECT count(id) as accept_count FROM prakruti_sales_return_grn_line WHERE accepted_qty > 0 AND grn_line_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                accept_count=int(line['accept_count'])
            if accept_count >= 1:
                cr.execute("SELECT stock_sales_grn(%s)", ((temp.id),))
            cr.execute("UPDATE prakruti_sales_return_grn SET state = 'done' WHERE prakruti_sales_return_grn.id = cast(%s as integer)", ((temp.id),))
        return {}
    
    
    '''
    Pull the data to GRN QC
    '''
    @api.one
    @api.multi 
    def grn_to_quality(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_id = self.pool.get('prakruti.sales_return_grn_qc').create(cr,uid, {
                'grn_no':temp.grn_no,
                'grn_date':temp.grn_date,
                'order_no':temp.order_no.id,
                'order_date':temp.order_date,
                'customer_id':temp.customer_id.id,
                'product_type_id':temp.product_type_id.id,
                'company_id':temp.company_id.id,
                'remarks':temp.remarks,
                'terms':temp.terms,
                'inquiry_no':temp.inquiry_no,
                'inquiry_date':temp.inquiry_date,
                'quotation_no':temp.quotation_no,
                'quotation_date':temp.quotation_date,
                'shipping_id':temp.shipping_id.id,
                'billing_id':temp.billing_id.id,
                'order_type':temp.order_type,
                'assessable_value':temp.assessable_value,
                'total_assessable_value':temp.total_assessable_value,
                'assessable_subtotal':temp.assessable_subtotal,
                'bed_type':temp.bed_type,
                'bed_percentage':temp.bed_percentage,
                'bed_qty':temp.bed_qty,
                'bed_amt':temp.bed_amt,
                'ed_cess_type':temp.ed_cess_type,
                'ed_cess_qty':temp.ed_cess_qty,
                'ed_cess_percentage':temp.ed_cess_percentage,
                'ed_cess_amt':temp.ed_cess_amt,
                'sec_cess_type':temp.sec_cess_type,
                'sec_cess_qty':temp.sec_cess_qty,
                'sec_cess_percentage':temp.sec_cess_percentage,
                'sec_cess_amt':temp.sec_cess_amt,
                'tax_type':temp.tax_type,
                'tax_value':temp.tax_value,
                'total_tax':temp.total_tax,
                'cst_value':temp.cst_value,
                'total_cst':temp.total_cst,
                'vat_value':temp.vat_value,
                'total_vat':temp.total_vat,
                'sbc_value':temp.sbc_value,
                'total_sbc':temp.total_sbc,
                'kkc_value':temp.kkc_value,
                'total_kkc':temp.total_kkc,
                'untaxed_amount':temp.untaxed_amount,
                'transporatation_charges':temp.transporatation_charges,
                'final_grand_total':temp.final_grand_total,
                'dispatch_id':temp.dispatch_id.id,
                'order_id':temp.order_id.id,
                'quotation_id':temp.quotation_id.id,
                'requested_id':temp.requested_id.id,
                'reference_date':temp.reference_date,
                'reference_no':temp.reference_no,   
                'revision_no':temp.revision_no,
                'state':'qc_check'
                    })
            for item in temp.grn_line:
                erp_id = self.pool.get('prakruti.sales_return_grn_qc_line').create(cr,uid, {
                    'product_id':item.product_id.id,
                    'uom_id':item.uom_id.id,
                    'specification_id':item.specification_id.id,
                    'description':item.description,
                    'quantity':item.quantity,
                    'remarks':item.remarks,
                    'unit_price': item.unit_price,
                    'tarrif_id':item.tarrif_id,
                    'mrp':item.mrp,
                    'total1':item.total1,
                    'batch_no':item.batch_no,
                    'mfg_date':item.mfg_date,
                    'exp_date':item.exp_date,
                    'total':item.total,
                    'state':'qc_check',
                    'status':'rejected',
                    'grn_grid_line_id':item.id,
                    'grn_qc_line_id': ebsl_id
                    })
            cr.execute('''UPDATE prakruti_sales_return_grn SET state = 'qc_check' WHERE prakruti_sales_return_grn.id = cast(%s as integer)''', ((temp.id),))
        return {}
    
    
    
class PrakrutiGRNLine(models.Model):
    _name = 'prakruti.sales_return_grn_line'
    _table = 'prakruti_sales_return_grn_line'
    _description = 'Sales GRN Line'
    
    grn_line_id = fields.Many2one('prakruti.sales_return_grn', ondelete='cascade')
    product_id  = fields.Many2one('product.product', string="Product Name",required= True)
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    description = fields.Text(string="Description")
    quantity = fields.Float('Qty.',digits=(6,3))
    remarks = fields.Text(string="Remarks")
    state =fields.Selection([
        ('draft','Draft'),
        ('sent_to_qc','Sent To Quality Check'),
        ('sent_to_dispatch','Sent to Dispatch'),
        ('qc_done','QC Done'),
        ('invoice','Invoiced'),
        ('return','returned')
        ], string= 'States',default='return')
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('par_reject', 'Partially Accepted'),
        ('accept_under_deviation','Accepted Under Deviation'),
        ('rejected','Rejected')
        ], string= 'Status')
    accepted_qty = fields.Float(string= 'Accept. Qty.',digits=(6,3))
    rejected_qty = fields.Float(string= 'Reject. Qty.',digits=(6,3))
    batch_no = fields.Char('Batch No.')
    batch_no = fields.Char(string="Batch No")
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    tarrif_id=fields.Text(string='Tarrif No')
    mrp=fields.Float(string="MRP",digits=(6,3))
    total= fields.Float(string='Total', compute='_compute_price_total', store=True,digits=(6,3)) 
    total1= fields.Float(string='Total1', compute='_compute_price_total1', store=True,digits=(6,3)) 
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    _sql_constraints = [
        ('unique_batch_no','unique(batch_no)','Batch No. must be Unique !')
        ]