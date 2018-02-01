'''
Company : EBSL
Author: Induja
Module: Proforma Invoice
Class 1: PrakrutiSalesProformaInvoice
Class 2: PrakrutiSalesProformaInvoiceItem
Table 1 & Reference Id: prakruti_sales_proforma_invoice ,grid_id
Table 2 & Reference Id: prakruti_sales_proforma_invoice_item,main_id
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
import re
import logging
from openerp.tools import amount_to_text
from openerp.tools.amount_to_text import amount_to_text_in 
from openerp.tools.amount_to_text import amount_to_text_in_without_word_rupees 



class PrakrutiSalesProformaInvoice(models.Model):
    _name = 'prakruti.sales_proforma_invoice'
    _table = "prakruti_sales_proforma_invoice"
    _description = 'Prakruti Sales Proforma Invoice Information'
    _order="id desc"
    _rec_name="proforma_invoice_no"
    
  
    '''Auto genereation function
    'Format: SPI\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SPI\EXFG\0262\17-18
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
        print '-------------------------------------1-------------------------------------'
        for temp in self:
            cr.execute('''SELECT cast(EXTRACT (month FROM proforma_invoice_date) AS integer) AS month ,cast(EXTRACT (year FROM proforma_invoice_date) AS integer) AS year ,id FROM prakruti_sales_proforma_invoice WHERE id=%s''',((temp.id),))
            print '--------------------------------2------------------------------------------'
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
                        
                cr.execute('''SELECT autogenerate_sales_proforma_invoice(%s)''', ((temp.id),)  ) # Database Function autogenerate_sales_proforma_invoice
                result = cr.dictfetchall()
                parent_invoice_id = 0
                print '---------------------------------3-----------------------------------------'
                for value in result: parent_invoice_id = value['autogenerate_sales_proforma_invoice'];
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
                    if temp.product_type_id.group_code:
                        style_format[record.id] = 'SPI\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:                        
                        style_format[record.id] = 'SPI\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)                   
                    cr.execute('''UPDATE prakruti_sales_proforma_invoice SET proforma_invoice_no =%s WHERE id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
        
        
        
    grid_id = fields.One2many('prakruti.sales_proforma_invoice_item', 'main_id',string='Grid')
    proforma_invoice_no=fields.Char(' Proforma Invoice No',default="New",readonly="True")
    proforma_invoice_date= fields.Date('Proforma Invoice Date', default=fields.Date.today,readonly=True)
    ord_no = fields.Char('Order Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id1 = fields.Integer('Auto Generating id',default= 0)
    order_no = fields.Char(string='Order No', readonly=True)
    order_date = fields.Date(string='Order Date', default= fields.Date.today, required=True)
    quotation_no= fields.Char(string='Quotation No' ,readonly=True)
    quotation_date = fields.Date(string='Quotation Date' ,readonly=True)
    inquiry_date= fields.Date('Inquiry Date',readonly=True)
    inquiry_no = fields.Char(' Inquiry No', readonly=True)
    customer_id = fields.Many2one('res.partner',string="Customer")
    product_type_id=fields.Many2one('product.group',string= 'Product Type')
    shipping_id = fields.Many2one('res.partner',string='Shipping Address')
    billing_id = fields.Many2one('res.partner',string='Billing Address')
    remarks = fields.Text(string="Remarks")
    terms =fields.Text('Terms and conditions')
    balance_line = fields.Integer('Any Balance Line',default=0,readonly=1)
    cash_amount = fields.Float(string="Amount",readonly=1,digits=(6,3))
    cash_remarks = fields.Text(string="Remarks",readonly=1)    
    cheque_amount = fields.Float(string="Amount",readonly=1,digits=(6,3))
    cheque_no = fields.Integer(string="Cheque No.",readonly=1)
    cheque_remarks = fields.Text(string="Remarks",readonly=1)    
    draft_amount = fields.Float(string="Amount",readonly=1,digits=(6,3))
    draft_no = fields.Integer(string="Draft No.",readonly=1)
    draft_remarks = fields.Text(string="Remarks",readonly=1)  
    reference_no= fields.Char(string='Ref No')
    reference_date= fields.Date(string='Ref Date', default=fields.Date.today) 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')     
    state =fields.Selection([
                    ('proforma','Proforma'),
                    ('invoice','Invoice')
                    ],default= 'proforma', string= 'Status')   
    any_adv_payment =fields.Selection([
                    ('no', 'No'),
                    ('yes','Yes')
                    ], string= 'Any Advance Payment')
    advance_payment_type =fields.Selection([
                    ('cash', 'CASH'),
                    ('cheque','CHEQUE'),
                    ('demand_draft','DEMAND DRAFT')
                    ], string= 'Any Advance Payment Done By',readonly=1)
    company_address = fields.Many2one('res.company',string="Company")
    total_no_of_products = fields.Integer(string="Total No of Products",readonly=1)
    proportionate_amount_to_products = fields.Float(string="Proportionate Amount to Products")
    freight_charges = fields.Float(string="Freight Charges")
    loading_and_packing_charges = fields.Float(string="Loading and Packing Charges")
    insurance_charges = fields.Float(string="Insurance Charges")
    other_charges =  fields.Float(string="Other Charges")
    all_additional_charges = fields.Float(string="All Additional Charges",readonly=1)
    total_amount_before_tax = fields.Float(string="Untaxed Amount",readonly=1)
    total_cgst_amount = fields.Float(string="CGST Amount",readonly=1)
    total_sgst_amount = fields.Float(string="SGST Amount",readonly=1)
    total_igst_amount = fields.Float(string="IGST Amount",readonly=1)
    total_gst_amount = fields.Float(string="Total GST",readonly=1)  
    total_amount_after_tax = fields.Float(string="Grand Total",readonly=1)
    grand_total= fields.Float(string='Grand Total',digits=(6,3),readonly=1)
    grand_total_in_words= fields.Text(compute= '_get_total_in_words',string='Total in words')
    type_of_gst = fields.Selection([
        ('cgst_sgst','CGST/SGST'),('igst','IGST')],default='cgst_sgst',string='Type Of GST')
    total_amount = fields.Float(string="Total Amount")
    total_gst_in_words= fields.Text(compute= '_get_total_gst_in_words',string='Total GST in words')
    total_taxable_value = fields.Float(string="Total Taxable Value",compute= '_compute_total_taxable_value')
    revision_no = fields.Char(' Rev No')
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete'))
        return super(PrakrutiSalesProformaInvoice, self).unlink()
    
    '''
    Total Taxavle Value Calculation
    '''
    @api.depends('grid_id.taxable_value')
    def _compute_total_taxable_value(self):
        for order in self:
            total_taxable_value = line_amount = 0
            for line in order.grid_id:
                line_amount += line.taxable_value
                order.update({
                    'total_taxable_value': line_amount
                    })
    
    '''
    Prints Total GST in words
    '''
    @api.depends('total_gst_amount','total_cgst_amount','total_sgst_amount','total_igst_amount')
    def _get_total_gst_in_words(self):
        for order in self:
            total_gst_amount = val1 = 0.0
            val1_in_words = ""
            val1 = order.total_gst_amount
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            order.update({                    
                'total_gst_in_words': val1_in_words.upper()
                })
    '''
    Prints Grand Total in words
    '''
    @api.depends('grand_total')
    def _get_total_in_words(self):
        for order in self:
            grand_total = val1 = 0.0
            val1_in_words = ""
            val1 = order.grand_total
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            order.update({                    
                'grand_total_in_words': val1_in_words.upper()
                })
    

class PrakrutiSalesProformaInvoiceItem(models.Model):
    _name = 'prakruti.sales_proforma_invoice_item'
    _table = "prakruti_sales_proforma_invoice_item"
    _description = 'Proforma Invoice Item'
    
    main_id = fields.Many2one('prakruti.sales_proforma_invoice',string="Grid")
    product_id  = fields.Many2one('product.product', string="Product Name",readonly=True)
    uom_id = fields.Many2one('product.uom',string="UOM",readonly=True)
    specification_id = fields.Many2one('product.specification.main', string = "Specification",readonly=True)
    description = fields.Text(string="Description",readonly=True)
    quantity = fields.Float(string = "Req.Qty",readonly=True,digits=(6,3))
    unit_price=fields.Float(string="Unit Price",readonly=True,digits=(6,3))
    remarks = fields.Text(string="Remarks")
    total= fields.Float(string='Total', store=True,readonly=True,digits=(6,3)) 
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    scheduled_date = fields.Date('Sch. Date', readonly= True)
    scheduled_qty = fields.Float('Sch. Qty', readonly= True,default=0,digits=(6,3))
    req_date = fields.Date('Req. Date')
    hsn_code = fields.Char(string='HSN/SAC')
    amount = fields.Float(string= 'Amount',readonly=1)
    discount_id = fields.Many2one('account.other.tax',string= 'Discount(%)',domain=[('select_type', '=', 'discount')])
    discount = fields.Float(string= 'Discount(%)',default=0)
    taxable_value = fields.Float(string= 'Taxable Value',readonly=1)
    proportionate_amount_to_products = fields.Float(related='main_id.proportionate_amount_to_products', string="Proportionate Amount to Products",store=1)
    taxable_value_with_charges = fields.Float(string= 'Taxable Value With Charges',readonly=1)
    gst_rate = fields.Float(string= 'GST Rate',readonly=1)    
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_value = fields.Float(related='cgst_id.per_amount',string= 'CGST Value',default=0,store=1)
    cgst_amount = fields.Float(string= 'CGST Amount',readonly=1)    
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_value = fields.Float(related='sgst_id.per_amount',string= 'SGST Value',default=0,store=1)
    sgst_amount = fields.Float(string= 'SGST Amount',readonly=1)    
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_value = fields.Float(related='igst_id.per_amount',string= 'IGST Value',default=0,store=1)
    igst_amount = fields.Float(string= 'IGST Amount',readonly=1)