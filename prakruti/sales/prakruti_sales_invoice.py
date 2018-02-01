'''
Company : EBSL
Author: Induja
Module: Sales Invoice
Class 1: PrakrutiSalesInvoice
Class 2: PrakrutiSalesInvoiceLine
Table 1 & Reference Id: prakruti_sales_invoice ,grid_id
Table 2 & Reference Id: prakruti_sales_invoice_line,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
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
from openerp.tools import amount_to_text
from openerp.tools.amount_to_text import amount_to_text_in 
from openerp.tools.amount_to_text import amount_to_text_in_without_word_rupees
from openerp import models, fields, api,_
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize, image_resize_image_big
from openerp import tools
from datetime import timedelta
from openerp.osv import osv,fields
from openerp import models, fields, api, _
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
#########################################################################################################

class PrakrutiSalesInvoice(models.Model):
    _name = 'prakruti.sales_invoice'
    _table = "prakruti_sales_invoice"
    _description = 'Sales Invoice'
    _order="id desc"
    _rec_name="order_no"
  
    '''Auto genereation function
    'Format: SINV\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SINV\CI\0416\17-18,SINV\EI\455\17-18
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
        for temp in self :
            cr.execute('''SELECT 
                                CAST(EXTRACT (month FROM invoice_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM invoice_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_sales_invoice 
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
            cr.execute('''SELECT autogenerate_sales_invoice(%s)''', ((temp.id),)  ) #Database Function : autogenerate_sales_invoice
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_sales_invoice'];
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
                if record.invoice_type == 'commercial_invoice':
                    style_format[record.id] = 'SINV\\'+'CI-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE prakruti_sales_invoice SET invoice_no =%s WHERE id=%s ''', ((style_format[record.id]),(temp.id),))
                elif record.invoice_type == 'export_invoice':
                    style_format[record.id] = 'SINV\\'+'EI-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE 
                                        prakruti_sales_invoice 
                                  SET 
                                        invoice_no =%s 
                                  WHERE 
                                        id=%s ''', ((style_format[record.id]),(temp.id),))
                else:
                    raise UserError(_('Oops...! Please Select Proper Invoice...'))
        return style_format
    
    
    
    grid_id = fields.One2many('prakruti.sales_invoice_line', 'main_id',string='Grid')
    invoice_type = fields.Selection([
        ('commercial_invoice','Commercial Invoice'),
        ('export_invoice','Export Invoice')
        ], string="Invoice Type", default='commercial_invoice')
    invoice_no = fields.Char('Invoice No:', readonly=True, default='New')
    invoice_date = fields.Date('Invoice Date',default= fields.Date.today)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=True)
    order_date = fields.Date('Order Date.',readonly=True)
    supplier_ref = fields.Char('Buyer/Customer Reference')
    other_ref = fields.Char('Other Referrence')
    customer_id = fields.Many2one ('res.partner',string= 'Customer',readonly=True)
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    dispatch_through = fields.Char(string='Dispatch Through')
    destination = fields.Char(string='Destination')
    terms_delivery = fields.Char('Terms Of Delivery')
    delivery_note= fields.Integer(' Delivery Note')
    delivery_date = fields.Date('Delivery Date')
    terms_payment = fields.Char('Terms Of Payment')
    bl_no = fields.Char('B/L No')
    bl_date = fields.Date('B/L Date')
    vessal_name = fields.Char('Vessal Name')
    country_origin = fields.Char('Country Origin')
    invoice_datetime =fields.Datetime(string='Date and time of issue of invoice')
    goods_datetime =fields.Datetime(string='Date and time of Removal of Goods')
    vehicle_no = fields.Char(string='Motor Vehicle No')
    exporter_datetime =fields.Datetime(string='Exporters Ref Date and time ')
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    order_type = fields.Selection([('with_tarrif','Sales'),('without_tarrif','PS')], string="Order Type", default='without_tarrif')
    company_address = fields.Many2one('res.company',string='Company Address')
    remarks = fields.Text(string="Remarks")
    serial_no = fields.Char(string='Serial No')
    form_to_recieve = fields.Char(string='Form to Recieve')
    excise_declaration = fields.Text(string="Excise declaration")
    inv_no = fields.Char('Order Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    dispatch_no = fields.Char(string='Dispatch No',readonly=True)
    dispatch_date = fields.Date('Dispatch Date',readonly=True)
    vat_tin = fields.Char('Companys VAT TIN')
    buyer_vat_tin = fields.Char('Buyers VAT TIN')
    cst_no = fields.Char('Companys CST No')
    buyer_cst_no = fields.Char('Buyers CST No')
    tax_no = fields.Char('TAX No')
    pan_no = fields.Char('PAN No')
    excise_regn_no = fields.Char('Excise regn No')
    port_of_landing = fields.Char('Port Of landing')
    port_of_discharge = fields.Char('Port Of Discharge')
    bank_details = fields.Char('Bank Details')
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By') 
    return_id =fields.Many2one('res.users','Return By')
    cash_amount = fields.Float(string="Amount",readonly=1,digits=(6,3))
    cash_remarks = fields.Text(string="Remarks",readonly=1)    
    cheque_amount = fields.Float(string="Amount",readonly=1,digits=(6,3))
    cheque_no = fields.Integer(string="Cheque No.",readonly=1)
    cheque_remarks = fields.Text(string="Remarks",readonly=1)    
    draft_amount = fields.Float(string="Amount",readonly=1,digits=(6,3))
    draft_no = fields.Integer(string="Draft No.",readonly=1)
    draft_remarks = fields.Text(string="Remarks",readonly=1) 
    po_no = fields.Char(string='P.O No.')
    slip_no= fields.Char(string='Slip No.',readonly=1)
    reference_no= fields.Char(string='Ref No')
    reference_date= fields.Date(string='Ref Date') 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')
    total_no_of_products = fields.Integer(string="Total No of Products")
    proportionate_amount_to_products = fields.Float(string="Proportionate Amount to Products")
    freight_charges = fields.Float(string="Freight Charges")
    loading_and_packing_charges = fields.Float(string="Loading and Packing Charges")
    insurance_charges = fields.Float(string="Insurance Charges")
    other_charges =  fields.Float(string="Other Charges")
    all_additional_charges = fields.Float(string="All Additional Charges")
    total_amount_before_tax = fields.Float(string="Untaxed Amount")
    total_cgst_amount = fields.Float(string="CGST Amount")
    total_sgst_amount = fields.Float(string="SGST Amount")
    total_igst_amount = fields.Float(string="IGST Amount")
    total_gst_amount = fields.Float(string="Total GST")  
    total_amount_after_tax = fields.Float(string="Total")
    grand_total= fields.Float(string='Grand Total')
    grand_total_in_words= fields.Text(compute= '_get_total_in_words',string='Total in words')
    total_amount = fields.Float(string="Total Amount")
    total_gst_in_words= fields.Text(compute= '_get_total_gst_in_words',string='Total GST in words')
    total_taxable_value = fields.Float(string="Total Taxable Value")     
    batch_line = fields.One2many('prakruti.sales_invoice_batch_list_line', 'sales_invoice_id',string='Batch line')
    type_of_gst = fields.Selection([
        ('cgst_sgst','CGST/SGST'),('igst','IGST')],default='cgst_sgst',string='Type Of GST')
    state =fields.Selection([
            ('inquiry', 'Inquiry'),
            ('quotation','Quotation'),
            ('order','Order'),
            ('partially_confirmed','Partially Invoiced'),
            ('invoice','Invoice'),
            ('gate_pass','Gate Pass'),
            ('return','Returned')
            ],default= 'invoice', string= 'Status')
    any_adv_payment =fields.Selection([
                    ('no', 'No'),
                    ('yes','Yes')
                    ], string= 'Any Advance Payment',readonly=1)
    advance_payment_type =fields.Selection([
                    ('cash', 'CASH'),
                    ('cheque','CHEQUE'),
                    ('demand_draft','DEMAND DRAFT')
                    ], string= 'Any Advance Payment Done By',readonly=1)
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    terms=fields.Text('Terms and conditions')
    reference_date= fields.Date(string='Ref Date')
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')
    
    _defaults = {
        'company_address': _default_company,
        'return_id': lambda s, cr, uid, c:uid
        }    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete...'))
        return super(PrakrutiSalesInvoice, self).unlink()
    
    @api.multi
    def print_local_invoice(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for record in self:
            cr.execute('''UPDATE prakruti_logistics_invoice_tracking SET invoice_generated_flag = 1 WHERE order_no = %s AND dispatch_no =%s AND invoice_no = %s''',((record.order_no.id),(record.dispatch_no),(record.invoice_no),))
        return self.env['report'].get_action(self, 'prakruti.report_prakruti_gst_sales_local_invoice_template')
    
    @api.multi
    def print_export_invoice(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for record in self:
            cr.execute('''UPDATE prakruti_logistics_invoice_tracking SET invoice_generated_flag = 1 WHERE order_no = %s AND dispatch_no =%s AND invoice_no = %s''',((record.order_no.id),(record.dispatch_no),(record.invoice_no),))
        return self.env['report'].get_action(self, 'prakruti.report_prakruti_gst_sales_export_invoice_template')
    
    '''
    Print Total GST in words
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
    Print GRAND TOTAL in words
    '''
    @api.depends('total_amount_after_tax','grand_total')
    def _get_total_in_words(self):
        for order in self:
            grand_total = val1 = 0.0
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
            cr.execute(''' SELECT calculation_update_sales_invoice_gst(%s)''',((temp.id),)) #Database Function calculation_update_sales_invoice_gst
        return {} 
                    
    '''
    Pulls the data to Sales Return Screen,Invoice Tracking screen and Gate pass screens
    '''
    @api.one
    @api.multi 
    def invoice_to_gate_pass(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_idea = self.pool.get('prakruti.gate_pass').create(cr,uid, {
                'order_no':temp.order_no.id,
                'order_date':temp.order_date,
                'invoice_no':temp.invoice_no,
                'invoice_date':temp.invoice_date,
                'customer_id':temp.customer_id.id,
                'dispatch_no':temp.dispatch_no,
                'dispatch_date':temp.dispatch_date,
                'vendor_id':temp.company_address.id,
                'company_id':temp.company_address.id,
                'vehicle_no':temp.vehicle_no,
                'requested_id':temp.requested_id.id,
                'order_id':temp.order_id.id,
                'quotation_id':temp.quotation_id.id,
                'dispatch_id':temp.dispatch_id.id,
                'coming_from':'sales',
                'document_type':'outward',
                'reference_no':temp.reference_no,
                'dc_no_outward_check':'yes',
                'e_way_bill_check':'yes',
                'customer_road_permit':'yes',
                'coa':'yes',
                'job_work_documents':'yes', 
                'terms':temp.terms,
                'remarks':temp.remarks,
                'date':temp.reference_date,
                'rev_no':temp.revision_no
                 })
            for item_line in temp.grid_id:
                erp_idea = self.pool.get('prakruti.gate_pass_line').create(cr,uid, {
                    'product_id':item_line.product_id.id,
                    'uom_id':item_line.uom_id.id,
                    'unit_price': item_line.unit_price,
                    'description': item_line.description,
                    'recieved_qty':item_line.quantity,
                    'packing_details':item_line.packing_details,
                    'quantity':item_line.quantity,
                    'main_id': ebsl_idea
                    })
            cr.execute("UPDATE prakruti_sales_invoice SET state = 'gate_pass' WHERE prakruti_sales_invoice.id = cast(%s as integer)",((temp.id),))
        return {}
                    
    '''
    Pulls the data to Sales Return Screen,Invoice Tracking screen and Gate pass screens
    '''
    @api.one
    @api.multi 
    def invoice_to_return(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_id = self.pool.get('prakruti.sales_return').create(cr,uid, {
                'order_no':temp.order_no.id,
                'order_date':temp.order_date,
                'invoice_no':temp.invoice_no,
                'invoice_date':temp.invoice_date,
                'dispatch_to':temp.customer_id.id,
                'company_id':temp.company_address.id,
                'product_type_id':temp.product_type_id.id,
                'dispatch_id':temp.dispatch_id.id,
                'order_id':temp.order_id.id,
                'quotation_id':temp.quotation_id.id,
                'requested_id':temp.requested_id.id,
                'return_id':temp.return_id.id,
                'return_type':'return_by_customer',
                'reference_no':temp.reference_no,
                'reference_date':temp.reference_date,  
                'terms':temp.terms,
                'remarks':temp.remarks,
                'revision_no':temp.revision_no
                 })
            for item_line in temp.grid_id:
                erp_id = self.pool.get('prakruti.sales_return_items').create(cr,uid, {
                    'product_id':item_line.product_id.id,
                    'uom_id':item_line.uom_id.id,
                    'specification_id':item_line.specification_id.id,
                    'description':item_line.description,
                    'rejected_qty':item_line.quantity,
                    'ordered_qty':item_line.quantity,
                    'unit_price':item_line.unit_price,
                    'batch_no':item_line.batch_no.id,
                    'main_id': ebsl_id
                    })
            ebsl_ida = self.pool.get('prakruti.logistics_invoice_tracking').create(cr,uid, {
                'invoice_no':temp.invoice_no,
                'invoice_date':temp.invoice_date,
                'order_no':temp.order_no.id,
                'order_date':temp.order_date,
                'customer_id':temp.customer_id.id,
                'reference_no':temp.reference_no,
                'dispatch_id':temp.dispatch_id.id,
                'order_id':temp.order_id.id,
                'quotation_id':temp.quotation_id.id,
                'requested_id':temp.requested_id.id,  
                'terms':temp.terms,
                'remarks':temp.remarks,
                'reference_date':temp.reference_date,
                'revision_no':temp.revision_no
                 })
            for item_line in temp.grid_id:
                erp_ida = self.pool.get('prakruti.sales_line_in_logistics').create(cr,uid, {
                    'product_id':item_line.product_id.id,
                    'uom_id':item_line.uom_id.id,
                    'quantity':item_line.quantity,
                    'unit_price': item_line.unit_price,
                    'packing_details': item_line.packing_details,
                    'logistics_line_id': ebsl_ida
                    })
            ebsl_idea = self.pool.get('prakruti.gate_pass').create(cr,uid, {
                'invoice_no':temp.invoice_no,
                'invoice_date':temp.invoice_date,
                'order_no':temp.order_no.id,
                'sales_order_date':temp.order_date,
                'customer_id':temp.customer_id.id,
                'vendor_id':temp.customer_id.id,
                'company_id':temp.company_address.id,
                'coming_from':'sales_return',
                'document_type':'inward',
                'reference_no':temp.reference_no,  
                'terms':temp.terms,
                'remarks':temp.remarks,
                'reference_date':temp.reference_date,
                'revision_no':temp.revision_no
                 })
            for item_line in temp.grid_id:
                erp_idea = self.pool.get('prakruti.gate_pass_line').create(cr,uid, {
                    'product_id':item_line.product_id.id,
                    'uom_id':item_line.uom_id.id,
                    'unit_price': item_line.unit_price,
                    'description': item_line.description,
                    'recieved_qty':item_line.quantity,
                    'quantity':item_line.quantity,
                    'main_id': ebsl_idea
                    })
            cr.execute("UPDATE prakruti_sales_invoice SET state = 'return' WHERE prakruti_sales_invoice.id = cast(%s as integer)",((temp.id),))
        return {}
    
class PrakrutiSalesInvoiceLine(models.Model):
    _name = 'prakruti.sales_invoice_line'
    _table = "prakruti_sales_invoice_line" 
    _description = 'Sales Invoice Line'
    
    main_id = fields.Many2one('prakruti.sales_invoice',string="Grid")
    product_id  = fields.Many2one('product.product', string="Product Name",required=True)
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    description = fields.Text(string="Description")
    external_reference = fields.Text(string="External Reference")
    quantity = fields.Float(string = "Qty",digits=(6,3))
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    mrp=fields.Float(string="MRP",digits=(6,3))
    remarks = fields.Text(string="Remarks") 
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    packing_style = fields.Float('Packing Style',digits=(6,3))
    no_of_packings = fields.Float('Packing Per Qty',digits=(6,3))
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0,digits=(6,3))
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')
    packing_details = fields.Char('Packing Details')
    total = fields.Float(string='Total')  
    hsn_code = fields.Char(string='HSN/SAC')
    amount = fields.Float(string= 'Amount')
    discount_id = fields.Many2one('account.other.tax',string= 'Discount(%)',domain=[('select_type', '=', 'discount')])
    discount = fields.Float(string= 'Discount(%)',default=0)
    taxable_value = fields.Float(string= 'Taxable Value')
    proportionate_amount_to_products = fields.Float(related='main_id.proportionate_amount_to_products', string="Proportionate Amount to Products",store=1)
    taxable_value_with_charges = fields.Float(string= 'Taxable Value With Charges')
    gst_rate = fields.Float(string= 'GST Rate')    
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_value = fields.Float(related='cgst_id.per_amount',string= 'CGST Value',default=0,store=1)
    cgst_amount = fields.Float(string= 'CGST Amount')    
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_value = fields.Float(related='sgst_id.per_amount',string= 'SGST Value',default=0,store=1)
    sgst_amount = fields.Float(string= 'SGST Amount')    
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_value = fields.Float(related='igst_id.per_amount',string= 'IGST Value',default=0,store=1)
    igst_amount = fields.Float(string= 'IGST Amount')
    batch_list = fields.Text(string= 'Batches',readonly=1)
    batch_wise_dispatch = fields.Text(string= 'Batch Wise Dispatch',readonly=1)
    status = fields.Selection([
		('accepted', 'Accepted'),
		('par_reject', 'Par. Rejected'),
		('rejected','Rejected')
		], string= 'Status')  
    
    '''
    MRP can't be -ve or 0
    '''
    @api.one
    @api.constrains('mrp')
    def _check_mrp(self):
        if self.mrp < 0:
            raise ValidationError(
                "MRP !!! Can't be Negative or 0")

    '''
    Unit price can't be -ve or 0
    '''
    @api.one
    @api.constrains('unit_price')
    def _check_unit_price(self):
        if self.unit_price <= 0:
            raise ValidationError(
                "Unit Price !!! Can't be Negative or 0")
    
class PrakrutiSalesInvoiceBatchListLine(models.Model):
    _name = 'prakruti.sales_invoice_batch_list_line'
    _table = 'prakruti_sales_invoice_batch_list_line'
    _description = 'Sales Invoice Batch Line'
    
    _sql_constraints = [        
        ('unique_batch_sales_invoice','unique(batch_no, sales_invoice_id)', 'Please Check There Might Be Some Batch No Which Is Already Entered...')
        ]
    
    sales_invoice_id = fields.Many2one('prakruti.sales_invoice',string="Sales Invoice ID")
    product_id  = fields.Many2one('product.product', string="Product Name",readonly=1,required=1)
    dispatched_qty = fields.Float('Dispatch Qty',digits=(6,3),readonly=1)
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No',readonly=1)
    packing_details= fields.Char('Packing Details',readonly=1)
    batch_size= fields.Float('Batch Size',readonly=1)
    batch_qty=fields.Float('Batch Qty',readonly=1)
    remarks = fields.Text(string="Remarks")