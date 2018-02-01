# -*- coding: utf-8 -*-
from openerp import models, fields, api

class prakruti_reserved_product(models.Model):
    _name = 'prakruti.reserved_product'
    _table = 'prakruti_reserved_product'
    _description = 'Reserved Product'
    _order= "id desc"
    
    
    
    
    slip_id = fields.Many2one('prakruti.production_slip',string='Slip No',readonly = 1)
    subplant_id = fields.Many2one('product.product',string = 'Subplant',readonly = 1)
    product_id = fields.Many2one('product.product',string = 'Product',readonly=1)
    reserved_qty = fields.Float(string = 'Reserved Qty',digits = (6,3),readonly = 1,default = 0.000)
    consumed_qty = fields.Float(string = 'Consumed Qty',digits = (6,3),readonly = 1,default = 0.000)
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")