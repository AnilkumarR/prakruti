'''
Company : EBSL
Author : Karan
Module : Purchase Requisition Approval
Class 1 : PurchaseRequisitionFromStoresApprove
Class 2 : PurchaseRequisitionLineApprove
Table 1 & Reference Id : prakruti_purchase_requisition_approve,requisition_line
Table 2 & Reference Id : prakruti_purchase_requisition_approve_line,order_id
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
from operator import itemgetter


class PurchaseRequisitionFromStoresApprove(models.Model):
    _name = 'prakruti.purchase_requisition_approve'
    _table = 'prakruti_purchase_requisition_approve'
    _description = 'Purchase Requisition Approval'
    _rec_name = 'requisition_no'
    _order="id desc"  
        
    requisition_line = fields.One2many('prakruti.purchase_requisition_approve_line','order_id',string='Order Lines')
    requisition_date = fields.Datetime(string = "Requisition Date")
    requisition_no = fields.Char(string = "Requisition No", readonly=True)
    remarks = fields.Text(string="Remarks")
    prepared_by = fields.Many2one('res.users','Requisition By',readonly=True)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=True)
    stores_incharge = fields.Many2one('res.users',string="Stores Incharge",readonly=True)
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager",readonly=True)
    to_name = fields.Many2one('res.users',string="Name", readonly= True)
    purchase_type = fields.Many2one('product.group',string= 'Purchase Type')
    approved_date = fields.Datetime(string = "Approve Date")
    approved_by = fields.Many2one('res.users','Approved By')
    product_id = fields.Many2one(related='requisition_line.product_id', string="Product Name")
    revise_status = fields.Selection([('revise_requisition','Revise Requisition'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    coming_from = fields.Char(string= 'Coming From',readonly=1)
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    state = fields.Selection([
                #('requisition', 'Draft Requisition'),
                ('approve', 'Requisition Approval Draft'),
                ('partially_approved', 'Requisition Partially Approved'),
                #('partial_confirm','Requisition Partially Confirmed'),
                ('requisition_analysis','Requisition Analysis'),
                ('partial_analysis','Requisition Partial Analysis'),
                ('request','Request'),
                ('quotation','Quotation'),
                ('analysis','Quotation Analysis'),
                ('order','Order'),
                ('rejected','Rejected'),
                ('confirm','Order Confirm')],default= 'approve', string= 'Status')
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods')
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No" , default='PPPL-PUR-F-004' , readonly=1)
    revision_no = fields.Char(string = "Rev. No", default='01' , readonly=1)
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today , readonly=1)
    company_id = fields.Many2one('res.company',string='Company',readonly=1)
    
    
    _defaults = {
        'approved_date':lambda *a: time.strftime('%Y-%m-%d'),
        'approved_by': lambda s, cr, uid, c:uid,
        'revise_id': lambda s, cr, uid, c:uid   
        }
    
    '''
    Strictly not allowing to delete the record
    '''
    @api.multi
    def unlink(self):
        for order in self:
            raise UserError(_('Can\'t Delete...'))
        return super(PurchaseRequisitionFromStoresApprove, self).unlink()
    
    '''
    Pulling data from Approve to Requisition Analysis
    '''
    @api.one
    @api.multi
    def action_approve_analysis(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            cr.execute("SELECT count(id) as approve_line from prakruti_purchase_requisition_approve_line where (status='approve' or status='partial_approve' or status='reject') and order_id = %s", ((temp.id),))
            for line in cr.dictfetchall():
                approve_line=line['approve_line']
            if approve_line:
                ebsl_id = self.pool.get('prakruti.purchase_requistion_analysis').create(cr,uid, {
                    'inquiry_no': 'From Requisition',
                    'request_date':temp.requisition_date,
                    'purchase_type':temp.purchase_type.id,
                    'state': 'requisition_analysis',
                    'request_no':temp.requisition_no,
                    'remarks':temp.remarks,
                    'purchase_manager':temp.prepared_by.id,
                    'stores_incharge':temp.stores_incharge.id,
                    'maintanence_manager':temp.prepared_by.id,
                    'approved_by':temp.approved_by.id,
                    'approved_date':temp.approved_date,
                    'to_name':temp.to_name.id,
                    'categorization':temp.categorization,
                    'plant_manager':temp.plant_manager.id,
                    'company_id':temp.company_id.id,
                    'document_no':temp.document_no,
                    'revision_no':temp.revision_no,
                    'default_pr_date':temp.default_pr_date,
                    'coming_from':'Requisition Approval'
                    })
                cr.execute("SELECT product_id,description,quantity,uom_id,required_date,remarks,last_price,last_purchase_date,last_purchase_vendor_id,hsn_code,requisition_line_id,slip_id from prakruti_purchase_requisition_approve_line where order_id = %s and  (status='approve' or status='partial_approve')", ((temp.id),))
                for item in cr.dictfetchall():
                    product_id=item['product_id']
                    description=item['description']
                    quantity=item['quantity']
                    uom_id=item['uom_id']
                    required_date=item['required_date']
                    remarks=item['remarks']
                    last_price=item['last_price']
                    last_purchase_date=item['last_purchase_date']
                    last_purchase_vendor_id=item['last_purchase_vendor_id']
                    hsn_code=item['hsn_code']
                    requisition_line_id=item['requisition_line_id']
                    slip_id=item['slip_id']
                    erp_id = self.pool.get('prakruti.purchase_requistion_analysis_line').create(cr,uid, {
                        'product_id': product_id,
                        'description': description,
                        'quantity_req': quantity,
                        'uom_id': uom_id,
                        'required_date': required_date,
                        'remarks': remarks,
                        'last_price': last_price,
                        'last_purchase_date': last_purchase_date,
                        'last_purchase_vendor_id': last_purchase_vendor_id,
                        'hsn_code':hsn_code,
                        'requisition_line_id':requisition_line_id,
                        'slip_id':slip_id,
                        'requistion_line_id': ebsl_id
                        })
            else:
                raise UserError(_('Please Select Status For The Products'))
            cr.execute("SELECT quantity,quantity_req from prakruti_purchase_requisition_approve_line where order_id = %s and  (status='approve' or status='partial_approve')", ((temp.id),))
            for line in cr.dictfetchall():
                quantity=line['quantity']
                quantity_req=line['quantity_req']
            if quantity_req == quantity:
                #cr.execute("UPDATE  prakruti_purchase_requistion_analysis SET state = 'requisition_analysis' WHERE prakruti_purchase_requistion_analysis.id = cast(%s as integer)",((temp.id),))
                cr.execute("UPDATE  prakruti_purchase_requisition_approve SET state = 'requisition_analysis' WHERE prakruti_purchase_requisition_approve.id = cast(%s as integer)",((temp.id),))
                cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'requisition_analysis' WHERE prakruti_purchase_requisition.requisition_no = %s",((temp.requisition_no),))
            else:
                #cr.execute("UPDATE  prakruti_purchase_requistion_analysis SET state = 'partially_approved' WHERE prakruti_purchase_requistion_analysis.id = cast(%s as integer)",((temp.id),))
                cr.execute("UPDATE  prakruti_purchase_requisition_approve SET state = 'partially_approved' WHERE prakruti_purchase_requisition_approve.id = cast(%s as integer)",((temp.id),))
                cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'partially_approved' WHERE prakruti_purchase_requisition.requisition_no = %s",((temp.requisition_no),))
            
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Purchase Approve')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    '''
    This Button helps for Revision(If any changes need to be done in prakruti_purchase_requistion_analysis_line click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_requisition(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ebsl_id = self.pool.get('prakruti.purchase_requisition_approve').create(cr,uid, {
                'requisition_no':temp.requisition_no,
                'requisition_date':temp.requisition_date,
                'prepared_by':temp.prepared_by.id,
                'remarks':temp.remarks,
                'state':temp.state,
                'purchase_type':temp.purchase_type.id,
                'plant_manager':temp.plant_manager.id,
                'stores_incharge':temp.stores_incharge.id,
                'purchase_manager':temp.purchase_manager.id,
                'to_name':temp.to_name.id,
                'product_id':temp.product_id.id,
                'approved_date':temp.approved_date,
                'approved_by':temp.approved_by.id,
                'coming_from':temp.coming_from,
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id, 
                'categorization':temp.categorization,
                'company_id':temp.company_id.id,
                'document_no':temp.document_no,
                'revision_no':temp.revision_no,
                'default_pr_date':temp.default_pr_date,               
                'revise_flag': 1
                })
            for item in temp.requisition_line:
                erp_id = self.pool.get('prakruti.purchase_requisition_approve_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description': item.description,
                    'quantity': item.quantity,
                    'quantity_req': item.quantity_req,
                    'suggested_packing_size': item.suggested_packing_size,
                    'required_date': item.required_date,
                    'current_date': item.current_date,
                    'remarks': item.remarks,
                    'stock_on_pr_date_ref': item.stock_on_pr_date_ref,
                    'last_purchase_date': item.last_purchase_date,
                    'revise_req_approve_line':item.revise_req_approve_line,
                    'slip_id':item.slip_id.id,
                    'order_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_purchase_requisition_approve SET revise_status = 'revise_requisition',is_revise = 'True' WHERE id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_purchase_requisition_approve_line SET revise_req_approve_line = 1 WHERE order_id = %s",((temp.id),))
            
        return {} 
    '''
    After doing changes in prakruti_purchase_requistion_analysis_line click this to visible Revise button and to update the changes in the screen
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
                    cr.execute("UPDATE prakruti_purchase_requisition_approve_line SET revise_req_approve_line = 2 WHERE order_id = %s",((temp.id),))
                    cr.execute('''SELECT revise_purchase_requisition_approve AS error_message FROM revise_purchase_requisition_approve(%s,%s)''',((temp.id),(temp.requisition_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record Cannot Be Revised':
                        raise UserError(_('Record...Can\'t Be Revised...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {}
    
    '''
    This will reject the order directly from here and will affect on both approve and requisition screen
    '''
    @api.one
    @api.multi 
    def action_reject(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            if temp.remarks:
                cr.execute("UPDATE  prakruti_purchase_requisition_approve SET state = 'rejected' WHERE prakruti_purchase_requisition_approve.id = %s",((temp.id),))
                cr.execute("UPDATE  prakruti_purchase_requisition SET state = 'rejected' WHERE prakruti_purchase_requisition.requisition_no = %s",((temp.requisition_no),))
            else:
                raise UserError(_('Please Enter Remarks...'))
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
                                    prakruti_purchase_requisition_approve_line 
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
                                            prakruti_purchase_requisition_approve_line.id 
                                        FROM 
                                            product_template INNER JOIN 
                                            product_product  ON 
                                            product_product.product_tmpl_id = product_template.id INNER JOIN 
                                            prakruti_stock ON 
                                            prakruti_stock.product_id = product_product.id INNER JOIN 
                                            prakruti_purchase_requisition_approve_line ON 
                                            prakruti_purchase_requisition_approve_line.product_id = prakruti_stock.product_id    
                                        WHERE 
                                            prakruti_purchase_requisition_approve_line.order_id = %s
                                        )as a 
                                        GROUP BY product_id,id
                                    ) as b 
                                WHERE 
                                    b.id = prakruti_purchase_requisition_approve_line.id''',((temp.id),))# Database function :stock_sales_dispatch
        return {}
    
    
class PurchaseRequisitionLineApprove(models.Model):
    _name = 'prakruti.purchase_requisition_approve_line'
    _table = 'prakruti_purchase_requisition_approve_line'
    _description = 'Purchase Requisition Approval Line'  
    
    order_id = fields.Many2one('prakruti.purchase_requisition_approve', string='Approve Id', ondelete='cascade')
    product_id = fields.Many2one('product.product' , string="Product Name", required=True)
    description = fields.Text(string = "Description ")
    quantity_req = fields.Float(string = "Qty. Req", required=True ,digits=(6,3) )
    quantity = fields.Float(string = "Quantity Approved", required=True ,digits=(6,3))
    suggested_packing_size = fields.Char(string="Suggested Packing Size")
    required_date = fields.Date(string="Required Date")
    current_date = fields.Date(string="Current Date")
    remarks = fields.Text(string="Remarks")
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)    
    stock_on_pr_date_ref = fields.Float(string="Available Stock",store=True,readonly=True ,digits=(6,3))
    last_purchase_date= fields.Date(string="Last Purchase Date",store=True,readonly=True)
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    last_purchase_vendor_id= fields.Many2one('res.partner',string="Last Purchase Vendor Name",readonly=True) 
    last_price = fields.Float(string = "Last Purchase Price", readonly=True ,digits=(6,3))
    hsn_code = fields.Char(string='HSN/SAC')
    requisition_line_id = fields.Integer(string= 'Requisition Line ID',readonly=1)
    status = fields.Selection([
                ('approve','Approved'),
                ('partial_approve','PartiallyApproved'),
                ('reject','Reject')],default= 'approve', string= 'Status')
    #Added as per requirement for reserving the product based on the Planning Request
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip ID',readonly=1)
    #added to  keep the grid is in readonly after revise
    revise_req_approve_line = fields.Integer(string= 'Revised Flag',default=0)
    
    _defaults = {
        'required_date':lambda *a: time.strftime('%Y-%m-%d'),
        'current_date':lambda *a: time.strftime('%Y-%m-%d')
        }
    
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
    Validation for Qty
    '''
    @api.one
    @api.constrains('quantity')
    def _check_quantity(self):
        if (self.quantity > self.quantity_req) or self.quantity <= 0:
            raise openerp.exceptions.ValidationError(
                "Please Check Qty") 
    '''
    Required Date can't be < than current date
    '''
    #@api.one
    #@api.constrains('required_date')
    #def _check_required_date(self):
        #if self.required_date < fields.Date.today():
            #raise openerp.exceptions.ValidationError(
                #"Can't Select Back Date!")