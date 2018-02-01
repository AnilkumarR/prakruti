'''
Company : EBSL
Author: Induja
Module: Inward Quality Control HA
Class 1: PrakrutiQualityControlHA
Class 2: PrakrutiQualityControlLineHA
Table 1 & Reference Id: prakruti_quality_control_ha ,control_line
Table 2 & Reference Id: prakruti_quality_control_line_ha,control_line_id
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

class PrakrutiQualityControlHA(models.Model):
    _name =  'prakruti.quality_control_ha'
    _table = 'prakruti_quality_control_ha'
    _description = 'Inward Quality Control HA'
    _order="id desc"
    _rec_name="grn_no"    
    
    control_line = fields.One2many('prakruti.quality_control_line_ha','control_line_id')
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
    remarks=fields.Text(' Remarks' )
    total_discount = fields.Float(string="Total Discount" ,digits=(6,3))
    total_tax = fields.Float(string="Total Tax" ,digits=(6,3))
    grand_total= fields.Float(string='Grand Total',digits=(6,3))
    amount_untaxed= fields.Float(string='Untaxed Amount',digits=(6,3))
    additional_charges = fields.Float(string='Additional Charges',digits=(6,3))
    frieght_charges_applied = fields.Selection([('yes','Yes'),('no','No')], string="Freight Charge Applied", default='no')
    frieght_charges = fields.Float(string="Frieght Charges",digits=(6,3))
    dispatch_through = fields.Char(string='Dispatch Through', readonly= "True" )
    packing_charges = fields.Float(string='Packing & Forwarding',digits=(6,3))
    prepared_by = fields.Many2one('res.users','Prepared By',readonly=True)
    maintanence_manager = fields.Many2one('res.users',string="Maintanence Manager")    
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager", readonly= "True" )
    purchase_type = fields.Selection([('extraction','Extraction'),('formulation','Formulation')],default= 'extraction',string="Purchase Type")
    state = fields.Selection([('qc_ha','Quality Control Higher Approval Draft'),          
                              ('done','Quality Control Approved'),
                              ('rejected','Quality Control Rejected')],default= 'qc_ha', string= 'Status') 
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
    product_id = fields.Many2one('product.product', related='control_line.product_id', string='Product Name')
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods')
    #added by induja on 20171011 for Other details
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
            if order.state in ['qc','qc_ha','done','rejected']:
                raise UserError(_('Can\'t Delete record went to further process'))
        return super(PrakrutiQualityControlHA, self).unlink()
    
    '''
    pulls the data to GRN  & if rejected qty is there means data pulls to material rejection store
    '''
    @api.one
    @api.multi 
    def ha_to_done(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("UPDATE prakruti_grn_inspection_details_line as b set accepted_qty =a.accepted_qty,rejected_qty=a.rejected_qty,status=a.status  FROM( SELECT control_line_id,grn_grid_common_id,product_id,status,accepted_qty,rejected_qty  FROM prakruti_quality_control_line_ha WHERE control_line_id= %s ) as a WHERE a.grn_grid_common_id = b.id AND a.product_id = b.product_id",((temp.id),))
            cr.execute("SELECT count(id) as count_value FROM prakruti_quality_control_line_ha WHERE status = 'accept' AND control_line_id = %s",((temp.id),))
            for item in cr.dictfetchall():
                count_value=int(item['count_value'])
                print '--------------------------------00000000000000000000000000000000-------------------------------------------',count_value
                if count_value > 0:
                    print '---------------------------------------------------------------------------',count_value
                    cr.execute("UPDATE prakruti_grn_inspection_details set flag_rejected_count =2 where grn_no=%s",((temp.grn_no),))
                    cr.execute("UPDATE prakruti_grn_inspection_details set state = 'accepted' where grn_no=%s",((temp.grn_no),))
                    cr.execute("UPDATE prakruti_quality_control_ha SET state = 'done' WHERE prakruti_quality_control_ha.id = cast(%s as integer)", ((temp.id),))
                    cr.execute("UPDATE prakruti_purchase_requisition SET state = 'qc_check_done' WHERE prakruti_purchase_requisition.requisition_no = %s ", ((temp.pr_no),))
            cr.execute("SELECT count(id) as reject_count FROM prakruti_quality_control_line_ha WHERE (status = 'reject' or status = 'par_accept') and rejected_qty > 0 AND control_line_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                reject_count=int(line['reject_count'])
            if reject_count >= 1:
                if temp.remarks:
                    cr.execute("UPDATE prakruti_quality_control_ha SET state = 'rejected' WHERE prakruti_quality_control_ha.id = cast(%s as integer)", ((temp.id),))
                    ebsl_id = self.pool.get('prakruti.material_rejected_store').create(cr,uid,{
                        'grn_no':temp.grn_no,
                        'grn_date':temp.grn_date,
                        'po_no':temp.po_no,
                        'company_address':temp.company_address.id,
                        'order_date':temp.order_date,
                        'remarks':temp.remarks,
                        'state':'draft',
                        'coming_from':'purchase'
                            })
                    cr.execute("SELECT product_id,uom_id,description,rejected_qty,remarks FROM prakruti_quality_control_line_ha WHERE (status = 'reject' or status = 'par_accept') and rejected_qty > 0 AND control_line_id = %s",((temp.id),))
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
                else:
                    raise UserError(_('Please Enter Remarks'))
        return {} 
    

class PrakrutiQualityControlLineHA(models.Model):    
    _name = 'prakruti.quality_control_line_ha'
    _table = 'prakruti_quality_control_line_ha'
    _description = 'Inward Quality Control HA Line'
    
    control_line_id = fields.Many2one('prakruti.quality_control_ha', ondelete='cascade')
    product_id = fields.Many2one('product.product',string='Product Name',required=True, readonly=1)    
    description = fields.Text(string='Description', readonly=1)
    scheduled_date =fields.Datetime(string='Due On')
    quantity = fields.Float(string='Received Quantity',digits=(6,3))
    actual_quantity = fields.Float(string='Ordered Quantity', readonly=1,digits=(6,3))
    unit_price = fields.Float(string='Unit price',digits=(6,3))
    uom_id = fields.Many2one('product.uom',string='UOM',required=True, readonly=1)
    discount = fields.Float(string='Discount(%)',digits=(6,3))
    tax_type = fields.Selection([('cst','CST'),('tin','TIN'),('tax','Tax'),('vat','VAT')], string="Tax", default= 'tax')
    tax_id = fields.Many2one('account.other.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    tax_price = fields.Float(related='tax_id.per_amount',string='Taxes', store=True,readonly=True,digits=(6,3)) 
    subtotal= fields.Float(string='Sub Total',digits=(6,3))
    total= fields.Float(string='Total',digits=(6,3))
    currency_id = fields.Many2one(related='control_line_id.currency_id', store=True, string='Currency', readonly=True)
    prakruti_stock_id = fields.Integer('SCREEN COMMON ID')
    remarks = fields.Text('Remarks')
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3))
    received_per_qty = fields.Float(string= 'Received Per Qty',digits=(6,3))
    test_result = fields.Text(string= 'Test Result') 
    status = fields.Selection([('accept','Accept'),
                               ('par_accept','Partially Accepted'),
                               ('accept_under_deviation','Accepted Under Deviation'),
                               ('reject','Reject')],string= 'Status')
    accepted_qty = fields.Float('Accepted Qty.',digits=(6,3))
    rejected_qty = fields.Float('Rejected Qty.',digits=(6,3))    
    grn_grid_common_id = fields.Integer('PR SCREEN COMMON ID')
    batch_no = fields.Char('Batch No.')
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    ar_no = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")
    
    @api.onchange('status')
    def onchange_status(self):
        if self.status == 'accept':
            self.accepted_qty = self.quantity
            self.test_result = None
        elif self.status == 'reject':
            self.rejected_qty = self.quantity
            self.test_result = None
        elif self.status == 'par_accept':
            self.test_result = None
        elif not self.status:
            self.test_result = None
        else:
            self.test_result = None
    
    '''
    The accepted, rejected Qty doesn't matches qty
    '''
    def _check_qty_entry(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for line in lines:
            print 'line.accepted_qty + line.rejected_qty', line.accepted_qty + line.rejected_qty
            print 'line.quantity', line.quantity
            if (line.accepted_qty + line.rejected_qty) > line.quantity:
                return False
        return True
     
    _constraints = [
         (_check_qty_entry, 'Your Accepted and Rejected Qty. doesn\'t match the Total Qty. !', ['accepted_qty','rejected_qty'])
    ]    
    
    '''
    rejected qty calculation
    '''
    @api.onchange('accepted_qty','status')
    def onchange_accepted_qty(self):
        self.update({
                    'rejected_qty': self.quantity - self.accepted_qty
                    })
    '''
    Accepted qty calculation
    '''
    @api.onchange('rejected_qty','status')
    def onchange_rejected_qty(self):
        self.update({
                    'accepted_qty': self.quantity - self.rejected_qty
                    })
