'''
Company : EBSL
Author: Induja
Module: Credit Note
Class 1: PrakrutiDebitNote
Class 2: PrakrutiDebitNoteLine
Table 1 & Reference Id: prakruti_debit_note ,order_line
Table 2 & Reference Id: prakruti_debit_note_line,line_id
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



class PrakrutiDebitNote(models.Model):
    _name='prakruti.debit.note'
    _table='prakruti_debit_note'
    _description = 'Debit Note'
    _order='id desc'
    _rec_name='debit_note_no'
    
    
  
    '''Auto genereation function
    'Format: DN\AUTO GENERATE NO\FINANCIAL YEAR
    Example: DN\0455\17-18
    Updated By : Induja
    Updated On : 20170831
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
                                CAST(EXTRACT (month FROM debit_date) AS integer) AS month ,
                                CAST(EXTRACT (year FROM debit_date) AS integer) AS year ,
                                id
                          FROM 
                                prakruti_debit_note 
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
                cr.execute('''SELECT autogenerate_debit_note(%s)''', ((temp.id),)  ) 
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_debit_note'];
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
                    style_format[record.id] = 'DN\\'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE 
                                    prakruti_debit_note 
                              SET 
                                    debit_note_no =%s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
   
    
    order_line = fields.One2many('prakruti.debit.note.line','line_id',string='Order Line')
    debit_note_no = fields.Char(string= 'Debit Note No.',readonly=1,default='New')
    debit_date = fields.Date(string= 'Date', default=fields.Date.today)
    purchase_return_id = fields.Many2one('prakruti.purchase_invoice',string = 'Select Invoice')
    vendor_id = fields.Many2one('res.partner',string = 'Vendor Name')
    dispatch_to = fields.Many2one('res.partner',string='Vendor Address')
    notes = fields.Text(string= 'Notes')
    note_no = fields.Char(compute= '_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    flag_count_accept = fields.Integer('Accepted Line is There',default= 1)
    ha_flag=fields.Integer('To HA',default= 0)
    po_no= fields.Char(string= "Order No.")
    order_date = fields.Date(string='Order Date')
    mrn_flag=fields.Integer('To MRN',default= 0)  
    return_id = fields.Many2one('prakruti.purchase_return',string='Return No.')
    flag_display_product= fields.Integer(string='Product List Shown',default=0)
    flag_delete_product= fields.Integer(string='Product List Deleted',default=0)
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager") 
    stores_incharge = fields.Many2one('res.users','Stores Incharge')
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods',string = 'Category') 
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No")
    revision_no = fields.Char(string = "Rev. No")
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today )
    plant_manager = fields.Many2one('res.users',string="Plant Manager")
    to_name = fields.Many2one('res.users',string="Name") 
    
    
    
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
    company_address = fields.Many2one('res.company',string='Company Address',default=lambda self: self.env.user.company_address, readonly= "True" )  
    
    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete'))
        return super(PrakrutiDebitNote, self).unlink()
   
    '''
    Pulls the data to Debit HA
    '''
    @api.one
    @api.multi
    def to_ha(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            to_dn_ha = self.pool.get('prakruti.debit.note.ha').create(cr,uid, {
                'debit_note_no':temp.debit_note_no,
                'debit_date':temp.debit_date,
                'return_id':temp.return_id.id,
                'vendor_id':temp.vendor_id.id,
                'dispatch_to':temp.dispatch_to.id,
                'notes':temp.notes,
                'categorization':temp.categorization,
                'to_name':temp.to_name.id,
                'plant_manager':temp.plant_manager.id,
                'stores_incharge':temp.stores_incharge.id,
                'purchase_manager':temp.purchase_manager.id,
                'company_address':temp.company_address.id,
                'document_no':temp.document_no,
                'revision_no':temp.revision_no,
                'default_pr_date':temp.default_pr_date,
                'total_no_of_products':temp.total_no_of_products,
                'proportionate_amount_to_products':temp.proportionate_amount_to_products,
                'freight_charges':temp.freight_charges,
                'loading_and_packing_charges':temp.loading_and_packing_charges,
                'insurance_charges':temp.insurance_charges,
                'other_charges':temp.other_charges,
                'all_additional_charges':temp.all_additional_charges,
                'total_amount_before_tax':temp.total_amount_before_tax,
                'total_cgst_amount':temp.total_cgst_amount,
                'total_sgst_amount':temp.total_sgst_amount,
                'total_igst_amount':temp.total_igst_amount,
                'total_gst_amount':temp.total_gst_amount,
                'total_amount_after_tax':temp.total_amount_after_tax,
                'total_amount':temp.total_amount,
                'total_taxable_value':temp.total_taxable_value
                 })
            for item in temp.order_line:
                grid_values = self.pool.get('prakruti.debit.note.ha.line').create(cr,uid, {
                    'product_id':item.product_id.id,
                    'uom_id':item.uom_id.id,
                    'return_qty':item.return_qty,
                    'unit_price':item.unit_price,
                    'total': item.total,
                    'amount': item.amount,  
                    'remarks': item.remarks,  
                    'purchase_line_common_id': item.purchase_line_common_id,
                    'hsn_code': item.hsn_code,
                    'discount_rate': item.discount_rate,
                    'cgst_id': item.cgst_id.id,
                    'cgst_rate': item.cgst_rate,
                    'cgst_amount': item.cgst_amount,   
                    'sgst_id': item.sgst_id.id,
                    'sgst_rate': item.sgst_rate,
                    'sgst_amount': item.sgst_amount,
                    'igst_id': item.igst_id.id,
                    'igst_rate': item.igst_rate,
                    'igst_amount': item.igst_amount,
                    'taxable_value': item.taxable_value,
                    'taxable_value_after_adding_other': item.taxable_value_after_adding_other,
                    'proportionate_amount_to_products':item.proportionate_amount_to_products,
                    'gst_rate': item.gst_rate,
                    'taxable_value_with_charges': item.taxable_value_with_charges,
                    'line_id':to_dn_ha
                    })
            cr.execute("UPDATE prakruti_debit_note SET ha_flag = 1 WHERE prakruti_debit_note.id = cast(%s as integer)",((temp.id),))
        return {}
            
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
            cr.execute(''' SELECT calculation_debit_note(%s)''',((temp.id),))
        return {} 
    
class PrakrutiDebitNoteLine(models.Model):
    _name = 'prakruti.debit.note.line'
    _table = "prakruti_debit_note_line"
    _description = 'Debit Note Line'
    
    line_id = fields.Many2one('prakruti.debit.note')
    product_id = fields.Many2one('product.product',string= 'Product')
    description = fields.Char(string= 'Description')
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