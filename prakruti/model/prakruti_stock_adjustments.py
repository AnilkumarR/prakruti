'''
Company : EBSL
Author : Karan
Module : Stock Adjustments

Class 1 : PrakrutiStockAdjustments
Class 2 : PrakrutiStockAdjustmentsLine
Class 3 : PrakrutiAllProductLine

Table 1 & Reference Id : prakruti_stock_adjustments,adjustment_line,product_line
Table 2 & Reference Id : prakruti_stock_adjustments_line,adjustment_id
Table 3 & Reference Id : prakruti_all_product_line,main_id

Updated By : Karan 
Updated Date & Version : 2017/08/23 & 0.1
'''
from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
import re
import logging
from datetime import timedelta

class PrakrutiStockAdjustments(models.Model):
    _name= 'prakruti.stock_adjustments'
    _table= 'prakruti_stock_adjustments'
    _description= 'Prakruti Stock Adjustments'
    _rec_name= 'adjustment_name'
    _order="id desc"

    
    adjustment_line = fields.One2many('prakruti.stock_adjustments_line','adjustment_id',string= 'Adjustment Line')
    product_line = fields.One2many('prakruti.all_product_line','main_id',string= 'All Product Line')
    company_id= fields.Many2one('res.company',string='Company Address',default=lambda self: self.env.user.company_id)
    adjustment_name = fields.Char(string= 'Name',required= True)
    location_id = fields.Many2one('prakruti.stock_location',string= 'Location')
    entered_date = fields.Datetime(string= 'Date')
    status = fields.Selection([('wait','Draft'),('done','Stock Adjustment Done')],string= 'Status')
    product_id = fields.Many2one('product.product', related='adjustment_line.product_id', string='Product Name')
    list_flag = fields.Integer(string= 'List Flag',default=0)
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'entered_date': datetime.now(),
        'status': 'wait'
        } 
    '''
    updating stock
    '''
    @api.one
    @api.multi
    def action_done(self):
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
            cr.execute("""SELECT stock_adjustments(%s)""",((temp.id),))
            cr.execute("UPDATE  prakruti_stock_adjustments SET status = 'done' WHERE prakruti_stock_adjustments.id = cast(%s as integer)",((temp.id),))
        return {} 
    '''
    Listing All products 
    '''
    @api.one
    @api.multi
    def list_all_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        item_id = 0
        item_code = ' '
        item_uom_id = 0
        main_id = 0
        item_uom = ' '
        for temp in self:
            cr.execute(''' SELECT list_all_products(%s) ''', ((temp.id),))
        return {} 
    '''
    Deleting ALl Products
    '''
    @api.one
    @api.multi
    def delete_all_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_all_product_line WHERE main_id=%s",((temp.id),))
            cr.execute("UPDATE  prakruti_stock_adjustments SET list_flag = 0 WHERE prakruti_stock_adjustments.id = cast(%s as integer)",((temp.id),))
        return {}

class PrakrutiStockAdjustmentsLine(models.Model):
    _name= 'prakruti.stock_adjustments_line'
    _table= 'prakruti_stock_adjustments_line'
    _description= 'Prakruti Stock Adjustments Line'
    _order="id desc"
    
    adjustment_id = fields.Many2one('prakruti.stock_adjustments',string = 'Adjustment ID',readonly=1)
    product_id = fields.Many2one('product.product',string = 'Product Name',required=1)
    description = fields.Text(string = 'Description',readonly=1)
    uom_id = fields.Many2one('product.uom',string = 'UOM',readonly=1)
    stock_qty = fields.Float(string = 'Theoretical Quantity',readonly=1)
    real_qty = fields.Float(string = 'Adjustment Quantity')
    actual_qty = fields.Float(string = 'Actual Stock',compute = '_compute_actual_qty')
    
    @api.depends('stock_qty','real_qty')
    def _compute_actual_qty(self):
        for item in self:
            item.update({
                'actual_qty': item.stock_qty + item.real_qty
                })
    
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    _sql_constraints=[        
        ('unique_product','unique(product_id,adjustment_id)', 'Item(s) must be Unique')
        ]
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description,etc.
    ''' 
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        qty_aval = 0.0
        uom_id = 0
        description = ''
        stock_qty = 0.0
        cr.execute('''  SELECT 
                            product_uom.id AS uom_id, 
                            product_uom.name AS uom_name, 
                            product_template.name AS description,
                            product_template.group_ref AS group_ref 
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
        cr.execute('''  SELECT 
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
            stock_qty = line['available_stock']
        print 'UOM ID',uom_id
        print 'PRODUCT NAME',description
        print 'AVAILABLE STOCK',stock_qty
        return {'value' :{'uom_id':uom_id,
                          'description':description,
                          'stock_qty': stock_qty or 0.0
                          }}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''     
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_product(cr, uid, [], vals['product_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('stock_qty','description','uom_id'):
            vals['stock_qty'] = onchangeResult['value']['stock_qty']
            vals['description'] = onchangeResult['value']['description']
            vals['uom_id'] = onchangeResult['value']['uom_id']
        return super(PrakrutiStockAdjustmentsLine, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiStockAdjustmentsLine, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        onchangeResult = self.onchange_product(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('stock_qty','description','uom_id'):
            vals['stock_qty'] = onchangeResult['value']['stock_qty']
            vals['description'] = onchangeResult['value']['description']
            vals['uom_id'] = onchangeResult['value']['uom_id']
        return super(PrakrutiStockAdjustmentsLine, self).write(cr, uid, ids, vals, context=context)

class PrakrutiAllProductLine(models.Model):
    _name= 'prakruti.all_product_line'
    _table= 'prakruti_all_product_line'
    _description= 'Prakruti All Product Line'
    
    main_id = fields.Many2one('prakruti.stock_adjustments',string = 'Main ID',readonly=1)    
    item_id = fields.Many2one('product.product',string = 'Item Name')
    name_template = fields.Text(string = 'Name',readonly=1)
    item_code = fields.Text(string = 'Item Code',readonly=1)
    item_uom_id = fields.Many2one('product.uom',string = 'UOM',readonly=1)
    item_quantity = fields.Float(string = 'Stock',readonly=1)
    item_uom = fields.Char(string= 'UOM',readonly=1)