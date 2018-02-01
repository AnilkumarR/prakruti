'''
Company : EBSL
Author: Induja
Module: Gate Pass
Class 1: PrakrutiGatePass
Class 2: PrakrutiGatePassLine
Table 1 & Reference Id: prakruti_gate_pass ,grid_id
Table 2 & Reference Id: prakruti_gate_pass_line,main_id
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
from openerp.exceptions import ValidationError
import re
import logging
######################################################################################

class PrakrutiGatePass(models.Model):
    _name= 'prakruti.gate_pass'
    _table= 'prakruti_gate_pass'
    _description= 'Gate Pass' 
    _order= 'id desc, pass_no desc'
    _rec_name= 'pass_no'  
    
  
    '''Auto genereation function
    'Format: GP-GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: GP-EXFG\0455\17-18
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
        for temp in self:
            #Addded since the number is generating as the screen is open now it will only allocate the number if button is clicked till then it will show as new 
            #On 20170915 by Karan
            if temp.state != 'draft':
                cr.execute('''SELECT 
                                    CAST(EXTRACT (month FROM pass_date) AS integer) AS month,
                                    CAST(EXTRACT (year FROM pass_date) AS integer) AS year,
                                    id 
                            FROM 
                                    prakruti_gate_pass 
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
                    cr.execute('''select autogenerate_gate_pass_no(%s)''', ((temp.id),)  ) # Database Function: autogenerate_gate_pass_no
                    result = cr.dictfetchall()
                    parent_invoice_id = 0
                    for value in result: parent_invoice_id = value['autogenerate_gate_pass_no'];
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
                        style_format[record.id] = 'GP-'+str(auto_gen) +'/'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE 
                                        prakruti_gate_pass 
                                SET 
                                        pass_no =%s 
                                WHERE 
                                        id=%s ''', ((style_format[record.id]),(temp.id),))
            return style_format
      
    grid_id= fields.One2many('prakruti.gate_pass_line', 'main_id',string= 'Grid')
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=True)
    sales_order_date = fields.Date(string='Sales Order Date', readonly=True)
    pass_no= fields.Char(string='Gate Pass No.', default= 'New', readonly=True)
    pass_date= fields.Date('Date', default= fields.Date.today,readonly=True)
    gp_no= fields.Char('Pass No', compute= '_get_auto')
    auto_no= fields.Integer('Auto')
    req_no_control_id= fields.Integer('Auto Generating id', default= 0)  
    company_id= fields.Many2one('res.company', string= "Company",readonly=True)
    vendor_id= fields.Many2one('res.partner', string= "Vendor", readonly=True)
    po_no = fields.Char(string='Order No', readonly=True)
    order_date = fields.Date(string='Order Date',readonly=True)
    customer_id= fields.Many2one('res.partner', string= "Customer", readonly=True)
    qa_no = fields.Char(string='Analysis No', readonly=True)
    pr_no = fields.Char(string='Requisition No', readonly=True)
    qo_no = fields.Char(string='Quotation No', readonly=True)
    req_no =fields.Char(string='Request No', readonly=True)
    vendor_reference = fields.Char(string='Vendor/Supplier Reference', readonly= "True" )
    payment = fields.Char(string='Mode/Terms of Payments')
    destination = fields.Char(string='Destination')
    other_reference = fields.Char(string='Other Reference')
    maintanence_manager = fields.Many2one('res.users',string="Maintanence Manager")
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager", readonly= "True" )
    stores_incharge = fields.Many2one('res.users','Stores Incharge')  
    terms_of_delivery = fields.Text(string='Terms of Delivery')
    request_date = fields.Date(string = "Requisition Date")
    amount_untaxed= fields.Float(string='Untaxed Amount',digits=(6,3))
    company_address = fields.Many2one('res.company',string='Company Address', readonly= "True" )
    delivery_address = fields.Many2one('res.company',string='Dispatch To', readonly= "True" )
    total_discount = fields.Float(string="Total Discount",digits=(6,3))
    total_tax = fields.Float(string="Total Tax",digits=(6,3))
    dispatch_through = fields.Char(string='Dispatch Through', readonly= "True" )
    excise_id = fields.Many2one('account.other.tax', string='Excise Duty', domain=['|', ('active', '=', False), ('active', '=', True)])
    excise_duty = fields.Float(related='excise_id.per_amount',string= 'Excise Duty(%)',store=True,digits=(6,3))
    total_excise_duty = fields.Float(string= 'Total Excise Duty',digits=(6,3))
    purchase_type = fields.Many2one('product.group',string= 'Purchase Type')
    remarks= fields.Text(string= "Remarks")
    dispatch_no = fields.Char(string='Dispatch No', readonly=True)
    dispatch_date= fields.Date('Dispatch Date', readonly=True)
    vehicle_no = fields.Char(string='Vehicle No')
    time = fields.Datetime('Time of Movement')
    security_id = fields.Many2one('res.users', string='Security Incharge')
    plant_incharge = fields.Many2one('res.users', string='Plant Incharge')
    transport_name = fields.Char(string='Name of the Transporter')
    driver_name = fields.Char(string='Name of the Driver')
    entry_no = fields.Char(string='Security Register Entry No.')
    document_no= fields.Char(string='Doc No.')
    rev_no= fields.Char(string='Rev No.')
    date= fields.Date(string=' Ref Date')
    order_close_flag= fields.Integer('Close The Order', default= 0)# Updated from The Purchase Invoice to set the value to 1 when for that particular gate pass is done or Checked
    order_close_pending= fields.Integer('Pending Order', default= 0)
    cash_amount = fields.Float(string="Amount",digits=(6,3))
    cash_remarks = fields.Text(string="Remarks")    
    cheque_amount = fields.Float(string="Amount",digits=(6,3))
    cheque_no = fields.Integer(string="Cheque No.")
    cheque_remarks = fields.Text(string="Remarks")
    draft_amount = fields.Float(string="Amount",digits=(6,3))
    draft_no = fields.Integer(string="Draft No.")
    draft_remarks = fields.Text(string="Remarks")
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By')
    reference_no= fields.Char(string='Ref No') 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')
    invoice_no_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Invoice Copy')
    dc_no_inward_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Delivery Challan')
    mod_vat_copy_collected_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Does MOD VAT Copy Collected')
    po_no_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Purchase Order No')
    does_lr_copy_received_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Does LR Copy Received')
    dc_no_outward_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Delivery Challan')
    e_way_bill_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'E-Sugama Bill')
    customer_road_permit = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Customer Road Permit')
    coa = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Purchase Order No')
    job_work_documents = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Job Work Documents')
    job_work_documents_remarks = fields.Text(string='Type of Transfer for Job Work') 
    completed_id = fields.Many2one('res.users',string= 'Completed By')
    completed_date = fields.Datetime(string= 'Completed Date',default= fields.Date.today)
    no_of_product = fields.Integer(string= "No of Products")
    amount_taxed= fields.Float(string='Taxed Amount')    
    total_cgst= fields.Float(string='Total CGST')
    total_sgst= fields.Float(string='Total SGST')
    total_igst= fields.Float(string='Total IGST')
    total_gst= fields.Float(string='Total GST')
    insurance_charges = fields.Float(string="Insurance Charges" ,digits=(6,3))
    frieght_charges_applied = fields.Selection([('yes','Yes'),('no','No')], string="Freight Charge Applied", default='no')
    frieght_charges = fields.Float(string="Frieght Charges" ,digits=(6,3))
    additional_charges = fields.Float(string='Additional Charges' ,digits=(6,3))
    packing_charges = fields.Float(string='Packing & Forwarding' ,digits=(6,3))
    grand_total= fields.Float(string='Grand Total')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    vendor_grid_id = fields.Integer(string= 'Price Request Vendor Grid ID',readonly=1)
    any_adv_payment =fields.Selection([
                    ('no', 'No'),
                    ('yes','Yes')
                    ], string= 'Any Advance Payment')
    advance_payment_type =fields.Selection([
                    ('cash', 'CASH'),
                    ('cheque','CHEQUE'),
                    ('demand_draft','DEMAND DRAFT')
                    ], string= 'Done By')
    coming_from =fields.Selection([
		('sales_return', 'Sales Return'),
		('sales', 'Sales'),
		('purchase', 'Purchase'),
		('purchase_return','Purchase Return')
		], string='Coming From',readonly=1)
    document_type = fields.Selection([
		('outward', 'SALES OUTWARD'),
		('inward', 'PURCHASE INWARD'),
		#Newly Added as on 20171205
		('purchase_outward', 'PURCHASE(RETURN) OUTWARD'),
		('sales_inward', 'SALES(RETURN) INWARD'),
		], string='Type of Document',readonly=1)
    
    #added by induja for Dis-->Invoice-->GP-->Logistic flow on 20170912
    invoice_no = fields.Char('Invoice No:', readonly=1)
    invoice_date = fields.Date('Invoice Date',readonly=1)
    
    #Added the state for the reflection same in Tracking for PO on 20170912
    #Updated state instead of checked replace with INWARD DONE and OUTWARD DONE by Karan on 20170920
    state =fields.Selection([
        ('draft', 'In-Transit'),
        ('inward_done', 'Inward Done'),
        ('outward_done', 'Outward Done')], string='Status',readonly=1,default='draft')
    
    #Added as per the updating in the Tracking Screen as on 20170913 by Karan
    actual_date= fields.Date(string= "Actual Delivery Date")
    vendor_accepted_delivery_date = fields.Date(string= 'Vendor Accepted Delivery Date')
    
    
    list_in_pi_line=fields.Integer(string= 'Revised Flag',default=0)
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods')    
    #added by induja on 20171011 for Other details
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today , readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=True) 
    to_name = fields.Many2one('res.users',string="Name") 
    terms=fields.Text('Terms and conditions')

    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')
    
    _defaults = {
        'company_id': _default_company,
        'completed_id': lambda s, cr, uid, c:uid
        }
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['draft','inward_done','outward_done']:
                raise UserError(_('Can\'t Delete record went to further process'))
        return super(PrakrutiGatePass, self).unlink()
    
    '''
    If we select job work documents is "No" then Job work documents remarks is invisible automatically
    '''
    @api.onchange('job_work_documents')
    def _onchange_job_work_documents(self):
        if self.job_work_documents == 'no':
            self.job_work_documents_remarks = ''
    
    '''
    Validation: Gate pass date Can't be less than current date
    '''
    @api.one
    @api.constrains('pass_date')
    def _check_pass_date(self):
        if self.pass_date < fields.Date.today():
            raise ValidationError(
                "Can\'t Select Back Date") 
    
    '''
    Updates the Status
    '''
    @api.one
    @api.multi 
    def action_purchase_return_outward(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("UPDATE prakruti_gate_pass SET state = 'outward_done' WHERE prakruti_gate_pass.id = CAST(%s as integer)",((temp.id),))
        return {}
    
    '''
    Pulls the data to Sales GRN
    '''
    @api.one
    @api.multi 
    def action_checked_incoming_sales_grn(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        c_line = 0
        t_line = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_id = self.pool.get('prakruti.sales_return_grn').create(cr,uid, {
                'return_type':'return_by_customer',
                'order_no':temp.order_no.id,
                'order_date':temp.sales_order_date,
                'customer_id':temp.customer_id.id,
                'company_id':temp.company_id.id,
                'terms':temp.terms,
                'remarks':temp.remarks,
                'reference_date':temp.date,
                'reference_no':temp.reference_no,   
                'revision_no':temp.rev_no
                })
            for item in temp.grid_id:
                grid_id = self.pool.get('prakruti.sales_return_grn_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description': item.description,
                    'quantity': item.quantity,
                    'rejected_qty': item.recieved_qty,
                    'grn_line_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_gate_pass SET state = 'inward_done' WHERE prakruti_gate_pass.id = CAST(%s as integer)",((temp.id),))
        return {}
    
    
    @api.one
    @api.multi 
    def action_checked_outgoing(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        c_line = 0
        t_line = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.dc_no_outward_check and temp.e_way_bill_check and temp.customer_road_permit and temp.coa and temp.job_work_documents:
                ebsl_id = self.pool.get('prakruti.logistics_invoice_tracking').create(cr,uid, {
                    'invoice_no':temp.invoice_no,
                    'invoice_date':temp.invoice_date,
                    'order_no':temp.order_no.id,
                    'order_date':temp.order_date,
                    'dispatch_no':temp.dispatch_no,
                    'dispatch_date':temp.dispatch_date,
                    'customer_id':temp.customer_id.id,
                    'requested_id':temp.requested_id.id,
                    'order_id':temp.order_id.id,
                    'quotation_id':temp.quotation_id.id,
                    'dispatch_id':temp.dispatch_id.id,
                    'reference_no':temp.reference_no,
                    'dc_no_outward_check':'yes',
                    'e_way_bill_check':'yes',
                    'customer_road_permit':'yes',
                    'coa':'yes',
                    'job_work_documents':'yes',
                    'coming_from':'sales',
                    'terms':temp.terms,
                    'remarks':temp.remarks,
                    'reference_date':temp.date,
                    'reference_no':temp.reference_no,   
                    'revision_no':temp.rev_no
                    })
                for item_line in temp.grid_id:
                    erp_id = self.pool.get('prakruti.sales_line_in_logistics').create(cr,uid, {
                        'product_id':item_line.product_id.id,
                        'uom_id':item_line.uom_id.id,
                        'quantity':item_line.quantity,
                        'unit_price':item_line.unit_price,
                        'packing_details': item_line.packing_details,
                        'logistics_line_id': ebsl_id
                    })
                #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Gate Pass Outgoing')],context=context)[0]
                #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True) 
                cr.execute("UPDATE prakruti_gate_pass SET state = 'outward_done' WHERE prakruti_gate_pass.id = CAST(%s as integer)",((temp.id),))
                #updating the product level checked if it is received in the gate pass line
                cr.execute('''  UPDATE 
                                    prakruti_gate_pass_line 
                                SET 
                                    checked_flag = 1,
                                    checked_status = 'Delivered'
                                WHERE 
                                    main_id = %s''',((temp.id),))    
            else:
                raise UserError(_('Please enter Checklist'))
        return {}
    
    '''
    Pulls the data to GRN Analysis
    '''
    @api.one
    @api.multi 
    def action_checked_incoming(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        line1 = 0
        c_line = 0
        t_line = 0
        no_of_line = 0
        entered_line = 0
        checked_line = 0
        date_entry_line = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.invoice_no_check and temp.dc_no_inward_check and temp.mod_vat_copy_collected_check and temp.po_no_check and temp.does_lr_copy_received_check and temp.actual_date:
                cr.execute('''  SELECT
                                    COUNT(id) AS date_entry_line 
                                FROM
                                    prakruti_gate_pass_line
                                WHERE
                                    main_id = %s AND checked_flag = 0 AND actual_date IS NOT NULL ''',((temp.id),))
                for line in cr.dictfetchall():
                    date_entry_line = line['date_entry_line']
                cr.execute('''  SELECT
                                    COUNT(id) AS checked_line 
                                FROM
                                    prakruti_gate_pass_line
                                WHERE
                                    main_id = %s AND checked_flag = 0 AND ((no_of_packings * pack_per_qty) + extra_packing) > 0 AND recieved_qty > 0''',((temp.id),))
                for line in cr.dictfetchall():
                    checked_line = line['checked_line']
                if checked_line == date_entry_line:
                    ebsl_id = self.pool.get('prakruti.grn_analysis').create(cr,uid, {
                        'cash_amount':temp.cash_amount,
                        'cash_remarks':temp.cash_remarks,
                        'cheque_amount':temp.cheque_amount,
                        'cheque_no':temp.cheque_no,
                        'cheque_remarks':temp.cheque_remarks,
                        'draft_amount':temp.draft_amount,
                        'draft_no':temp.draft_no,
                        'draft_remarks':temp.draft_remarks,
                        'advance_payment_type':temp.advance_payment_type,
                        'any_adv_payment':temp.any_adv_payment,
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
                        'state':'grn_analysis',
                        'remarks':temp.remarks,
                        'request_date':temp.request_date,
                        'order_date':temp.order_date,                        
                        'amount_untaxed':temp.amount_untaxed,
                        'additional_charges':temp.additional_charges,
                        'grand_total':temp.grand_total,
                        'frieght_charges_applied':temp.frieght_charges_applied,
                        'frieght_charges':temp.frieght_charges,
                        'packing_charges':temp.packing_charges,
                        'total_discount':temp.total_discount,
                        'total_tax':temp.total_tax,
                        'dispatch_through':temp.dispatch_through,
                        'excise_duty':temp.excise_duty,
                        'total_excise_duty':temp.total_excise_duty,
                        'purchase_type':temp.purchase_type.id,
                        'to_name':temp.to_name.id,
                        'plant_manager':temp.plant_manager.id,
                        'company_address':temp.company_id.id,
                        'document_no':temp.document_no,
                        'revision_no':temp.rev_no,
                        'default_pr_date':temp.default_pr_date,
                        'transporter_name':temp.transport_name,
                        'list_in_pi_line':temp.list_in_pi_line,
                        'insurance_charges':temp.insurance_charges
                        })
                    cr.execute('''  SELECT 
                                        product_id,
                                        description,
                                        quantity,
                                        recieved_qty,
                                        uom_id,
                                        scheduled_date,
                                        remarks,
                                        no_of_packings,
                                        pack_per_qty,
                                        extra_packing,
                                        slip_id,
                                        unit_price,
                                        purchase_line_common_id,
                                        hsn_code,
                                        discount_id,
                                        discount_rate,
                                        cgst_id,
                                        cgst_rate,
                                        sgst_id,
                                        sgst_rate,
                                        igst_id,
                                        igst_rate,
                                        taxable_value_after_adding_other,
                                        taxable_value
                                    FROM
                                        prakruti_gate_pass_line
                                    WHERE
                                        main_id = %s AND checked_flag = 0 AND ((no_of_packings * pack_per_qty) + extra_packing) > 0 
                                ''',((temp.id),))
                    for item in cr.dictfetchall():
                        erp_id = self.pool.get('prakruti.grn_analysis_line').create(cr,uid, {
                            'product_id': item['product_id'],
                            'description': item['description'],
                            'actual_quantity': item['quantity'],
                            'unit_price': item['unit_price'],
                            'accepted_qty': ((item['no_of_packings'] * item['pack_per_qty']) + item['extra_packing']),
                            'quantity': ((item['no_of_packings'] * item['pack_per_qty']) + item['extra_packing']),
                            'uom_id': item['uom_id'],
                            'scheduled_date': item['scheduled_date'],
                            'remarks':item['remarks'],
                            'packing_style': item['no_of_packings'],
                            'received_per_qty': item['pack_per_qty'],
                            'extra_packing': item['extra_packing'],
                            'purchase_line_common_id':item['purchase_line_common_id'],
                            'slip_id':item['slip_id'],
                            'hsn_code':item['hsn_code'],
                            'discount_id':item['discount_id'],
                            'discount_rate':item['discount_rate'],
                            'cgst_id':item['cgst_id'],
                            'cgst_rate':item['cgst_rate'],
                            'sgst_id':item['sgst_id'],
                            'sgst_rate':item['sgst_rate'],
                            'igst_id':item['igst_id'],
                            'igst_rate':item['igst_rate'], 
                            'taxable_value':item['taxable_value'],
                            'taxable_value_after_adding_other':item['taxable_value_after_adding_other'],                             
                            'analysis_line_id': ebsl_id
                        })
                    #updating the product level checked if it is received in the gate pass line
                    cr.execute('''  UPDATE 
                                        prakruti_gate_pass_line 
                                    SET 
                                        checked_flag = 1,
                                        checked_status = 'Delivered'
                                    WHERE 
                                        main_id = %s AND 
                                        ((no_of_packings * pack_per_qty) + extra_packing) > 0 ''',((temp.id),)) 
                    #Updating the Expected Date if not entered in the Grid Level
                    cr.execute('''  UPDATE 
                                        prakruti_gate_pass_line 
                                    SET 
                                        actual_date = a.actual_date
                                    FROM(
                                        SELECT
                                            prakruti_gate_pass.actual_date,
                                            prakruti_gate_pass.id
                                        FROM
                                            prakruti_gate_pass
                                        WHERE
                                            prakruti_gate_pass.id = %s
                                        ) AS a 
                                    WHERE 
                                        main_id = %s AND 
                                        a.id = prakruti_gate_pass_line.main_id AND 
                                        prakruti_gate_pass_line.actual_date IS NULL
                                        ''',((temp.id),(temp.id),))    
                    cr.execute('''  UPDATE 
                                        prakruti_purchase_line AS b 
                                    SET 
                                        status= 'close', 
                                        balance_qty = a.balance_qty, 
                                        no_of_packings = a.no_of_packings, 
                                        pack_per_qty = a.pack_per_qty, 
                                        extra_packing = a.extra_packing 
                                    FROM(
                                        SELECT 
                                            main_id,
                                            purchase_line_common_id,
                                            product_id,
                                            balance_qty,
                                            status,
                                            no_of_packings,
                                            pack_per_qty,
                                            extra_packing 
                                        FROM 
                                            prakruti_gate_pass_line 
                                        WHERE main_id= %s 
                                        ) AS a 
                                    WHERE 
                                        a.purchase_line_common_id = b.id AND 
                                        a.product_id = b.product_id AND 
                                        a.balance_qty <= 0''',((temp.id),))
                    cr.execute('''  UPDATE 
                                        prakruti_purchase_line AS b 
                                    SET 
                                        balance_qty = a.balance_qty, 
                                        no_of_packings = a.no_of_packings, 
                                        pack_per_qty = a.pack_per_qty, 
                                        extra_packing = a.extra_packing 
                                    FROM(
                                        SELECT 
                                            main_id,
                                            purchase_line_common_id,
                                            product_id,
                                            balance_qty,
                                            status,
                                            no_of_packings,
                                            pack_per_qty,
                                            extra_packing 
                                        FROM 
                                            prakruti_gate_pass_line 
                                        WHERE 
                                            main_id= %s 
                                        ) AS a 
                                    WHERE 
                                        a.purchase_line_common_id = b.id AND 
                                        a.product_id = b.product_id AND 
                                        a.balance_qty > 0''',((temp.id),))
                    #Updating Records in the Logistics PO Tracking like Delivery Date and Vendor Actual Delivery date
                    cr.execute('''  UPDATE
                                        prakruti_logistics_po_tracking
                                    SET
                                        actual_date = a.actual_date
                                    FROM(
                                        SELECT
                                            prakruti_gate_pass.actual_date,
                                            prakruti_gate_pass.vendor_accepted_delivery_date,
                                            prakruti_gate_pass.po_no
                                        FROM
                                            prakruti_gate_pass JOIN
                                            prakruti_gate_pass_line ON
                                            prakruti_gate_pass.id = prakruti_gate_pass_line.main_id
                                        WHERE
                                            prakruti_gate_pass.id = %s
                                        ) AS a
                                    WHERE
                                        prakruti_logistics_po_tracking.po_no = a.po_no AND
                                        prakruti_logistics_po_tracking.status = 'in_transit'
                                    ''',((temp.id),))
                    #Updating Records in the Logistics PO Tracking Grid like Delivery Date and Vendor Actual Delivery date
                    cr.execute('''  UPDATE
                                        prakruti_purchase_line_in_logistics
                                    SET
                                        actual_date = a.actual_date
                                    FROM(
                                        SELECT
                                            prakruti_gate_pass_line.actual_date,
                                            prakruti_gate_pass_line.vendor_accepted_delivery_date,
                                            prakruti_gate_pass_line.requisition_line_id
                                        FROM
                                            prakruti_gate_pass_line
                                        WHERE
                                            prakruti_gate_pass_line.main_id = %s
                                        ) AS a
                                    WHERE
                                        prakruti_purchase_line_in_logistics.requisition_line_id = a.requisition_line_id
                                    ''',((temp.id),))
                    #Updating Records in the Logistics PO Tracking like status
                    cr.execute('''  SELECT 
                                        count(prakruti_purchase_line.id) AS total_no_close_line 
                                    FROM
                                        prakruti_purchase_line JOIN
                                        prakruti_purchase_order ON
                                        prakruti_purchase_line.purchase_line_id = prakruti_purchase_order.id
                                    WHERE
                                        prakruti_purchase_line.status = 'close' AND
                                        prakruti_purchase_order.po_no = %s
                                            ''',((temp.po_no),))
                    for line in cr.dictfetchall():
                        total_no_close_line = line['total_no_close_line']
                    cr.execute('''  SELECT 
                                        count(prakruti_purchase_line.id) AS total_no_line 
                                    FROM
                                        prakruti_purchase_line JOIN
                                        prakruti_purchase_order ON
                                        prakruti_purchase_line.purchase_line_id = prakruti_purchase_order.id
                                    WHERE
                                        prakruti_purchase_order.po_no = %s
                                            ''',((temp.po_no),))
                    for line in cr.dictfetchall():
                        total_no_line = line['total_no_line']
                    if total_no_line == total_no_close_line:
                        cr.execute('''  UPDATE 
                                            prakruti_logistics_po_tracking 
                                        SET
                                            status = 'deliver'
                                        WHERE
                                            prakruti_logistics_po_tracking.po_no = %s
                                        ''',((temp.po_no),))
                        cr.execute('''UPDATE prakruti_gate_pass SET state = 'inward_done' WHERE prakruti_gate_pass.id = %s''',((temp.id),))
                    else:
                        cr.execute('''  UPDATE 
                                            prakruti_logistics_po_tracking 
                                        SET
                                            status = 'partial_deliver'
                                        WHERE
                                            prakruti_logistics_po_tracking.po_no = %s
                                        ''',((temp.po_no),))
                        cr.execute('''UPDATE prakruti_gate_pass SET state = 'inward_done' WHERE prakruti_gate_pass.id = %s''',((temp.id),))
                    cr.execute('''  SELECT
                                        COUNT(id) AS no_of_line 
                                    FROM
                                        prakruti_gate_pass_line
                                    WHERE
                                        main_id = %s''',((temp.id),))
                    for line in cr.dictfetchall():
                        no_of_line = line['no_of_line']
                    cr.execute('''  SELECT
                                        COUNT(id) AS entered_line 
                                    FROM
                                        prakruti_gate_pass_line
                                    WHERE
                                        main_id = %s AND checked_flag = 1 ''',((temp.id),))
                    for line in cr.dictfetchall():
                        entered_line = line['entered_line']
                    if no_of_line == entered_line:
                        cr.execute('''UPDATE prakruti_purchase_requisition SET state = 'inward_done' where prakruti_purchase_requisition.requisition_no = %s  ''', ((temp.pr_no),))
                        #cr.execute('''UPDATE prakruti_purchase_order SET state = 'order' WHERE prakruti_purchase_order.po_no = %s''',((temp.po_no),))
                else:
                    raise UserError(_('No Any Product left...\nOr might be Packing Style and Packing Per Qty are Not Entered Yet...\nOr might be Delivery Date Not Yet Entered...'))                   
            else:
                raise UserError(_('Please Enter Checklist...\nOR\nTheir Might Be Delivery Date Not Entered Yet...'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Gate Pass Incoming')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    
    
    
    
class PrakrutiGatePassLine(models.Model):
    _name= 'prakruti.gate_pass_line'
    _table= 'prakruti_gate_pass_line'
    _description= 'Gate Pass Line'

    main_id = fields.Many2one('prakruti.gate_pass', string= "Grid Line") 
    product_id= fields.Many2one('product.product', string= "Product Name", readonly=True)    
    description = fields.Text(string='Description')
    uom_id = fields.Many2one('product.uom',string='UOM')
    scheduled_date =fields.Datetime(string='Due On')
    unit_price = fields.Float(string='Unit price',digits=(6,3))
    discount = fields.Float(string='Discount(%)',digits=(6,3))
    tax_id = fields.Many2one('account.other.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    tax_price = fields.Float(related='tax_id.per_amount',string='Taxes', store=True,digits=(6,3)) 
    no_of_packings= fields.Float(string= "No. of Packings",digits=(6,3))
    pack_per_qty= fields.Float(string= "Packing Per. Qty.",digits=(6,3)) 
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0,digits=(6,3))
    quantity= fields.Float(string= 'Ordered Qty.',digits=(6,3)) 
    recieved_qty= fields.Float(string= 'Received Qty.',compute='_compute_received_quantity',store=True,digits=(6,3)) 
    remarks= fields.Text(string= "Remarks")
    balance_qty = fields.Float(string="Balance Qty",compute='_compute_balance_qty',store=True,digits=(6,3))
    packing_details = fields.Char('Packing Details')
    hsn_code = fields.Char(string='HSN/SAC',readonly=1)
    discount_id = fields.Many2one('account.other.tax', string='Discount', domain=['|', ('active', '=', False), ('active', '=', True)])
    discount_rate = fields.Float(string='Discount Rate' ,digits=(6,3),default=0)
    discount_value = fields.Float(string= 'Discount Amount',digits=(6,3)) 
    taxable_value = fields.Float(string= 'Taxable Value',digits=(6,3)) 
    taxable_value_after_adding_other= fields.Float(string='Taxable Value After Adding Other Charges',digits=(6,3))
    total= fields.Float(string='Total',digits=(6,3))
    cgst_id = fields.Many2one('account.other.tax', string='CGST Rate', domain=['|', ('active', '=', False), ('active', '=', True)])
    cgst_rate = fields.Float(string='CGST Rate' ,digits=(6,3),default=0)
    cgst_value = fields.Float(string= 'CGST Amount',digits=(6,3))
    sgst_id = fields.Many2one('account.other.tax', string='SGST Rate', domain=['|', ('active', '=', False), ('active', '=', True)])
    sgst_rate = fields.Float(string='SGST Rate' ,digits=(6,3),default=0)
    sgst_value = fields.Float(string= 'SGST Amount',digits=(6,3)) 
    igst_id = fields.Many2one('account.other.tax', string='IGST Rate', domain=['|', ('active', '=', False), ('active', '=', True)])
    igst_rate = fields.Float(string='IGST Rate' ,digits=(6,3),default=0)
    igst_value = fields.Float(string= 'IGST Amount',digits=(6,3))
    packing_charges = fields.Float(string='Packing Charges')
    frieght_charges = fields.Float(string='Frieght Charges')
    additional_charges = fields.Float(string='Additional Charges')
    no_of_product = fields.Integer(string= "No of Products")
    subtotal = fields.Float(string= 'Sub Total',digits=(6,3))
    insurance_charges = fields.Float(string='Insurance Charges') 
    purchase_line_common_id = fields.Integer(string="Purchase Line ID")  
    requisition_line_id = fields.Integer(string= 'Requisition Line ID',readonly=1)
    status = fields.Selection([
		('open', 'Open'),
		('close','Close')],default= 'open', string= 'Status')
    
    # Added On 20170912 for the Particular Item is Received or Not    
    checked_flag = fields.Integer(string = 'Is Delivered',default = 0,readonly=1)    
    checked_status = fields.Char(string = 'Is Delivered',default = 'Not Yet Delivered',readonly=1)
    #Added for productwise delivery date as on 20170913 by Karan
    #Delivery date will be updated to the Tracking Screen
    expected_date = fields.Date(string= "Expected Delivery Date",readonly=1)
    actual_date = fields.Date(string= "Actual Delivery Date")
    vendor_accepted_delivery_date = fields.Date(string= 'Vendor Accepted Delivery Date')
    #Added as per requirement for reserving the product based on the Planning Request
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip ID',readonly=1)
    
   
    
    '''
    Balance Qty Calculation
    '''
    @api.depends('quantity','recieved_qty')
    def _compute_balance_qty(self):
        for order in self:
            balance_qty = 0.0            
            order.update({                
                'balance_qty': order.quantity - order.recieved_qty 
            })
    
    '''
    Received Qty Calculation
    '''
    @api.depends('no_of_packings','pack_per_qty','extra_packing')
    def _compute_received_quantity(self):
        for order in self:
            recieved_qty = 0.0
            order.update({
                    'recieved_qty': ((order.no_of_packings * order.pack_per_qty) + order.extra_packing)
                    })