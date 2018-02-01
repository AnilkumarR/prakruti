'''
Company : EBSL
Author: Induja
Module: Inward Qulaity Control
Class 1: PrakrutiQualityControl
Class 2: PrakrutiQualityControlLine
Table 1 & Reference Id: prakruti_quality_control ,control_line
Table 2 & Reference Id: prakruti_quality_control_line,control_line_id
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
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


class PrakrutiQualityControl(models.Model):
    _name =  'prakruti.quality_control'
    _table = 'prakruti_quality_control'
    _description = 'Inward Qulaity Control'
    _order="id desc"
    _rec_name="grn_no"
    
    control_line = fields.One2many('prakruti.quality_control_line','control_line_id')
    qc_date = fields.Date(string = 'QC Date',default = fields.Date.today,readonly=1)
    
    grn_no= fields.Char(string='GRN No')
    invoice_no= fields.Char(string='Invoice No')    
    po_no = fields.Char(string='Order No', readonly=True)
    pr_no = fields.Char(string='Requisition No', readonly=True)
    qa_no = fields.Char(string='Analysis No', readonly=True)
    qo_no = fields.Char(string='Quotation No', readonly=True)
    req_no =fields.Char(string='Request No', readonly=True)
    vendor_id = fields.Many2one('res.partner',string='Vendor Name', readonly= "True")
    logo = fields.Binary(related='company_address.logo')
    vendor_reference = fields.Char(string='Vendor Ref.', readonly= "True" )
    other_reference = fields.Char(string='Other Reference')
    request_date = fields.Date(string = "Requisition Date")
    order_date = fields.Date(string='Order Date')
    destination = fields.Char(string='Destination')
    company_address = fields.Many2one('res.company',string='Company Address', readonly= "True" )
    delivery_address = fields.Many2one('res.company',string='Dispatch To', readonly= "True" )
    payment = fields.Char(string='Mode/Terms of Payments')
    terms_of_delivery = fields.Text(string='Terms of Delivery')
    remarks=fields.Text('Received Remarks', readonly= "True" )
    total_discount = fields.Float(string="Total Discount",digits=(6,3) )
    total_tax = fields.Float(string="Total Tax" ,digits=(6,3))
    grand_total= fields.Float(string='Grand Total',digits=(6,3))
    amount_untaxed= fields.Float(string='Untaxed Amount',digits=(6,3))
    additional_charges = fields.Float(string='Additional Charges',digits=(6,3))
    frieght_charges_applied = fields.Selection([('yes','Yes'),('no','No')], string="Freight Charge Applied", default='no')
    frieght_charges = fields.Float(string="Frieght Charges",digits=(6,3))
    dispatch_through = fields.Char(string='Dispatch Through', readonly= "True" )
    packing_charges = fields.Float(string='Packing & Forwarding',digits=(6,3))
    prepared_by = fields.Many2one('res.users','Prepared By')
    maintanence_manager = fields.Many2one('res.users',string="Maintanence Manager")    
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager", readonly= "True" )
    purchase_type = fields.Selection([('extraction','Extraction'),('formulation','Formulation')],default= 'extraction',string="Purchase Type")
    state = fields.Selection([('qc','Quality Control Draft'),
                              ('validate','Quality Control Validated'),
                              #('done','Quality Control Done'),
                              ('qc_ha','Quality Control Higher Approval'),
                              ('sent_to_grn','Sent To GRN'),
                              ('accepted','Quality Control Approved'),
                              ('accepted_under_deviation','Quality Control Accepted on Deviation'),
                              ('rejected','Quality Control Rejected')],default= 'qc', string= 'Status')
    pr_common_id = fields.Integer('PR SCREEN COMMON ID')
    grand_total_in_words= fields.Text(string='Total in words')
    currency_id = fields.Many2one('res.currency', 'Currency')
    prakruti_stock_id = fields.Integer('SCREEN COMMON ID')
    excise_duty = fields.Float(string= 'Excise Duty(%)',digits=(6,3))
    total_excise_duty = fields.Float(string= 'Total Excise Duty',digits=(6,3))
    stores_incharge = fields.Many2one('res.users','Stores Incharge')
    grn_remarks=fields.Text('Remarks')
    gc_no=fields.Char('GC No')
    gc_date=fields.Date('GC Date')
    dc_no=fields.Char('DC No')
    dc_date=fields.Date('DC Date')
    transporter_name=fields.Text('Name of Transporter')
    transporter_payment_details=fields.Text('Transporter Payment Details')
    doc_no=fields.Char('Doc. No',default='PPPL-STR-F-001',readonly=1)
    rev_no=fields.Char('Rev. No',default='02',readonly=1)
    doc_date=fields.Date('Document Date',default= fields.Date.today,readonly=1)
    grn_date= fields.Date('GRN Date',readonly=1)
    invoice_date= fields.Date('Invoice Date',readonly=1)
    quality_incharge= fields.Many2one('res.users','Quality Incharge')
    flag_rejected_count = fields.Integer('Flag', default=1) 
    product_id = fields.Many2one('product.product', related='control_line.product_id', string='Product Name')
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods') 
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No" , default='PPPL-PUR-F-004' , readonly=1)
    revision_no = fields.Char(string = "Rev. No", default='01' , readonly=1)
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today , readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=True) 
    to_name = fields.Many2one('res.users',string="Name") 
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'grn_no':'New',
        'invoice_no':'New',
        'prepared_by': lambda s, cr, uid, c:uid, #Current login user will display automatically
        'quality_incharge': lambda s, cr, uid, c:uid, #Current login user will display automatically   
        'company_address': _default_company,
        'delivery_address': _default_company,
        }
    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['validate','qc_ha','sent_to_grn','accepted_under_deviation','accepted','done','rejected','qc']:
                raise UserError(_('Can\'t Delete record went to further process'))
        return super(PrakrutiQualityControl, self).unlink()
    
    '''
    Based upon the status flag will generate
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
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Purchase QC')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            cr.execute(''' SELECT count(id) as status_marked FROM prakruti_quality_control_line WHERE (status = 'accept' OR status = 'reject') AND control_line_id = %s''',((temp.id),))
            for no_of_line in cr.dictfetchall():
                status_marked = int(no_of_line['status_marked'])
            if status_marked == len(temp.control_line):
                cr.execute("UPDATE prakruti_quality_control SET state = 'validate' WHERE id=%s",((temp.id),))
                cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'validate' WHERE prakruti_purchase_requisition.requisition_no = %s ", ((temp.pr_no),))
                cr.execute("SELECT count(id) as count_value FROM prakruti_quality_control_line WHERE status = 'reject' AND control_line_id = %s",((temp.id),))
                for item in cr.dictfetchall():
                    count_value=int(item['count_value'])
                    print '------------------------1111111111111111111111111111-------------------',count_value
                    if count_value >= accept_value:
                        cr.execute("update prakruti_quality_control set flag_rejected_count =2 where id=%s",((temp.id),))
                cr.execute("SELECT count(id) as accept_value FROM prakruti_quality_control_line WHERE status = 'accept' AND control_line_id = %s",((temp.id),))
                for item in cr.dictfetchall():
                    accept_value=int(item['accept_value'])    
                    print '--------------------------------00000000000000000000000000000000-------------------------------------------',accept_value
                    if count_value == accept_value:
                        print '------------------------------updateeeeeeeeeeeeee---------------------------------------------',accept_value
                        cr.execute("update prakruti_quality_control set flag_rejected_count =2 where id=%s",((temp.id),))
                    elif count_value == 0:
                        print '------------------------------count_value---------------------------------------------',count_value
                        cr.execute("update prakruti_quality_control set flag_rejected_count =4 where id=%s",((temp.id),))
                        cr.execute("update prakruti_grn_inspection_details set flag_rejected_count =4 where grn_no=%s",((temp.grn_no),))
            else:
                raise UserError(_('Please Enter Accepted Qty\nPlease Check Status'))
        return {}
    '''
    Pulls the data to GRN
    '''
    @api.one
    @api.multi 
    def update_to_grn(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("UPDATE prakruti_grn_inspection_details_line as b set accepted_qty =a.accepted_qty,status=a.status  FROM( SELECT control_line_id,grn_grid_common_id,product_id,status,accepted_qty FROM prakruti_quality_control_line WHERE control_line_id= %s ) as a WHERE a.grn_grid_common_id = b.id AND a.product_id = b.product_id",((temp.id),))            
            cr.execute("UPDATE prakruti_quality_control set state ='accepted' where id=%s",((temp.id),))
            cr.execute("UPDATE prakruti_grn_inspection_details SET state = 'accepted' WHERE prakruti_grn_inspection_details.grn_no = %s", ((temp.grn_no),))
            cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'qc_check_done' WHERE prakruti_purchase_requisition.requisition_no = %s ", ((temp.pr_no),))
        return {}
    
    
    '''
    Pulls the data to Inward QC HA 
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
            cr.execute("update prakruti_quality_control set state ='qc_ha' where id=%s",((temp.id),))
            ebsl_id = self.pool.get('prakruti.quality_control_ha').create(cr,uid, {
                'po_no':temp.po_no,
                    'qa_no':temp.qa_no,
                    'pr_no':temp.pr_no,
                    'qo_no':temp.qo_no,
                    'req_no':temp.req_no,
                    'grn_no':temp.grn_no,
                    'grn_date':temp.grn_date,
                    'invoice_no':temp.invoice_no,
                    'invoice_date':temp.invoice_date,
                    'vendor_reference':temp.vendor_reference,
                    'payment':temp.payment,
                    'destination':temp.destination,
                    'other_reference':temp.other_reference,
                    'maintanence_manager':temp.maintanence_manager.id,
                    'purchase_manager':temp.purchase_manager.id,
                    'stores_incharge':temp.stores_incharge.id,
                    'terms_of_delivery':temp.terms_of_delivery,
                    'vendor_id': temp.vendor_id.id,
                    'state':'qc_ha',
                    'remarks':temp.remarks,
                    'request_date':temp.request_date,
                    'order_date':temp.order_date,                        
                    'amount_untaxed':temp.amount_untaxed,
                    'additional_charges':temp.additional_charges,
                    'grand_total':temp.grand_total,
                    'frieght_charges_applied':temp.frieght_charges_applied,
                    'frieght_charges':temp.frieght_charges,
                    'packing_charges':temp.packing_charges,
                    'total_discount':temp.total_discount,
                    'total_tax':temp.total_tax,
                    'dispatch_through':temp.dispatch_through,
                    'excise_duty':temp.excise_duty,
                    'categorization':temp.categorization,
                    'to_name':temp.to_name.id,
                    'plant_manager':temp.plant_manager.id,
                    'company_address':temp.company_address.id,
                    'doc_no':temp.doc_no,
                    'rev_no':temp.rev_no,
                    'default_pr_date':temp.default_pr_date,
                    'total_excise_duty':temp.total_excise_duty,
                    })
            for item in temp.control_line:
                erp_id = self.pool.get('prakruti.quality_control_line_ha').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'specification_id':item.specification_id.id,
                    'ar_no':item.ar_no.id,
                    'description': item.description,
                    'actual_quantity': item.quantity,
                    'quantity': item.quantity,
                    'accepted_qty':item.accepted_qty, 
                    'rejected_qty':item.rejected_qty,
                    'uom_id': item.uom_id.id,
                    'scheduled_date': item.scheduled_date,                   
                    'unit_price': item.unit_price,
                    'discount': item.discount,
                    'tax_price': item.tax_price,
                    'tax_id': item.tax_id.id,
                    'subtotal': item.subtotal,
                    'remarks':item.remarks,
                    'status':item.status,
                    'packing_style':item.packing_style,
                    'received_per_qty':item.received_per_qty,
                    'batch_no':item.batch_no,
                    'test_result':item.test_result,                    
                    'grn_grid_common_id':item.grn_grid_common_id,
                    'control_line_id': ebsl_id
                    })
            cr.execute("update prakruti_quality_control set flag_rejected_count =3 where id=%s",((temp.id),))
            cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'qc_ha' WHERE prakruti_purchase_requisition.requisition_no = %s ", ((temp.pr_no),))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Purchase QC HA')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    
    
    

