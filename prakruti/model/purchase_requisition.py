'''
Company : EBSL
Author : Karan
Module : Purchase Requisition
Class 1 : PurchaseRequisitionFromStores
Class 2 : PurchaseRequisitionLine
Table 1 & Reference Id : prakruti_purchase_requisition,requisition_line
Table 2 & Reference Id : prakruti_purchase_requisition_line,order_id
Updated By : Karan 
Updated Date & Version : 2017/08/21 & 0.1
'''

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


class PurchaseRequisitionFromStores(models.Model):
    _name = 'prakruti.purchase_requisition'
    _table = 'prakruti_purchase_requisition'
    _description = 'Purchase Requisition'
    _rec_name = 'requisition_no'
    _order="id desc" 
    
    '''
    Its an unique autogenerated requisition Number which will be in the format of
    Format : PR\PRODUCT_TYPE\NUMBER\FINANCIAL YEAR
    Example : PR\EXFG\0001\17-18
    Updated By : Karan
    Updated On : 2017/08/21
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
                                CAST(EXTRACT(month FROM requisition_date) AS INTEGER) AS month,
                                CAST(EXTRACT(year FROM requisition_date) AS INTEGER) AS year,
                                id 
                          FROM 
                                prakruti_purchase_requisition 
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
            cr.execute('''SELECT autogenerate_purchase_requistion(%s)''', ((temp.id),)  ) 
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_purchase_requistion'];
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
                if temp.purchase_type.group_code:
                    style_format[record.id] ='PR\\'+ temp.purchase_type.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                else:                        
                    style_format[record.id] ='PR\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE 
                                    prakruti_purchase_requisition 
                              SET 
                                    requisition_no = %s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
        return style_format
        
    requisition_line = fields.One2many('prakruti.purchase_requisition_line','order_id',string='Order Lines')
    requisition_date = fields.Datetime(string = "Requisition Date", readonly=1,  default=lambda *a: datetime.now())
    requisition_no = fields.Char(string = "Requisition No", readonly=1)
    document_no = fields.Char(string ="Document No" )
    revision_no = fields.Char(string = "Rev. No")
    remarks = fields.Text(string="Remarks")
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today)
    prepared_by = fields.Many2one('res.users','Prepared By',readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",required=1)
    stores_incharge = fields.Many2one('res.users',string="Stores Incharge",required=1)
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager",required=1)
    to_name = fields.Many2one('res.users',string="Name", required= 1)
    name1 = fields.Char('name1')
    requistion_no = fields.Char('Purchase Requisition Number', compute='_get_auto', readonly=1)    
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    purchase_type = fields.Many2one('product.group',string= 'Purchase Type')
    is_duplicate = fields.Boolean(string= 'Is a Duplicate',default=False,readonly=1)
    duplicate_flag = fields.Char(string= 'Duplicate Flag',default=0,readonly=1) 
    product_id = fields.Many2one('product.product', related='requisition_line.product_id', string='Product Name')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id)
    revise_status = fields.Selection([('revise_requisition','Revise Requisition'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    state = fields.Selection([
                ('requisition', 'Requisition Draft'),
                ('approve', 'Requisition Approval Draft'),
                ('partially_approved', 'Requisition Partially Approved'),
                ('requisition_analysis','Requisition Analysis'),
                ('partial_analysis','Requisition Partially Analyzed'),
                ('request','Purchase Price Request'),
                ('quotation','Purchase Quotation'),
                ('analysis','Purchase Quotation Analysis'),
                ('order','Purchase Order'),
                ('confirm','Purchase Order Confirmed'),
                ('in_transit','Logistic In Transit/Gate Pass Draft'),
                #('deliver',' Gate Pass Draft'),
                ('inward_done','Gate Inward Done '),
                ('grn','GRN Analysis/GRN'),
                ('qc_check','Quality Control Open'),
                ('validate','Quality Control Validated'),
                ('qc_ha','Quality Control Higher Approval'),
                ('qc_check_done','Quality Control Accepted'),
                ('partial_grn','GRN Partially Confirmed'),
                ('done','GRN Done'),
                ('rejected','Purchase Order Rejected')],default= 'requisition', string= 'Status')
    
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods')
    
    
    _defaults = {
        'requisition_no':'New',
        'prepared_by': lambda s, cr, uid, c:uid,
        'revise_id': lambda s, cr, uid, c:uid,
        'plant_manager': lambda s, cr, uid, c:uid,
        'stores_incharge': lambda s, cr, uid, c:uid,
        'purchase_manager': lambda s, cr, uid, c:uid,
        'to_name': lambda s, cr, uid, c:uid,
        'purchase_type': 2
        }
    
    '''
    Avoiding to do duplicate from the existing type
    '''
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Forbbiden to duplicate'), _('It Is not possible to duplicate from here...'))
    
    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ['requisition']:
                raise UserError(_('Can\'t Delete, Since the Requisition went for further Process.'))
        return super(PurchaseRequisitionFromStores, self).unlink() 
    
    '''
    One should not create Empty Requisition so this validation is required so to enter at least one entry
    '''
    def _check_the_grid(self, cr, uid, ids, context=None, * args):
        for line_id in self.browse(cr, uid, ids, context=context):
            if len(line_id.requisition_line) == 0:
                return False
        return True
    
    
    _constraints = [
         (_check_the_grid, 'Sorry !!!, Please enter some products to procced further, Thank You !', ['requisition_line']),
    ]
    
    '''
    Pulling data from requisition to approve screen
    '''
    @api.one
    @api.multi
    def action_approve_requistion(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        gf = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_id = self.pool.get('prakruti.purchase_requisition_approve').create(cr,uid, {
                'requisition_date':temp.requisition_date,
                'purchase_type':temp.purchase_type.id,
                'state': 'approve',
                'requisition_no':temp.requisition_no,
                'remarks':temp.remarks,
                'purchase_manager':temp.purchase_manager.id,
                'plant_manager':temp.plant_manager.id,
                'stores_incharge':temp.stores_incharge.id,
                'maintanence_manager':temp.prepared_by.id,
                'prepared_by':temp.prepared_by.id,
                'to_name':temp.to_name.id,
                'document_no':temp.document_no,
                'revision_no':temp.revision_no,
                'default_pr_date':temp.default_pr_date,
                'categorization':temp.categorization,
                'company_id':temp.company_id.id,
                'coming_from':'Purchase Requisition'
                })
            for item in temp.requisition_line:
                erp_id = self.pool.get('prakruti.purchase_requisition_approve_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'description': item.description,
                    'quantity_req': item.quantity_req,
                    'quantity': item.quantity_req,
                    'uom_id': item.uom_id.id,
                    'required_date': item.required_date,
                    'remarks': item.remarks,
                    'suggested_packing_size': item.suggested_packing_size,
                    'stock_on_pr_date_ref': item.stock_on_pr_date_ref,
                    'last_purchase_date': item.last_purchase_date,
                    'last_price': item.last_price,
                    'last_purchase_vendor_id': item.last_purchase_vendor_id.id,
                    'hsn_code':item.hsn_code,
                    'requisition_line_id':item.id,
                    'slip_id':item.slip_id.id,
                    'order_id': ebsl_id
                    })
            cr.execute("UPDATE  prakruti_purchase_requisition_approve SET state = 'approve' WHERE prakruti_purchase_requisition_approve.id = cast(%s as integer)",((temp.id),))
            cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'approve' WHERE prakruti_purchase_requisition.id = cast(%s as integer)",((temp.id),))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Purchase Requisition')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    '''
    To Create Duplicate purchase Requistionn
    '''
    @api.one
    @api.multi
    def duplicate_requisition(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Purchase Requisition Duplicate')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            ebsl_id = self.pool.get('prakruti.purchase_requisition').create(cr,uid, {
                'requisition_no':'Duplicate',
                'requisition_date':temp.requisition_date,
                'prepared_by':temp.prepared_by.id,
                'document_no':temp.document_no,
                'revision_no':temp.revision_no,
                'remarks':temp.remarks,
                'default_pr_date':temp.default_pr_date,
                'state':'requisition',
                'name1':temp.name1,
                'purchase_type':temp.purchase_type.id,
                'plant_manager':temp.plant_manager.id,
                'stores_incharge':temp.stores_incharge.id,
                'purchase_manager':temp.purchase_manager.id,
                'company_id':temp.company_id.id,
                'categorization':temp.categorization,
                'to_name':temp.to_name.id,
                'is_duplicate':'True',
                'duplicate_flag': 1
                })
            for item in temp.requisition_line:
                erp_id = self.pool.get('prakruti.purchase_requisition_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description': item.description,
                    'quantity_req': item.quantity_req,
                    'suggested_packing_size': item.suggested_packing_size,
                    'required_date': item.required_date,
                    'current_date': item.current_date,
                    'remarks': item.remarks,
                    'stock_on_pr_date_ref': item.stock_on_pr_date_ref,
                    'last_purchase_date': item.last_purchase_date,
                    'slip_id':item.slip_id.id,
                    'order_id': ebsl_id
                    })
        return {}
     
    '''
    This Button helps for Revision(If any changes need to be done in table 2 click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_requisition(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ebsl_id = self.pool.get('prakruti.purchase_requisition').create(cr,uid, {
                'requisition_no':temp.requisition_no,
                'requisition_date':temp.requisition_date,
                'prepared_by':temp.prepared_by.id,
                'document_no':temp.document_no,
                'revision_no':temp.revision_no,
                'remarks':temp.remarks,
                'default_pr_date':temp.default_pr_date,
                'state':temp.state,
                'name1':temp.name1,
                'purchase_type':temp.purchase_type.id,
                'plant_manager':temp.plant_manager.id,
                'stores_incharge':temp.stores_incharge.id,
                'purchase_manager':temp.purchase_manager.id,
                'to_name':temp.to_name.id,
                'auto_no':temp.auto_no,
                'req_no_control_id':temp.req_no_control_id,
                'is_duplicate':temp.is_duplicate,
                'duplicate_flag':temp.duplicate_flag,
                'product_id':temp.product_id.id,
                'company_id':temp.company_id.id,
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,                
                'revise_flag': 1
                })
            for item in temp.requisition_line:
                erp_id = self.pool.get('prakruti.purchase_requisition_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description': item.description,
                    'quantity_req': item.quantity_req,
                    'suggested_packing_size': item.suggested_packing_size,
                    'required_date': item.required_date,
                    'current_date': item.current_date,
                    'remarks': item.remarks,
                    'stock_on_pr_date_ref': item.stock_on_pr_date_ref,
                    'last_purchase_date': item.last_purchase_date,
                    'slip_id':item.slip_id.id,
                    'order_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_purchase_requisition SET revise_status = 'revise_requisition',is_revise = 'True' WHERE id = %s",((temp.id),))
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
                    cr.execute('''SELECT revise_purchase_requisition AS error_message FROM revise_purchase_requisition(%s,%s)''',((temp.id),(temp.requisition_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record Cannot Be Revised':
                        raise UserError(_('Record...Can\'t Be Revised...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {}
    
    @api.one
    @api.multi
    def check_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
                cr.execute('''  UPDATE 
                                    prakruti_purchase_requisition_line 
                                SET 
                                    stock_on_pr_date_ref= qty_aval 
                                FROM ( 
                                    SELECT 
                                        product_id,
                                        sum(product_qty) as qty_aval,
                                        id 
                                    FROM ( 
                                        SELECT 
                                            prakruti_stock.product_id, 
                                            prakruti_stock.product_qty,
                                            order_id,
                                            prakruti_purchase_requisition_line.id 
                                        FROM 
                                            product_template INNER JOIN 
                                            product_product  ON 
                                            product_product.product_tmpl_id = product_template.id INNER JOIN 
                                            prakruti_stock ON 
                                            prakruti_stock.product_id = product_product.id INNER JOIN 
                                            prakruti_purchase_requisition_line ON 
                                            prakruti_purchase_requisition_line.product_id = prakruti_stock.product_id    
                                        WHERE 
                                            prakruti_purchase_requisition_line.order_id = %s
                                        )as a 
                                        GROUP BY product_id,id
                                    ) as b 
                                WHERE 
                                    b.id = prakruti_purchase_requisition_line.id''',((temp.id),))# Database function :stock_sales_dispatch
        return {}
    
class PurchaseRequisitionLine(models.Model):
    _name = 'prakruti.purchase_requisition_line'
    _table = 'prakruti_purchase_requisition_line'
    _description = 'Purchase Requisition Line'  
     
    order_id = fields.Many2one('prakruti.purchase_requisition', string='Requisition Id',ondelete='cascade')
    product_id = fields.Many2one('product.product' , string="Product Name", required=1)
    description = fields.Text(string = "Description ")
    quantity_req = fields.Float(string = "Required Qty", required=1  ,digits=(6,3))
    suggested_packing_size = fields.Char(string="Suggested Packing Size")
    required_date = fields.Date(string="Required Date")
    current_date = fields.Date(string="Current Date")
    remarks = fields.Text(string="Remarks")
    uom_id = fields.Many2one('product.uom',string="UOM",required=1)    
    stock_on_pr_date_ref = fields.Float(string="Available Stock",readonly=1 ,digits=(6,3))
    last_purchase_date= fields.Date(string="Last Purchase Date",readonly=1)
    last_purchase_vendor_id= fields.Many2one('res.partner',string="Last Purchase Vendor Name") 
    last_price = fields.Float(string = "Last Purchase Price",digits=(6,3))
    hsn_code = fields.Char(string='HSN/SAC')
    #Added as per requirement for reserving the product based on the Planning Request
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip ID',readonly=1)
    
    _defaults = {
        'required_date':lambda *a: time.strftime('%Y-%m-%d'),
        'current_date':lambda *a: time.strftime('%Y-%m-%d')
        }
        
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product_id the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''
    def create(self, cr, uid, vals, context=None):
        product_values = self.onchange_product_id(cr, uid, [], vals['product_id'])
        if product_values.get('value') or product_values['value'].get('stock_on_pr_date_ref','last_purchase_date','last_purchase_vendor_id','last_price'):
            vals['stock_on_pr_date_ref'] = product_values['value']['stock_on_pr_date_ref']
            vals['last_purchase_date'] = product_values['value']['last_purchase_date']
            vals['last_purchase_vendor_id'] = product_values['value']['last_purchase_vendor_id']
            vals['last_price'] = product_values['value']['last_price']
        return super(PurchaseRequisitionLine, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PurchaseRequisitionLine, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        product_values = self.onchange_product_id(cr, uid, ids, store_type)
        if product_values.get('value') or product_values['value'].get('stock_on_pr_date_ref','last_purchase_date','last_purchase_vendor_id','last_price'):
            vals['stock_on_pr_date_ref'] = product_values['value']['stock_on_pr_date_ref']
            vals['last_purchase_date'] = product_values['value']['last_purchase_date']
            vals['last_purchase_vendor_id'] = product_values['value']['last_purchase_vendor_id']
            vals['last_price'] = product_values['value']['last_price']
        return super(PurchaseRequisitionLine, self).write(cr, uid, ids, vals, context=context)
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as Units Of Measure, Store Qty,Last Purchase Date,etc.
    '''
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        available_stock = 0.0
        uom_id = 0
        description = ''
        last_purchase_date = False
        last_purchase_vendor_id = 0
        uom_name = ''
        last_price = 0
        hsn_code = ''
        cr.execute('''SELECT 
                            product_uom.id AS uom_id, 
                            product_uom.name AS uom_name, 
                            product_template.name AS description,
                            product_template.hsn_code AS hsn_code 
                      FROM 
                            product_uom JOIN 
                            product_template ON 
                            product_uom.id=product_template.uom_id JOIN 
                            product_product ON 
                            product_template.id=product_product.product_tmpl_id 
                      WHERE 
                            product_product.id = cast(%s as integer)''', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
            hsn_code = line['hsn_code']
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
        cr.execute('''SELECT 
                            ppl.unit_price AS last_price,
                            ppo.vendor_id AS last_purchase_vendor_id, 
                            order_date AS last_purchase_date 
                      FROM 
                            prakruti_purchase_order AS ppo JOIN 
                            prakruti_purchase_line AS ppl ON 
                            ppo.id = ppl.purchase_line_id 
                      WHERE 
                            ppl.product_id = CAST(%s as integer) AND 
                            ppo.state = 'order_close' 
                      ORDER BY 
                            ppo.id DESC LIMIT 1''', ((product_id),))
        for line in cr.dictfetchall():
            last_price = line['last_price']
            last_purchase_date = line['last_purchase_date']
            last_purchase_vendor_id = line['last_purchase_vendor_id']
            print 'Last Purchase Price : ',last_price
            print 'Last Purchase Date : ',last_purchase_date
            print 'Last Purchase Vendor Name or ID : ',last_purchase_vendor_id
        return {'value' :{
                    'uom_id':uom_id,
                    'description':description,
                    'stock_on_pr_date_ref': available_stock,
                    'last_purchase_date': last_purchase_date, 
                    'last_purchase_vendor_id': last_purchase_vendor_id,
                    'last_price':last_price,
                    'hsn_code':hsn_code
                    }}
    '''
    The required date which will tell that on which date the material is required and the date should not be less than that the current date
    '''
    def _date_validation(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        required_date = obj.required_date
        current_date = obj.current_date
        if required_date < current_date:
            return False
        return True    
    '''
    The Qty shoud be always greater than Zero 
    '''
    def _check_qty(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for line in lines:
            if line.quantity_req <= 0:
                return False
        return True
     
    _constraints = [
         (_check_qty, 'Order quantity cannot be negative or zero !', ['quantity_req']),
         #(_date_validation, 'Your Required date should not be less than Current date',['required_date']),
         ]
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    _sql_constraints = [        
        ('unique_product_id','unique(product_id, order_id)', 'Item(s) should be Unique')
        ]