'''
Company : EBSL
Author: Induja
Module: Production SLip
Class 1: PrakrutiProductionSlip
Class 2: PrakrutiProductionSlipLine
Table 1 & Reference Id: prakruti_production_slip ,grid_id
Table 2 & Reference Id: prakruti_production_slip_line,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''
# -*- coding: utf-8 -*-
import time
from openerp.tools import image_resize_image_big
from openerp.exceptions import ValidationError
from openerp import api, fields, models, _
from openerp.exceptions import except_orm, Warning as UserError 
import openerp
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize, image_resize_image_big
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
####################################################################


class PrakrutiProductionSlip(models.Model):
    _name= 'prakruti.production_slip'
    _table= 'prakruti_production_slip'
    _description= 'Production Slip' 
    _order= 'id desc'
    _rec_name= 'slip_no'  
    
  
    '''Auto genereation function
    'Format: PS\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: PS\EXFG\0455\17-18
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
                                CAST(EXTRACT (month FROM slip_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM slip_date) AS integer) AS year,
                                id
                          FROM 
                                prakruti_production_slip 
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
                cr.execute('''select autogenerate_slip_no(%s)''', ((temp.id),)  ) 
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_slip_no'];# Database Function autogenerate_slip_no
                auto_gen = int(parent_invoice_id)
                if len(str(auto_gen)) < 2:
                    auto_gen = '000'+ str(auto_gen)
                elif len(str(auto_gen)) < 3:
                    auto_gen = '00' + str(auto_gen)
                elif len(str(auto_gen)) == 3:
                    auto_gen = '0'+str(auto_gen)
                else:
                    auto_gen = str(auto_gen)
                for record in self:
                    cr.execute("SELECT total_ordered_qty,quantity FROM prakruti_production_slip_line WHERE main_id = CAST(%s AS INTEGER)",((temp.id),))
                    for line in cr.dictfetchall():
                        total_ordered_qty = line['total_ordered_qty']
                        quantity = line['quantity']
                    if temp.slip_type == 'based_on_order':
                        if temp.product_type_id.group_code and (total_ordered_qty == quantity):
                            style_format[record.id] = 'PS\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                        elif total_ordered_qty != quantity:
                            style_format[record.id] = 'PS-PENDING\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                        else:                        
                            style_format[record.id] = 'PS\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:
                        if temp.product_type_id.group_code:
                            style_format[record.id] = 'PS\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                        else:                        
                            style_format[record.id] = 'PS\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                        
                cr.execute('''UPDATE 
                                    prakruti_production_slip 
                              SET
                                    slip_no =%s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
    
    
        
    grid_id= fields.One2many('prakruti.production_slip_line', 'main_id',string= 'Grid')
    slip_no= fields.Char(string='Slip No.', default= 'New',readonly=1)
    slip_date= fields.Date('Slip Date', default= fields.Date.today,readonly=1)    
    sl_no= fields.Char('Slip No', compute= '_get_auto')
    auto_no= fields.Integer('Auto')
    req_no_control_id= fields.Integer('Auto Generating id', default= 0)        
    company_id= fields.Many2one('res.company',string='Company Address',default=lambda self: self.env.user.company_id,required="True")
    order_no= fields.Char(string='Order No.',readonly=1)
    order_date= fields.Date('Order Date',readonly=1)
    product_type_id=fields.Many2one('product.group',string= 'Product Type',default = 5)
    quotation_no= fields.Char(string='Quotation No' ,readonly=1)
    quotation_date = fields.Date(string='Quotation Date' ,readonly=1)
    inquiry_date= fields.Date('Inquiry Date',readonly=1)
    inquiry_no = fields.Char(' Inquiry No', readonly=1)
    customer_id = fields.Many2one('res.partner',string="Customer",readonly=1)    
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    remarks = fields.Text(string="Remarks")
    terms =fields.Text('Terms and conditions')         
    state= fields.Selection(
        [
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
        ], string= 'Status', default= 'slip_request')
    requested_id =fields.Many2one('res.users','Requested By',readonly=1)
    quotation_id =fields.Many2one('res.users','Quotation By',readonly=1)
    order_id =fields.Many2one('res.users','Order By')
    reference_no= fields.Char(string='Ref No') 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')
    all_send_to_request = fields.Integer(string='All Send To Request',default=0,readonly=1)
    all_send_to_planning = fields.Integer(string='All Send To Planning',default=0,readonly=1)
    revise_status = fields.Selection([('revise_production_slip','Revise Production Slip'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    
    #Added as on 20170923 for Provision to create Production Slip for Buffer Stock by Karan
    slip_type = fields.Selection([
        ('based_on_order','Production Based On Order'),
        ('buffer','Buffer Production')],default = 'buffer',string = 'Production Type',readonly=1)
    
    #Added new state for Buffer Creation on 20171009 by Karan
    buffer_status = fields.Selection([('draft','Draft'),('done','Created')],string = 'Status',default='draft')
    buffer_status_update = fields.Char(string='Update Status',compute='_on_save')
    revision_no = fields.Char(' Rev No')
    reference_date= fields.Date(string='Ref Date') 
    
    po_no= fields.Char(string='P.O No')    
    
    
    @api.one
    @api.constrains('grid_id')
    def _check_grid(self):
        '''
        Grid Can't be Empty
        '''
        if len(self.grid_id) == 0:
            raise ValidationError(
                "Please Enter Some Products...") 
    
    @api.one
    @api.multi
    def _on_save(self):
        '''
        while saving the record this will update status to done for buffer
        '''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self:
            if temp.slip_type == 'buffer':
                cr.execute('''update prakruti_production_slip set buffer_status = 'done',state='' where id = %s ''', ((temp.id),))
        return {}
    
    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')
    
    _defaults = {
        'company_id': _default_company,
        'revise_id': lambda s, cr, uid, c:uid   
        }
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete...'))
        return super(PrakrutiProductionSlip, self).unlink()
    
    '''
   This button helps to check the stock for products
    '''
    @api.one
    @api.multi
    def check_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute('''SELECT stock_production_slip(%s)''',((temp.id),)) #Database Function :stock_production_slip
        return {}
    
    '''
    Pulls the data to sales order
    '''
    @api.one
    @api.multi 
    def to_salesorder(self):
        error_message = ''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Production Slip')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            cr.execute("SELECT production_slip_to_sales_order AS error_message FROM production_slip_to_sales_order(%s,%s,%s,%s)",((temp.id),(temp.order_no),(temp.quotation_no),(temp.inquiry_no),))
            for line in cr.dictfetchall():
                error_message = line['error_message']
            if error_message == 'Oops...! Please Enter Scheduled Qty.':
                raise UserError(_('Oops...! Please Enter Scheduled Qty.'))    
        return True
        
    
    '''
   This button helps to send the data to planning 
    '''     
    @api.one
    @api.multi 
    def raise_planning(self):
        error_message = ''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute('''SELECT production_slip_to_production_planning AS error_message FROM production_slip_to_production_planning(%s)''',((temp.id),))
            for line in cr.dictfetchall():
                error_message = line['error_message']
            if error_message == 'No Any Product to send for Planning':
                raise UserError(_('No Any Product to send for Planning'))
        return {}
        
    
    '''
    After Planning done this data will send to BMR Requistion
    '''    
    @api.one
    @api.multi 
    def raise_bmr_requisition(self):
        error_message = ''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute('''SELECT production_slip_to_bmr_requisition AS error_message FROM production_slip_to_bmr_requisition(%s)''',((temp.id),))
            for line in cr.dictfetchall():
                error_message = line['error_message']
            if error_message == 'No Any Product to send for BMR Request (or) Planning Not done Yet':
                raise UserError(_('No Any Product to send for BMR Request (or)\nPlanning Not done Yet'))
            elif error_message == 'empty_grid':
                raise UserError(_('Record...Can\'t Be Empty...'))
        return {}
    
    '''
    This Button helps for Revision(If any changes need to be done in prakruti_production_slip_line click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_production_slip(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            #LET US TAKE A BACKUP OF EXISTING ENTRY SO TO KEEP TRACK OF OLDER RECORDS JUST LIKE THE DUPLICATION
            ebsl_id = self.pool.get('prakruti.production_slip').create(cr,uid, {
                'order_no':temp.order_no,
                'order_date':temp.order_date,
                'product_type_id':temp.product_type_id.id,
                'produc_remarks':temp.remarks,
                'customer_id':temp.customer_id.id,
                'terms':temp.terms,
                'inquiry_no':temp.inquiry_no,
                'inquiry_date':temp.inquiry_date,
                'quotation_no':temp.quotation_no,
                'quotation_date':temp.quotation_date,
                'billing_id':temp.billing_id.id,
                'remarks':temp.remarks,
                'requested_id':temp.requested_id.id,
                'quotation_id':temp.quotation_id.id,
                'order_id':temp.order_id.id,
                'reference_no':temp.reference_no,     
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,                
                'revise_flag': 1
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.production_slip_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'specification_id': item.specification_id.id,
                    'description': item.description,
                    'remarks': item.remarks,
                    'quantity':item.quantity,
                    'balance_qty': item.balance_qty,
                    'req_date':item.req_date,
                    'unit_price': item.unit_price,
                    'so_line_grid_id': item.so_line_grid_id,
                    'ordered_qty': item.ordered_qty,
                    'balance_qty': item.balance_qty,
                    'total_scheduled_qty':item.total_scheduled_qty,
                    'total_dispatch_qty': item.total_dispatch_qty,
                    'inquiry_line_id':item.inquiry_line_id,
                    'revise_slip_line':item.revise_slip_line,
                    'main_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_production_slip SET revise_status = 'revise_production_slip',is_revise = 'True' WHERE id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_production_slip_line SET revise_slip_line = 1 WHERE main_id = %s",((temp.id),))
        return {} 
    
    '''
    After doing changes in prakruti_production_slip_line click this to visible Revise button and to update the changes in the screen
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
                    cr.execute("UPDATE prakruti_production_slip_line SET revise_slip_line = 2 WHERE main_id = %s",((temp.id),))
                    cr.execute('''SELECT revise_production_slip AS error_message FROM revise_production_slip(%s,%s)''',((temp.id),(temp.inquiry_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record...Cannot Be Revised...Please Contact Your Administrator...!!!':
                        raise UserError(_('Record...Can\'t Be Revised...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 
    
    '''
    This button helps to reject the particualr order and the status will update to order screen
    '''    
    @api.one
    @api.multi 
    def action_reject(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Production Slip Rejected')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            if temp.remarks:
                cr.execute('''UPDATE  prakruti_production_slip SET state = 'rejected' WHERE prakruti_production_slip.id = %s and customer_id = %s''',((temp.id),(temp.customer_id.id),))
                cr.execute('''UPDATE  prakruti_sales_order SET remarks= 'Rejected From Production',state = 'rejected' WHERE prakruti_sales_order.order_no = %s and customer_id = %s ''',((temp.order_no),(temp.customer_id.id),))
            else:
                raise UserError(_('Please Enter Remarks...'))
        return {}
    
    
class PrakrutiProductionSlipLine(models.Model):
    _name= 'prakruti.production_slip_line'
    _table= 'prakruti_production_slip_line'
    _description= 'Production Slip Line' 
    
    main_id = fields.Many2one('prakruti.production_slip', string= "Grid Line")
    product_id= fields.Many2one('product.product', string= "Product",required=1)
    description= fields.Text(string= 'Description')
    uom_id= fields.Many2one('product.uom', string="UOM")
    specification_id= fields.Many2one('product.specification.main', string= "Specification")
    quantity= fields.Float(string= 'Req. Qty.',digits=(6,3))
    req_date= fields.Date('Req. Date',readonly=1)
    remarks= fields.Text(string= "Remarks")
    scheduled_date = fields.Date('Sch. Date')
    scheduled_qty = fields.Float('Sch. Qty.',default=0,digits=(6,3))
    so_line_grid_id = fields.Integer('Sales Order Line Grid ID')
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    total= fields.Float(string='Total',digits=(6,3)) 
    balance_qty = fields.Float(string="Balance Qty",compute='_compute_balance_qty',store=1,default=0,digits=(6,3))
    total_dispatch_qty = fields.Float(string= 'Total Disp. Qty.',default=0,digits=(6,3))
    total_ordered_qty = fields.Float('Total Ordered Qty.',digits=(6,3))
    ordered_qty = fields.Float(string="Ordered Qty",digits=(6,3),default=0)
    total_scheduled_qty = fields.Float(string="Total Sch Qty",digits=(6,3),default=0,readonly=1)
    total_dispatched_qty=fields.Float(string="Total Dispatch Qty",readonly=1,digits=(6,3),default=0)
    store_qty = fields.Float(string="Available Qty",digits=(6,3),readonly=1)
    bmr_status = fields.Boolean(string="BMR Request", default='1')
    bmr_flag = fields.Integer(string='BMR Request Flag',default=0,readonly=1)
    planning_status = fields.Boolean(string="Planning Request", default=1)
    planning_flag = fields.Integer(string='Planning Flag',default=0,readonly=1)
    planning_done = fields.Boolean(string='Planning Done',default=0,readonly=1)
    inquiry_line_id=fields.Integer(string='Grid id of inquiry')
           
    revise_slip_line = fields.Integer(string= 'Revised Flag',default=0) 
    
    
    #Added as on 20170923 for Provision to create Production Slip for Buffer Stock by Karan
    slip_type = fields.Selection(related = 'main_id.slip_type',string = 'Production Type',store=1,default = 'buffer')
    
    
    '''
    Balance Qty Calculation
    '''
    
    @api.depends('quantity','scheduled_qty')
    def _compute_balance_qty(self):
        for order in self:
            balance_qty = 0.0            
            order.update({                
                'balance_qty': order.quantity - order.scheduled_qty 
            }) 
    
    '''
     Balance Qty Can't be -ve
    '''
    @api.one
    @api.constrains('balance_qty')
    def _check_balance_qty(self):
        if self.slip_type == 'based_on_order':
            if self.balance_qty < 0:
                raise ValidationError(
                "Balance Qty !!! Can't be Negative")    
        
        
    '''
    Scheduled can't be less than Current date
    '''
    #@api.one
    #@api.constrains('scheduled_date')
    #def _check_scheduled_date(self):
        #if self.scheduled_date < fields.Date.today():
            #raise ValidationError(
                #"Scheduled Date can't be less than current date!")
        
        
        
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as Units Of Measure, Store Qty,Last Purchase Date,etc.
    '''
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        available_stock = 0.0
        uom_id = 0
        description = ''
        cr.execute('''SELECT 
                            product_uom.id AS uom_id,  
                            product_template.name AS description 
                      FROM 
                            product_uom JOIN 
                            product_template ON 
                            product_uom.id=product_template.uom_id JOIN 
                            product_product ON 
                            product_template.id=product_product.product_tmpl_id 
                      WHERE 
                            product_product.id = CAST(%s AS INTEGER)''', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
        cr.execute('''SELECT 
                            available_stock 
                      FROM(
                      SELECT 
                            uom, 
                            product_id, 
                            name, 
                            product_qty as available_stock 
                            FROM(
                            SELECT 
                                  uom,
                                  product_id, 
                                  name, 
                                  sum(product_qty) as product_qty 
                                  FROM(
                                  SELECT 
                                        product_uom.name as uom,
                                        prakruti_stock.product_id, 
                                        product_product.name_template as name,
                                        prakruti_stock.product_qty
                                  FROM 
                                    product_uom JOIN 
                                    product_template ON 
                                    product_uom.id = product_template.uom_id JOIN 
                                    product_product ON 
                                    product_product.product_tmpl_id = product_template.id JOIN 
                                    prakruti_stock ON 
                                    prakruti_stock.product_id = product_product.id 
                                  WHERE 
                                    product_product.id = CAST(%s as integer)
                                      ) as a group by product_id, name, uom 
                                ) as a 
                            ) AS b 
                        ORDER BY product_id''', ((product_id),))
        for line in cr.dictfetchall():
            available_stock = line['available_stock']
        return {'value' :{
                    'uom_id':uom_id,
                    'description':description,
                    'store_qty': available_stock
                    }}
        
        
        
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''
    def create(self, cr, uid, vals, context=None):
        product_values = self.onchange_product(cr, uid, [], vals['product_id'])
        if product_values.get('value') or product_values['value'].get('store_qty'):
            vals['store_qty'] = product_values['value']['store_qty']
        return super(PrakrutiProductionSlipLine, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiProductionSlipLine, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        product_values = self.onchange_product(cr, uid, ids, store_type)
        if product_values.get('value') or product_values['value'].get('store_qty'):
            vals['store_qty'] = product_values['value']['store_qty']
        return super(PrakrutiProductionSlipLine, self).write(cr, uid, ids, vals, context=context)
        
        
        
        
        
        
        
        
        