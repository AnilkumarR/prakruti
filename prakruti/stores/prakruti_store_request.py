'''
Company : EBSL
Author: Induja
Module: Store Request
Class 1: PrakrutiStoreRequest
Class 2: PrakrutiStoreRequestItem 
Table 1 & Reference Id: prakruti_store_request ,grid_id
Table 2 & Reference Id: prakruti_store_request_item,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''


# -*- coding: utf-8 -*-

from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
from openerp.exceptions import ValidationError
import re
import logging

class PrakrutiStoreRequest(models.Model):
    _name = 'prakruti.store_request'
    _table = "prakruti_store_request"
    _description = 'Store Request'
    _order='id desc'
    _rec_name = "store_request_no"
    
    
  
    '''Auto genereation function
    'Format: ST\REQ\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: ST\REQ\FG\0455\17-18
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
                                CAST(EXTRACT (month FROM request_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM request_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_store_request 
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
            cr.execute('''SELECT autogenerate_store_request_no(%s)''', ((temp.id),)  ) # Database function :autogenerate_store_request_no
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_store_request_no'];
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
                style_format[record.id] = 'ST\\'+'REQ\\'+'FG\\'+str(auto_gen) +'/'+str(display_present_year)+'-'+str(dispay_year)
            cr.execute('''UPDATE 
                                prakruti_store_request 
                          SET 
                                store_request_no =%s 
                          WHERE 
                                id=%s ''', ((style_format[record.id]),(temp.id),)  )
        return style_format
    
    
    grid_id = fields.One2many('prakruti.store_request_item', 'main_id',string='Grid') 
    purchase_type= fields.Selection([('extraction','Extraction'),('formulation','Formulation')],'Purchase Type')
    request_date = fields.Date('Request Date', required=True, default=fields.Date.today)    
    dept_id = fields.Many2one('res.company','Department')    
    company_id = fields.Many2one('res.company',string="Company")    
    store_request_no= fields.Char(string='Request No')    
    requested_by= fields.Many2one('res.users',string="Requested By",required=True)
    store_incharge = fields.Many2one('res.users','Store Incharge',readonly=True)
    plant_incharge = fields.Many2one('res.users',string="Plant Incharge",required=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    production_incharge = fields.Many2one('res.users',string="Production Incharge", required= True)
    doc_no = fields.Char(' Doc No')
    rev_no = fields.Char(' Rev No')  
    state =fields.Selection([
		('request', 'Request Draft'),
                ('approve','Store Request Approval'),
                ('partial_approve','Store Request Partially Approved'),
                ('issue','Store Issue'),
                ('partial_issue','Store Partially Issued'),
                ('issued','Store Issued'),
                ('extra_issue','Extra Issued')],default= 'request', string= 'Status')
    indent_disable_id = fields.Integer('Indent Disable')
    indent_increment_id = fields.Integer('Ident increment No')  
    req_no = fields.Char('Store Request Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    extraction_bom_id = fields.Integer(' Extraction BOM Common id')
    syrup_bom_id = fields.Integer(' Syrup BOM Common id')
    tablet_bom_id = fields.Integer('Tablet BOM Common id')
    powder_bom_id = fields.Integer(' Powder BOM Common id')
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No',readonly=1)
    coming_from = fields.Char(string = "Coming From")
    store_location_id= fields.Many2one('stock.location','Store Location')
    syrup_packing_bom_id = fields.Integer('Syrup Packing BOM Common id')
    tablet_packing_bom_id = fields.Integer('Tablet Packing BOM Common id')
    powder_packing_bom_id = fields.Integer('Powder Packing BOM Common id')
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Product",readonly=1)  
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')
    location_id = fields.Many2one('prakruti.stock_location','Store Location')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    
    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'purchase_type':'extraction',
        'store_request_no':'New',
        'requested_by': lambda s, cr, uid, c:uid,
        'store_incharge': lambda s, cr, uid, c:uid,
        'plant_incharge': lambda s, cr, uid, c:uid,
        'production_incharge': lambda s, cr, uid, c:uid,
        'company_id':_default_company,
        'indent_disable_id':1,
        }
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['approve','issue','partial_issue','partial_approve','issued'] or order.coming_from in ['Extraction BOM','Tablet BOM','Syrup BOM','Powder BOM']:
                raise UserError(_('Can\'t be Deleted'))
        return super(PrakrutiStoreRequest, self).unlink()
    
    
    '''
   ATLEAST ONE PRODUCT IS REQUIRED IN GRID
    '''  
    
    def _check_the_grid(self, cr, uid, ids, context=None, * args):
        for line_id in self.browse(cr, uid, ids, context=context):
            if len(line_id.grid_id) == 0:
                return False
        return True
    
    
    _constraints = [
         (_check_the_grid, 'Sorry !!!, Please Enter Some Products!', ['grid_id']),
    ]
    
    '''
    this button helps to update the stock in prakruti_store_request_item
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
                                prakruti_store_request_item 
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
                                        prakruti_store_request_item.id 
                                    FROM 
                                        product_template INNER JOIN 
                                        product_product  ON 
                                        product_product.product_tmpl_id = product_template.id INNER JOIN 
                                        prakruti_stock ON 
                                        prakruti_stock.product_id = product_product.id INNER JOIN 
                                        prakruti_store_request_item ON 
                                        prakruti_store_request_item.product_id = prakruti_stock.product_id 
                                    WHERE 
                                        prakruti_store_request_item.main_id = %s
                                      )as a 
                                    GROUP BY product_id,id
                                ) as b 
                            WHERE 
                                b.id = prakruti_store_request_item.id''',((temp.id),))
        return {}
    
    
    '''
    Pulls the data to store issue
    '''
    #REQUEST THAT COME FROM BOM DOESN'T REQUIRE APPROVAL SO DIRECT ISSUE LINK    
    @api.one
    @api.multi
    def action_to_issue(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}  
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Store Request')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)            
            cr.execute("SELECT count(id) as total_line FROM prakruti_store_request_item WHERE main_id = %s",((temp.id),))
            for item in cr.dictfetchall():
                total_line = item['total_line']            
            cr.execute("SELECT count(id) as avail_stock_line FROM prakruti_store_request_item WHERE main_id = %s AND store_qty > requested_quantity",((temp.id),))
            for item in cr.dictfetchall():
                avail_stock_line = item['avail_stock_line']
            print 'TOTAL LINE',total_line
            print 'STOCK AVAILABILITY LINE',avail_stock_line
            #if total_line == avail_stock_line:
            ebsl_id = self.pool.get('prakruti.store_issue').create(cr,uid, {
                'request_date':temp.request_date,
                'request_no':temp.store_request_no,
                'dept_id':temp.dept_id.id,
                'company_id':temp.company_id.id,
                'store_incharge':temp.store_incharge.id,
                'plant_incharge':temp.plant_incharge.id,
                'doc_no':temp.doc_no,
                'date':temp.date,
                'production_incharge':temp.production_incharge.id,
                'extraction_bom_id':temp.extraction_bom_id,
                'syrup_bom_id':temp.syrup_bom_id,
                'tablet_bom_id':temp.tablet_bom_id,
                'powder_bom_id':temp.powder_bom_id,
                'powder_packing_bom_id':temp.powder_packing_bom_id,
                'batch_no':temp.batch_no.id,
                'store_location_id':temp.store_location_id.id,
                'syrup_packing_bom_id':temp.syrup_packing_bom_id,                
                'tablet_packing_bom_id':temp.tablet_packing_bom_id,
                'subplant_id':temp.subplant_id.id,
                'coming_from':temp.coming_from
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                        'style_flag':item.style_flag,
                        'packing_flag':item.packing_flag,
                        'product_id':item.product_id.id,
                        'uom_id':item.uom_id.id,
                        'description':item.description,
                        'requested_quantity':item.requested_quantity,
                        'approved_quantity':item.requested_quantity,
                        'remarks':item.remarks,
                        'store_qty':item.store_qty,
                        'grid_common_id_bom':item.grid_common_id,
                        'grn_no': item.grn_no.id,
                        'ar_no': item.ar_no.id,
                        'extra_issued_qty': item.extra_issued_qty,
                        'extra_readonly_flag':item.extra_readonly_flag,
                        'extra_issued_packing':item.extra_issued_packing,
                        'request_line_id':item.id, 
                        'main_id':ebsl_id
                    })                
            cr.execute("UPDATE  prakruti_store_request SET state = 'issue' WHERE prakruti_store_request.id = cast(%s as integer)",((temp.id),))
        return {}
    
    '''
    Pulls the data to store Approve
    '''
    @api.one
    @api.multi
    def action_to_approve(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}  
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Store Request Approve')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            #print 'template_idtemplate_idtemplate_id',template_id
            #print 'email_objemail_objemail_objemail_obj',email_obj            
            cr.execute("SELECT count(id) as total_line FROM prakruti_store_request_item WHERE main_id = %s",((temp.id),))
            for item in cr.dictfetchall():
                total_line = item['total_line']            
            cr.execute("SELECT count(id) as avail_stock_line FROM prakruti_store_request_item WHERE main_id = %s AND store_qty > requested_quantity",((temp.id),))
            for item in cr.dictfetchall():
                avail_stock_line = item['avail_stock_line']
            print 'TOTAL LINE',total_line
            print 'STOCK AVAILABILITY LINE',avail_stock_line
            #if total_line == avail_stock_line:
            ebsl_id = self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                    'request_date':temp.request_date,
                    'request_no':temp.store_request_no,
                    'dept_id':temp.dept_id.id,
                    'company_id':temp.company_id.id,
                    'store_incharge':temp.store_incharge.id,
                    'plant_incharge':temp.plant_incharge.id,
                    'doc_no':temp.doc_no,
                    'date':temp.date,
                    'requested_by':temp.requested_by.id,
                    'production_incharge':temp.production_incharge.id,
                    'extraction_bom_id':temp.extraction_bom_id,
                    'syrup_bom_id':temp.syrup_bom_id,
                    'tablet_bom_id':temp.tablet_bom_id,
                    'batch_no':temp.batch_no.id,
                    'store_location_id':temp.store_location_id.id,                
                    'syrup_packing_bom_id':temp.syrup_packing_bom_id,
                    'powder_bom_id':temp.powder_bom_id,
                    'powder_packing_bom_id':temp.powder_packing_bom_id,
                    'tablet_packing_bom_id':temp.tablet_packing_bom_id
                    })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                        'style_flag':item.style_flag,
                        'packing_flag':item.packing_flag,
                        'product_id':item.product_id.id,
                        'uom_id':item.uom_id.id,
                        'description':item.description,
                        'requested_quantity':item.requested_quantity,
                        'approved_quantity':item.requested_quantity,
                        'store_qty':item.store_qty,
                        'remarks':item.remarks,
                        'grid_common_id':item.grid_common_id,
                        'grn_no': item.grn_no.id,
                        'ar_no': item.ar_no.id,
                        'extra_readonly_flag':item.extra_readonly_flag,
                        'extra_issued_packing':item.extra_issued_packing,
                        'request_line_id':item.id, 
                        'main_id':ebsl_id
                    })
            cr.execute("UPDATE  prakruti_store_request SET state = 'approve' WHERE prakruti_store_request.id = cast(%s as integer)",((temp.id),))
        return {}
    
