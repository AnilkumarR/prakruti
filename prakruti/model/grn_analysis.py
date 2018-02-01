'''
Company : EBSL
Author : Karan
Module : Purchase GRN Analysis

Class 1 : PrakrutiGRNAnalysis
Class 2 : PrakrutiGRNAnalysisLine

Table 1 & Reference Id : prakruti_grn_analysis,order_line
Table 2 & Reference Id : prakruti_grn_analysis_line,analysis_line_id

Updated By : Karan 
Updated Date & Version : 2017/08/23 & 0.1
'''
from openerp import models, fields, api,_
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

class PrakrutiGRNAnalysis(models.Model):
    _name =  'prakruti.grn_analysis'
    _table = 'prakruti_grn_analysis'
    _description = 'Purchase GRN Analysis'
    _rec_name = 'analysis_no'    
    _order="id desc"  
    
    '''
    Its an unique autogenerated Number which will be in the format of
    Format : GRN-NUMBER\FINANCIAL YEAR
    Example : GRN-0001\17-18
    Updated By : Karan
    Updated On : 2017/08/23
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
        for temp in self :
            cr.execute('''SELECT 
                                CAST(EXTRACT(month FROM analysis_date) AS INTEGER) AS month,
                                CAST(EXTRACT(year FROM analysis_date) AS INTEGER) AS year,
                                id 
                          FROM 
                                prakruti_grn_analysis 
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
            cr.execute('''SELECT autogenerate_purchase_grn_analysis(%s)''', ((temp.id),)  ) 
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_purchase_grn_analysis'];
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
                if temp.purchase_type.group_code:
                    style_format[record.id] ='GRN-A\\'+ temp.purchase_type.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                else:                        
                    style_format[record.id] ='GRN_A\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE 
                                    prakruti_grn_analysis 
                              SET 
                                    analysis_no = %s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
        return style_format
    
    order_line = fields.One2many('prakruti.grn_analysis_line','analysis_line_id')
    analysis_no= fields.Char(string='Analysis No.',default= 'New',readonly=1)
    analysis_date= fields.Date(string='Analysis Date',default= fields.Date.today,required=True)
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)    
    analysis_number= fields.Char(string='Analysis No',compute= '_get_auto')
    po_no= fields.Char(string= "Order Number",readonly=True)
    pr_no = fields.Char(string='Requisition No', readonly=True)
    qa_no = fields.Char(string='Analysis No', readonly=True)
    qo_no = fields.Char(string='Quotation No', readonly=True)
    req_no =fields.Char(string='Request No', readonly=True)
    vendor_id = fields.Many2one('res.partner',string='Vendor/Supplier', readonly= "True")
    vendor_reference = fields.Char(string='Vendor/Supplier Reference', readonly= "True" )
    other_reference = fields.Char(string='Other Reference')
    request_date = fields.Date(string = "Requisition Date")
    order_date = fields.Date(string='Order Date')
    destination = fields.Char(string='Destination')
    company_address = fields.Many2one('res.company',string='Company Address', readonly= "True" )
    delivery_address = fields.Many2one('res.company',string='Dispatch To', readonly= "True" )
    payment = fields.Char(string='Mode/Terms of Payments')
    terms_of_delivery = fields.Text(string='Terms of Delivery')
    remarks=fields.Text('Remarks', readonly= "True" )
    dispatch_through = fields.Char(string='Dispatch Through', readonly= "True" )
    prepared_by = fields.Many2one('res.users','Prepared By',readonly=True)
    maintanence_manager = fields.Many2one('res.users',string="Maintanence Manager")    
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager", readonly= "True" )
    purchase_type = fields.Many2one('product.group',string= 'Purchase Type')
    pr_common_id = fields.Integer('PR SCREEN COMMON ID')
    prakruti_stock_id = fields.Integer('SCREEN COMMON ID')
    stores_incharge = fields.Many2one('res.users','Stores Incharge')
    grn_remarks=fields.Text('Remarks')
    gc_no=fields.Char('GC No')
    gc_date=fields.Date('GC Date')
    dc_no=fields.Char('DC No')
    dc_date=fields.Date('DC Date')
    transporter_name=fields.Text('Name of Transporter')
    transporter_payment_details=fields.Text('Transporter Payment Details')
    doc_no=fields.Char('Doc. No',default='PPPL-STR-F-001',readonly=1)
    rev_no=fields.Char('Rev. No',default='02',readonly=1)
    doc_date=fields.Date('Document Date',default= fields.Date.today,readonly=1)
    flag_rejected_count = fields.Integer('Flag', default=1)
    st_loc = fields.Many2one('stock.location', string='Stock Location')
    st_loc_remarks = fields.Text(string='Stock Location Remarks')
    flag_count_accept = fields.Integer('Accepted Line is There',default= 0)
    flag_count_reject = fields.Integer('Rejected Line is There',default= 0)
    flag_count_par_reject = fields.Integer('Partial Rejected Line is There',default= 0)
    product_id = fields.Many2one('product.product', related='order_line.product_id', string='Product Name') 
    coming_from = fields.Char(string= 'Coming From',readonly=1)
    category = fields.Selection([
        ('maintanence','Non Testing Material'),
        ('qc','Testing Material')
        ],default= 'maintanence', string= 'Category')
    state = fields.Selection([
        ('grn_analysis','Goods Received Note Analysis'),
        ('grn','Goods Received Note'),
        ('qc_check','Quality Control'),                              
        ('accepted','Accepted'),
        ('rejected','Rejected'),
        ('accepted_under_deviation','Accepted Under Deviation'),
        ('qc_check_done','Quality Control Done'),
        ('invoice','Invoice'),
        ('done','Goods Received Note Done')],default= 'grn_analysis', string= 'Status')
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods')    
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No" , default='PPPL-PUR-F-004' , readonly=1)
    revision_no = fields.Char(string = "Rev. No", default='01' , readonly=1)
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today , readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=True) 
    to_name = fields.Many2one('res.users',string="Name")  
    
    #Updated for Creating Invoice
    #Updated on 20171018 by Karan
    list_in_pi_line=fields.Integer(string= 'Revised Flag',default=0)
    any_adv_payment =fields.Selection([
                    ('no', 'No'),
                    ('yes','Yes')
                    ], string= 'Any Advance Payment')
    advance_payment_type =fields.Selection([
                    ('cash', 'CASH'),
                    ('cheque','CHEQUE'),
                    ('demand_draft','DEMAND DRAFT')
                    ], string= 'Done By')
    cash_amount = fields.Float(string="Amount",digits=(6,3))
    cash_remarks = fields.Text(string="Remarks")    
    cheque_amount = fields.Float(string="Amount",digits=(6,3))
    cheque_no = fields.Integer(string="Cheque No.")
    cheque_remarks = fields.Text(string="Remarks")
    draft_amount = fields.Float(string="Amount",digits=(6,3))
    draft_no = fields.Integer(string="Draft No.")
    draft_remarks = fields.Text(string="Remarks")
    insurance_charges = fields.Float(string="Insurance Charges" ,digits=(6,3))
    frieght_charges_applied = fields.Selection([('yes','Yes'),('no','No')], string="Freight Charge Applied", default='no')
    frieght_charges = fields.Float(string="Frieght Charges" ,digits=(6,3))
    additional_charges = fields.Float(string='Additional Charges' ,digits=(6,3))
    packing_charges = fields.Float(string='Packing & Forwarding' ,digits=(6,3))
    
    
    
    @api.multi
    def unlink(self):
        for order in self:
            raise UserError(_('Can\'t Delete...'))
        return super(PrakrutiGRNAnalysis, self).unlink()
    
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'stores_incharge': lambda s, cr, uid, c:uid,
        'prepared_by': lambda s, cr, uid, c:uid,
        'company_address': _default_company,
        'delivery_address': _default_company,
        }  
    
    @api.one
    @api.constrains('analysis_date')
    def _check_analysis_date(self):
        if self.analysis_date <  fields.Date.today():
            raise ValidationError(
                "Can\'t Select Back Date")
    
    @api.one
    @api.multi 
    def analysis_to_grn(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.category:
                if temp.category == 'maintanence':
                    grn_entry = self.pool.get('prakruti.grn_inspection_details').create(cr,uid, {                        
                        'po_no':temp.po_no,
                        'qa_no':temp.qa_no,
                        'pr_no':temp.pr_no,
                        'qo_no':temp.qo_no,
                        'req_no':temp.req_no,
                        'vendor_reference':temp.vendor_reference,
                        'payment':temp.payment,
                        'destination':temp.destination,
                        'other_reference':temp.other_reference,
                        'maintanence_manager':temp.maintanence_manager.id,
                        'purchase_manager':temp.purchase_manager.id,
                        'stores_incharge':temp.stores_incharge.id,
                        'terms_of_delivery':temp.terms_of_delivery,
                        'vendor_id': temp.vendor_id.id,
                        'state':'grn',
                        'remarks':temp.remarks,
                        'request_date':temp.request_date,
                        'order_date':temp.order_date,
                        'dispatch_through':temp.dispatch_through,
                        'purchase_type':temp.purchase_type.id,
                        'transporter_name':temp.transporter_name,
                        'transporter_payment_details':temp.transporter_payment_details,
                        'gc_no':temp.gc_no,
                        'gc_date':temp.gc_date,
                        'dc_date':temp.dc_date,
                        'categorization':temp.categorization,
                        'dc_no':temp.dc_no,
                        'to_name':temp.to_name.id,
                        'plant_manager':temp.plant_manager.id,
                        'document_no':temp.document_no,
                        'revision_no':temp.revision_no,
                        'default_pr_date':temp.default_pr_date,
                        'coming_from': 'GRN Analysis',
                        'list_in_pi_line':temp.list_in_pi_line,
                        'any_adv_payment':temp.any_adv_payment,
                        'advance_payment_type':temp.advance_payment_type,
                        'cash_amount':temp.cash_amount,
                        'cash_remarks':temp.cash_remarks,
                        'cheque_amount':temp.cheque_amount,
                        'cheque_no':temp.cheque_no,
                        'cheque_remarks':temp.cheque_remarks,
                        'draft_amount':temp.draft_amount,
                        'draft_no':temp.draft_no,
                        'draft_remarks':temp.draft_remarks,
                        'insurance_charges':temp.insurance_charges,
                        'frieght_charges_applied':temp.frieght_charges_applied,
                        'frieght_charges':temp.frieght_charges,
                        'additional_charges':temp.additional_charges,
                        'company_address':temp.company_address.id,
                        'packing_charges':temp.packing_charges
                        })
                    for item in temp.order_line:
                        grid_values = self.pool.get('prakruti.grn_inspection_details_line').create(cr,uid, {
                            'product_id': item.product_id.id,
                            'description': item.description,
                            'actual_quantity': item.actual_quantity,
                            'accepted_qty': item.quantity,
                            'quantity': item.quantity,
                            'mfg_date':item.mfg_date,
                            'exp_date':item.exp_date,
                            'uom_id': item.uom_id.id,
                            'scheduled_date': item.scheduled_date,                   
                            'unit_price': item.unit_price,
                            'remarks':item.remarks,
                            'packing_style': item.packing_style,
                            'batch_no': item.batch_no,
                            'received_per_qty': item.received_per_qty,
                            'extra_packing':item.extra_packing,
                            'slip_id':item.slip_id.id,
                            'purchase_line_common_id':item.purchase_line_common_id,
                            'hsn_code':item.hsn_code,
                            'discount_id':item.discount_id.id,
                            'discount_rate':item.discount_rate,
                            'cgst_id':item.cgst_id.id,
                            'cgst_rate':item.cgst_rate,
                            'sgst_id':item.sgst_id.id,
                            'sgst_rate':item.sgst_rate,
                            'igst_id':item.igst_id.id,
                            'igst_rate':item.igst_rate, 
                            'taxable_value':item.taxable_value,
                            'taxable_value_after_adding_other':item.taxable_value_after_adding_other,
                            'extra_packing': item.extra_packing,
                            'inspection_line_id': grn_entry
                            })
                    cr.execute('''UPDATE prakruti_grn_analysis SET state = 'grn' WHERE id = %s  ''', ((temp.id),))
                    cr.execute("UPDATE prakruti_purchase_requisition SET state = 'grn' WHERE prakruti_purchase_requisition.requisition_no = %s ", ((temp.pr_no),))
                else:
                    for item in temp.order_line:
                        grn_entry_1 = self.pool.get('prakruti.grn_inspection_details').create(cr,uid, {
                            'po_no':temp.po_no,
                            'qa_no':temp.qa_no,
                            'pr_no':temp.pr_no,
                            'qo_no':temp.qo_no,
                            'req_no':temp.req_no,
                            'vendor_reference':temp.vendor_reference,
                            'payment':temp.payment,
                            'destination':temp.destination,
                            'other_reference':temp.other_reference,
                            'maintanence_manager':temp.maintanence_manager.id,
                            'purchase_manager':temp.purchase_manager.id,
                            'stores_incharge':temp.stores_incharge.id,
                            'terms_of_delivery':temp.terms_of_delivery,
                            'vendor_id': temp.vendor_id.id,
                            'state':'grn',
                            'remarks':temp.remarks,
                            'request_date':temp.request_date,
                            'order_date':temp.order_date,
                            'dispatch_through':temp.dispatch_through,
                            'purchase_type':temp.purchase_type.id,
                            'transporter_name':temp.transporter_name,
                            'transporter_payment_details':temp.transporter_payment_details,
                            'gc_no':temp.gc_no,
                            'gc_date':temp.gc_date,
                            'dc_date':temp.dc_date,
                            'to_name':temp.to_name.id,
                            'plant_manager':temp.plant_manager.id,
                            'document_no':temp.document_no,
                            'revision_no':temp.revision_no,
                            'default_pr_date':temp.default_pr_date,
                            'dc_no':temp.dc_no,
                            'coming_from': 'GRN Analysis',                            
                            'list_in_pi_line':temp.list_in_pi_line,
                            'any_adv_payment':temp.any_adv_payment,
                            'advance_payment_type':temp.advance_payment_type,
                            'cash_amount':temp.cash_amount,
                            'cash_remarks':temp.cash_remarks,
                            'cheque_amount':temp.cheque_amount,
                            'cheque_no':temp.cheque_no,
                            'cheque_remarks':temp.cheque_remarks,
                            'draft_amount':temp.draft_amount,
                            'draft_no':temp.draft_no,
                            'draft_remarks':temp.draft_remarks,
                            'insurance_charges':temp.insurance_charges,
                            'frieght_charges_applied':temp.frieght_charges_applied,
                            'frieght_charges':temp.frieght_charges,
                            'additional_charges':temp.additional_charges,
                            'company_address':temp.company_address.id,
                            'packing_charges':temp.packing_charges
                            })
                        grid_values_1 = self.pool.get('prakruti.grn_inspection_details_line').create(cr,uid, {
                            'product_id': item.product_id.id,
                            'description': item.description,
                            'actual_quantity': item.actual_quantity,
                            'accepted_qty': item.quantity,
                            'quantity': item.quantity,
                            'uom_id': item.uom_id.id,
                            'scheduled_date': item.scheduled_date,                   
                            'unit_price': item.unit_price,
                            'remarks':item.remarks,
                            'packing_style': item.packing_style,
                            'received_per_qty': item.received_per_qty,
                            'batch_no': item.batch_no,
                            'slip_id':item.slip_id.id,
                            'purchase_line_common_id':item.purchase_line_common_id,
                            'hsn_code':item.hsn_code,
                            'discount_id':item.discount_id.id,
                            'discount_rate':item.discount_rate,
                            'cgst_id':item.cgst_id.id,
                            'cgst_rate':item.cgst_rate,
                            'sgst_id':item.sgst_id.id,
                            'sgst_rate':item.sgst_rate,
                            'igst_id':item.igst_id.id,
                            'igst_rate':item.igst_rate, 
                            'taxable_value':item.taxable_value,
                            'taxable_value_after_adding_other':item.taxable_value_after_adding_other,
                            'extra_packing': item.extra_packing,
                            'inspection_line_id': grn_entry_1
                            })
                    cr.execute('''UPDATE prakruti_grn_analysis SET state = 'grn' WHERE id = %s  ''', ((temp.id),))
                    cr.execute("UPDATE prakruti_purchase_requisition SET state = 'grn' WHERE prakruti_purchase_requisition.requisition_no = %s ", ((temp.pr_no),))
            else:
                raise UserError(_('Oops...! Please Select Category'))
        return {}

class PrakrutiGRNAnalysisLine(models.Model):
    _name = 'prakruti.grn_analysis_line'
    _table = 'prakruti_grn_analysis_line'
    _description = 'Purchase GRN Analysis Line'
    
    analysis_line_id = fields.Many2one('prakruti.grn_analysis', ondelete='cascade')
    product_id = fields.Many2one('product.product',string='Product Name',required=True, readonly=1)   
    description = fields.Text(string='Description', readonly=1)
    scheduled_date =fields.Datetime(string='Due On')
    quantity = fields.Float(string='Received Quantity',store=True ,digits=(6,3))
    actual_quantity = fields.Float(string='Quantity', readonly=1 ,digits=(6,3))
    unit_price = fields.Float(string='Unit price' ,digits=(6,3))
    uom_id = fields.Many2one('product.uom',string='UOM',required=True, readonly=1)
    mfg_date = fields.Date(string='Mfg. Date')
    exp_date = fields.Date(string="Expiry Date")
    prakruti_stock_id = fields.Integer('SCREEN COMMON ID')
    remarks = fields.Text('Remarks')
    packing_style = fields.Float(string= 'Packing Style' ,digits=(6,3))
    received_per_qty = fields.Float(string= 'Received Per Qty.' ,digits=(6,3))
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0 ,digits=(6,3))
    accepted_qty = fields.Float('Accepted Qty.', store=True ,digits=(6,3))
    rejected_qty = fields.Float('Rejected Qty.', readonly=True ,digits=(6,3))
    status = fields.Selection([('open','Open'),
                               ('close','Close')],string= 'Status')
    batch_no = fields.Char('Batch No.')
    #Added as per requirement for reserving the product based on the Planning Request
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip ID',readonly=1)    
    
    #Added as per new update so that to close or update the order based on the received qty in Purchase Order by passing this line ID
    #By Karan on 20171018
    purchase_line_common_id = fields.Integer(string="Purchase Line ID")    
    hsn_code = fields.Char(string='HSN/SAC',readonly=1)
    discount_id = fields.Many2one('account.other.tax',string= 'Discount(%)',domain=[('select_type', '=', 'discount')])
    discount_rate = fields.Float(string= 'Discount(%)',default=0)
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_rate = fields.Float(related='cgst_id.per_amount',string= 'CGST Rate',default=0,store=1)
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_rate = fields.Float(related='sgst_id.per_amount',string= 'SGST Rate',default=0,store=1)
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_rate = fields.Float(related='igst_id.per_amount',string= 'IGST Rate',default=0,store=1)
    taxable_value = fields.Float(string= 'Taxable Value',digits=(6,3)) 
    taxable_value_after_adding_other= fields.Float(string='Taxable Value After Adding Other Charges',digits=(6,3))
    
    _sql_constraints = [
        ('unique_batch_no','unique(batch_no)','Batch No. must be Unique !')
        ]
    
    @api.onchange('packing_style','received_per_qty','extra_packing')
    def _compute_total_quantity(self):
        for order in self:
            accepted_qty = 0.0
            quantity = 0.0
            order.update({
                    'accepted_qty': ((order.packing_style * order.received_per_qty) + order.extra_packing),
                    'quantity': ((order.packing_style * order.received_per_qty) + order.extra_packing)
                    })