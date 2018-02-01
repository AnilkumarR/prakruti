'''
Company : EBSL
Author: Induja
Module: Standard Product
Class 1: PrakrutiStandardProduct
Class 2: PrakrutiStandardProductLine
Table 1 & Reference Id: prakruti_standard_product ,subplant_line
Table 2 & Reference Id: prakruti_standard_product_line,standard_line_id
Updated By: Induja
Updated Date & Version: 20170828 ,0.1
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


#########################################################################################################


class PrakrutiStandardProduct(models.Model):
    _name = 'prakruti.standard_product'
    _table = 'prakruti_standard_product'
    _description = 'Standard Product '
    _order= "id desc"
    _rec_name="standard_batch_size"
    
    subplant_line= fields.One2many('prakruti.standard_product_line','standard_line_id',string="Standard Line")
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant",required=True)
    standard_batch_size= fields.Float(string="Standard Batch Size",required=True,digits=(6,3))
    standard_output_yield= fields.Float(string="Standard Output Yield",required=True,digits=(6,3))
    duplicate_flag = fields.Char(string= 'Duplicate Flag',default=0,readonly=True)
    is_duplicate = fields.Boolean(string= 'Is a Duplicate',default=False,readonly=True) 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    
    _sql_constraints = [('subplant_with_standard_batch_size', 'unique(subplant_id,standard_batch_size)','Subplant and Batch Size must be Unique !')]  
    
    @api.one
    @api.constrains('standard_batch_size')
    def _check_standard_batch_size(self):
        if self.standard_batch_size <= 0:
            raise ValidationError(
                "Standard Batch Size !!! Can't be Negative OR 0 ")
        
    @api.one
    @api.constrains('standard_output_yield')
    def _check_standard_output_yield(self):
        if self.standard_output_yield <= 0:
            raise ValidationError(
                "Standard Output Yield !!! Can't be Negative OR 0 ")
    
    
    '''
    Duplicate Standard Product
    '''
    @api.one
    @api.multi
    def duplicate_standard_bom(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            d_request = self.pool.get('prakruti.standard_product').create(cr,uid, {
                'subplant_id':temp.subplant_id.id,
                'standard_batch_size':0,
                'standard_output_yield':temp.standard_output_yield,
                'is_duplicate':'True',
                'duplicate_flag': 1
                })
            for item in temp.subplant_line:
                grid_values = self.pool.get('prakruti.standard_product_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'description': item.description,
                    'uom_id': item.uom_id.id,
                    'standard_value': item.standard_value,
                    'standard_line_id': d_request
                    })
        return {}
    '''
    Checking stock 
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
                                    prakruti_standard_product_line 
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
                                            standard_line_id,
                                            prakruti_standard_product_line.id 
                                        FROM 
                                            product_template INNER JOIN 
                                            product_product  ON 
                                            product_product.product_tmpl_id = product_template.id INNER JOIN 
                                            prakruti_stock ON 
                                            prakruti_stock.product_id = product_product.id INNER JOIN 
                                            prakruti_standard_product_line ON 
                                            prakruti_standard_product_line.product_id = prakruti_stock.product_id    
                                        WHERE 
                                            prakruti_standard_product_line.standard_line_id = %s
                                        )as a 
                                    GROUP BY product_id,id
                                    ) as b 
                                WHERE 
                                    b.id = prakruti_standard_product_line.id''',((temp.id),))
        return {}

class PrakrutiStandardProductLine(models.Model):
    _name= 'prakruti.standard_product_line'
    _table = 'prakruti_standard_product_line'
    _description = 'Standard Product Line'
    _order= "id desc"
    
    standard_line_id = fields.Many2one('prakruti.standard_product', string="Line ID",readonly=True)
    product_id= fields.Many2one('product.product', string="Name",required=True)
    description = fields.Text(string= 'Description',required=True)
    uom_id= fields.Many2one('product.uom', string="UOM",required=True)
    standard_value=fields.Float(string='Standard Qty',required=True,digits=(6,3))
    store_qty = fields.Float(string= 'Store Qty',digits=(6,3))
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description
    '''
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = 0
        description = ''
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id  WHERE product_product.id = cast(%s as integer)', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
        return {'value' :{
                'uom_id':uom_id,
                'description':description
                          }}
    
    
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description, Store qty etc
    '''
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        qty_aval = 0.0
        uom_id = 0
        description = ''
        store_qty = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description,product_template.group_ref AS group_ref FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id = cast(%s as integer)', ((product_id),))
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
            store_qty = line['qty_aval']
        print 'PRODUCT NAME',description
        print 'UOM ID',uom_id
        print 'AVAILABLE STOCK',store_qty
        return {'value' :{'uom_id':uom_id,
                          'description':description,
                          'store_qty': store_qty or 0.0,
                          }}