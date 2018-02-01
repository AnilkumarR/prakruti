'''
Company : EBSL
Author: Induja
Module: Sales Quotation
Class 1: PrakrutiSalesQuotation
Class 2: PrakrutiSalesQuotationLine
Table 1 & Reference Id: prakruti_sales_quotation ,grid_id
Table 2 & Reference Id: prakruti_sales_quotation_line,main_id
Updated By: Induja
Updated Date & Version: 20170822 ,0.1
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
#########################################################################################################

class PrakrutiSalesQuotation(models.Model):
    _name = 'prakruti.sales_quotation'
    _table = 'prakruti_sales_quotation'
    _description = 'Sales Quotation '
    _order= "id desc"
    _rec_name= "quotation_no"  
    
  
    '''Auto genereation function
    'Format: SQ\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SQ\EXFG\0262\17-18
    Updated By : Induja
    Updated On : 20170822
    Version :0.1
    '''
    @api.one
    @api.multi
    def _get_automatic_no(self):
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
                                CAST(EXTRACT (month FROM quotation_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM quotation_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_sales_quotation 
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
                        
                cr.execute('''select autogenerate_sales_quotation(%s)''', ((temp.id),)  ) #Database Function autogenerate_sales_quotation
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_sales_quotation'];
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
                        style_format[record.id] = 'SQ\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:                        
                        style_format[record.id] = 'SQ\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE 
                                        prakruti_sales_quotation 
                                  SET 
                                        quotation_no =%s 
                                  WHERE
                                        id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
          
    
    grid_id = fields.One2many('prakruti.sales_quotation_line', 'main_id',string='Grid')
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    inquiry_no = fields.Char(' Inquiry No',readonly=True)
    inquiry_date= fields.Date('Inquiry Date')
    customer_id = fields.Many2one('res.partner',string="Customer", required=True)
    quotation_date = fields.Date (string='Quotation Date', default= fields.Date.today)
    quotation_no = fields.Char(string='Quotation No', readonly=True)
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    remarks = fields.Text(string="Remarks")
    qo_no = fields.Char('Quotation Number', compute='_get_automatic_no')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    terms = fields.Text(string='Terms & Conditions')
    remarks = fields.Text(string='Remarks')
    requested_id =fields.Many2one('res.users','Requested By',readonly=True)
    quotation_id =fields.Many2one('res.users','Quotation By')
    reference_no= fields.Char(string='Ref No')
    reference_date= fields.Date(string='Ref Date') 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')
    state =fields.Selection([
                    ('quotation','Sales Quotation Draft'),
                    ('order','Sales Order'),
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
                    ],default= 'quotation', string= 'Status')
    company_address = fields.Many2one('res.company',string="Company")   
    total_no_of_products = fields.Integer(string="Total No of Products",compute= '_compute_total_no_of_products')
    proportionate_amount_to_products = fields.Float(string="Proportionate Amount to Products",compute= '_compute_proportionate_amount_to_products')
    freight_charges = fields.Float(string="Freight Charges")
    loading_and_packing_charges = fields.Float(string="Loading and Packing Charges")
    insurance_charges = fields.Float(string="Insurance Charges")
    other_charges =  fields.Float(string="Other Charges")
    all_additional_charges = fields.Float(string="All Additional Charges",compute= '_compute_all_additional_charges')
    total_amount_before_tax = fields.Float(string="Untaxed Amount",compute= '_compute_total_amount_before_tax')
    total_cgst_amount = fields.Float(string="CGST Amount",compute= '_compute_total_cgst_amount')
    total_sgst_amount = fields.Float(string="SGST Amount",compute= '_compute_total_sgst_amount')
    total_igst_amount = fields.Float(string="IGST Amount",compute= '_compute_total_igst_amount')
    total_gst_amount = fields.Float(string="Total GST",compute= '_compute_total_gst_amount')  
    total_amount_after_tax = fields.Float(string="Grand Total",compute= '_compute_total_amount_after_tax')
    grand_total_in_words= fields.Text(compute= '_get_total_in_words',string='Total in words')
    type_of_gst = fields.Selection([
        ('cgst_sgst','CGST/SGST'),('igst','IGST')],default='cgst_sgst',string='Type Of GST')    
    total_amount = fields.Float(string="Total Amount",compute= '_compute_total_amount')
    total_gst_in_words= fields.Text(compute= '_get_total_gst_in_words',string='Total GST in words')
    total_taxable_value = fields.Float(string="Total Taxable Value",compute= '_compute_total_taxable_value') 
    revise_status = fields.Selection([('revise_quotation','Revise Quotation'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    revision_no = fields.Char(' Rev No')
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'inquiry_no':'Direct Quotation',
        'quotation_no':'New',
        'quotation_id': lambda s, cr, uid, c:uid,
        'indent_disable_id':1,
        'revise_id': lambda s, cr, uid, c:uid   
        }
    
    '''
    Cannot able to delete this record if state is in quotation,order and rejected
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['quotation','order','rejected']:
                raise UserError(_('Can\'t Delete, Since the Quotation went for further Process.'))
        return super(PrakrutiSalesQuotation, self).unlink() 
    
    
    
    
    '''
    This will helps to pull the data to Order screen and this will create new record in Order screen
    ''' 
    
    
    @api.one
    @api.multi
    def action_to_order(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            type_of_gst = ''
            for line in temp.grid_id:
                cr.execute("SELECT prakruti_sales_quotation_line.unit_price,prakruti_sales_quotation_line.sale_price , prakruti_sales_quotation_line.actual_unit_price FROM public.prakruti_sales_quotation, public.prakruti_sales_quotation_line WHERE prakruti_sales_quotation.id = prakruti_sales_quotation_line.main_id AND prakruti_sales_quotation_line.product_id = CAST(%s AS INTEGER) AND prakruti_sales_quotation.id = CAST(%s AS INTEGER)", ((line.product_id.id),(temp.id),))
                for item in cr.dictfetchall():
                    unit_price = item['unit_price']
                    sale_price = item['sale_price']
                    actual_unit_price = item['actual_unit_price']
                if unit_price < sale_price:
                    raise UserError(_('Your Entered Sales Price is %s for the Product [ %s ] which is not equal to the Minimum Sales Price i.e. %s') %(unit_price,line.product_id.name_template,sale_price))
            cr.execute("SELECT unit_price FROM prakruti_sales_quotation_line WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                unit_price = line['unit_price']
            cr.execute("SELECT prakruti_sales_quotation.type_of_gst as type_of_gst,cgst_value,sgst_value,igst_value FROM prakruti_sales_quotation_line INNER JOIN prakruti_sales_quotation ON prakruti_sales_quotation_line.main_id = prakruti_sales_quotation.id WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                type_of_gst = line['type_of_gst']
                cgst_value = line['cgst_value']
                sgst_value = line['sgst_value']
                igst_value = line['igst_value']
                if type_of_gst == 'cgst_sgst':
                    if cgst_value:
                        if not sgst_value:
                            raise UserError(_('Please Enter Equal Tax for SGST Also'))
                    if sgst_value:
                        if not cgst_value: 
                            raise UserError(_('Please Enter Equal Tax for CGST Also'))               
                    if (cgst_value + sgst_value) in [0,5,12,18,28]:
                        if igst_value:
                            raise UserError(_('You are not supposed to enter IGST details'))
                        if cgst_value:
                            if not sgst_value:
                                raise UserError(_('Please Enter Equal Tax for SGST Also'))
                        if sgst_value:
                            if not cgst_value:
                                raise UserError(_('Please Enter Equal Tax for CGST Also'))
                    else:
                        raise UserError(_('Please Enter Proper Tax Details'))
                elif type_of_gst == 'igst':
                    if cgst_value:
                        raise UserError(_('Sorry You are not supposed to enter CGST Details'))
                    if sgst_value:
                        raise UserError(_('Sorry You are not supposed to enter SGST Details'))
                    if (igst_value) not in [0,5,12,18,28]:
                        raise UserError(_('Please Enter Proper Tax Details'))
                else:
                    raise UserError(_('Sorry Please Select GST TYPE'))
            if unit_price != 0:
                sales_order = self.pool.get('prakruti.sales_order').create(cr,uid, {
                    'customer_id':temp.customer_id.id,
                    'terms':temp.terms,
                    'requested_id':temp.requested_id.id,
                    'quotation_id':temp.quotation_id.id,
                    'inquiry_no':temp.inquiry_no,
                    'inquiry_date':temp.inquiry_date,
                    'quotation_no':temp.quotation_no,
                    'quotation_date':temp.quotation_date,
                    'shipping_id':temp.shipping_id.id,
                    'billing_id':temp.billing_id.id,
                    'company_address':temp.company_address.id,
                    'product_type_id':temp.product_type_id.id,
                    'remarks':temp.remarks,
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
                    'reference_no':temp.reference_no,  
                    'revision_no':temp.revision_no,
                    'reference_date':temp.reference_date     
                    })
                for item in temp.grid_id:
                    grid_values = self.pool.get('prakruti.sales_order_item').create(cr,uid, {
                        'product_id': item.product_id.id,
                        'quantity': item.quantity,
                        'balance_qty': item.quantity,
                        'uom_id': item.uom_id.id,
                        'description':item.description,
                        'specification_id':item.specification_id.id,
                        'unit_price': item.unit_price,
                        'actual_unit_price':item.actual_unit_price,
                        'total':item.total,
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
                        'sale_price':item.sale_price,
                        'inquiry_line_id':item.inquiry_line_id,
                        'main_id':sales_order
                    })
                cr.execute("UPDATE  prakruti_sales_quotation SET state = 'order' WHERE prakruti_sales_quotation.id = cast(%s as integer)",((temp.id),))
                cr.execute("UPDATE  prakruti_sales_inquiry SET state = 'order' WHERE prakruti_sales_inquiry.inquiry_no = %s",((temp.inquiry_no),))
            else:
                raise UserError(_("Unit Price Not Yet Entered"))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales Quotation')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True) 
        return {}
    
    '''
    Total Taxable Calculation
    '''
    @api.depends('grid_id.taxable_value')
    def _compute_total_taxable_value(self):
        for order in self:
            total_taxable_value = line_amount = 0
            for line in order.grid_id:
                line_amount += line.taxable_value
                order.update({
                    'total_taxable_value': line_amount
                    })
    '''
    Total Amount Calculation
    '''
    @api.depends('grid_id.amount','grid_id.unit_price','grid_id.quantity')
    def _compute_total_amount(self):
        for order in self:
            total_amount = line_amount = 0
            for line in order.grid_id:
                line_amount += line.amount
                order.update({
                    'total_amount': line_amount
                    })
    
    '''
    Grand Total Calculation
    '''
    @api.depends('grid_id.total','freight_charges','loading_and_packing_charges','insurance_charges','other_charges')
    def _compute_total_amount_after_tax(self):
        for order in self:
            total_amount_after_tax = line_amount =0
            for line in order.grid_id:
                line_amount += line.total
                order.update({
                    'total_amount_after_tax': line_amount
                    })

    '''
    Grand GST Calculation
    '''
    @api.depends('total_cgst_amount','total_sgst_amount','total_igst_amount')
    def _compute_total_gst_amount(self):
        for order in self:
            total_gst_amount = 0
            order.update({
                'total_gst_amount': order.total_cgst_amount + order.total_sgst_amount + order.total_igst_amount
                })
    
    ''' 
    IGST Amount Calculation
    '''
    @api.depends('grid_id.igst_amount')
    def _compute_total_igst_amount(self):
        for order in self:
            total_igst_amount = t_igst_amount =0
            for line in order.grid_id:
                t_igst_amount += line.igst_amount
                order.update({
                    'total_igst_amount': t_igst_amount
                    })
    
    ''' 
    SGST Amount Calculation
    '''
    @api.depends('grid_id.sgst_amount')
    def _compute_total_sgst_amount(self):
        for order in self:
            total_sgst_amount = t_sgst_amount =0
            for line in order.grid_id:
                t_sgst_amount += line.sgst_amount
                order.update({
                    'total_sgst_amount': t_sgst_amount
                    })
    
    '''
    CGST Amount Calculation
    '''
    @api.depends('grid_id.cgst_amount')
    def _compute_total_cgst_amount(self):
        for order in self:
            total_cgst_amount = t_cgst_amount = 0
            for line in order.grid_id:
                t_cgst_amount += line.cgst_amount
                order.update({
                    'total_cgst_amount': t_cgst_amount
                    })
    
    '''
    Untaxed Amount Calculation
    '''
    @api.depends('grid_id.taxable_value_with_charges')
    def _compute_total_amount_before_tax(self):
        for order in self:
            total_amount_before_tax = taxed_value_with_charges =0
            for line in order.grid_id:
                taxed_value_with_charges += line.taxable_value_with_charges
                order.update({
                    'total_amount_before_tax': taxed_value_with_charges
                    })
    
    '''
    Total No of Products Calculation
    '''
    @api.depends('grid_id.quantity')
    def _compute_total_no_of_products(self):
        for order in self:
            total_no_of_products = no_of_qty = 0
            for line in order.grid_id:
                no_of_qty += line.quantity
                order.update({
                    'total_no_of_products': no_of_qty
                    })
    '''
    All Additional Charges Calculation
    '''
    @api.depends('freight_charges', 'loading_and_packing_charges','insurance_charges', 'other_charges')
    def _compute_all_additional_charges(self):
        for order in self:
            all_additional_charges = 0.0            
            order.update({                
                'all_additional_charges': order.freight_charges + order.loading_and_packing_charges + order.insurance_charges + order.other_charges
            })
    '''
    Proportionate Amount to Products Calculation
    '''
    @api.depends('freight_charges', 'loading_and_packing_charges','insurance_charges', 'other_charges','total_taxable_value')
    def _compute_proportionate_amount_to_products(self):
        for order in self:
            proportionate_amount_to_products = 0.0
            if order.total_taxable_value == 0:
                order.update({  
                    'proportionate_amount_to_products': 0
                    })
            else:
                order.update({
                    'proportionate_amount_to_products': order.all_additional_charges/order.total_taxable_value
                    })
                
                
    '''
    Prints Total GST in Words
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
    Prints Grand Total in Words 
    '''
    @api.depends('total_amount_after_tax')
    def _get_total_in_words(self):
        for order in self:
            total_amount_after_tax = val1 = 0.0
            val1_in_words = ""
            val1 = order.total_amount_after_tax
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            order.update({                    
                'grand_total_in_words': val1_in_words.upper()
                })
    
    
    
    '''
    This Button helps for Revision(If any changes need to be done in table 2 click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_quotation(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ebsl_id = self.pool.get('prakruti.sales_quotation').create(cr,uid, {
                'customer_id':temp.customer_id.id,
                'terms':temp.terms,
                'requested_id':temp.requested_id.id,
                'quotation_id':temp.quotation_id.id,
                'inquiry_no':temp.inquiry_no,
                'inquiry_date':temp.inquiry_date,
                'quotation_no':temp.quotation_no,
                'quotation_date':temp.quotation_date,
                'shipping_id':temp.shipping_id.id,
                'billing_id':temp.billing_id.id,
                'company_address':temp.company_address.id,
                'product_type_id':temp.product_type_id.id,
                'remarks':temp.remarks,
                'total_no_of_products':temp.total_no_of_products,
                'proportionate_amount_to_products':temp.proportionate_amount_to_products,
                'freight_charges':temp.freight_charges,
                'loading_and_packing_charges':temp.loading_and_packing_charges,
                'insurance_charges':temp.insurance_charges,
                'other_charges':temp.other_charges,
                'all_additional_charges':temp.all_additional_charges,
                'reference_no':temp.reference_no,
                'reference_date':temp.reference_date,
                'revise_status':temp.revise_status,  
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,   
                'revision_no':temp.revision_no,                   
                'revise_flag': 1
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.sales_quotation_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'quantity': item.quantity,
                    'uom_id': item.uom_id.id,
                    'description':item.description,
                    'specification_id':item.specification_id.id,
                    'unit_price': item.unit_price,
                    'actual_unit_price':item.actual_unit_price,
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
                    'inquiry_line_id':item.inquiry_line_id,
                    'revise_quotation_line':item.revise_quotation_line,
                    'main_id':ebsl_id
                    })
            cr.execute("UPDATE prakruti_sales_quotation SET revise_status = 'revise_quotation',is_revise = 'True' WHERE id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_sales_quotation_line SET revise_quotation_line = 1 WHERE main_id = %s",((temp.id),))
        return {}
    
    
    '''
    After doing changes in table 2 click this to visible Revise button and to update the changes in the screen
    '''
    @api.one
    @api.multi
    def revise_done(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context' 
        revise_done_by = False
        error_message = ''
        for temp in self:
            if temp.revise_remarks:
                if temp.revise_id:
                    cr.execute("UPDATE prakruti_sales_quotation_line SET revise_quotation_line = 2 WHERE main_id = %s",((temp.id),))
                    cr.execute('''SELECT revise_sales_quotation AS error_message FROM revise_sales_quotation(%s,%s)''',((temp.id),(temp.inquiry_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record Cannot Be Revised':
                        raise UserError(_('Record...Can\'t Be Revised...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 
        
class PrakrutiSalesQuotationLine(models.Model):
    _name = 'prakruti.sales_quotation_line'
    _table = 'prakruti_sales_quotation_line'
    _description = 'Sales Quotation Line'
    _order= "id desc"
    
    main_id = fields.Many2one('prakruti.sales_quotation',string="Grid")
    product_id  = fields.Many2one('product.product', string="Product Name",required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    description = fields.Text(string="Description")    
    actual_unit_price=fields.Float(string="Actual Unit Price",digits=(6,3))
    quantity = fields.Float(string = "Qty",required=True,digits=(6,3))
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    remarks = fields.Text(string="Remarks")
    total= fields.Float(string='Total',compute= '_compute_total') 
    hsn_code = fields.Char(string='HSN/SAC')
    amount = fields.Float(string= 'Amount',compute= '_compute_amount')
    discount_id = fields.Many2one('account.other.tax',string= 'Discount(%)',domain=[('select_type', '=', 'discount')])
    discount = fields.Float(string= 'Discount(%)',default=0)
    taxable_value = fields.Float(string= 'Taxable Value',compute= '_compute_taxable_value')
    proportionate_amount_to_products = fields.Float(related='main_id.proportionate_amount_to_products', string="Proportionate Amount to Products")
    taxable_value_with_charges = fields.Float(string= 'Taxable Value With Charges',compute= '_compute_taxable_value_with_charges')
    gst_rate = fields.Float(string= 'GST Rate',compute= '_compute_gst_rate')    
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_value = fields.Float(related='cgst_id.per_amount',string= 'CGST Value',default=0,store=1)
    cgst_amount = fields.Float(string= 'CGST Amount',compute= '_compute_cgst_amount')    
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_value = fields.Float(related='sgst_id.per_amount',string= 'SGST Value',default=0,store=1)
    sgst_amount = fields.Float(string= 'SGST Amount',compute= '_compute_sgst_amount')    
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_value = fields.Float(related='igst_id.per_amount',string= 'IGST Value',default=0,store=1)
    igst_amount = fields.Float(string= 'IGST Amount',compute= '_compute_igst_amount')
    inquiry_line_id=fields.Integer(string='Grid id of inquiry')
    
    revise_quotation_line = fields.Integer(string= 'Revised Flag',default=0)    
    sale_price=fields.Float(string="Sale Price",digits=(6,3))          
                
    '''
    If any uom id, description, unit price is there for particular product then this will automatically dispalys while selecting  that particular product
    '''
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        cr.execute('SELECT  product_uom.id AS uom_id,product_uom.name,product_template.name as description,product_template.sale_price as sale_price,product_template.list_price as actual_unit_price,product_template.hsn_code as hsn_code FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id=cast(%s as integer)', ((product_id),))
        for values in cr.dictfetchall():
            uom_id = values['uom_id']
            description = values['description']
            sale_price = values['sale_price']
            actual_unit_price = values['actual_unit_price']
            hsn_code = values['hsn_code']
            return {'value' :{ 'uom_id': uom_id,'description':description,'sale_price':sale_price,'actual_unit_price':actual_unit_price,'hsn_code':hsn_code }}
    
    '''
    Total Calculation
    ''' 
    
    @api.depends('cgst_amount','sgst_amount','igst_amount','taxable_value_with_charges')
    def _compute_total(self):
        for order in self:
            total = 0.0            
            order.update({                
                'total': order.taxable_value_with_charges + order.cgst_amount + order.sgst_amount + order.igst_amount
            })
            
    '''
    IGST Amount Calculation
    '''
    @api.depends('igst_value', 'taxable_value_with_charges')
    def _compute_igst_amount(self):
        for order in self:
            igst_amount = 0.0            
            order.update({                
                'igst_amount': order.taxable_value_with_charges * (order.igst_value/100)
            })
    '''
    SGST Amount Calculation
    '''
    @api.depends('sgst_value', 'taxable_value_with_charges')
    def _compute_sgst_amount(self):
        for order in self:
            sgst_amount = 0.0            
            order.update({                
                'sgst_amount': order.taxable_value_with_charges * (order.sgst_value/100)
            })
    '''
    CGST Amount Calculation
    '''
    @api.depends('cgst_value', 'taxable_value_with_charges')
    def _compute_cgst_amount(self):
        for order in self:
            cgst_amount = 0.0            
            order.update({                
                'cgst_amount': order.taxable_value_with_charges * (order.cgst_value/100)
            })
    
    '''
    GST Rate Calculation
    '''
    @api.depends('cgst_value', 'sgst_value', 'igst_value')
    def _compute_gst_rate(self):
        for order in self:
            gst_rate = 0.0            
            order.update({                
                'gst_rate': order.cgst_value + order.sgst_value + order.igst_value
            })
    '''
    Taxable Value With Charges Calculation
    '''
    @api.depends('taxable_value', 'proportionate_amount_to_products')
    def _compute_taxable_value_with_charges(self):
        for order in self:
            taxable_value_with_charges = 0.0            
            order.update({                
                'taxable_value_with_charges': order.taxable_value +(order.taxable_value * order.proportionate_amount_to_products)
            })
    '''
    amount Calculation
    '''
    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for order in self:
            amount = 0.0            
            order.update({                
                'amount': order.quantity * order.unit_price 
            })
    '''
    Taxable Value Calculation
    '''
    @api.depends('quantity', 'unit_price','amount','discount')
    def _compute_taxable_value(self):
        for order in self:
            taxable_value = 0.0            
            order.update({                
                'taxable_value': order.amount - (order.amount*(order.discount/100)) 
             }) 
                
    '''
    validating Expiry date  (Can't be less than Manufactured date)
    '''
    @api.one
    @api.constrains('exp_date')
    def _check_expiry_date(self):
        if self.exp_date < self.mfg_date:
            raise ValidationError(
                "Expiry Date can't be less than Manufactured date!")
    '''
    Validation for negative values & 0
    '''
    @api.one
    @api.constrains('quantity')
    def _check_quantity(self):
        if self.quantity <= 0:
            raise ValidationError(
                "Quantity !!! Can't be Negative OR 0 ")
    