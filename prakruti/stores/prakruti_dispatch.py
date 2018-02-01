'''
Company : EBSL
Author: Induja
Module: Sales Dispatch
Class 1: PrakrutiDispatch
Class 2: PrakrutiDispatchLine
Table 1 & Reference Id: prakruti_dispatch ,grid_id
Table 2 & Reference Id: prakruti_dispatch_line,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''
# -*- coding: utf-8 -*-
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

class PrakrutiDispatch(models.Model):
    _name = 'prakruti.dispatch'
    _table = 'prakruti_dispatch'
    _description = 'Sales Dispatch'
    _order="id desc"
    _rec_name="dispatch_no"
    
    
  
    '''
    Auto genereation function
    Format: DISP\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: DISP\EXFG\0455\17-18
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
                                CAST(EXTRACT (month FROM dispatch_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM dispatch_date) AS integer) AS year,
                                id
                          FROM 
                                prakruti_dispatch 
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
                        
                cr.execute('''SELECT autogenerate_dispatch(%s)''', ((temp.id),)  ) #Database Function: autogenerate_dispatch
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_dispatch'];
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
                        style_format[record.id] = 'DISP\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:                        
                        style_format[record.id] = 'DISP\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE 
                                    prakruti_dispatch 
                              SET 
                                    dispatch_no =%s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
    

    dispatch_no = fields.Char(string='Dispatch No', default='New')
    dispatch_date = fields.Date('Dispatch Date', default= fields.Date.today)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No')
    order_date = fields.Date('Order Date')
    dispatch_to = fields.Many2one('res.partner', string='Dispatch To')
    dis_no = fields.Char('Dis No', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id1 = fields.Integer('Auto Generating id',default= 0)
    grid_id = fields.One2many('prakruti.dispatch_line', 'main_id',string='Grid')
    company_id = fields.Many2one('res.company',string="Company")
    flag_count_accept = fields.Integer('Accepted Line is There',default= 0)
    flag_count_reject = fields.Integer('Rejected Line is There',default= 0)
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    flag_count_par_reject = fields.Integer('Partial Rejected Line is There')
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    any_partial_line = fields.Integer(string= 'Any Partial Line',default=0)
    vehicle_no = fields.Char(string="Vehicle No.")
    transport_name = fields.Char(string="Name of the Transporter")
    flag_count = fields.Integer('Accepted Line is There',default= 1)
    quotation_no= fields.Char(string='Quotation No' ,readonly=True)
    quotation_date = fields.Date(string='Quotation Date' ,readonly=True)
    inquiry_date= fields.Date('Inquiry Date',readonly=True)
    inquiry_no = fields.Char(' Inquiry No', readonly=True)
    customer_id = fields.Many2one('res.partner',string="Customer")
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    remarks = fields.Text(string="Remarks")
    terms =fields.Text('Terms and conditions')
    countflag = fields.Integer('Flag Line is There',default= 0)
    flag_count_display_product = fields.Integer(default=0)    
    flag_rejected_count = fields.Integer('Flag', default=1)
    any_adv_payment =fields.Selection([
            ('no', 'No'),
            ('yes','Yes')
            ], string= 'Any Advance Payment')
    advance_payment_type =fields.Selection([
            ('cash', 'CASH'),
            ('cheque','CHEQUE'),
            ('demand_draft','DEMAND DRAFT')
            ], string= 'Any Advance Payment Done By')
    state =fields.Selection([
            ('draft','Draft Dispatch'),
            ('sent_to_qc','Quality Check Pending'),          
            ('quality_check_done','Quality Check Done'),
            
            ('partially_confirmed','Order Partially Dispatched/Confirmed/Invoiced '),
            ('invoice','Order Dispatched/Confirmed/Invoiced'),            
                        
            ('extra_partially_confirmed','Extra Order Partially Dispatched/Confirmed/Invoiced'),
            ('extra_invoice','Extra Order Dispatched/Confirmed/Invoiced '),            
                        
            ('done','Rejected')
            ], string= 'Dispatch Status',default= 'draft')
    
    qc_status = fields.Selection([
        ('qc_done','Quality Control Approved'),#QC
        ('qc_ha','Quality Control Higher Approval'),#QC HA
        ('process_qcha_done','Quality Control HA Done'),#QC HA
        ],string = 'QC Status')
    
    qa_status = fields.Selection([
        ('process_qa_done','Quality Assurance Approved'),#QA
        ('process_qa_ha','Quality Assurance HA'),
        ('process_qaha_done','Quality Assurance HA Done'),#QA HA
        ],string = 'QA Status')
    
    
    cash_amount = fields.Float(string="Amount",digits=(6,3))
    cash_remarks = fields.Text(string="Remarks")    
    cheque_amount = fields.Float(string="Amount",digits=(6,3))
    cheque_no = fields.Integer(string="Cheque No.")
    cheque_remarks = fields.Text(string="Remarks")    
    draft_amount = fields.Float(string="Amount",digits=(6,3))
    draft_no = fields.Integer(string="Draft No.")
    draft_remarks = fields.Text(string="Remarks")  
    po_no= fields.Char(string='P.O No')
    slip_no= fields.Char(string='Slip No.',readonly=1)#20170420
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By')
    reference_no= fields.Char(string='Ref No')
    reference_date= fields.Date(string='Ref Date')  
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')  
    reject_flag = fields.Integer(string="Reject Flag",default=0)
    dispatch_flag = fields.Integer(string="Dispatch Flag",default=0)
    qc_check_flag = fields.Integer(string= 'QC Check Done',default=1,readonly=1)
    qa_check_flag = fields.Integer(string= 'QA Check Done',default=1,readonly=1)
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
    total_amount_after_tax = fields.Float(string="Grand Total")
    all_send_to_invoice = fields.Integer(string='All Send To Invoice',default=0,readonly=1)
    coming_from =fields.Selection([
		('qc_check', 'QC'),
		('dispatch', 'Dispatch'),
		], string='Coming From',default='dispatch',readonly=True)    
    batch_line = fields.One2many('prakruti.dispatch_batch_list_line', 'dispatch_id',string='Batch line')
    revision_no = fields.Char(' Rev No')
    #If not BATCH LINE IS EMPTY THEN USER MUST HAVE TO ENTR DOCUMENT NUMBER
    doc_no = fields.Char(' Doc No')
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')
    
    _defaults = {
        'company_id': _default_company, 
        'dispatch_id': lambda s, cr, uid, c:uid
        }
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(_('Can\'t Delete...'))
        return super(PrakrutiDispatch, self).unlink()
    
    '''
    While selecting Order no it will extract data from Order Screen 
    '''    
    def onchange_order_no(self, cr, uid, ids, order_no, context=None):
        process_type = self.pool.get('prakruti.sales_order').browse(cr, uid, order_no, context=context)
        result = {
            'dispatch_to': process_type.customer_id.id,
            'po_no': process_type.po_no,
            'order_date': process_type.order_date,
            'quotation_no': process_type.quotation_no,
            'quotation_date': process_type.quotation_date,
            'inquiry_date': process_type.inquiry_date,
            'inquiry_no': process_type.inquiry_no,
            'shipping_id': process_type.shipping_id.id,
            'billing_id': process_type.billing_id.id,
            'customer_id': process_type.customer_id.id,
            'product_type_id': process_type.product_type_id.id,
            'terms':process_type.terms,
            'cash_amount':process_type.cash_amount,
            'cash_remarks':process_type.cash_remarks,
            'cheque_amount':process_type.cheque_amount,
            'cheque_no':process_type.cheque_no,
            'cheque_remarks':process_type.cheque_remarks,
            'draft_amount':process_type.draft_amount,
            'draft_no':process_type.draft_no,
            'draft_remarks':process_type.draft_remarks,
            'advance_payment_type':process_type.advance_payment_type,
            'any_adv_payment':process_type.any_adv_payment,
            'slip_no':process_type.slip_no,
            'requested_id':process_type.requested_id.id,
            'order_id':process_type.order_id.id,
            'quotation_id':process_type.quotation_id.id,
            'reference_no':process_type.reference_no,
            'reference_date':process_type.reference_date,
            'company_id':process_type.company_address.id,
            'revision_no':process_type.revision_no,
            'total_no_of_products':process_type.total_no_of_products,
            'proportionate_amount_to_products':process_type.proportionate_amount_to_products,
            'freight_charges':process_type.freight_charges,
            'loading_and_packing_charges':process_type.loading_and_packing_charges,
            'insurance_charges':process_type.insurance_charges,
            'other_charges':process_type.other_charges,
            'all_additional_charges':process_type.all_additional_charges,
            'total_amount_before_tax':process_type.total_amount_before_tax,
            'total_cgst_amount':process_type.total_cgst_amount,
            'total_sgst_amount':process_type.total_sgst_amount,
            'total_igst_amount':process_type.total_igst_amount,
            'total_gst_amount':process_type.total_gst_amount,
            'total_amount_after_tax':process_type.total_amount_after_tax,
            'remarks':process_type.remarks,             
            }
        return {'value': result}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_order_no the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''
    
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_order_no(cr, uid, [], vals['order_no'])
        if onchangeResult.get('value') or onchangeResult['value'].get('order_date','dispatch_to','shipping_id','billing_id','product_type_id','terms','inquiry_no','po_no','slip_no','customer_id','reference_no','reference_date','company_id','revision_no','order_id','quotation_id','requested_id','remarks'):
            vals['order_date'] = onchangeResult['value']['order_date']
            vals['dispatch_to'] = onchangeResult['value']['dispatch_to']
            vals['shipping_id'] = onchangeResult['value']['shipping_id']
            vals['billing_id'] = onchangeResult['value']['billing_id']
            vals['product_type_id'] = onchangeResult['value']['product_type_id']
            vals['terms'] = onchangeResult['value']['terms']
            vals['inquiry_no'] = onchangeResult['value']['inquiry_no']
            vals['po_no'] = onchangeResult['value']['po_no']
            vals['slip_no'] = onchangeResult['value']['slip_no']
            vals['customer_id'] = onchangeResult['value']['customer_id']
            vals['reference_no'] = onchangeResult['value']['reference_no']
            vals['reference_date'] = onchangeResult['value']['reference_date']
            vals['company_id'] = onchangeResult['value']['company_id']
            vals['revision_no'] = onchangeResult['value']['revision_no']
            vals['order_id'] = onchangeResult['value']['order_id']
            vals['quotation_id'] = onchangeResult['value']['quotation_id']
            vals['requested_id'] = onchangeResult['value']['requested_id']
            vals['remarks'] = onchangeResult['value']['remarks']
        return super(PrakrutiDispatch, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiDispatch, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.order_no.id
        onchangeResult = self.onchange_order_no(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('order_date','dispatch_to','shipping_id','billing_id','product_type_id','terms','inquiry_no','po_no','slip_no','customer_id','reference_no','reference_date','company_id','revision_no','order_id','quotation_id','requested_id','remarks'):
            vals['order_date'] = onchangeResult['value']['order_date']
            vals['dispatch_to'] = onchangeResult['value']['dispatch_to']
            vals['shipping_id'] = onchangeResult['value']['shipping_id']
            vals['billing_id'] = onchangeResult['value']['billing_id']
            vals['product_type_id'] = onchangeResult['value']['product_type_id']
            vals['terms'] = onchangeResult['value']['terms']
            vals['inquiry_no'] = onchangeResult['value']['inquiry_no']
            vals['po_no'] = onchangeResult['value']['po_no']
            vals['slip_no'] = onchangeResult['value']['slip_no']
            vals['customer_id'] = onchangeResult['value']['customer_id']
            vals['reference_no'] = onchangeResult['value']['reference_no']
            vals['reference_date'] = onchangeResult['value']['reference_date']
            vals['company_id'] = onchangeResult['value']['company_id']
            vals['revision_no'] = onchangeResult['value']['revision_no']
            vals['order_id'] = onchangeResult['value']['order_id']
            vals['quotation_id'] = onchangeResult['value']['quotation_id']
            vals['requested_id'] = onchangeResult['value']['requested_id']
            vals['remarks'] = onchangeResult['value']['remarks']
        return super(PrakrutiDispatch, self).write(cr, uid, ids, vals, context=context)
    '''
    To list out the products after selcting order no in prakruti_dispatch_line
    '''
    @api.one
    @api.multi
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''SELECT sales_dispatch_list_products(%s,%s)''',((temp.order_no.id),(temp.id),))
        return {}
    
    '''
    To delete the products  in prakruti_dispatch_line
    '''       
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''  DELETE FROM 
                                prakruti_dispatch_line 
                            WHERE 
                                prakruti_dispatch_line.main_id =%s''',((temp.id),))
            cr.execute('''  UPDATE  
                                prakruti_dispatch 
                            SET 
                                flag_count =1 
                            WHERE 
                                prakruti_dispatch.id =%s''',((temp.id),))
            cr.execute('''  UPDATE  
                                prakruti_dispatch 
                            SET 
                                flag_count_display_product = 0 
                            WHERE 
                                prakruti_dispatch.id = %s''',((temp.id),))
        return {}
    '''
    this button helps to update the stock in prakruti_dispatch_line
    '''
    @api.one
    @api.multi
    def check_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
                cr.execute('''  UPDATE 
                                    prakruti_dispatch_line 
                                SET 
                                    store_qty= qty_aval 
                                FROM ( 
                                    SELECT 
                                        product_id,
                                        sum(product_qty) as qty_aval,
                                        id 
                                    FROM ( 
                                        SELECT 
                                            prakruti_stock.product_id, 
                                            prakruti_stock.product_qty,
                                            main_id,
                                            prakruti_dispatch_line.id 
                                        FROM 
                                            product_template INNER JOIN 
                                            product_product  ON 
                                            product_product.product_tmpl_id = product_template.id INNER JOIN 
                                            prakruti_stock ON 
                                            prakruti_stock.product_id = product_product.id INNER JOIN 
                                            prakruti_dispatch_line ON 
                                            prakruti_dispatch_line.product_id = prakruti_stock.product_id    
                                        WHERE 
                                            prakruti_dispatch_line.main_id = %s
                                        )as a 
                                        GROUP BY product_id,id
                                    ) as b 
                                WHERE 
                                    b.id = prakruti_dispatch_line.id''',((temp.id),))# Database function :stock_sales_dispatch
        return {}
    
    '''
   Pulls data to QC & QA Screens
    '''
    @api.one
    @api.multi 
    def dispatch_to_qc(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            if len(temp.grid_id) != 0 :
                cr.execute('''SELECT sales_dispatch_to_qc AS error_message FROM sales_dispatch_to_qc(%s,%s)''',((temp.id),(temp.dispatch_no),))
                for message in cr.dictfetchall():
                    error_message = message['error_message']
                if error_message == 'Please select the Status as Dispatch... Click Check Stock':
                    raise UserError(_('Please select the Status as Dispatch... \nClick Check Stock'))
                elif error_message == 'Not Enough Stock (OR)... No Any Products To Send For Further Process':
                    raise UserError(_('Not Enough Stock (OR)... \nNo Any Products To Send For Further Process'))
            else:
                raise UserError(_('Please select the Order No. and list out the Products...'))
        return {}
    
   

    '''
    This button helps to dispatch the product and the stock will deduct after clicking this button & pulls the data to Sales invoice,Gate Pass, invoice tracking screens
    '''
    @api.one
    @api.multi
    def UpdateDispatchStock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        extra_quantity_line = 0
        for temp in self:
            if temp.qa_status in ['process_qa_done','process_qaha_done']:
                for item in temp.grid_id:
                    if item.status in ['rejected']:
                        temp.flag_count_reject = 1
                    elif item.status in ['accepted','accept_under_deviation']:
                        temp.flag_count_accept = 1
                    elif item.status in ['par_reject']:
                        temp.flag_count_par_reject = 1
                #CONVERSION FROM GRAM TO KG
                cr.execute('''  SELECT 
                                    product_uom.id AS uom_id,
                                    product_uom.name AS uom_name,
                                    prakruti_dispatch_line.uom_id AS current_uom_id
                                FROM
                                    product_uom JOIN
                                    prakruti_dispatch_line ON
                                    prakruti_dispatch_line.uom_id = product_uom.id
                                WHERE
                                    prakruti_dispatch_line.main_id = %s
                                    ''',((temp.id),))
                for val in cr.dictfetchall():
                    uom_id = val['uom_id']
                    uom_name = val['uom_name']
                    current_uom_id = val['current_uom_id']
                    print 'UOM ID',uom_id
                    print 'UOM NAME',uom_name
                    print 'CURRENT UOM ID',current_uom_id
                cr.execute('''  UPDATE 
                                    prakruti_dispatch_line 
                                SET 
                                    actual_dispatched_qty = a.actual_dispatched_qty
                                FROM(
                                    SELECT 
                                        product_uom.id AS uom_id,
                                        product_uom.name AS uom_name,
                                        prakruti_dispatch_line.uom_id AS current_uom_id,
                                        coalesce(dispatched_qty,0)/1000 AS actual_dispatched_qty,
                                        prakruti_dispatch.id AS main_id,
                                        prakruti_dispatch_line.id AS sub_id
                                    FROM
                                        product_uom JOIN
                                        prakruti_dispatch_line ON
                                        prakruti_dispatch_line.uom_id = product_uom.id JOIN
                                        prakruti_dispatch ON
                                        prakruti_dispatch_line.main_id = prakruti_dispatch.id
                                    WHERE
                                        prakruti_dispatch_line.main_id = %s AND product_uom.name in ('Gms','Ml')                                            
                                    ) AS a
                                WHERE
                                    prakruti_dispatch_line.main_id = a.main_id AND
                                    prakruti_dispatch_line.id = a.sub_id
                                    ''',((temp.id),))
                cr.execute('''  UPDATE 
                                    prakruti_dispatch_line 
                                SET 
                                    actual_dispatched_qty = a.actual_dispatched_qty
                                FROM(
                                    SELECT 
                                        product_uom.id AS uom_id,
                                        product_uom.name AS uom_name,
                                        prakruti_dispatch_line.uom_id AS current_uom_id,
                                        coalesce(dispatched_qty,0) AS actual_dispatched_qty,
                                        prakruti_dispatch.id AS main_id,
                                        prakruti_dispatch_line.id AS sub_id
                                    FROM
                                        product_uom JOIN
                                        prakruti_dispatch_line ON
                                        prakruti_dispatch_line.uom_id = product_uom.id JOIN
                                        prakruti_dispatch ON
                                        prakruti_dispatch_line.main_id = prakruti_dispatch.id
                                    WHERE
                                        prakruti_dispatch_line.main_id = %s AND product_uom.name not in ('Gms','Ml')                                            
                                    ) AS a
                                WHERE
                                    prakruti_dispatch_line.main_id = a.main_id AND
                                    prakruti_dispatch_line.id = a.sub_id
                                    ''',((temp.id),))
                if len(temp.batch_line) == 0 and not temp.doc_no:
                    raise UserError(_('Please Enter the Doc No. In the Other Details Tab. If There is No Batch Number For that list of the Product'))
                if len(temp.batch_line) > 0 or temp.doc_no:                    
                    cr.execute('''SELECT count(id) as entered_batch_number from prakruti_dispatch_batch_list_line WHERE batch_no > 0 AND dispatch_id = %s''',((temp.id),))
                    for values in cr.dictfetchall():
                        entered_batch_number = values['entered_batch_number']
                    if entered_batch_number == 0:
                        cr.execute('''  INSERT INTO prakruti_dispatch_batch_list_line(product_id,uom_id,dispatched_qty,packing_details,dispatch_id,remarks)
                                        SELECT 
                                            prakruti_dispatch_line.product_id,
                                            prakruti_dispatch_line.uom_id,
                                            coalesce(prakruti_dispatch_line.dispatched_qty,0) AS dispatched_qty,
                                            prakruti_dispatch_line.packing_details,
                                            prakruti_dispatch.id AS dispatch_id,
                                            prakruti_dispatch.doc_no AS remarks
                                        FROM
                                            prakruti_dispatch_line JOIN
                                            prakruti_dispatch ON
                                            prakruti_dispatch.id = prakruti_dispatch_line.main_id 
                                        WHERE
                                            (prakruti_dispatch_line.status = 'accepted' OR prakruti_dispatch_line.status = 'par_reject' OR prakruti_dispatch_line.status = 'accept_under_deviation') AND 
                                            prakruti_dispatch_line.main_id = %s AND 
                                            prakruti_dispatch_line.store_qty >= prakruti_dispatch_line.dispatched_qty AND 
                                            prakruti_dispatch_line.send_status = 'dispatch' AND 
                                            prakruti_dispatch_line.dispatch_status='Not Yet Dispatched' AND 
                                            prakruti_dispatch_line.send_flag = 0 AND 
                                            prakruti_dispatch.dispatch_no = %s''',((temp.id),(temp.dispatch_no)))
                        
                        #CONVERSION FROM GRAM TO KG
                        cr.execute('''  SELECT 
                                            product_uom.id AS uom_id,
                                            product_uom.name AS uom_name,
                                            prakruti_dispatch_batch_list_line.uom_id AS current_uom_id
                                        FROM
                                            product_uom JOIN
                                            prakruti_dispatch_batch_list_line ON
                                            prakruti_dispatch_batch_list_line.uom_id = product_uom.id
                                        WHERE
                                            prakruti_dispatch_batch_list_line.dispatch_id = %s
                                            ''',((temp.id),))
                        for val in cr.dictfetchall():
                            uom_id = val['uom_id']
                            uom_name = val['uom_name']
                            current_uom_id = val['current_uom_id']
                            print 'UOM ID',uom_id
                            print 'UOM NAME',uom_name
                            print 'CURRENT UOM ID',current_uom_id
                        cr.execute('''  UPDATE 
                                            prakruti_dispatch_batch_list_line 
                                        SET 
                                            actual_dispatched_qty = a.actual_dispatched_qty
                                        FROM(
                                            SELECT 
                                                product_uom.id AS uom_id,
                                                product_uom.name AS uom_name,
                                                prakruti_dispatch_batch_list_line.uom_id AS current_uom_id,
                                                coalesce(dispatched_qty,0)/1000 AS actual_dispatched_qty,
                                                prakruti_dispatch.id AS main_id,
                                                prakruti_dispatch_batch_list_line.id AS sub_id
                                            FROM
                                                product_uom JOIN
                                                prakruti_dispatch_batch_list_line ON
                                                prakruti_dispatch_batch_list_line.uom_id = product_uom.id JOIN
                                                prakruti_dispatch ON
                                                prakruti_dispatch_batch_list_line.dispatch_id = prakruti_dispatch.id
                                            WHERE
                                                prakruti_dispatch_batch_list_line.dispatch_id = %s AND product_uom.name in ('Gms','Ml')                                            
                                            ) AS a
                                        WHERE
                                            prakruti_dispatch_batch_list_line.dispatch_id = a.main_id AND
                                            prakruti_dispatch_batch_list_line.id = a.sub_id
                                            ''',((temp.id),))
                        cr.execute('''  UPDATE 
                                            prakruti_dispatch_batch_list_line 
                                        SET 
                                            actual_dispatched_qty = a.actual_dispatched_qty
                                        FROM(
                                            SELECT 
                                                product_uom.id AS uom_id,
                                                product_uom.name AS uom_name,
                                                prakruti_dispatch_batch_list_line.uom_id AS current_uom_id,
                                                coalesce(dispatched_qty,0) AS actual_dispatched_qty,
                                                prakruti_dispatch.id AS main_id,
                                                prakruti_dispatch_batch_list_line.id AS sub_id
                                            FROM
                                                product_uom JOIN
                                                prakruti_dispatch_batch_list_line ON
                                                prakruti_dispatch_batch_list_line.uom_id = product_uom.id JOIN
                                                prakruti_dispatch ON
                                                prakruti_dispatch_batch_list_line.dispatch_id = prakruti_dispatch.id
                                            WHERE
                                                prakruti_dispatch_batch_list_line.dispatch_id = %s AND product_uom.name not in ('Gms','Ml')                                            
                                            ) AS a
                                        WHERE
                                            prakruti_dispatch_batch_list_line.dispatch_id = a.main_id AND
                                            prakruti_dispatch_batch_list_line.id = a.sub_id
                                            ''',((temp.id),))
                        
                cr.execute('''SELECT stock_dispatch AS error_message FROM stock_dispatch(%s,%s,%s,%s)''',((temp.id),(temp.dispatch_no),(temp.order_no.id),(temp.inquiry_no),))
                for message in cr.dictfetchall():
                    error_message = message['error_message']
                if error_message == 'Oops...! Something Went Wrong.':
                    raise UserError(_('Oops...! Something Went Wrong.'))
                elif error_message == 'Oops...! Please Enter Packing Details.':
                    raise UserError(_('Oops...! Please Enter Packing Details.'))
                elif error_message == 'Not Enough Stock (OR)... No Any Products To Send For Further Process':
                    raise UserError(_('Not Enough Stock (OR)... No Any Products To Send For Further Process'))
            else:
                raise UserError(_('Still the Quality Assurance Process is not done yet...\nSo Order can\'t be Dispatched...'))
        return {}
    
    
    
class PrakrutiDispatchLine(models.Model):
    _name = 'prakruti.dispatch_line'
    _table = 'prakruti_dispatch_line'
    _description = 'Sales Dispatch Line'
    
    main_id = fields.Many2one('prakruti.dispatch',string="Dispatch ID",readonly=True)
    product_id  = fields.Many2one('product.product', string="Product Name",readonly=True)
    uom_id = fields.Many2one('product.uom',string="UOM",readonly=True)
    specification_id = fields.Many2one('product.specification.main', string = "Specification",readonly=True)
    description = fields.Text(string="Description",readonly=True)
    ordered_qty = fields.Float('Ordered Qty',readonly=True,digits=(6,3))
    scheduled_date = fields.Date('Scheduled Date',readonly=True)
    scheduled_qty = fields.Float('Scheduled Qty',readonly=True,digits=(6,3))
    dispatched_qty = fields.Float('Dispatch Qty',digits=(6,3))#Should not exceeds total_scheduled_qty
    remarks = fields.Text(string="Remarks")
    state =fields.Selection([
                ('draft','Draft'),
		('sent_to_qc','Sent To Quality Check'),
		('sent_to_dispatch','Sent to Dispatch'),
		('qc_done','QC Done'),
		('invoice','Invoice'),
		], string= 'States',default= 'draft')
    status = fields.Selection([
		('accepted', 'Accepted'),
		('par_reject', 'Par. Rejected'),
		('rejected','Rejected'),
                ('accept_under_deviation','Accepted Under Deviation')
		], string= 'Status',readonly=True)
    accepted_qty = fields.Float(string= 'Accept. Qty.',digits=(6,3))
    rejected_qty = fields.Float(string= 'Reject. Qty.',digits=(6,3))
    previous_dispatch_qty = fields.Float(string= 'Prev. Disp. Qty.',digits=(6,3))
    total_dispatch_qty = fields.Float(string= 'Dispatched Qty.',digits=(6,3),readonly=1)
    quantity = fields.Float(string = "Req.Qty",digits=(6,3))
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    packing_style = fields.Float('Packing Style',default=0,digits=(6,3))
    no_of_packings = fields.Float('Packing Per Qty',default=0,digits=(6,3))
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0,digits=(6,3))
    total_scheduled_qty = fields.Float(string="Total Sch Qty",readonly=True,digits=(6,3),default=0)
    remaining_dispatched_qty = fields.Float(string="Remaining Dispatch Qty",readonly=True,digits=(6,3),default=0)
    store_qty = fields.Float(string="Store Qty",digits=(6,3),readonly=1)
    packing_details = fields.Char('Packing Details')
    send_status = fields.Selection([('dispatch','Dispatch'),('hold','Hold')],default='dispatch',string= 'Status')
    send_flag = fields.Integer(string = 'Dispatch Flag',default = 0,readonly=1)
    qc_flag = fields.Integer(string = 'QC Flag',default = 0,readonly=1)
    dispatch_status = fields.Char(string = 'Is Dispatch',default = 'Not Yet Dispatched',readonly=1)
    total= fields.Float(string= 'Total')  
    hsn_code = fields.Char(string= 'HSN/SAC')
    amount = fields.Float(string= 'Amount')
    discount_id = fields.Many2one('account.other.tax',string= 'Discount(%)',domain=[('select_type', '=', 'discount')])
    discount = fields.Float(string= 'Discount(%)',default=0)
    taxable_value = fields.Float(string= 'Taxable Value')
    proportionate_amount_to_products = fields.Float(string="Proportionate Amount to Products")
    taxable_value_with_charges = fields.Float(string= 'Taxable Value With Charges')
    gst_rate = fields.Float(string= 'GST Rate')    
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_value = fields.Float(string= 'CGST Value',default=0)
    cgst_amount = fields.Float(string= 'CGST Amount')    
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_value = fields.Float(string= 'SGST Value',default=0)
    sgst_amount = fields.Float(string= 'SGST Amount')    
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_value = fields.Float(string= 'IGST Value',default=0)
    igst_amount = fields.Float(string= 'IGST Amount')    
    batch_list = fields.Text(string= 'Batches',readonly=1)
    batch_wise_dispatch = fields.Text(string= 'Batch Wise Dispatch',readonly=1)
    
    
    #Value after the conversion from gm to kg and ml to lt
    actual_dispatched_qty = fields.Float(string = 'Actual Dispatched Qty',readonly = 1,digits = (6,3))
    
    '''
    Button action
    '''
    def action_dispatch_qty_transfer(self, cr, uid, ids, context=None):
        prakruti_dispatch_line = self.browse(cr, uid, ids[0], context=context)
        for temp in prakruti_dispatch_line:
            if temp.store_qty <=0:
                raise UserError(_('Please Check Stock...'))
            else:
                return {
                    'name': ('Batch Allocation'),
                    'view_type':'form',
                    'view_mode':'form',
                    'res_model': 'batch.wise_allocation',
                    'view_id':False,
                    'type':'ir.actions.act_window',
                    'target':'new',
                    'context': {'default_dispatch_line_id':prakruti_dispatch_line.id,
                                'default_product_id':prakruti_dispatch_line.product_id.id,
                                'default_uom_id':prakruti_dispatch_line.uom_id.id,
                                'default_dispatched_qty':prakruti_dispatch_line.dispatched_qty,
                                'default_store_qty':prakruti_dispatch_line.store_qty
                                }, 
                    }
    
    '''
    Validation Accepted can't be > than Scheduled Qty
    '''    
    def _check_accepted_qty(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for line in lines:
            if line.accepted_qty > line.total_scheduled_qty:
                return False
            return True
        
    _constraints = [
        (_check_accepted_qty, 'Accepted quantity cannot be greater than Scheduled Qty !', ['accepted_qty'])
    ]
    
class PrakrutiDispatchBatchListLine(models.Model):
    _name = 'prakruti.dispatch_batch_list_line'
    _table = 'prakruti_dispatch_batch_list_line'
    _description = 'Dispatch Batch Line'
    
    dispatch_id = fields.Many2one('prakruti.dispatch',string="Dispatch ID")
    product_id  = fields.Many2one('product.product', string="Product",readonly=1,required=1)
    uom_id = fields.Many2one('product.uom',string="UOM",readonly=1)
    dispatched_qty = fields.Float('Dispatch Qty',digits=(6,3),readonly=1)
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No',readonly=1)
    packing_details= fields.Char('Packing Details',readonly=1)
    batch_size= fields.Float('Batch Size',readonly=1)
    batch_qty=fields.Float('Batch Qty',readonly=1)
    remarks = fields.Text(string="Remarks")
    send_to_invoice_flag = fields.Integer(string= 'Send Status',default=0)
    send_to_qc_qa_flag = fields.Integer(string= 'Send QC/QA Status',default=0)
    specification_id = fields.Many2one('product.specification.main', string = "Specification",readonly=1)
    ar_id = fields.Many2one('prakruti.specification.ar.no', string = "AR No.",readonly=1)
    
    
    #Value after the conversion from gm to kg and ml to lt
    actual_dispatched_qty = fields.Float(string = 'Actual Dispatched Qty',readonly = 1,digits = (6,3))
    
    
    '''
    The Batch No & Dispatch Id which will be entered shoud be unique, that means same Batch No & Dispatch Id must not be entered more than one 
    '''
    _sql_constraints = [        
        ('unique_batch_dispatch','unique(batch_no, dispatch_id)', 'Please Check There Might Be Some Batch No Which Is Already Entered...')
        ]