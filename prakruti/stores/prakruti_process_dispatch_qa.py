'''
Company : EBSL
Author: Induja
Module: Quality Process QA
Class 1: PrakrutiProcessDispatchQA
Class 2: PrakrutiProcessDispatchLineQa
Table 1 & Reference Id: prakruti_process_quality_control_qa ,qc_check_line
Table 2 & Reference Id: prakruti_process_quality_control_line_qa,qc_check_line_id
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

class PrakrutiProcessDispatchQA(models.Model):
    _name =  'prakruti.process_quality_control_qa'
    _table = 'prakruti_process_quality_control_qa'
    _description = 'Quality Process QA'
    _order="id desc"
    _rec_name= "dispatch_no"
    
    qc_check_line = fields.One2many('prakruti.process_quality_control_line_qa','qc_check_line_id')    
    checked_by = fields.Many2one('res.users',string = 'Checked By')
    qc_date = fields.Date('QA Date', default=fields.Date.today)
    dispatch_no = fields.Char('Dispatch No', readonly=True)
    dispatch_date = fields.Date('Dispatch Date', readonly=True)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=True)
    order_date = fields.Date('Order Date', readonly=True)
    dispatch_to = fields.Many2one('res.partner', string='Dispatch To', readonly=True)
    customer_id = fields.Many2one('res.partner',string="Customer")
    state =fields.Selection([
		('draft','Quality Assurance Draft'),
		('validate','Quality Assurance Validated'),
		#('sent_to_dispatch','Sent to Dispatch'),
		#('qc_done','Quality Control Done'),
		#('qc_ha_done','Quality Control HA Done'),
		('process_qa_done',' Quality Assurance Done'),
		('process_qa_ha',' Quality Assurance HA'),
		],default= 'draft', string= 'Status', readonly=True) 
    
    store_incharge = fields.Many2one('res.users', string="Store Incharge")
    quality_incharge = fields.Many2one('res.users', string="Quality Incharge")    
    remarks = fields.Text(string="Remarks")
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By')
    reference_no= fields.Char(string='Ref No')  
    product_id = fields.Many2one('product.product', related='qc_check_line.product_id', string='Product Name')    
    flag_rejected_count = fields.Integer('Flag', default=1) 
    dispatch_flag = fields.Integer(string="Dispatch Flag")
    qc_check_flag = fields.Integer(string= 'QC Check Done',readonly=1)
    coming_from =fields.Selection([
		('qc_check', 'QC'),
		('dispatch', 'Dispatch'),
		], string='Coming From',default='dispatch',readonly=True)
    
    revision_no = fields.Char(' Rev No')
    terms=fields.Text('Terms and conditions')
    reference_date= fields.Date(string='Ref Date')     
    batch_line = fields.One2many('prakruti.dispatch_qa_batch_list_line', 'dispatch_qa_id',string='Batch line')
    company_id = fields.Many2one('res.company',string="Company")
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['draft','done']:
                raise UserError(_('Can\'t Delete...'))
        return super(PrakrutiProcessDispatchQA, self).unlink()
    
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
            cr.execute(''' SELECT dispatch_qa_validate as error_message FROM dispatch_qa_validate(%s,%s)''',((temp.id),(temp.dispatch_no),))
            for error in cr.dictfetchall():
                error_message = error['error_message']
            if error_message == 'please_check_status':
                raise UserError(_('Please Enter Accepted Qty\nPlease Check Status'))
        return {}
    
   
    
    '''
    Pulls the data to dispatch screen
    '''
    @api.one
    @api.multi 
    def update_to_dispatch(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        dispatch_state = ''
        for temp in self:
            cr.execute(''' SELECT dispatch_qa_to_dispatch as error_message FROM  dispatch_qa_to_dispatch(%s,%s)''',((temp.id),(temp.dispatch_no),))
            for error in cr.dictfetchall():
                error_message = error['error_message']
            if error_message == 'Please Select the Quality Incharge and Checked By Person':
                raise UserError(_('Please Select the Quality Incharge and Checked By Person'))
            elif error_message == 'Quality Check Is Not Done Yet Still If You want to Dispatch The Material Please Go for the HA':
                raise UserError(_('Quality Check Is Not Done Yet Still If You want to Dispatch The Material Please Go for the HA'))
            
        return {}
    
     
    '''
    Pulls the data to QC HA Screen
    '''
    @api.one
    @api.multi 
    def quality_to_ha(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute(''' SELECT dispatch_qa_to_ha as error_message FROM dispatch_qa_to_ha(%s,%s)''',((temp.id),(temp.dispatch_no),))
            for error in cr.dictfetchall():
                error_message = error['error_message']
            if error_message == 'Please Select the Quality Incharge and Checked By Person':
                raise UserError(_('Please Select the Quality Incharge and Checked By Person'))
        return {}
    
class PrakrutiProcessDispatchLineQa(models.Model):
    _name = 'prakruti.process_quality_control_line_qa'
    _table = 'prakruti_process_quality_control_line_qa'
    _description = 'Quality Process QA'
    
    qc_check_line_id = fields.Many2one('prakruti.process_quality_control_qa', ondelete='cascade')    
    product_id = fields.Many2one('product.product',string='Product Name')
    uom_id = fields.Many2one('product.uom',string='UOM')
    description = fields.Text(string='Description')
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    ar_no = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")
    ordered_qty = fields.Float('Ordered Qty',digits=(6,3))
    dispatched_qty = fields.Float('Dispatched Qty',digits=(6,3))
    remarks = fields.Text(string="Remarks")
    status = fields.Selection([
		('accepted', 'Accepted'),
		('rejected','Rejected')
		],default= 'rejected', string= 'Status')
    state =fields.Selection([
		('draft','Draft'),
		('done','Done')
		],default= 'draft', string= 'State', readonly=True)
    test_result = fields.Text('Test Result')
    accepted_qty = fields.Float(string= 'Accept. Qty.',digits=(6,3))
    rejected_qty = fields.Float(string= 'Reject. Qty.', store=True , compute='_compute_rejected_qty',digits=(6,3))
    scheduled_qty = fields.Float(string= 'Sch. Qty.',digits=(6,3))    
    dispatch_line_grid_id = fields.Integer(string= 'Dispatch Line QA Grid ID')
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')
    send_flag = fields.Integer(string='Dispatch Flag',readonly=1)
    qc_flag = fields.Integer(string='QC Flag',default = 0,readonly=1)    
    batch_list = fields.Text(string= 'Batches',readonly=1)
    
    '''
    Validation for -ve values
    ''' 
    @api.one
    @api.constrains('rejected_qty')
    def _check_rejected_qty(self):
        if self.rejected_qty < 0:
            raise ValidationError(
                "Rejected Qty. !!! Can't be Negative") 
    
    '''
    Rejected Qty Calculation
    '''
    @api.depends('dispatched_qty','accepted_qty')
    def _compute_rejected_qty(self):
        print 'automatautomat-----------------1'
        for order in self:
            print 'automatautomat-----------------2'
            rejected_qty = 0.0            
            order.update({                
                'rejected_qty': order.dispatched_qty - order.accepted_qty 
            })
      
    '''
    When we select status test result will automatically display
    '''         
    @api.onchange('status')
    def onchange_status(self):
        if self.status == 'accepted':
            self.accepted_qty = self.dispatched_qty
            self.test_result = 'TESTED OK'
        elif self.status == 'rejected':
            self.rejected_qty = self.dispatched_qty
            self.accepted_qty = 0.0
            self.test_result = 'TESTED OK'
        else:
            self.accepted_qty = 0.0
            self.rejected_qty = 0.0
            self.test_result = 'NO SELECTION' 
    
class PrakrutiDispatchQABatchListLine(models.Model):
    _name = 'prakruti.dispatch_qa_batch_list_line'
    _table = 'prakruti_dispatch_qa_batch_list_line'
    _description = 'Dispatch Batch QA Line'
    
    dispatch_qa_id = fields.Many2one('prakruti.process_quality_control_qa',string="QA ID",readonly=1)
    
    product_id  = fields.Many2one('product.product', string="Product",readonly=1,required=1)
    uom_id = fields.Many2one('product.uom',string="UOM",readonly=1)
    dispatched_qty = fields.Float('Dispatch Qty',digits=(6,3),readonly=1)
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No',readonly=1)
    packing_details= fields.Char('Packing Details',readonly=1)
    batch_size= fields.Float('Batch Size',readonly=1)
    batch_qty=fields.Float('Batch Qty',readonly=1)
    remarks = fields.Text(string="Remarks")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    ar_id = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")
    
    dispatch_batch_line_id = fields.Integer(string = 'Dispatch Batch Line ID',readonly=1)
    
    
    '''
    The Batch No & Dispatch Id which will be entered shoud be unique, that means same Batch No & Dispatch Id must not be entered more than one 
    '''
    _sql_constraints = [        
        ('unique_batch_dispatch','unique(batch_no, dispatch_qa_id)', 'Please Check There Might Be Some Batch No Which Is Already Entered...')
        ]   