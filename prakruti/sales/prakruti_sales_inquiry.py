'''
Company : EBSL
Author: Induja
Module: Sales Inquiry
Class 1: PrakrutiSalesInquiry
Class 2: PrakrutiSalesInquiryItem
Table 1 & Reference Id: prakruti_sales_inquiry ,grid_id
Table 2 & Reference Id: prakruti_sales_inquiry_item,main_id
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


class PrakrutiSalesInquiry(models.Model):
    _name = 'prakruti.sales_inquiry'
    _table = "prakruti_sales_inquiry"
    _description = 'Sales Inquiry'
    _order="id desc"
    _rec_name= "inquiry_no"
    
    
    '''Auto genereation function'
    Format: SI\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SI\EXFG\0262\17-18
    Updated By : Induja
    Updated On : 20170822
    Version :0.1
   '''
   
    @api.one
    @api.multi
    def _get_auto(self):
        format_style = {}
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
                                CAST(EXTRACT (month FROM inquiry_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM inquiry_date) AS integer) AS year,
                                id 
                        FROM 
                                prakruti_sales_inquiry 
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
                cr.execute('''SELECT autogenerate_sales_inquiry(%s)''', ((temp.id),)  ) #Database Function - autogenerate_sales_inquiry
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_sales_inquiry'];
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
                        format_style[record.id] = 'SI\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:                        
                       format_style[record.id] = 'SI\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE 
                                        prakruti_sales_inquiry 
                                  SET 
                                        inquiry_no =%s 
                                  WHERE 
                                        id=%s ''', ((format_style[record.id]),(temp.id),)  )
            return format_style
 
    
    grid_id = fields.One2many('prakruti.sales_inquiry_item', 'main_id',string='Grid')
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    inquiry_date= fields.Date('Inquiry Date', default=fields.Date.today,readonly=1)
    inquiry_no = fields.Char(' Inquiry No',readonly=1,default='New')
    requested_id =fields.Many2one('res.users','Requested By',readonly=1)
    customer_id = fields.Many2one('res.partner',string="Customer", required=1)
    remarks = fields.Text(string="Remarks")
    terms_id=fields.Text('Terms and conditions')
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    state =fields.Selection([
                    ('inquiry', 'Draft Inquiry'),
                    ('quotation','Sales Quotation'),
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
                    
                    ('short_close','Sales Order Short Closed'),                    
                    ('rejected','Sales Order Rejected')
                    ],default= 'inquiry', string= 'Status')
    inq_no = fields.Char('Inquiry Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id1 = fields.Integer('Auto Generating id',default= 0)
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    reference_date= fields.Date(string='Ref Date', default=fields.Date.today) 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')    
    company_address = fields.Many2one('res.company',string="Company Address")
    revise_status = fields.Selection([('revise_inquiry','Revise Inquiry'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'requested_id': lambda s, cr, uid, c:uid,
        'revision_no':lambda s, cr, uid, c:uid,
        'product_type_id':5,
        'revise_id': lambda s, cr, uid, c:uid   
        }

    #@api.multi
    #def print_inquiry(self):
        #self.filtered(lambda s: s.state == 'inquiry').write({'state': 'quotation'})
        #return self.env['report'].get_action(self, 'prakruti.sales.report_salesinquiry')
    
    '''
    Cannot able to delete this record if state not in inquiry 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ['inquiry']:
                raise UserError(_('Can\'t Delete, Since the Inquiry went for further Process.'))
        return super(PrakrutiSalesInquiry, self).unlink()
    
    
    '''
    This will tell if there is no items in Inquiry atleast 1 product entry is required
    '''
    def _check_the_grid(self, cr, uid, ids, context=None, * args):
        for line_id in self.browse(cr, uid, ids, context=context):
            if len(line_id.grid_id) == 0:
                return False
        return True
     
    _constraints = [
         (_check_the_grid, 'Enter Some Products To Proceed Further !', ['grid_id'])
                ]
    
    '''
    This will helps to pull the data to another screen and this will create new record in Quotation screen
    ''' 
    @api.one
    @api.multi
    def action_to_quotation(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}  
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales Inquiry')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True) 
            cr.execute("SELECT count(id) as no_of_line FROM prakruti_sales_inquiry_item WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                no_of_line = line['no_of_line']            
            cr.execute("SELECT count(distinct(product_id)) as no_of_product_line FROM prakruti_sales_inquiry_item WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                no_of_product_line = line['no_of_product_line']
            if no_of_line == no_of_product_line:
                ebsl_id = self.pool.get('prakruti.sales_quotation').create(cr,uid, {
                    'reference_no':temp.reference_no,   
                    'revision_no':temp.revision_no,
                    'customer_id':temp.customer_id.id,
                    'shipping_id':temp.shipping_id.id,
                    'billing_id':temp.billing_id.id,
                    'terms':temp.terms_id,
                    'inquiry_no':temp.inquiry_no,
                    'remarks':temp.remarks,
                    'product_type_id':temp.product_type_id.id,
                    'requested_id':temp.requested_id.id,
                    'company_address':temp.company_address.id,
                    'inquiry_date':temp.inquiry_date,
                    'reference_date':temp.reference_date,
                    })
                for item in temp.grid_id:
                    erp_id = self.pool.get('prakruti.sales_quotation_line').create(cr,uid, {
                        'product_id':item.product_id.id,
                        'uom_id':item.uom_id.id,
                        'description':item.description,
                        'specification_id':item.specification_id.id,
                        'material_type':item.material_type,
                        'quantity':item.quantity,
                        'remarks':item.remarks,
                        'actual_unit_price':item.actual_unit_price,
                        'hsn_code':item.hsn_code,
                        'inquiry_line_id':item.id, 
                        'sale_price':item.sale_price, 
                        'main_id':ebsl_id
                    })
            else:
                raise UserError(_('Can\'t Proceed, Since Product line is having Duplicate Entries.'))
            cr.execute("UPDATE  prakruti_sales_inquiry SET state = 'quotation' WHERE prakruti_sales_inquiry.id = cast(%s as integer)",((temp.id),))
        return {}
    
    
    
    '''
    This Button helps for Revision(If any changes need to be done in table 2 click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_inquiry(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            #LET US TAKE A BACKUP OF EXISTING ENTRY SO TO KEEP TRACK OF OLDER RECORDS JUST LIKE THE DUPLICATION
            ebsl_id = self.pool.get('prakruti.sales_inquiry').create(cr,uid, {
                'reference_no':temp.reference_no,
                'revision_no':temp.revision_no,
                'inquiry_date':temp.inquiry_date,
                'inquiry_no':temp.inquiry_no,
                'requested_id':temp.requested_id.id,
                'customer_id':temp.customer_id.id,
                'remarks':temp.remarks,
                'terms_id':temp.terms_id,
                'product_type_id':temp.product_type_id.id,
                'state':temp.state,
                'shipping_id':temp.shipping_id.id,
                'billing_id':temp.billing_id.id,
                'reference_date':temp.reference_date,
                'company_address':temp.company_address.id,
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,                
                'revise_flag': 1
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.sales_inquiry_item').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'specification_id': item.specification_id.id,
                    'material_type': item.material_type,
                    'description': item.description,
                    'remarks': item.remarks,
                    'quantity':item.quantity,
                    'actual_unit_price': item.actual_unit_price,
                    'hsn_code': item.hsn_code,
                    'sale_price':item.sale_price,
                    'main_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_sales_inquiry SET revise_status = 'revise_inquiry',is_revise = 'True' WHERE id = %s",((temp.id),))
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
        error_message = ''
        for temp in self:
            if temp.revise_remarks:
                if temp.revise_id:
                    cr.execute('''SELECT revise_sales_inquiry AS error_message FROM revise_sales_inquiry(%s,%s)''',((temp.id),(temp.inquiry_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record Cannot Be Revised':
                        raise UserError(_('Record...Can\'t Be Revised...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 
    
    
    
class PrakrutiSalesInquiryItem(models.Model):
    _name = 'prakruti.sales_inquiry_item'
    _table = "prakruti_sales_inquiry_item"
    _description = 'Sales Inquiry Item'
   
   
    main_id = fields.Many2one('prakruti.sales_inquiry',string="Grid", ondelete='cascade')
    product_id  = fields.Many2one('product.product', string="Product Name",required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    material_type= fields.Selection([('extraction','Extraction'),('formulation','Formulation')], string= 'Material Type', default= 'extraction')
    description = fields.Text(string="Description")
    remarks = fields.Text(string="Remarks")
    quantity = fields.Float(string = "Req Qty",required=True,digits=(6,3))
    actual_unit_price=fields.Float(string="Unit Price",digits=(6,3))
    hsn_code = fields.Char(string='HSN/SAC')
    
    serial_number = fields.Integer(compute = '_compute_serial_no',string = 'Compute Serial Number')
    serial_no = fields.Integer('Sl No',readonly=1,default=1)
    sale_price=fields.Float(string="Minimum Sale Price",digits=(6,3)) 
    
    def _compute_serial_no(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line in first_line_rec.main_id.grid_id:
                line.serial_no = line_num
                line_num += 1
    
    '''
    If any specification is there for particular product means it will automatically update the specification while selecting that particular product
    '''
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.specification_id = False
   
    
    '''
    If any uom id, description, unit price,hsn code is there for particular product then this will automatically dispalys for that particular product
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
    Negative Value Validation()
    '''
    def _check_qty(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for line in lines:
            if line.quantity <= 0:
                return False
        return True
     
    _constraints = [
         (_check_qty, 'Requested quantity cannot be negative or zero !', ['quantity'])
         ]