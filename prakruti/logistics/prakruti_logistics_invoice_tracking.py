'''
Company : EBSL
Author: Induja
Module: Invoice Tracking
Class 1: prakruti_logistics_invoice_tracking
Class 2: PrakrutiSalesLineInLogistics
Table 1 & Reference Id: prakruti_logistics_invoice_tracking ,order_line
Table 2 & Reference Id: prakruti_sales_line_in_logistics,logistics_line_id
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
'''

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

class prakruti_logistics_invoice_tracking(models.Model):
    _name= "prakruti.logistics_invoice_tracking"
    _table= "prakruti_logistics_invoice_tracking"
    _order= "id desc"
    _description = 'Logistics Tracking'
    _rec_name= "tracking_number"
    
    order_line = fields.One2many('prakruti.sales_line_in_logistics','logistics_line_id',string='Purchase Order Line of Logistics')
    order_no = fields.Many2one('prakruti.sales_order', string='Order No')
    order_date = fields.Date('Order Date',readonly=True)
    dispatch_no = fields.Char('Dispatch No:', readonly=True)
    dispatch_date = fields.Date('Dispatch Date',default= fields.Date.today)
    customer_id = fields.Many2one ('res.partner',string= 'Customer',readonly=True)
    tracking_number= fields.Char(string= "Tracking Number")
    expected_date= fields.Date(string= "Expected Delivery Date")
    actual_date= fields.Date(string= "Actual Delivery Date")
    status= fields.Selection([
        ('open','Open'),
        ('in_transit','In-Transit'),
        ('deliver','Delivered')],string= "Status",default='open')
    invoice_no = fields.Char('Invoice No:', readonly=True)
    invoice_date = fields.Date('Invoice Date', readonly=True)
    vehicle_no = fields.Char(string="Vehicle No.")
    transport_name=fields.Char(string="Name of the Transporter")
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By')
    reference_no= fields.Char(string='Ref No')  
    tracking_date=fields.Date(string= "Tracking Date") 
    product_id = fields.Many2one('product.product', related='order_line.product_id', string='Product Name')    
    coming_from = fields.Selection([('sales','Sales'),('sales_return','Sales Return')],string= 'Coming From')
    
    dc_no_outward_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Delivery Challan')
    e_way_bill_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'E-Sugama Bill')
    customer_road_permit = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Customer Road Permit')
    coa = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Purchase Order No')
    job_work_documents = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Job Work Documents')
    job_work_documents_remarks = fields.Text(string='Type of Transfer for Job Work')
    
    #Added by Karan to activate the invoice tracing when print is done as on 20170921
    invoice_generated_flag = fields.Integer(default=0)    
    is_invoice_generated = fields.Char(string='Invoice Generated or Not',compute='_on_save')    
    remarks = fields.Text(string="Remarks")
    terms=fields.Text('Terms and conditions')
    revision_no = fields.Char(' Rev No')
    reference_date= fields.Date(string='Ref Date')
    company_address = fields.Many2one('res.company',string='Company Address')
    '''
    while opening the record this will see whether the invoice print is done or not if is done than only the window will open other wise it will raise an message
    '''
    @api.one
    @api.multi
    def _on_save(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self:
            if temp.invoice_generated_flag == 1:
                pass
            else:
                raise UserError(_('Invoice Not Yet Generated...'))
        return {}
    
    '''
    If  job work documents is 'No' then job work document remarks is none
    '''
    @api.onchange('job_work_documents')
    def _onchange_job_work_documents(self):
        if self.job_work_documents == 'no':
            self.job_work_documents_remarks = ''
    
    '''
    Cannot able to delete this record 
    '''       
    @api.multi
    def unlink(self):
        for order in self:
            if order.status in ['open','deliver','in_transit']:
                raise UserError(_('Can\'t Delete'))
        return super(prakruti_logistics_invoice_tracking, self).unlink()
    '''
    Updating status to in transit
    '''
    @api.one
    @api.multi 
    def invoice_in_transit(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Invoice Tracking')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            if temp.tracking_number:
                if temp.expected_date:
                    if temp.expected_date >= temp.order_date:
                        cr.execute('''UPDATE prakruti_logistics_invoice_tracking SET status = 'in_transit' where id = %s  ''', ((temp.id),))
                    else:
                        raise UserError(_('Oops...! Your Expected delivery date should not be less than Order date'))
                else:
                    raise UserError(_('Oops...! Please Enter Expected delivery date'))
            else:
                raise UserError(_('Oops...! Please Enter Tracking Number'))
        return True
    '''
    Updating status to deliver
    '''
    @api.one
    @api.multi 
    def transit_to_deliver(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.actual_date >= temp.order_date:
                #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Logistics Invoice GRN')],context=context)[0]
                #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True) 
                cr.execute('''UPDATE prakruti_logistics_invoice_tracking SET status = 'deliver' WHERE id = %s  ''', ((temp.id),))
            else:
                raise UserError(_('Oops...! Delivery Date should not be less than order date'))
        return True
    
class PrakrutiSalesLineInLogistics(models.Model):
    _name = 'prakruti.sales_line_in_logistics'
    _table = 'prakruti_sales_line_in_logistics'
    _description = 'Logistics Tracking Line'
    
    logistics_line_id = fields.Many2one('prakruti.logistics_invoice_tracking', ondelete='cascade')       
    product_id  = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('product.uom',string='UOM')
    quantity = fields.Float(string = "Qty",digits=(6,3))
    unit_price = fields.Float(string='Unit price',digits=(6,3))
    remarks = fields.Text(string = "Remarks")
    packing_style = fields.Float('Packing Style',default=0,digits=(6,3))
    no_of_packings = fields.Float('Packing Per Qty',default=0,digits=(6,3))
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0,digits=(6,3))
    packing_details = fields.Char('Packing Details')