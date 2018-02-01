'''
Company : EBSL
Author: Induja
Module: Sales Order
Class 1: PrakrutiSalesOrder
Class 2: PrakrutiSalesOrderItem
Table 1 & Reference Id: prakruti_sales_order ,grid_id
Table 2 & Reference Id: prakruti_sales_order_item,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''

# -*- coding: utf-8 -*-
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

class PrakrutiSalesOrder(models.Model):
    _name = 'prakruti.sales_order'
    _table = "prakruti_sales_order"
    _description = 'Sales Order'
    _order="id desc"
    _rec_name= "order_no"
    
  
    '''Auto genereation function
    'Format: SO\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SO\EXFG\0262\17-18
    Updated By : Induja
    Updated On : 20170823
    Version :0.1
    '''
    
    
    @api.one
    @api.multi
    def _get_auto(self):
        style_format = {}
        month_value=0
        year_value=0
        next_year=0
        dispay_year=''
        display_present_year=''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self:
            cr.execute('''SELECT 
                                CAST(EXTRACT (month FROM order_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM order_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_sales_order
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
                dispay_year=str(next_year)[-2:]
                display_present_year=str(year_value)[-2:]
                        
                cr.execute('''SELECT autogenerate_sales_order(%s)''', ((temp.id),)  ) # Database Function autogenerate_sales_order
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_sales_order'];
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
                        style_format[record.id] = 'SO\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:                        
                        style_format[record.id] = 'SO\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE 
                                        prakruti_sales_order 
                                  SET 
                                        order_no =%s 
                                  WHERE 
                                        id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
    
    
    grid_id = fields.One2many('prakruti.sales_order_item', 'main_id',string='Grid')
    countflag = fields.Integer('Flag Line is There',default= 0)
    order_no = fields.Char(string='Order No', readonly=True)
    order_date = fields.Date(string='Order Date', default= fields.Date.today, required=True)
    quotation_no= fields.Char(string='Quotation No' ,readonly=True)
    quotation_date = fields.Date(string='Quotation Date' ,readonly=True)
    inquiry_date= fields.Date('Inquiry Date',readonly=True)
    inquiry_no = fields.Char(' Inquiry No', readonly=True)
    customer_id = fields.Many2one('res.partner',string="Customer")
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    remarks = fields.Text(string="Remarks")
    ord_no = fields.Char('Order Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id1 = fields.Integer('Auto Generating id',default= 0)
    terms =fields.Text('Terms and conditions')
    balance_line = fields.Integer('Any Balance Line',default=0,readonly=1)    
    cash_amount = fields.Float(string="Amount",digits=(6,3),default=0)
    cash_remarks = fields.Text(string="Remarks")    
    cheque_amount = fields.Float(string="Amount",digits=(6,3),default=0)
    cheque_no = fields.Integer(string="Cheque No.")
    cheque_remarks = fields.Text(string="Remarks")    
    draft_amount = fields.Float(string="Amount",digits=(6,3),default=0)
    draft_no = fields.Integer(string="Draft No.")
    draft_remarks = fields.Text(string="Remarks")
    amount_flag = fields.Integer(string="Is Payment Done",default=0)        
    slip_no= fields.Char(string='Slip No.')
    po_no= fields.Char(string='P.O No')    
    requested_id =fields.Many2one('res.users','Requested By',readonly=True)
    quotation_id =fields.Many2one('res.users','Quotation By',readonly=True)
    order_id =fields.Many2one('res.users','Order By')
    reference_no= fields.Char(string='Ref No')
    reference_date= fields.Date(string='Ref Date')
    revise_flag= fields.Integer(string='Revised No.',default=0) 
    revise_comments= fields.Text(string='Revised Comments') 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')     
    state =fields.Selection([
        ('order','Order'),
        ('slip_request','Production Slip Issued'),
        ('partially_confirmed','Production Slip Partially Confirmed'),
        ('production_slip_confirmed','Production Slip Completely Confirmed'),
        
        ('partial_order','Order Partially Dispatched/Confirmed/Invoiced'),
        ('confirm','Order Dispatched/Confirmed/Invoiced'),
        
        #('without_qc_partially_confirmed','Without Quality Control Order Partially Dispatched/Confirmed/Invoiced'),
        #('without_qc_invoice','Without Quality Control Order Dispatched/Confirmed/Invoiced'), 
        
        ('extra_partial_order','Extra Order Partially Dispatched/Confirmed/Invoiced'),
        ('extra_confirm','Extra Order Dispatched/Confirmed/Invoiced'),
        
        #('extra_without_qc_partially_confirmed','Extra Without Quality Control Order Partially Dispatched/Confirmed/Invoiced'),
        #('extra_without_qc_invoice','Extra Without Quality Control Order Dispatched/Confirmed/Invoiced'),
        
        ('rejected','Sales Order Rejected'),
        ('short_close','Sales Order Short Closed')
        ],default= 'order', string= 'Status')  
    any_adv_payment =fields.Selection([
        ('no', 'No'),
        ('yes','Yes')
        ],default='no' ,string= 'Any Advance Payment')
    advance_payment_type =fields.Selection([
        ('cash', 'CASH'),
        ('cheque','CHEQUE'),
        ('demand_draft','DEMAND DRAFT')
        ], string= 'Done By')
    company_address = fields.Many2one('res.company',string="Company")
    total_no_of_products = fields.Integer(string="Total No of Products",readonly=1)
    proportionate_amount_to_products = fields.Float(string="Proportionate Amount to Products")
    freight_charges = fields.Float(string="Freight Charges")
    loading_and_packing_charges = fields.Float(string="Loading and Packing Charges")
    insurance_charges = fields.Float(string="Insurance Charges")
    other_charges =  fields.Float(string="Other Charges")
    all_additional_charges = fields.Float(string="All Additional Charges",readonly=1)
    total_amount_before_tax = fields.Float(string="Untaxed Amount",readonly=1)
    total_cgst_amount = fields.Float(string="CGST Amount",readonly=1)
    total_sgst_amount = fields.Float(string="SGST Amount",readonly=1)
    total_igst_amount = fields.Float(string="IGST Amount",readonly=1)
    total_gst_amount = fields.Float(string="Total GST",readonly=1)  
    total_amount_after_tax = fields.Float(string="Total",readonly=1)
    grand_total= fields.Float(string='Grand Total',digits=(6,3),readonly=1)
    grand_total_in_words= fields.Text(compute= '_get_total_in_words',string='Total in words')    
    type_of_gst = fields.Selection([
        ('cgst_sgst','CGST/SGST'),('igst','IGST')],default='cgst_sgst',string='Type Of GST')    
    total_amount = fields.Float(string="Total Amount",readonly=1)
    total_gst_in_words= fields.Text(compute= '_get_total_gst_in_words',string='Total GST in words')
    total_taxable_value= fields.Float(string='Total Taxable Value',digits=(6,3),readonly=1)
    revise_status = fields.Selection([('revise_order','Revise Order'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    revised_by=fields.Many2one('res.users',string='Revised By')
    short_close_remarks = fields.Text(string="Remarks For Short Close")
    revision_no = fields.Char(' Rev No')  
    
    po_no= fields.Char(string='P.O No')    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'quotation_no':'Direct Order',
        'order_no':'New',
        'order_id': lambda s, cr, uid, c:uid,
        'revise_id': lambda s, cr, uid, c:uid   
        }
    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete'))
        return super(PrakrutiSalesOrder, self).unlink() 
    
    '''
    If we select advance payment is "No" then payment type is invisible automatically
    '''
    @api.onchange('any_adv_payment')
    def onchange_any_adv_payment(self):
        if self.any_adv_payment == 'no':
            self.advance_payment_type = None
    
    @api.onchange('advance_payment_type')
    def onchange_advance_payment_type(self):
        if self.advance_payment_type == 'cash':
            self.cheque_amount = 0
            self.cheque_no = 0
            self.cheque_remarks = ''
            self.draft_amount = 0
            self.draft_no = 0
            self.draft_remarks = ''
        if self.advance_payment_type == 'cheque':
            self.cash_amount = 0
            self.cash_remarks = ''
            self.draft_amount = 0
            self.draft_no = 0
            self.draft_remarks = ''
        if self.advance_payment_type == 'demand_draft':
            self.cash_amount = 0
            self.cash_remarks = ''
            self.cheque_amount = 0
            self.cheque_no = 0
            self.cheque_remarks = ''
        else:
            self.cash_amount = 0
            self.cash_remarks = ''
            self.cheque_amount = 0
            self.cheque_no = 0
            self.cheque_remarks = ''
            self.draft_amount = 0
            self.draft_no = 0
            self.draft_remarks = ''
    '''
    Negative Value Validation
    '''
    @api.one
    @api.constrains('draft_amount')
    def _check_draft_amount(self):
        if self.draft_amount < 0:
            raise ValidationError(
                "Draft Amount !!! Can't be Negative") 
    
    '''
    Negative Value Validation
    '''
    @api.one
    @api.constrains('cash_amount')
    def _check_cash_amount(self):
        if self.cash_amount < 0:
            raise ValidationError(
                "Cash Amount !!! Can't be Negative") 
    
    '''
    Negative Value Validation
    '''
    @api.one
    @api.constrains('cheque_amount')
    def _check_cheque_amount(self):
        if self.cheque_amount < 0:
            raise ValidationError(
                "Check Amount !!! Can't be Negative")  
   
   
    '''
    Negative Value Validation
    '''     
    @api.one
    @api.constrains('order_date')
    def _check_order_date(self):
        if self.order_date < fields.Date.today():
            raise ValidationError(
                "Order Date can't be less than current date!")
        
    '''
    Prints Total Gst in words
    '''
    @api.depends('total_gst_amount','total_cgst_amount','total_sgst_amount','total_igst_amount')
    def _get_total_gst_in_words(self):
        for order in self:
            total_gst_amount = val1 = 0.0
            val1_in_words = ""
            val1 = order.total_gst_amount
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            order.update({                    
                'total_gst_in_words': val1_in_words.upper()
                })
    '''
    Prints Grand Total in words
    '''
    @api.depends('grand_total')
    def _get_total_in_words(self):
        for order in self:
            val1 = 0.0
            val1_in_words = ""
            val1 = order.grand_total
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            order.update({
                'grand_total_in_words': val1_in_words.upper()
                })
    '''
    While Clicking this button calculation part will calculate Automatically
    '''
    @api.one
    @api.multi
    def calculate_total(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute(''' SELECT calculation_update_sales_order_gst(%s)''',((temp.id),)) #Database Function calculation_update_sales_order_gst
        return {} 
    
    '''
    Pulls the Data to Production SLip Screen
    '''
    @api.one
    @api.multi 
    def order_to_slip(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context' 
        error_message = ''
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            for line in temp.grid_id:
                cr.execute("SELECT prakruti_sales_order_item.unit_price,prakruti_sales_order_item.sale_price FROM public.prakruti_sales_order, public.prakruti_sales_order_item WHERE prakruti_sales_order.id = prakruti_sales_order_item.main_id AND prakruti_sales_order_item.product_id = CAST(%s AS INTEGER) AND prakruti_sales_order.id = CAST(%s AS INTEGER)", ((line.product_id.id),(temp.id),))
                for item in cr.dictfetchall():
                    unit_price = item['unit_price']
                    sale_price = item['sale_price']
                if unit_price < sale_price:
                    raise UserError(_('Your Entered Sales Price is %s for the Product [ %s ] which is not equal to the Minimum Sales Price i.e. %s') %(unit_price,line.product_id.name_template,sale_price))
            if temp.any_adv_payment == 'yes':
                if not(temp.cash_amount or temp.draft_amount or temp.cheque_amount):
                    raise UserError (_('Please Enter Adv. Payment Details'))
            cr.execute('''SELECT sales_order_to_production_slip AS error_message FROM sales_order_to_production_slip(%s,%s,%s,%s)''',((temp.id),(temp.inquiry_no),(temp.quotation_no),(temp.order_no),))
            for line in cr.dictfetchall():
                error_message = line['error_message']
            if error_message == 'Please Enter Required Date...':
                raise UserError(_('Please Enter Required Date...'))
            if error_message == 'No Item to give to an Production':
                raise UserError(_('No Item to give to an Production'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales Order')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    '''
    Pulls data to Proforma Invoice Screen
    '''
    @api.one
    @api.multi
    def action_performa_invoice(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_id = self.pool.get('prakruti.sales_proforma_invoice').create(cr,uid, {
                'customer_id':temp.customer_id.id,
                'terms':temp.terms,
                'inquiry_no':temp.inquiry_no,
                'inquiry_date':temp.inquiry_date,
                'quotation_no':temp.quotation_no,
                'quotation_date':temp.quotation_date,
                'shipping_id':temp.shipping_id.id,
                'billing_id':temp.billing_id.id,
                'product_type_id':temp.product_type_id.id,
                'company_address':temp.company_address.id,
                'remarks':temp.remarks,
                'order_date':temp.order_date,
                'order_no':temp.order_no,
                'cash_amount':temp.cash_amount,
                'cash_remarks':temp.cash_remarks,
                'cheque_amount':temp.cheque_amount,
                'cheque_no':temp.cheque_no,
                'cheque_remarks':temp.cheque_remarks,
                'draft_amount':temp.draft_amount,
                'draft_no':temp.draft_no,
                'draft_remarks':temp.draft_remarks,
                'advance_payment_type':temp.advance_payment_type,
                'any_adv_payment':temp.any_adv_payment,
                'total_no_of_products':temp.total_no_of_products,
                'proportionate_amount_to_products':temp.proportionate_amount_to_products,
                'freight_charges':temp.freight_charges,
                'loading_and_packing_charges':temp.loading_and_packing_charges,
                'insurance_charges':temp.insurance_charges,
                'other_charges':temp.other_charges,
                'all_additional_charges':temp.all_additional_charges,
                'total_amount_before_tax':temp.total_amount_before_tax,
                'total_cgst_amount':temp.total_cgst_amount,
                'total_sgst_amount':temp.total_sgst_amount,
                'total_igst_amount':temp.total_igst_amount,
                'total_gst_amount':temp.total_gst_amount,
                'total_amount_after_tax':temp.total_amount_after_tax,
                'total_amount':temp.total_amount,
                'grand_total':temp.grand_total,
                'reference_no':temp.reference_no,
                'reference_date':temp.reference_date,   
                'revision_no':temp.revision_no 
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.sales_proforma_invoice_item').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'quantity': item.quantity,
                    'uom_id': item.uom_id.id,
                    'description':item.description,
                    'specification_id':item.specification_id.id,
                    'unit_price': item.unit_price,
                    'mfg_date':item.mfg_date,
                    'exp_date':item.exp_date,
                    'total':item.total,
                    'scheduled_date':item.scheduled_date,
                    'scheduled_qty':item.scheduled_qty,
                    'req_date':item.req_date,
                    'remarks':item.remarks,
                    'hsn_code': item.hsn_code,
                    'amount': item.amount,
                    'discount_id': item.discount_id.id,
                    'discount': item.discount,
                    'taxable_value': item.taxable_value,
                    'proportionate_amount_to_products':item.proportionate_amount_to_products,
                    'taxable_value_with_charges':item.taxable_value_with_charges,
                    'gst_rate': item.gst_rate,
                    'cgst_id':item.cgst_id.id,
                    'cgst_value': item.cgst_value,
                    'cgst_amount':item.cgst_amount,
                    'sgst_id':item.sgst_id.id,
                    'sgst_value': item.sgst_value,
                    'sgst_amount':item.sgst_amount,
                    'igst_id':item.igst_id.id,
                    'igst_value': item.igst_value,
                    'igst_amount':item.igst_amount,
                    'main_id':ebsl_id
                 })
        return {} 
    
    '''
    When clicking this button the order will be shoer closed and the status is updated , with the same inquiry no again we will raise the order
    '''
    @api.one
    @api.multi 
    def short_close_order(self):        
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.short_close_remarks:
                cr.execute('''SELECT short_close_sales(%s,%s,%s)''', ((temp.id),(temp.inquiry_no),(temp.quotation_no),))
            else:
                raise UserError(_('Please enter remarks for Short Close'))
        return {}       
    
    
    '''
    This Button helps for Revision(If any changes need to be done in prakruti_sales_order_item click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_order(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            #LET US TAKE A BACKUP OF EXISTING ENTRY SO TO KEEP TRACK OF OLDER RECORDS JUST LIKE THE DUPLICATION
            ebsl_id = self.pool.get('prakruti.sales_order').create(cr,uid, {
                'countflag':temp.countflag,
                'order_no':temp.order_no,
                'order_date':temp.order_date,
                'quotation_no':temp.quotation_no,
                'quotation_date':temp.quotation_date,
                'inquiry_no':temp.inquiry_no,
                'inquiry_date':temp.inquiry_date,
                'customer_id':temp.customer_id.id,
                'product_type_id':temp.product_type_id.id,
                'shipping_id':temp.shipping_id.id,
                'billing_id':temp.billing_id.id,
                'company_address':temp.company_address.id,
                'remarks':temp.remarks,
                'terms':temp.terms,
                'balance_line':temp.balance_line,
                'cash_amount':temp.cash_amount,
                'cash_remarks':temp.cash_remarks,
                'cheque_amount':temp.cheque_amount,
                'cheque_no':temp.cheque_no,
                'cheque_remarks':temp.cheque_remarks,
                'draft_amount':temp.draft_amount,
                'draft_no':temp.draft_no,
                'draft_remarks':temp.draft_remarks,
                'amount_flag':temp.amount_flag,
                'slip_no':temp.slip_no,
                'po_no':temp.po_no,
                'requested_id':temp.requested_id.id,
                'quotation_id':temp.quotation_id.id,
                'order_id':temp.order_id.id,
                'reference_no':temp.reference_no,
                'reference_date':temp.reference_date,
                'product_id':temp.product_id.id,
                'state':temp.state,
                'any_adv_payment':temp.any_adv_payment,
                'advance_payment_type':temp.advance_payment_type,
                'ord_no' : temp.ord_no,
                'auto_no' : temp.auto_no,
                'req_no_control_id1' : temp.req_no_control_id1,
                'total_no_of_products':temp.total_no_of_products,
                'proportionate_amount_to_products':temp.proportionate_amount_to_products,
                'freight_charges':temp.freight_charges,
                'loading_and_packing_charges':temp.loading_and_packing_charges,
                'insurance_charges':temp.insurance_charges,
                'other_charges':temp.other_charges,
                'all_additional_charges':temp.all_additional_charges,
                'total_amount_before_tax':temp.total_amount_before_tax,
                'total_cgst_amount':temp.total_cgst_amount,
                'total_sgst_amount':temp.total_sgst_amount,
                'total_igst_amount':temp.total_igst_amount,
                'total_gst_amount':temp.total_gst_amount,
                'total_amount_after_tax':temp.total_amount_after_tax,
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,     
                'short_close_remarks':temp.short_close_remarks,   
                'revision_no':temp.revision_no,           
                'revise_flag': 1
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.sales_order_item').create(cr,uid, {
                    'unit_price':item.unit_price,
                    'total':item.total,
                    'scheduled_date':item.scheduled_date,
                    'scheduled_qty':item.scheduled_qty,
                    'req_date':item.req_date,
                    'balance_qty':item.balance_qty,
                    'dispatched_qty':item.dispatched_qty,
                    'accepted_qty':item.accepted_qty,
                    'status':item.status,
                    'state':item.state,
                    'total_dispatched_qty':item.total_dispatched_qty,
                    'total_scheduled_qty':item.total_scheduled_qty,
                    'previous_scheduled_qty':item.previous_scheduled_qty,
                    'previous_dispatched_qty':item.previous_dispatched_qty,
                    'remaining_dispatched_qty':item.remaining_dispatched_qty,
                    'hsn_code': item.hsn_code,
                    'amount': item.amount,
                    'discount_id': item.discount_id.id,
                    'discount': item.discount,
                    'taxable_value': item.taxable_value,
                    'proportionate_amount_to_products':item.proportionate_amount_to_products,
                    'taxable_value_with_charges':item.taxable_value_with_charges,
                    'gst_rate': item.gst_rate,
                    'cgst_id':item.cgst_id.id,
                    'cgst_value': item.cgst_value,
                    'cgst_amount':item.cgst_amount,
                    'sgst_id':item.sgst_id.id,
                    'sgst_value': item.sgst_value,
                    'sgst_amount':item.sgst_amount,
                    'igst_id':item.igst_id.id,
                    'igst_value': item.igst_value,
                    'igst_amount':item.igst_amount,
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'specification_id': item.specification_id.id,
                    'description': item.description,
                    'remarks': item.remarks,
                    'quantity':item.quantity,
                    'hsn_code': item.hsn_code,
                    'inquiry_line_id':item.inquiry_line_id,
                    'sale_price':item.sale_price,
                    'revise_order_line':item.revise_order_line,
                    'main_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_sales_order SET revise_status = 'revise_order',is_revise = 'True' WHERE id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_sales_order_item SET revise_order_line = 1 WHERE main_id = %s",((temp.id),))
        return {}
    
    
    '''
    After doing changes in prakruti_sales_order_item click this to visible Revise button and to update the changes in the screen
    '''
    
    @api.one
    @api.multi
    def revise_done(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context' 
        revise_done_by = False
        line_id = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            for line in temp.grid_id:
                cr.execute("SELECT prakruti_sales_order_item.unit_price,prakruti_sales_order_item.sale_price FROM public.prakruti_sales_order, public.prakruti_sales_order_item WHERE prakruti_sales_order.id = prakruti_sales_order_item.main_id AND prakruti_sales_order_item.product_id = CAST(%s AS INTEGER) AND prakruti_sales_order.id = CAST(%s AS INTEGER)", ((line.product_id.id),(temp.id),))
                for item in cr.dictfetchall():
                    unit_price = item['unit_price']
                    sale_price = item['sale_price']
                if unit_price < sale_price:
                    raise UserError(_('Your Entered Sales Price is %s for the Product [ %s ] which is not equal to the Minimum Sales Price i.e. %s') %(unit_price,line.product_id.name_template,sale_price))
            if temp.revise_remarks:
                if temp.revise_id:
                    cr.execute("UPDATE prakruti_sales_order_item SET revise_order_line = 2 WHERE main_id = %s",((temp.id),))
                    cr.execute('''SELECT revise_sales_order AS error_message FROM revise_sales_order(%s,%s)''',((temp.id),(temp.inquiry_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record Cannot be Revised':
                        raise UserError(_('Record...Can\'t Be Revised...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 
    
     
    '''
    Rejecting the Order and the status is  updating in inquiry, quotation, order screens
    '''
    @api.one
    @api.multi 
    def action_reject(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            if temp.remarks:
                cr.execute('''SELECT reject_sales_order(%s,%s,%s,%s)''',((temp.id),(temp.customer_id.id),(temp.quotation_no),(temp.inquiry_no),))
            else:
                raise UserError(_('Please Enter Remarks...'))
        return {}
   
    
class PrakrutiSalesOrderItem(models.Model):
    _name = 'prakruti.sales_order_item'
    _table = "prakruti_sales_order_item"
    _description = 'Sales Order Item'
    
    main_id = fields.Many2one('prakruti.sales_order',string="Grid")
    product_id  = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    description = fields.Text(string="Description")
    quantity = fields.Float(string = "Qty",digits=(6,3))
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    remarks = fields.Text(string="Remarks") 
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    scheduled_date = fields.Date('Sch. Date', readonly= True)
    scheduled_qty = fields.Float('Sch. Qty', readonly= True,default=0,digits=(6,3))
    req_date = fields.Date('Required Date')
    balance_qty = fields.Float(string="Balance Qty",digits=(6,3))
    dispatched_qty=fields.Float(string="Dispatch Qty",digits=(6,3))
    accepted_qty=fields.Float(string="Accepted Qty",digits=(6,3))
    status = fields.Selection([
        ('open', 'Open'),
        ('wait','Waiting'),
        ('close','Closed'),
        ('accepted', 'Accepted'),
        ('par_reject', 'Par. Rejected'),
        ('rejected','Rejected'),
        ('accept_under_deviation','Accepted Under Deviation')
        ],default= 'open', string= 'Status')    
    state =fields.Selection([
        ('order','Order'),
        ('slip_request','Production Slip Issued'),
        ('partially_confirmed','Production Slip Partially Confirmed'),
        ('production_slip_confirmed','Production Slip Confirmed'),
        ('partial_order','Partially Dispatched/Confirmed/Invoiced'),
        ('confirm','Dispatched/Confirmed/Invoiced'),
        ('without_qc_partially_confirmed','With out QC Partially Dispatched/Confirmed/Invoiced'),
        ('without_qc_invoice','With out QC Dispatched/Confirmed/Invoiced'),
        ('rejected','Rejected')
        ],default= 'order', string= 'Status')
    total_dispatched_qty=fields.Float(string="Total Dispatch Qty",readonly=True,digits=(6,3),default=0)
    total_scheduled_qty = fields.Float(string="Total Sch Qty",readonly=True,digits=(6,3),default=0)
    previous_scheduled_qty = fields.Float(string="Previous Sch Qty",readonly=True,digits=(6,3),default=0)
    previous_dispatched_qty = fields.Float(string="Previous Dispatch Qty",readonly=True,digits=(6,3),default=0)
    remaining_dispatched_qty = fields.Float(string="Remaining Dispatch Qty",readonly=True,digits=(6,3),default=0)
    total= fields.Float(string='Total',readonly=1)   
    hsn_code = fields.Char(string='HSN/SAC')
    amount = fields.Float(string= 'Amount',readonly=1)
    discount_id = fields.Many2one('account.other.tax',string= 'Discount(%)',domain=[('select_type', '=', 'discount')])
    discount = fields.Float(string= 'Discount(%)',default=0)
    taxable_value = fields.Float(string= 'Taxable Value',readonly=1)
    proportionate_amount_to_products = fields.Float(related='main_id.proportionate_amount_to_products', string="Proportionate Amount to Products",store=1)
    taxable_value_with_charges = fields.Float(string= 'Taxable Value With Charges',readonly=1)
    gst_rate = fields.Float(string= 'GST Rate',readonly=1)    
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_value = fields.Float(related='cgst_id.per_amount',string= 'CGST Value',default=0,store=1)
    cgst_amount = fields.Float(string= 'CGST Amount',readonly=1)    
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_value = fields.Float(related='sgst_id.per_amount',string= 'SGST Value',default=0,store=1)
    sgst_amount = fields.Float(string= 'SGST Amount',readonly=1)    
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_value = fields.Float(related='igst_id.per_amount',string= 'IGST Value',default=0,store=1)
    igst_amount = fields.Float(string= 'IGST Amount',readonly=1)
    inquiry_line_id=fields.Integer(string='Grid id of inquiry')
           
    revise_order_line = fields.Integer(string= 'Revised Flag',default=0)   
    sale_price=fields.Float(string="Sale Minimum Price",digits=(6,3))           
    
    '''
    If  uom id is there for particular product then this will automatically dispalys while selecting that particular product
    '''
    
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        cr.execute('SELECT  product_uom.id AS uom_id,product_uom.name,product_template.name as description,product_template.sale_price as sale_price,product_template.hsn_code as hsn_code FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id=cast(%s as integer)', ((product_id),))
        for values in cr.dictfetchall():
            uom_id = values['uom_id']
            description = values['description']
            sale_price = values['sale_price']
            hsn_code = values['hsn_code']
            return {'value' :{ 'uom_id': uom_id,'description':description,'sale_price':sale_price,'hsn_code':hsn_code }}

    '''
    Validation for Required Date(Can't be less than current date)
    '''
    @api.one
    @api.constrains('req_date')
    def _check_req_date(self):
        if self.req_date < fields.Date.today():
            raise ValidationError(
                "Required Date can't be less than current date!")
    

    '''
    Validation for negative value And 0
    '''
    @api.one
    @api.constrains('unit_price')
    def _check_unit_price(self):
        if self.unit_price <= 0:
            raise ValidationError(
                "Unit Price !!! Can't be Negative OR 0 ")