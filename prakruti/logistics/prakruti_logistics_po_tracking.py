'''
Company : EBSL
Author: Induja
Module: PO Logistics Tracking
Class 1: prakruti_logistics_po_tracking
Class 2: PrakrutiPurchaseLineInLogistics
Table 1 & Reference Id: prakruti_logistics_po_tracking ,order_line
Table 2 & Reference Id: prakruti_purchase_line_in_logistics,logistics_line_id
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
'''

# -*- coding: utf-8 -*-
import openerp
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize, image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
from openerp import tools
from datetime import timedelta
from openerp.osv import osv,fields
from openerp import models, fields, api, _
from openerp.tools.translate import _
import sys, os, urllib2, urlparse
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import email, re
from datetime import datetime
from datetime import date, timedelta
from lxml import etree
import cgi
import logging
import lxml.html
import lxml.html.clean as clean
import openerp.pooler as pooler
import random
import re
import socket
import threading
import time
from openerp.tools import image_resize_image_big

class prakruti_logistics_po_tracking(models.Model):
    _name= "prakruti.logistics_po_tracking"
    _table= "prakruti_logistics_po_tracking"
    _description = 'PO Logistics Tracking'
    _order= "id desc"
    _rec_name= "tracking_number"
    
    order_line = fields.One2many('prakruti.purchase_line_in_logistics','logistics_line_id',string='Order Line of Logistics')
    po_no = fields.Char(string='Order No', readonly=True)
    order_date= fields.Date(string= "Order Date")
    vendor_id= fields.Many2one('res.partner',string= "Vendor Name")
    tracking_number= fields.Char(string= "Tracking Number")
    expected_date= fields.Date(string= "Expected Delivery Date")
    tracking_date=fields.Date(string= "Tracking Date")
    actual_date= fields.Date(string= "Delivery Date")
    vendor_accepted_delivery_date = fields.Date(string= 'Vendor Accepted Delivery Date',default=fields.Date.today,required=1)
    flag_count_display_product = fields.Integer(default=0)
    qa_no = fields.Char(string='Analysis No')
    pr_no = fields.Char(string='Requisition No')
    qo_no = fields.Char(string='Quotation No')
    req_no =fields.Char(string='Request No')
    vendor_reference = fields.Char(string='Vendor/Supplier Reference')
    payment = fields.Char(string='Mode/Terms of Payments')
    destination = fields.Char(string='Destination')
    other_reference = fields.Char(string='Other Reference')
    maintanence_manager = fields.Many2one('res.users',string="Maintanence Manager")
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager")
    stores_incharge = fields.Many2one('res.users',string="Stores Incharge")
    terms_of_delivery = fields.Text(string='Terms of Delivery')
    remarks=fields.Text('Remarks')
    request_date = fields.Date(string = "Requisition Date")
    amount_untaxed= fields.Float(string='Untaxed Amount',digits=(6,3))
    dispatch_through = fields.Char(string='Dispatch Through')
    total_discount = fields.Float(string="Total Discount",digits=(6,3))
    total_tax = fields.Float(string="Total Tax",digits=(6,3))
    excise_id = fields.Many2one('account.other.tax', string='Excise Duty', domain=['|', ('active', '=', False), ('active', '=', True)])
    excise_duty = fields.Float(related='excise_id.per_amount',string= 'Excise Duty(%)',store=True,digits=(6,3))
    total_excise_duty = fields.Float(string= 'Total Excise Duty',digits=(6,3))
    purchase_type = fields.Many2one('product.group',string= 'Purchase Type')
    company_address = fields.Many2one('res.company',string='Company Address')
    vehicle_no = fields.Char(string="Vehicle No.")
    transport_name=fields.Char(string="Name of the Transporter")
    cash_amount = fields.Float(string="Amount",digits=(6,3))
    cash_remarks = fields.Text(string="Remarks")    
    cheque_amount = fields.Float(string="Amount",digits=(6,3))
    cheque_no = fields.Integer(string="Cheque No.")
    cheque_remarks = fields.Text(string="Remarks")    
    draft_amount = fields.Float(string="Amount",digits=(6,3))
    draft_no = fields.Integer(string="Draft No.")
    draft_remarks = fields.Text(string="Remarks") 
    product_id = fields.Many2one('product.product', related='order_line.product_id', string='Product Name')
    invoice_no_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Invoice Copy')
    dc_no_inward_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Delivery Challan')
    mod_vat_copy_collected_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Does MOD VAT Copy Collected')
    po_no_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Purchase Order No')
    does_lr_copy_received_check = fields.Selection([('yes','Yes'),('no','No')],default='yes',string= 'Does LR Copy Received')
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
    state = fields.Selection([
		('requisition', 'Draft Requisition'),
		('request','Purchase Price Request'),
		('quotation','Purchase Quotation'),
                ('analysis','Purchase Quotation Analysis'),
                ('reject','Purchase Order Rejected'),
                ('order','Purchase Order Accepted'),
                ('confirm','Purchase Order Confirm')], string= "Order Status",default = 'confirm')
    any_adv_payment =fields.Selection([
                    ('no', 'No'),
                    ('yes','Yes')
                    ], string= 'Any Advance Payment')
    advance_payment_type =fields.Selection([
                    ('cash', 'CASH'),
                    ('cheque','CHEQUE'),
                    ('demand_draft','DEMAND DRAFT')
                    ], string= 'Done By')
    # Status Updated for Entry in the Gate Pass When it is in the In-Transit and also partially is newly updated on 20170912
    status = fields.Selection([
        ('open','Logistic Draft'),
        ('in_transit','Logistic In Transit'),
        ('partial_deliver','Partially Delivered'),
        ('deliver','Delivered')],string= "Tracking Status",default='open')
    # Added as on 20170918 by karan to restrict the number of entry in GP since earlier it was having multiple entry for the same order
    send_to_gatepass_flag = fields.Integer(string= "Sent to Gate Pass",default = 0)
    
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods',string = 'Category')    
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No" , default='PPPL-PUR-F-004' , readonly=1)
    revision_no = fields.Char(string = "Rev. No", default='01' , readonly=1)
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today , readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=True) 
    to_name = fields.Many2one('res.users',string="Name") 
    
  
    '''
    Cannot able to delete this record 
    '''
            
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete'))
        return super(prakruti_logistics_po_tracking, self).unlink()            
            
    
    '''
    Updating status tp in transit
    '''        
    @api.one
    @api.multi 
    def order_in_transit(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.send_to_gatepass_flag == 0:
                if temp.tracking_number and temp.vehicle_no and temp.transport_name:
                    if temp.expected_date:
                        if temp.expected_date >= temp.order_date:
                            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Logistics PO Tracking')],context=context)[0]
                            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
                            #Updating the Expected Date if not entered in the Grid Level
                            cr.execute('''  UPDATE 
                                                prakruti_purchase_line_in_logistics 
                                            SET 
                                                expected_date = a.expected_date
                                            FROM(
                                                SELECT
                                                    prakruti_logistics_po_tracking.expected_date,
                                                    prakruti_logistics_po_tracking.id
                                                FROM
                                                    prakruti_logistics_po_tracking
                                                WHERE
                                                    prakruti_logistics_po_tracking.id = %s
                                                ) AS a 
                                            WHERE 
                                                logistics_line_id = %s AND 
                                                a.id = prakruti_purchase_line_in_logistics.logistics_line_id AND 
                                                prakruti_purchase_line_in_logistics.expected_date IS NULL
                                                ''',((temp.id),(temp.id),))
                            #Updating the Vendor Expected Date if not entered in the Grid Level
                            cr.execute('''  UPDATE 
                                                prakruti_purchase_line_in_logistics 
                                            SET 
                                                vendor_accepted_delivery_date = a.vendor_accepted_delivery_date
                                            FROM(
                                                SELECT
                                                    prakruti_logistics_po_tracking.vendor_accepted_delivery_date,
                                                    prakruti_logistics_po_tracking.id
                                                FROM
                                                    prakruti_logistics_po_tracking
                                                WHERE
                                                    prakruti_logistics_po_tracking.id = %s
                                                ) AS a 
                                            WHERE 
                                                logistics_line_id = %s AND 
                                                a.id = prakruti_purchase_line_in_logistics.logistics_line_id AND 
                                                prakruti_purchase_line_in_logistics.vendor_accepted_delivery_date IS NULL
                                                ''',((temp.id),(temp.id),))
                            to_gate_pass= self.pool.get('prakruti.gate_pass').create(cr,uid, {
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
                                'remarks':temp.remarks,
                                'request_date':temp.request_date,
                                'order_date':temp.order_date,                        
                                'amount_untaxed':temp.amount_untaxed,
                                'total_discount':temp.total_discount,
                                'total_tax':temp.total_tax,
                                'dispatch_through':temp.dispatch_through,
                                'excise_id':temp.excise_id.id,
                                'excise_duty':temp.excise_duty,
                                'total_excise_duty':temp.total_excise_duty,
                                'purchase_type':temp.purchase_type.id,
                                'customer_id':temp.company_address.id,
                                'company_id':temp.company_address.id,
                                'vehicle_no':temp.vehicle_no,
                                'transport_name':temp.transport_name,
                                'coming_from':'purchase',
                                'document_type':'inward',    
                                'invoice_no_check':temp.invoice_no_check,
                                'dc_no_inward_check':temp.dc_no_inward_check,
                                'mod_vat_copy_collected_check':temp.mod_vat_copy_collected_check,
                                'po_no_check':temp.po_no_check,
                                'does_lr_copy_received_check':temp.does_lr_copy_received_check,
                                'no_of_product':temp.no_of_product,
                                'amount_taxed':temp.amount_taxed,
                                'total_cgst':temp.total_cgst,
                                'total_sgst':temp.total_sgst,
                                'total_igst':temp.total_igst,
                                'total_gst':temp.total_gst,
                                'insurance_charges':temp.insurance_charges,
                                'frieght_charges_applied':temp.frieght_charges_applied,
                                'frieght_charges':temp.frieght_charges,
                                'packing_charges':temp.packing_charges,
                                'additional_charges':temp.additional_charges,
                                'grand_total':temp.grand_total,
                                'categorization':temp.categorization,
                                'to_name':temp.to_name.id,
                                'plant_manager':temp.plant_manager.id,
                                'document_no':temp.document_no,
                                'rev_no':temp.revision_no,
                                'default_pr_date':temp.default_pr_date,
                                'vendor_accepted_delivery_date':temp.vendor_accepted_delivery_date
                                    })
                            for item in temp.order_line:
                                gate_pass_grid_item= self.pool.get('prakruti.gate_pass_line').create(cr,uid, {
                                    'product_id': item.product_id.id,
                                    'description': item.description,
                                    'actual_quantity': item.quantity,
                                    'accepted_qty': item.quantity,
                                    'quantity': item.quantity,
                                    'uom_id': item.uom_id.id,
                                    'scheduled_date': item.scheduled_date,                   
                                    'unit_price': item.unit_price,
                                    'discount': item.discount,
                                    'tax_price': item.tax_price,
                                    'tax_id': item.tax_id.id,
                                    'remarks':item.remarks,
                                    'no_of_packings': item.no_of_packings,
                                    'pack_per_qty': item.pack_per_qty,
                                    'extra_packing':item.extra_packing,
                                    'purchase_line_common_id':item.purchase_line_common_id,
                                    'hsn_code': item.hsn_code,
                                    'discount_id':item.discount_id.id,
                                    'discount_rate':item.discount_rate,
                                    'discount_value':item.discount_value,
                                    'taxable_value': item.taxable_value,
                                    'total':item.total,
                                    'cgst_id':item.cgst_id.id,
                                    'cgst_rate':item.cgst_rate,
                                    'cgst_value': item.cgst_value,
                                    'sgst_id':item.sgst_id.id,
                                    'sgst_rate':item.sgst_rate,
                                    'sgst_value': item.sgst_value,
                                    'igst_id':item.igst_id.id,
                                    'igst_rate':item.igst_rate,
                                    'igst_value': item.igst_value,
                                    'taxable_value_after_adding_other':item.taxable_value_after_adding_other,
                                    'subtotal': item.subtotal,
                                    'no_of_product':item.no_of_product,
                                    'packing_charges':item.packing_charges,
                                    'frieght_charges':item.frieght_charges,
                                    'additional_charges':item.additional_charges,
                                    'insurance_charges':item.insurance_charges,
                                    'expected_date':item.expected_date,
                                    'requisition_line_id':item.requisition_line_id,
                                    'vendor_accepted_delivery_date':item.vendor_accepted_delivery_date,
                                    'slip_id':item.slip_id.id,
                                    'main_id':to_gate_pass
                                        })
                            cr.execute('''UPDATE prakruti_logistics_po_tracking SET status = 'in_transit',send_to_gatepass_flag = 1 where prakruti_logistics_po_tracking.id = %s  ''', ((temp.id),)) 
                            cr.execute('''UPDATE prakruti_purchase_requisition SET state = 'in_transit' where prakruti_purchase_requisition.requisition_no = %s  ''', ((temp.pr_no),))
                        else:
                            raise UserError(_('Oops...! Your Expected delivery date should not be less than Order date'))
                    else:
                        raise UserError(_('Oops...! Please Enter Expected delivery date'))
                else:
                    raise UserError(_('Oops...! Please Enter\nTracking Number\nVehicle Number\nTransporter Name'))
            else:
                raise UserError(_('The Action is already Performed...\nPlease Refresh the Page...'))
        return True

class PrakrutiPurchaseLineInLogistics(models.Model):
    _name = 'prakruti.purchase_line_in_logistics'
    _table = 'prakruti_purchase_line_in_logistics'
    _description = 'PO Logistics Tracking Line'
    
    logistics_line_id = fields.Many2one('prakruti.logistics_po_tracking', ondelete='cascade')        
    product_id = fields.Many2one('product.product',string='Product Name')    
    description = fields.Text(string='Description')
    uom_id = fields.Many2one('product.uom',string='UOM')
    scheduled_date =fields.Datetime(string='Due On')
    unit_price = fields.Float(string='Unit price',digits=(6,3))
    discount = fields.Float(string='Discount(%)',digits=(6,3))
    tax_type = fields.Selection([('cst','CST'),('tin','TIN'),('tax','Tax'),('vat','VAT')], string="Tax", default= 'tax')
    tax_id = fields.Many2one('account.other.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    tax_price = fields.Float(related='tax_id.per_amount',string='Taxes', store=True,digits=(6,3)) 
    remarks=fields.Text('Remarks')
    status = fields.Selection([
		('open', 'Open'),
		('close','Close')],default= 'open', string= 'Status') 
    purchase_line_common_id = fields.Integer(string="Purchase Line ID")
    quantity = fields.Float(string='Quantity',digits=(6,3))    
    no_of_packings= fields.Float(string= "No. of Packings",digits=(6,3))
    pack_per_qty= fields.Float(string= "Packing Per. Qty.",digits=(6,3))
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0,digits=(6,3))
    hsn_code = fields.Char(string='HSN/SAC',readonly=1)
    discount_id = fields.Many2one('account.other.tax', string='Discount', domain=['|', ('active', '=', False), ('active', '=', True)])
    discount_rate = fields.Float(string='Discount Rate' ,digits=(6,3),default=0)
    discount_value = fields.Float(string= 'Discount Amount',digits=(6,3)) 
    taxable_value = fields.Float(string= 'Taxable Value',digits=(6,3))
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
    taxable_value_after_adding_other= fields.Float(string='Taxable Value After Adding Other Charges',digits=(6,3))
    packing_charges = fields.Float(string='Packing Charges')
    frieght_charges = fields.Float(string='Frieght Charges')
    additional_charges = fields.Float(string='Additional Charges')
    no_of_product = fields.Integer(string= "No of Products")
    subtotal = fields.Float(string= 'Sub Total',digits=(6,3))
    insurance_charges = fields.Float(string='Insurance Charges')
    requisition_line_id = fields.Integer(string= 'Requisition Line ID',readonly=1)
    #Added for productwise delivery date and expected date as on 20170913 by Karan
    # If expected date is entered than no need to update here if not than it will update from the Master
    expected_date= fields.Date(string= "Expected Delivery Date")
    actual_date= fields.Date(string= "Actual Delivery Date",readonly=1)#will be updated from the Gate Pass
    vendor_accepted_delivery_date = fields.Date(string= 'Vendor Accepted Delivery Date',default=fields.Date.today,required=1)
    #Added as per requirement for reserving the product based on the Planning Request
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip ID',readonly=1)
    
    
    
    '''
    Quantity calculation
    '''
    @api.onchange('no_of_packings','pack_per_qty','extra_packing')
    def _compute_total_quantity(self):
        for order in self:
            quantity = 0.0
            order.update({
                    'quantity': ((order.no_of_packings * order.pack_per_qty) + order.extra_packing)
                    })
    
    
