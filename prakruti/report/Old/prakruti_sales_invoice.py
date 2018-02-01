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
#########################################################################################################

class PrakrutiSalesInvoice(models.Model):
    _name = 'prakruti.sales_invoice'
    _table = "prakruti_sales_invoice"
    _description = 'Prakruti Sales Invoice Information'
    _order="id desc"
    _rec_name="order_no"
    
    
    @api.one
    @api.multi
    def _get_auto(self):
        x = {}
        month_value=0
        year_value=0
        next_year=0
        dispay_year=''
        display_present_year=''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self :
            cr.execute('''select cast(extract (month from invoice_date) as integer) as month ,cast(extract (year from invoice_date) as integer) as year ,id from prakruti_sales_invoice where id=%s''',((temp.id),))
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
            cr.execute('''select autogenerate_sales_invoice(%s)''', ((temp.id),)  ) 
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_sales_invoice'];
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
                if record.invoice_type == 'd_e_i':
                    x[record.id] = 'SINV\\'+'DE-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'd_ct1_i':
                    x[record.id] = 'SINV\\'+'DCT1-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'ex_i':
                    x[record.id] = 'SINV\\'+'EX-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'meis_i':
                    x[record.id] = 'SINV\\'+'MEIS-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'pro_i':
                    x[record.id] = 'SINV\\'+'PRO-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'r_m_i':
                    x[record.id] = 'SINV\\'+'RM-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'com_i':
                    x[record.id] = 'SINV\\'+'COM-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'tra_i':
                    x[record.id] = 'SINV\\'+'TRA-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'ex_i_s':
                    x[record.id] = 'SINV\\'+'EXIS-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                elif record.invoice_type == 'c_i_s':
                    x[record.id] = 'SINV\\'+'COMIS-'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''update prakruti_sales_invoice set invoice_no =%s where id=%s ''', ((x[record.id]),(temp.id),))
        return x
    
    
    @api.one
    @api.multi 
    def invoice_to_tracking(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            order_line = self.pool.get('prakruti.logistics_invoice_tracking').create(cr,uid, {
                'order_no':temp.order_no,
                'order_date':temp.order_date,
                'invoice_no':temp.invoice_no,
                'invoice_date':temp.invoice_date,
                'customer_id':temp.customer_id.id,
                 })
            for item_line in temp.grid_id:
                product_line = self.pool.get('prakruti.sales_line_in_logistics').create(cr,uid, {
                    'product_id':item_line.product_id.id,
                    'quantity':item_line.quantity,
                    'logistics_line_id': order_line
                    })
        cr.execute("UPDATE  prakruti_sales_invoice SET state = 'invoice_tracking' WHERE prakruti_sales_invoice.id = cast(%s as integer)",((temp.id),))
        return {}  
    
    @api.depends('grid_id.quantity','grid_id.unit_price','bed_type','total_assessable_value','bed_percentage','bed_qty','bed_amt')
    def _get_grand_total_in_words(self):
        for order in self:
            bed_amt =val1=0.0
            val1_in_words = ""
            bed_amt= (order.total_assessable_value )* (order.bed_percentage/100)
            
            val1 = bed_amt
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            print 'Grand Total in Words--------------------Grand Total in Words',val1_in_words.title()
            order.update({                    
                'grand_total_in_words': val1_in_words.title()
                })
                
    @api.depends('grid_id.quantity','grid_id.unit_price','bed_type','total_assessable_value','bed_percentage','bed_qty','bed_amt')
    def _get_cess_amount_in_words(self):
        for order in self:
            sec_cess_amt =val1=0.0
            val1_in_words = ""
            sec_cess_amt= ((order.bed_amt )* (order.ed_cess_percentage/100))
            
            val1 = sec_cess_amt
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            print 'Cess Amount in Words-----------------------Cess Amount in Words',val1_in_words.title()
            order.update({                    
                'cess_amount_in_words': val1_in_words.title()
                })
                
    @api.depends('grid_id.quantity','grid_id.unit_price','bed_type','total_assessable_value','bed_percentage','bed_qty','bed_amt')
    def _get_final_grand_total_in_words(self):
        for order in self:
            final_grand_total =val1=0.0
            val1_in_words = ""
            final_grand_total=(order.untaxed_amount )+(order.transporatation_charges )+(order.total_tax )+(order.total_sbc )+(order.total_kkc )
            
            val1 = final_grand_total
            val1_in_words = str(amount_to_text_in_without_word_rupees(round(val1),"Rupee"))
            print 'Final Grand Total in Words---------------------------------Final Grand Total in Words',val1_in_words.title()
            order.update({                    
                'final_grand_total_in_words': val1_in_words.title()
                })
    
            
    invoice_type = fields.Selection([
        ('d_e_i','Deemed Export Invoice'),
        ('d_ct1_i','Domestic CT1 Invoice'),
        ('ex_i','Excise Invoice'),
        ('meis_i','Meis Invoice'),
        ('pro_i','Processing Invoice'),
        ('r_m_i','Raw Material Invoice'),
        ('com_i','Commercial Invoice'),
        ('tra_i','Trading Invoice'),
        ('ex_i_s','Excise Invoice Sales'),
        ('c_i_s','Commercial Invoice Sales')
        ], string="Invoice Type", default='com_i')
    invoice_no = fields.Char('Invoice No:', readonly=True, default='New')
    invoice_date = fields.Date('Invoice Date',default= fields.Date.today)
    order_no = fields.Char('Order No.',readonly=True)
    order_date = fields.Date('Order Date.',readonly=True)
    supplier_ref = fields.Char('Supplier Reference')
    other_ref = fields.Char('Other Referrence')
    customer_id = fields.Many2one ('res.partner',string= 'Customer',readonly=True)
    billing_id = fields.Many2one('res.partner',string='Billing Address',readonly=True)
    shipping_id = fields.Many2one('res.partner',string='Shipping Address',readonly=True)
    dispatch_through = fields.Char(string='Dispatch Through')
    destination = fields.Char(string='Destination')
    terms_delivery = fields.Char('Terms Of Delivery')
    delivery_note= fields.Integer(' Delivery Note')
    delivery_date = fields.Date('Delivery Date')
    terms_payment = fields.Char('Terms Of Payment')
    bl_no = fields.Char('B/L No')
    bl_date = fields.Date('B/L Date')
    vessal_name = fields.Char('Vessal Name')
    country_origin = fields.Char('Country Origin')
    invoice_datetime =fields.Datetime(string='Date and time of issue of invoice')
    goods_datetime =fields.Datetime(string='Date and time of Removal of Goods')
    vehicle_no = fields.Char(string='Motar Vehicle No')
    exporter_datetime =fields.Datetime(string='Exporters Ref Date and time ')
    product_type_id=fields.Many2one('product.group',string= 'Product Type',required=True)
    order_type = fields.Selection([('with_tarrif','With Tarrif'),('without_tarrif','Without Tarrif')], string="Order Type", default='without_tarrif')
    company_address = fields.Many2one('res.company',string='Company Address')
    
    assessable_value=fields.Float(string='Assessable Value(%)',default=65)
    total_assessable_value= fields.Float(string='Total Assesable value')
    assessable_subtotal=fields.Float(string='Assesable  Total')
    subtotal= fields.Float(string='Sub Total')
    
    ####################################
    #Edited from Here
    
    #Bed
    bed_type= fields.Many2one('account.other.tax', string='BED TYPE', domain=[('active', '=', True),('select_type','=','bed')])
    bed_percentage = fields.Float(related='bed_type.per_amount',string="BED %", store=True,readonly=True)
    bed_qty = fields.Float(related='bed_type.amount',string="BED Qty.", store=True,readonly=True)
    bed_amt = fields.Float(string="BED Total",store=True)
    what_is_bed_type=fields.Selection([('per_amount','%'),('amount','Amount')],related='bed_type.tax_type',string='What is Bed Type')
    
    #Ed Cess
    ed_cess_type = fields.Many2one('account.other.tax', string='ED CESS TYPE', domain=[('active', '=', True),('select_type','=','ed_cess')])
    ed_cess_percentage = fields.Float(related='ed_cess_type.per_amount',string="Ed Cess %", store=True,readonly=True)
    ed_cess_qty = fields.Float(related='ed_cess_type.amount',string="Ed Cess Qty.", store=True,readonly=True)
    ed_cess_amt = fields.Float(string="Ed Cess Total",store=True)
    what_is_ed_cess_type=fields.Selection([('per_amount','%'),('amount','Amount')],related='ed_cess_type.tax_type',string='What is Ed Cess Type')
    
    #Sec Cess
    sec_cess_type = fields.Many2one('account.other.tax', string='SEC CESS TYPE', domain=[('active', '=', True),('select_type','=','sec_cess')])
    sec_cess_percentage = fields.Float(related='sec_cess_type.per_amount',string="Sec Cess %", store=True,readonly=True)
    sec_cess_qty = fields.Float(related='sec_cess_type.amount',string="Sec Cess Qty.", store=True,readonly=True)
    sec_cess_amt = fields.Float(string="Sec Cess Total",store=True)
    what_is_sec_cess_type=fields.Selection([('per_amount','%'),('amount','Amount')],related='sec_cess_type.tax_type',string='What is Sec Cess Type')
    
    #Tax
    tax_id = fields.Many2one('account.other.tax', string='Tax', domain=[('active', '=', True),('select_type','=','tax')])
    tax_value = fields.Float(related='tax_id.per_amount',string='Tax %', store=True,readonly=True)
    total_tax = fields.Float(string="Total Tax")
    
    #Vat
    vat_id = fields.Many2one('account.other.tax', string='Vat', domain=[('active', '=', True),('select_type','=','vat')])
    vat_value = fields.Float(related='vat_id.per_amount',string='Vat %', store=True,readonly=True)
    total_vat = fields.Float(string="Total Vat")
    
    #Cst
    cst_id = fields.Many2one('account.other.tax', string='Cst', domain=[('active', '=', True),('select_type','=','cst')])
    cst_value = fields.Float(related='cst_id.per_amount',string='Cst %', store=True,readonly=True)
    total_cst = fields.Float(string="Total Cst")
    
    #Swachh Bharat
    sbc_id =  fields.Many2one('account.other.tax', string='Swachh Bharat', domain=[('active', '=', True),('select_type','=','swach_bharat')])
    sbc_value = fields.Float(related='sbc_id.per_amount',string='Swachh %', store=True,readonly=True)
    total_sbc = fields.Float(string="Swachh Bharat Cess")
    
    #Krishi Kalyan    
    kkc_id =  fields.Many2one('account.other.tax', string='Krishi Kalyan', domain=[('active', '=', True),('select_type','=','krishi_kalyan')])
    kkc_value = fields.Float(related='kkc_id.per_amount',string='Krishi %', store=True,readonly=True)
    total_kkc = fields.Float(string="Krishi Kalayan Cess")
    
    #Newly Added as on 18.1.17 so that all the taxes will appear in the form of Many2one fields and can be selected according to the requirements
    tax_line_id = fields.One2many('sales.invoice.tax.line','ref_id',string='All Taxes')
    
    # To be filled automatically
    new_bed_amt = fields.Float(string="New BED Total",readonly=1)
    new_ed_cess_amt = fields.Float(string="New Ed Cess Total",readonly=1)
    new_sec_cess_amt = fields.Float(string="New Sec Cess Total",readonly=1)
    new_total_tax = fields.Float(string="New Total Tax",readonly=1)
    new_total_vat = fields.Float(string="New Total Vat",readonly=1)
    new_total_cst = fields.Float(string="New Total Cst",readonly=1)
    new_total_sbc = fields.Float(string="New Swachh Bharat",readonly=1)
    new_total_kkc = fields.Float(string="New Krishi Kalayan",readonly=1)
    
    untaxed_amount = fields.Float(string="Untaxed Amount")
    transporatation_charges=fields.Float(string='Trasportation Charges')
    final_grand_total = fields.Float(string=" Grand Total")
    state =fields.Selection([
		('inquiry', 'Inquiry'),
		('quotation','Quotation'),
		('order','Order'),
		('invoice','Invoice'),
		('invoice_tracking','Invoice Tracking'),
		('in_transit','Transit'),
		('deliver','Delivered'),
		('proforma','Proforma')
		],default= 'invoice', string= 'State')
    grid_id = fields.One2many('prakruti.sales_invoice_line', 'main_id',string='Grid')
    inv_no = fields.Char('Order Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    dispatch_no = fields.Char(string='Dispatch No',readonly=True)
    dispatch_date = fields.Date('Dispatch Date',readonly=True)
    vat_tin = fields.Char('Companys VAT TIN',required=True)
    buyer_vat_tin = fields.Char('Buyers VAT TIN',required=True)
    cst_no = fields.Char('Companys CST No',required=True)
    buyer_cst_no = fields.Char('Buyers CST No',required=True)
    tax_no = fields.Char('TAX No',required=True)
    pan_no = fields.Char('PAN No',required=True)
    excise_regn_no = fields.Char('Excise regn No',required=True)

    port_of_landing = fields.Char('Port Of landing')
    port_of_discharge = fields.Char('Port Of Discharge')
    bank_details = fields.Char('Bank Details')
    grand_total_in_words= fields.Text( compute= '_get_grand_total_in_words' ,method=True, string='Total in words')
    cess_amount_in_words=fields.Text(compute='_get_cess_amount_in_words',string='Amount of Cess in words')
    final_grand_total_in_words=fields.Text(compute='_get_final_grand_total_in_words',string='Grand total in words')
    
    @api.one
    @api.multi 
    def to_proforma(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            inv_to_proforma = self.pool.get('prakruti.sales_proforma_invoice').create(cr,uid, {
                'invoice_type':temp.invoice_type,
                'invoice_no':temp.invoice_no,
                'invoice_date':temp.invoice_date,
                'supplier_ref':temp.supplier_ref,
                'other_ref':temp.other_ref,
                'customer_id':temp.customer_id.id,
                'dispatch_through':temp.dispatch_through,
                'destination':temp.destination,
                'terms_delivery':temp.terms_delivery,
                'delivery_note':temp.delivery_note,
                'delivery_date':temp.delivery_date,
                'terms_payment':temp.terms_payment,
                'bl_no':temp.bl_no,
                'bl_date':temp.bl_date,
                'vessal_name':temp.vessal_name,
                'country_origin':temp.country_origin,
                'invoice_datetime':temp.invoice_datetime,
                'goods_datetime':temp.goods_datetime,
                'vehicle_no':temp.vehicle_no,
                'exporter_datetime':temp.exporter_datetime,
                'order_no':temp.order_no,
                'product_type_id':temp.product_type_id.id,
                'order_date':temp.order_date,
                'shipping_id':temp.shipping_id.id,
                'billing_id':temp.billing_id.id,
                'order_type':temp.order_type,
                'assessable_value':temp.assessable_value,
                'total_assessable_value':temp.total_assessable_value,
                'assessable_subtotal':temp.assessable_subtotal,
                
                'subtotal':temp.subtotal,
                'bed_type':temp.bed_type.id,
                'bed_percentage':temp.bed_percentage,
                'bed_qty':temp.bed_qty,
                'bed_amt':temp.bed_amt,
                'ed_cess_type':temp.ed_cess_type.id,
                'ed_cess_qty':temp.ed_cess_qty,
                'ed_cess_percentage':temp.ed_cess_percentage,
                'ed_cess_amt':temp.ed_cess_amt,
                'sec_cess_type':temp.sec_cess_type.id,
                'sec_cess_qty':temp.sec_cess_qty,
                'sec_cess_percentage':temp.sec_cess_percentage,
                'sec_cess_amt':temp.sec_cess_amt,
                'tax_id':temp.tax_id.id,
                'tax_value':temp.tax_value,
                'total_tax':temp.total_tax,
                'what_is_bed_type':temp.what_is_bed_type,
                'what_is_ed_cess_type':temp.what_is_ed_cess_type,
                'what_is_sec_cess_type':temp.what_is_sec_cess_type,
                
                'new_bed_amt':temp.new_bed_amt,
                'new_ed_cess_amt':temp.new_ed_cess_amt,
                'new_sec_cess_amt':temp.new_sec_cess_amt,
                'new_total_tax':temp.new_total_tax,
                'new_total_vat':temp.new_total_vat,
                'new_total_cst':temp.new_total_cst,
                'new_total_sbc':temp.new_total_sbc,
                'new_total_kkc':temp.new_total_kkc,
                
                
                
                'sbc_value':temp.sbc_value,
                'total_sbc':temp.total_sbc,
                'kkc_value':temp.kkc_value,
                'total_kkc':temp.total_kkc,
                'untaxed_amount':temp.untaxed_amount,
                'transporatation_charges':temp.transporatation_charges,
                'final_grand_total':temp.final_grand_total
                
                 })
            for item in temp.grid_id:
                grid_values = self.pool.get('prakruti.sales_proforma_invoice_item').create(cr,uid, {
                    'product_id':item.product_id.id,
                    'description':item.description,
                    'uom_id':item.uom_id.id,
                    'specification_id':item.specification_id.id,
                    'quantity':item.quantity,
                    'assessable_value':item.assessable_value,
                    'iv_assessable_value':item.iv_assessable_value,
                    'total1':item.total1,
                    'order_type': item.order_type,
                    'total_assessable_value':item.total_assessable_value,
                    'assessable_subtotal':item.assessable_subtotal,
                    'subtotal':item.subtotal,
                    'bed_itype': item.bed_itype,
                    'bed_ipercentage':item.bed_ipercentage,
                    'bed_iqty':item.bed_iqty,
                    'bed_iamt':item.bed_iamt,
                    'ed_cess_itype': item.ed_cess_itype,
                    'ed_cess_iqty':item.ed_cess_iqty,
                    'ed_cess_ipercentage':item.ed_cess_ipercentage,
                    'ed_cess_iamt':item.ed_cess_iamt,
                    'status':item.status,
                    'sec_cess_iqty':item.sec_cess_iqty,
                    'sec_cess_ipercentage':item.sec_cess_ipercentage,
                    'sec_cess_iamt': item.sec_cess_iamt,
                    #'ordered_qty':item.ordered_qty,
                    #'dispatched_qty':item.dispatched_qty,
                    'remarks':item.remarks,
                    'unit_price': item.unit_price,
                    'tarrif_id':item.tarrif_id.id,
                    'mrp':item.mrp,
                    'total1':item.total1,
                    'batch_no':item.batch_no,
                    'mfg_date':item.mfg_date,
                    'exp_date':item.exp_date,
                    'total':item.total,
                    
                    'main_id':inv_to_proforma
                 })
        cr.execute('''UPDATE prakruti_sales_invoice SET state= 'proforma' WHERE prakruti_sales_invoice.id = CAST(%s AS INTEGER)''',((temp.id),))
        return {}
    
    
################################added by latha on 18/01/2017#################################################

    
    def print_deemed_export_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice', 'datas': datas, 'nodestroy': True};
    
    
    def print_domestic_ct1_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice1', 'datas': datas, 'nodestroy': True};
    
    def print_excise_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice2', 'datas': datas, 'nodestroy': True};
    
    def print_meis_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice3', 'datas': datas, 'nodestroy': True};
    
    
    def print_processing_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice4', 'datas': datas, 'nodestroy': True};
    
    
    def print_raw_material_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice5', 'datas': datas, 'nodestroy': True};
    
    def print_commercial_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice6', 'datas': datas, 'nodestroy': True};
    
    
    def print_trading_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice7', 'datas': datas, 'nodestroy': True};
    
    def print_excise_sales_invoice(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice11', 'datas': datas, 'nodestroy': True};
    
    def print_commercial_invoice_sales(self, cr, uid, ids, context=None):
        
         	              
        datas = {
                 'model': 'prakruti.sales_invoice',
                 'ids': ids,
                 'form': self.read(cr, uid, ids, context=context),
        }
        #_logger.warning('datas');
        return {'type': 'ir.actions.report.xml', 'report_name': 'prakruti.report_sales_invoice12', 'datas': datas, 'nodestroy': True};
    
    
    
#############################################################################################################   
    
class PrakrutiSalesInvoiceTaxLine(models.Model):
    _name = 'sales.invoice.tax.line'
    _table = 'sales_invoice_tax_line'
    _description = 'Prakruti Sales Invoice Tax Line'
    _order= "id desc"
    
    ref_id = fields.Many2one('prakruti.sales_invoice',string="Reference Id")
    
    tax_type = fields.Many2one('account.other.tax', string='Taxes', domain=[('active', '=', True)])
    tax_percent = fields.Float(related='tax_type.per_amount',string="Tax %",store=1,readonly=1)
    tax_amount = fields.Float(related='tax_type.amount',string="Tax Amt.",store=1,readonly=1)
    total_value = fields.Float(string="Total Value",readonly=1)    
    
  
class PrakrutiSalesInvoiceLine(models.Model):
    _name = 'prakruti.sales_invoice_line'
    _table = "prakruti_sales_invoice_line"
    
    product_id  = fields.Many2one('product.product', string="Product",required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    description = fields.Text(string="Description")
    tarrif_id=fields.Many2one('prakruti.tarrif_master',string='Tarrif')
    quantity = fields.Float(string = "Req.Qty",required=True)
    unit_price=fields.Float(string="Unit Price")
    mrp=fields.Float(string="MRP")
    assessable_value=fields.Float(string='Assessable Value(%)',default=65)
    iv_assessable_value=fields.Float(string="IV Assessable Value", compute='_compute_iv_assessable_value')
    remarks = fields.Text(string="Remarks")
    total= fields.Float(string='Total', compute='_compute_price_total', store=True) 
    total1= fields.Float(string='Total1', compute='_compute_price_total1', store=True)     
    batch_no = fields.Char(string="Batch No")
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    main_id = fields.Many2one('prakruti.sales_invoice',string="Grid")
    order_type = fields.Selection(related='main_id.order_type',string="Order Type", default='without_tarrif')
    
    assessable_value=fields.Float(string='Assessable Value(%)',default=65)
    total_assessable_value= fields.Float(string='Total Assesable value',compute='_compute_total_assessable_value',store=True)
    assessable_subtotal=fields.Float(string='Assesable  Total',compute='_compute_assessable_subtotal',store=True)
    subtotal= fields.Float(string='Sub Total',compute='_compute_subtotal',store=True)
    
    
    bed_itype= fields.Many2one(related='main_id.bed_type', string='BED TYPE')
    bed_ipercentage = fields.Float(related='main_id.bed_percentage',string="BED %")
    bed_iqty = fields.Float(related='main_id.bed_qty',string="BED qty")
    bed_iamt = fields.Float(related='main_id.bed_amt',string="BED Total")
    what_is_bed_type=fields.Selection([('per_amount','%'),('amount','Amount')],related='main_id.bed_type.tax_type',string='What is Bed Type')
    
    ed_cess_itype = fields.Many2one(related='main_id.ed_cess_type', string='ED CESS TYPE')
    ed_cess_iqty = fields.Float(related='main_id.ed_cess_qty',string="Ed Cess qty")
    ed_cess_ipercentage = fields.Float(related='main_id.ed_cess_percentage',string="Ed Cess %")
    ed_cess_iamt = fields.Float(related='main_id.ed_cess_amt',string="Ed Cess Total")
    what_is_ed_cess_type=fields.Selection([('per_amount','%'),('amount','Amount')],related='main_id.ed_cess_type.tax_type',string='What is Ed Cess Type')
    
    sec_cess_itype = fields.Many2one(related='main_id.sec_cess_type', string='SEC CESS TYPE')
    sec_cess_iqty = fields.Float(related='main_id.sec_cess_qty',string="Sec Cess qty")
    sec_cess_ipercentage = fields.Float(related='main_id.sec_cess_percentage',string="Sec Cess %")
    sec_cess_iamt = fields.Float(related='main_id.sec_cess_amt',string="Sec Cess Total")
    what_is_sec_cess_type=fields.Selection([('per_amount','%'),('amount','Amount')],related='main_id.sec_cess_type.tax_type',string='What is Sec Cess Type')
    
    status = fields.Selection([
		('accepted', 'Accepted'),
		('par_reject', 'Par. Rejected'),
		('rejected','Rejected')
		], string= 'Status')
  
    @api.multi
    def unlink(self):
        for order in self:
            if order.status in ['accepted']:
                raise UserError(_('Sorry....You Can\'t Delete the Order Item\'s.... Since the products are already Confirmed..... Please Discard it to retain back the products.... '))
        return super(PrakrutiSalesInvoice, self).unlink()
    
    @api.depends('quantity','mrp','assessable_value')
    def _compute_iv_assessable_value(self):
        for order in self:
            subtotal  = total_amount=0.0
            total_amount = (order.quantity * order.mrp )*(order.assessable_value/100)
            order.update({
                'iv_assessable_value': total_amount
                    })
    @api.depends('mrp','iv_assessable_value','bed_ipercentage','bed_iqty','bed_iamt','bed_itype')
    def _compute_bed_iamt(self):
        for order in self:
            bed_ipercentage = 0.0
            mrp=0
            if order.bed_itype=='percentage':
               if order.mrp>0 :
                    order.update({
                        'bed_iamt':( (order.quantity * order.mrp )*(order.assessable_value/100))* (order.bed_ipercentage/100)
                            })
                  
            elif order.bed_itype=='quantity':
                order.update({
                    'bed_iamt': order.bed_iqty
                            })
    @api.depends('bed_iamt','ed_cess_ipercentage','ed_cess_iamt','ed_cess_iqty')
    def _compute_ed_cess_iamt(self):
        for order in self:
            ed_cess_ipercentage = 0.0
            mrp=0
            if order.ed_cess_itype == 'percentage':
                print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                if order.mrp>0:
                    order.update({
                        'ed_cess_iamt': ((order.quantity * order.mrp )*(order.assessable_value/100)* (order.bed_ipercentage/100))* (order.ed_cess_ipercentage/100)
                            })
            else:
                print 'cccccccccccccccccccccccc'
                order.update({
                    'ed_cess_iamt': order.ed_cess_iqty
                            })
                
                
    @api.depends('bed_iamt','sec_cess_ipercentage','sec_cess_iamt','sec_cess_iqty')
    def _compute_sec_cess_iamt(self):
        for order in self:
            sec_cess_ipercentage = 0.0
            mrp=0
            if order.sec_cess_itype == 'percentage':
                 if order.mrp>0:
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
                    order.update({
                        'sec_cess_iamt': ( (order.quantity * order.mrp )*(order.assessable_value/100))* (order.bed_ipercentage/100)* (order.sec_cess_ipercentage/100)
                        })
            else:
                order.update({
                    'sec_cess_iamt': order.sec_cess_iqty
           
            })
                
    @api.onchange('bed_itype')
    def onchange_bed_itype(self):
        if self.bed_itype == 'percentage':
            self.bed_iqty = 0.0
        else :
            self.bed_ipercentage=0.0
        
            
    
    @api.onchange('ed_cess_itype')
    def onchange_ed_cess_itype(self):
        if self.ed_cess_itype == 'percentage':
            self.ed_cess_iqty = 0.0
        else :
            self.ed_cess_ipercentage=0.0
            
    @api.onchange('sec_cess_itype')
    def onchange_sec_cess_itype(self):
        if self.sec_cess_itype == 'percentage':
            self.sec_cess_iqty = 0.0
        else :
            self.sec_cess_ipercentage=0.0             
    @api.depends('quantity', 'unit_price')
    def _compute_price_total(self):
        for order in self:
            total = 0.0            
            order.update({                
                'total': order.quantity * order.unit_price 
            })
    @api.depends('quantity', 'mrp')
    def _compute_price_total1(self):
        for order in self:
            total = 0.0            
            order.update({                
                'total1': order.quantity * order.mrp 
            })         
    
    def _check_required_quantity(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for line in lines:
            if line.quantity == 0:
                return False
            return True
        
     
    def _check_price(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for line in lines:
            if line.unit_price == 0:
                return False
            return True