class PrakrutiStoreRequestItem(models.Model):
    _name = 'prakruti.store_request_item'
    _table = "prakruti_store_request_item"
    _description = 'Store Request Item'
        
    main_id = fields.Many2one('prakruti.store_request',string="Grid", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product Name", required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    description = fields.Text(string = "Description", required=True)
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')
    requested_quantity = fields.Float(string = "Req.Quantity", required=True,digits=(6,3))
    remarks = fields.Text(string="Remarks")
    store_qty = fields.Float(string="Store Qty",digits=(6,3),readonly="1")
    grid_common_id = fields.Integer('Grid common id')
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.')
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.')
    extra_issued_qty =fields.Float(string='Extra Qty',digits=(6,3))    
    style_flag = fields.Integer(string= 'Style',default=0)
    packing_flag = fields.Integer(string= 'Packing',default=0)
    extra_readonly_flag = fields.Integer(string= 'Extra Flag',default=0)
    extra_issued_packing = fields.Float(string= 'Extra Packing',default=0,digits=(6,3))
    
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    
    _sql_constraints=[
        ('unique_product_id','unique(product_id,main_id)', 'Item(s) should be Unique')
        ]
    '''
    The Requested qty can't be -ve or 0
    '''
    @api.one
    @api.constrains('requested_quantity')
    def _check_requested_quantity(self):
        if self.requested_quantity < 0 :
            raise ValidationError(
                "Requested Qty. Can't be Negative or Zero !!!")  
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id etc.
    '''
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = False
            self.description = ''
            self.batch_no = ''
            self.requested_quantity = 0
            self.remarks = ''
            self.store_qty = 0.0
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description etc.
    '''
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        qty_aval = 0.0
        uom_id = 0
        description = ''
        qty_aval = 0
        purchase_date = False
        last_purchase_vendor_name = False
        uom_name = ''
        last_price = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id = cast(%s as integer)', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
        cr.execute('''SELECT 
                            qty_aval 
                      FROM(
                      SELECT 
                            uom, 
                            product_id, 
                            name, 
                            product_qty as qty_aval 
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
            qty_aval = line['qty_aval']
        cr.execute('''  SELECT ppl.unit_price AS last_price,ppo.vendor_id AS last_purchase_vendor_name, order_date AS purchase_date FROM prakruti_purchase_order AS ppo INNER JOIN prakruti_purchase_line AS ppl ON ppo.id = ppl.purchase_line_id WHERE ppl.product_id = CAST(%s as integer) and ppo.state = 'order_close' order by ppo.id DESC LIMIT 1''', ((product_id),))
        for line in cr.dictfetchall():
            last_price = line['last_price']
            purchase_date = line['purchase_date']
            last_purchase_vendor_name = line['last_purchase_vendor_name']
        print 'UOM ID',uom_id
        print 'AVAILABLE STOCK',qty_aval
        print 'PRODUCT NAME',description
        print 'VENDOR  NAME',last_purchase_vendor_name
        print 'LAST PRICE',last_price
        return {'value' :{'uom_id':uom_id,
                          'description':description,
                          'store_qty': qty_aval or 0.0
                          }}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''   
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_product(cr, uid, [], vals['product_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('store_qty'):
            vals['store_qty'] = onchangeResult['value']['store_qty']
        return super(PrakrutiStoreRequestItem, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiStoreRequestItem, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        onchangeResult = self.onchange_product(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('store_qty'):
            vals['store_qty'] = onchangeResult['value']['store_qty']
        return super(PrakrutiStoreRequestItem, self).write(cr, uid, ids, vals, context=context)
