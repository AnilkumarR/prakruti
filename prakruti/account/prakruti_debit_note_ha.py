'''
Company : EBSL
Author: Induja
Module: Debit Note  
Class 1: PrakrutiDebitNoteHa
Class 2: PrakrutiDebitNoteHaLine
Table 1 & Reference Id: prakruti_debit_note_ha ,order_line
Table 2 & Reference Id: prakruti_debit_note_ha_line,line_id
Updated By: Induja
Updated Date & Version: 20170831 ,0.1
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
import re
import logging

class PrakrutiDebitNoteHa(models.Model):
    _name='prakruti.debit.note.ha'
    _table='prakruti_debit_note_ha'
    _order='id desc'
    _rec_name='debit_note_no'
    
    order_line = fields.One2many('prakruti.debit.note.ha.line','line_id',string='Order Line')
    debit_note_no = fields.Char(string= 'Debit Note No.',readonly=1)
    debit_date = fields.Date(string= 'Date', default=fields.Date.today)
    purchase_return_id = fields.Many2one('prakruti.purchase_invoice',string = 'Select Invoice')
    vendor_id = fields.Many2one('res.partner',string = 'Vendor Name')
    dispatch_to = fields.Many2one('res.partner',string='Vendor Address')
    notes = fields.Text(string= 'Notes')
    return_id = fields.Many2one('prakruti.purchase_return',string='Return No.')
    company_address = fields.Many2one('res.company',string='Company Address',default=lambda self: self.env.user.company_id,readonly="True" )  
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods',string = 'Category')
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No" , default='PPPL-PUR-F-004' , readonly=1)
    revision_no = fields.Char(string = "Rev. No", default='01' , readonly=1)
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today , readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=1)
    to_name = fields.Many2one('res.users',string="Name") 
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager") 
    stores_incharge = fields.Many2one('res.users','Stores Incharge')
    
    
    total_no_of_products = fields.Integer(string="Total No of Products")
    proportionate_amount_to_products = fields.Float(string="Proportionate Amount to Products")
    freight_charges = fields.Float(string="Freight Charges")
    loading_and_packing_charges = fields.Float(string="Loading and Packing Charges")
    insurance_charges = fields.Float(string="Insurance Charges")
    other_charges =  fields.Float(string="Other Charges")
    all_additional_charges = fields.Float(string="All Additional Charges")
    total_amount_before_tax = fields.Float(string="Untaxed Amount")
    total_cgst_amount = fields.Float(string="CGST Amount")
    total_sgst_amount = fields.Float(string="SGST Amount")
    total_igst_amount = fields.Float(string="IGST Amount")
    total_gst_amount = fields.Float(string="Total GST")  
    total_amount_after_tax = fields.Float(string="Total")
    total_amount = fields.Float(string="Total Amount")
    total_taxable_value = fields.Float(string="Total Taxable Value")
    
    
            
    '''
    While Clicking this button calculation part will calculate Automatically
    '''
    @api.one
    @api.multi
    def calculate_total(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute(''' SELECT calculation_debit_note_ha(%s)''',((temp.id),))
        return {} 
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete '))
        return super(PrakrutiDebitNoteHa, self).unlink()
    
class PrakrutiDebitNoteHaLine(models.Model):
    _name = 'prakruti.debit.note.ha.line'
    _table = "prakruti_debit_note_ha_line"
    
    line_id = fields.Many2one('prakruti.debit.note.ha')    
    product_id = fields.Many2one('product.product',string= 'Product',readonly=1,required=1)
    uom_id = fields.Many2one('product.uom',string= 'Units')
    return_qty = fields.Float(string= 'Qty.',digits=(6,3))
    unit_price = fields.Float(string= 'Amount',digits=(6,3))
    total = fields.Float(string= 'Total',digits=(6,3))
    amount = fields.Float(string= 'Amount',digits=(6,3))    
    remarks= fields.Char(string="Remarks")    
    purchase_line_common_id = fields.Integer(string="Purchase Line ID") 
    hsn_code = fields.Char(string='HSN/SAC',readonly=1)
    discount_rate = fields.Float(string= 'Discount(%)',default=0)
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_rate = fields.Float(related='cgst_id.per_amount',string= 'CGST Rate',default=0,store=1)
    cgst_amount = fields.Float(string= 'CGST Amount')    
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_rate = fields.Float(related='sgst_id.per_amount',string= 'SGST Rate',default=0,store=1)
    sgst_amount = fields.Float(string= 'SGST Amount')    
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_rate = fields.Float(related='igst_id.per_amount',string= 'IGST Rate',default=0,store=1)
    igst_amount = fields.Float(string= 'IGST Amount')    
    taxable_value = fields.Float(string= 'Taxable Value',digits=(6,3)) 
    taxable_value_after_adding_other = fields.Float(string='Taxable Value After Adding Other Charges',digits=(6,3))
    proportionate_amount_to_products = fields.Float(related='line_id.proportionate_amount_to_products', string="Proportionate Amount to Products",store=1)
    gst_rate = fields.Float(string= 'GST Rate')
    taxable_value_with_charges = fields.Float(string= 'Taxable Value With Charges') 