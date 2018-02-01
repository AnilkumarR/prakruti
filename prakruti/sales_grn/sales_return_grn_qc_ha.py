'''
Company : EBSL
Author: Induja
Module: Sales Return GRN Quality Control HA
Class 1: PrakrutiSalesReturnGRNHA
Class 2: PrakrutiGRNLineHA
Table 1 & Reference Id: prakruti_sales_return_grn_qc_ha ,grn_qc_line
Table 2 & Reference Id: prakruti_sales_return_grn_qc_ha_line,grn_qc_ha_line_id
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



class PrakrutiSalesReturnGRNHA(models.Model):    
    _name =  'prakruti.sales_return_grn_qc_ha'
    _table = 'prakruti_sales_return_grn_qc_ha'
    _rec_name = 'grn_no'    
    _description = 'Sales GRN QC HA'
    _order="id desc"     
        
    grn_qc_line = fields.One2many('prakruti.sales_return_grn_qc_ha_line','grn_qc_ha_line_id')
    grn_no = fields.Char(string='GRN No', readonly=1)
    grn_date = fields.Date('GRN Date',readonly = 1)
    qc_date = fields.Date('QC Date',default= fields.Date.today,readonly = 1)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=1)
    customer_id = fields.Many2one('res.partner',string='Customer',readonly=1)
    order_date = fields.Date(string='Order Date', readonly= 1)
    company_id = fields.Many2one('res.company',string='Company', readonly= 1 )
    state = fields.Selection([('qc_check','Draft'),
                              ('done','Quality Control HA Done')],default= 'qc_check', string= 'Status')
    remarks = fields.Text(string="Remarks") 
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By') 
    checked_id =fields.Many2one('res.users','Checked By') 
    product_id = fields.Many2one('product.product', related='grn_qc_line.product_id', string='Product Name')
    
    terms=fields.Text('Terms and conditions')
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    reference_date= fields.Date(string='Ref Date')
    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['done','qc_check']:
                raise UserError(_('Sorry....You Can\'t Delete'))
        return super(PrakrutiSalesReturnGRNHA, self).unlink() 
    '''
    pulls the data to Sales GRN
    '''
    @api.one
    @api.multi 
    def ha_to_grn(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("UPDATE prakruti_sales_return_grn_line as b set accepted_qty =a.accepted_qty,rejected_qty=a.rejected_qty,status=a.status,state=a.state  FROM( SELECT grn_qc_ha_line_id,grn_grid_line_id,product_id,status,state,accepted_qty,rejected_qty  FROM prakruti_sales_return_grn_qc_ha_line WHERE grn_qc_ha_line_id= %s ) as a WHERE a.grn_grid_line_id = b.id AND a.product_id = b.product_id",((temp.id),))
            cr.execute("UPDATE prakruti_sales_return_grn_qc_ha SET state = 'done' WHERE prakruti_sales_return_grn_qc_ha.id = cast(%s as integer)", ((temp.id),))
            cr.execute("UPDATE prakruti_sales_return_grn set state = 'qc_check_done' where grn_no=%s",((temp.grn_no),))
            cr.execute("SELECT count(id) as reject_count FROM prakruti_sales_return_grn_qc_ha_line WHERE (status = 'rejected' or status = 'par_reject') and rejected_qty > 0 AND grn_qc_ha_line_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                reject_count=int(line['reject_count'])
            if reject_count >= 1:
                ebsl_id = self.pool.get('prakruti.material_rejected_store').create(cr,uid,{
                    'grn_no':temp.grn_no,
                    'grn_date':temp.grn_date,
                    'order_no':temp.order_no.id,
                    'order_date':temp.order_date,
                    'remarks':temp.remarks,
                    'state':'draft',
                    'terms':temp.terms,
                    'company_address':temp.company_id.id,
                    'reference_date':temp.reference_date,
                    'reference_no':temp.reference_no,   
                    'revision_no':temp.revision_no,
                    'coming_from':'sales'
                        })
                cr.execute("SELECT product_id,uom_id,description,rejected_qty,remarks FROM prakruti_sales_return_grn_qc_ha_line WHERE (status = 'rejected' or status = 'par_reject') and rejected_qty > 0 AND grn_qc_ha_line_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    product_id=line['product_id']
                    uom_id=line['uom_id']
                    description=line['description']
                    quantity=line['rejected_qty']
                    remarks=line['remarks']
                    grid_values = self.pool.get('prakruti.rejected_material_store_line').create(cr,uid, {
                        'product_id':product_id,
                        'uom_id':uom_id,
                        'description':description,
                        'quantity':quantity,
                        'remarks':remarks,
                        'qc_check_line_id':ebsl_id
                        })
        return {}
    
class PrakrutiGRNLineHA(models.Model):
    _name = 'prakruti.sales_return_grn_qc_ha_line'
    _table = 'prakruti_sales_return_grn_qc_ha_line'
    _description = 'Sales GRN QC HA Line'
    
    grn_qc_ha_line_id = fields.Many2one('prakruti.sales_return_grn_qc_ha', ondelete='cascade')
    product_id  = fields.Many2one('product.product', string="Product Name")
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    ar_no = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")
    batch_no = fields.Char(string="Batch No",readonly=1)
    description = fields.Text(string="Description")
    quantity = fields.Float('Qty.',digits=(6,3))
    remarks = fields.Text(string="Remarks")
    state =fields.Selection([
        ('qc_check','QC Check'),
        ('qc_done','QC Done'),
        ('done','Done')], string= 'States',default='qc_check',invisible=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('par_reject', 'Partially Accepted'),
        ('accept_under_deviation','Accepted Under Deviation'),
        ('rejected','Rejected')
        ], string= 'Status')
    accepted_qty = fields.Float(string= 'Accept. Qty.',digits=(6,3))
    rejected_qty = fields.Float(string= 'Reject. Qty.', compute='_compute_rejected_qty', store=True,digits=(6,3))
    grn_grid_line_id = fields.Integer(string= 'GRN Grid Line Id')
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
        elif self.status == 'par_accepted':
            self.rejected_qty = 0.0
            self.accepted_qty = 0.0
        else:
            self.accepted_qty = 0.0
            self.rejected_qty = 0.0