class PrakrutiQualityControlLine(models.Model):
    _name = 'prakruti.quality_control_line'
    _table = 'prakruti_quality_control_line'
    _description = 'Inward Qulaity Control Line'
    
    control_line_id = fields.Many2one('prakruti.quality_control', ondelete='cascade')
    product_id = fields.Many2one('product.product',string='Product Name',required=True, readonly=1)    
    description = fields.Text(string='Description', readonly=1)
    scheduled_date =fields.Datetime(string='Due On')
    quantity = fields.Float(string='Received Quantity',digits=(6,3))
    actual_quantity = fields.Float(string='Quantity', readonly=1,digits=(6,3))
    unit_price = fields.Float(string='Unit price',digits=(6,3))
    uom_id = fields.Many2one('product.uom',string='UOM',required=True, readonly=1)
    discount = fields.Float(string='Discount(%)',digits=(6,3))
    tax_type = fields.Selection([('cst','CST'),('tin','TIN'),('tax','Tax'),('vat','VAT')], string="Tax", default= 'tax')
    tax_id = fields.Many2one('account.other.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    tax_price = fields.Float(related='tax_id.per_amount',string='Taxes', store=True,readonly=True,digits=(6,3))     
    subtotal= fields.Float(string='Sub Total',digits=(6,3))
    total= fields.Float(string='Total',digits=(6,3))
    pr_common_id = fields.Integer('PR SCREEN COMMON ID')
    currency_id = fields.Many2one(related='control_line_id.currency_id', store=True, string='Currency', readonly=True)
    prakruti_stock_id = fields.Integer('SCREEN COMMON ID')
    remarks = fields.Text('Remarks')
    accepted_qty = fields.Float('Accepted Qty.',digits=(6,3))
    rejected_qty = fields.Float('Rejected Qty.', readonly=True , compute='_compute_rejected_qty',store=True,digits=(6,3))
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3))
    received_per_qty = fields.Float(string= 'Received Per Qty',digits=(6,3))
    test_result = fields.Text(string= 'Test Result') 
    status = fields.Selection([('accept','Accept'),
                               ('reject','Reject')],string= 'Status',default='reject')
    qc_common_id= fields.Integer('Common id')
    control_id= fields.Many2one('prakruti.quality_control')
    grn_grid_common_id = fields.Integer('PR SCREEN COMMON ID')
    batch_no = fields.Char('Batch No.')
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    ar_no = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")
    '''
    Rejected Qty calculation
    '''
    @api.depends('quantity','accepted_qty')
    def _compute_rejected_qty(self):
        print 'automatautomat-----------------1'
        for order in self:
            print 'automatautomat-----------------2'
            rejected_qty = 0.0            
            order.update({                
                'rejected_qty': order.quantity - order.accepted_qty 
            })
            
    @api.onchange('status')
    def onchange_status(self):
        if self.status == 'accept':
            self.accepted_qty = self.quantity
            self.test_result = None
        elif not self.status:
            self.accepted_qty = 0.0
            self.test_result = None
        else:
            self.accepted_qty = 0.0
            self.test_result = None