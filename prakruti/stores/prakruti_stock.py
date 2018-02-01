'''
Company : EBSL
Author: Karan
Module: Stock
Class 1: prakrutiStock
Class 2: PrakrutiStockLocation
Table 1: prakruti_stock
Table 2: prakruti_stock_location
Created By: Karan
Created Date: 20170925
Updated Date & Version: 20170925 ,0.1
'''
# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models, _
from openerp.exceptions import except_orm, Warning as UserError
from datetime import date, datetime

class PrakrutiStockLocation(models.Model):
    _name = 'prakruti.stock_location'
    _table = 'prakruti_stock_location'
    _description = 'Stock Location'
    _order="id desc"
    
    name = fields.Char(string = 'Location Name')
    description = fields.Char(string = 'Description')
    remarks = fields.Char(string = 'Remarks')
    company_id = fields.Many2one('res.company',string = 'Company',default=lambda self: self.env.user.company_id,readonly=1)

class PrakrutiStock(models.Model):
    _name = 'prakruti.stock'
    _table = 'prakruti_stock'
    _description = 'Stock'
    _order="id desc"
    
    product_id = fields.Many2one('product.product', string = 'Product',readonly=1)
    uom_id = fields.Many2one('product.uom', string = 'UOM',readonly=1)
    entered_date = fields.Date(string = 'Date',readonly=1)
    location_id = fields.Many2one('prakruti.stock_location',string = 'Stock Location',readonly=1)
    origin = fields.Char(string = 'Origin',readonly=1)
    company_id = fields.Many2one('res.company',string = 'Company',default=lambda self: self.env.user.company_id,readonly=1)
    grn_id = fields.Many2one('prakruti.grn_inspection_details',string = 'GRN No',readonly=1)
    issue_id = fields.Many2one('prakruti.store_issue',string = 'Issue No',readonly=1)
    batch_id = fields.Many2one('prakruti.batch_master',string = 'Batch No',readonly=1)
    dispatch_id = fields.Many2one('prakruti.dispatch',string = 'Dispatch No',readonly=1)
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip No',readonly=1)
    adjustment_id = fields.Many2one('prakruti.stock_adjustments',string = 'Adjustment',readonly=1)
    inward_id = fields.Many2one('prakruti.production_inward',string = 'Inward No',readonly=1)
    sales_grn_id = fields.Many2one('prakruti.sales_return_grn',string = 'Return GRN No',readonly=1)
    virtual_qty = fields.Float(string = 'Virtual Qty',readonly=1)
    product_qty = fields.Float(string = 'Product Qty',readonly=1)
    reserved_qty = fields.Float(string = 'Reserved Qty',readonly=1)#If it is reserved than there will exists slip_id
    customer_id = fields.Many2one('res.partner',string = 'Customer',readonly=1)
    vendor_id = fields.Many2one('res.partner',string = 'Vendor/Supplier',readonly=1)
    mrn_id = fields.Many2one('prakruti.return_items',string = 'MRN No',readonly=1)
    remarks = fields.Text(string = 'Remarks',readonly=1)
    
    
    
    '''
    Cannot able to delete this record 
    '''
    
    @api.multi
    def unlink(self):
        raise UserError(_('Sorry... Record can\'t be Deleted...'))
        return super(PrakrutiStock, self).unlink()