# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
import re
import logging

class PrakrutiSalesScrap(models.Model):    
    _name =  'prakruti.sales_scrap'
    _table = 'prakruti_sales_scrap'
    _description = 'This Scrap is filled by the returned items from GRN'
    _rec_name = 'grn_no'    
    _order="id desc"
    
    grn_no= fields.Char(string='GRN No', readonly=True)
    inward_no = fields.Char(string='PTN/Inward No')
    po_no= fields.Char(string='Order No', readonly=True)
    grn_date=fields.Date('Date', readonly=True)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=True)
    customer_id = fields.Many2one('res.partner',string='Customer', readonly=True)
    order_date = fields.Date(string='Order Date', readonly=True)
    company_id = fields.Many2one('res.company',string='Company', readonly=True)
    remarks= fields.Text('Remarks')
    state = fields.Selection([('scrap','Scrap')],default= 'scrap', string= 'Status')
    scrap_line = fields.One2many('prakruti.sales_scrap_line','scrap_line_id')
    coming_from = fields.Selection([('sales','Sales'),('purchase','Purchase'),('production','Production')],default= 'sales', string = "Coming From",readonly=True) 
    product_id = fields.Many2one('product.product', related='scrap_line.product_id', string='Product Name')
    terms=fields.Text('Terms and conditions')
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    reference_date= fields.Date(string='Ref Date')
    
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['scrap']:
                raise UserError(_('Can\'t Delete '))
        return super(PrakrutiSalesScrap, self).unlink()
    
class PrakrutiSalesScrapLine(models.Model):
    _name = 'prakruti.sales_scrap_line'
    _table = 'prakruti_sales_scrap_line'
    
    scrap_line_id = fields.Many2one('prakruti.sales_scrap', ondelete='cascade')
    product_id  = fields.Many2one('product.product', string="Product Name")
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    material_type= fields.Selection([('extraction','Extraction'),('formulation','Formulation')], string= 'Material Type', default= 'extraction')
    description = fields.Text(string="Description")
    quantity = fields.Float('Rejected Qty.',digits=(6,3))
    remarks = fields.Text(string="Remarks")
    state =fields.Selection([('scrap','Scrap'),
                              ('done','Done')],default= 'scrap', string= 'Status')