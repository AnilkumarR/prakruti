'''
Company : EBSL
Author: Induja
Module: Sales Return
Class 1: PrakrutiSalesReturn
Class 2: PrakrutiSalesReturnItems
Table 1 & Reference Id: prakruti_sales_return ,grid_id
Table 2 & Reference Id: prakruti_sales_return_items,main_id
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

class PrakrutiSalesReturn(models.Model):
    _name = 'prakruti.sales_return'
    _table = 'prakruti_sales_return'
    _description = 'Sales Return'
    _order="id desc"
    _rec_name="return_no"
    
  
    '''Auto genereation function
    'Format: SR\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: SR\EXFG\0262\17-18
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
            cr.execute('''SELECT 
                                CAST(EXTRACT (month FROM return_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM return_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_sales_return 
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
                        
                cr.execute('''SELECT autogenerate_sales_return(%s)''', ((temp.id),)  ) # Database Function : autogenerate_sales_return
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_sales_return'];
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
                        style_format[record.id] = 'SR\\'+temp.product_type_id.group_code+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    else:                        
                        style_format[record.id] = 'SR\\'+'MISC'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                    cr.execute('''UPDATE 
                                        prakruti_sales_return 
                                  SET 
                                        return_no =%s 
                                  WHERE 
                                        id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
    
    
    grid_id = fields.One2many('prakruti.sales_return_items', 'main_id',string='Grid Line')    
    return_no=fields.Char(string='Return No',default='New')
    return_date = fields.Date('Return Date', default= fields.Date.today, required=True)    
    ret_no = fields.Char('Return Number', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id1 = fields.Integer('Auto Generating id',default= 0)
    return_type =fields.Selection([
        ('from_dispatch','From Dispatch'),
        ('return_by_customer','From Invoice')
       ],default='from_dispatch', string= 'Type',readonly=True)
    dispatch_date = fields.Date('Dispatch Date')
    invoice_date = fields.Date('Invoice Date')
    order_no = fields.Many2one('prakruti.sales_order', string='Order No.')
    order_date = fields.Date('Order Date')
    dispatch_to = fields.Many2one('res.partner', string='Dispatch To')
    company_id = fields.Many2one('res.company',string="Company")
    state =fields.Selection([
        ('draft','Sales Return Draft'),
        ('validate','Sales Return Validate'),
        ('sent_to_qc','Sent To Quality Check'),
        ('sent_to_dispatch','Sent to Dispatch'),
        ('qc_done','Quality Check Done'),
        ('invoice','Sales Return Invoiced'),
        ('return','Returned'),
        ('grn','Sales Return GRN'),
        ], default="draft", string= 'Status')
    remarks = fields.Text('Remarks')
    vehicle_no=fields.Char(string="Vehicle No")
    product_type_id=fields.Many2one('product.group',string= 'Product Type')    
    dispatch_no = fields.Many2one('prakruti.dispatch',string='Dispatch No.')
    invoice_no = fields.Char(string='Invoice No.',readonly=True)    
    flag_count_accept = fields.Integer('Accepted Line is There',default= 1)
    customer_id = fields.Many2one('res.partner',string="Customer")
    dispatch_id =fields.Many2one('res.users','Dispatch By') 
    requested_id =fields.Many2one('res.users','Requested By')
    quotation_id =fields.Many2one('res.users','Quotation By')
    order_id =fields.Many2one('res.users','Order By') 
    return_id =fields.Many2one('res.users','Return By')
    reference_no= fields.Char(string='Ref No')
    reference_date= fields.Date(string='Ref Date', default=fields.Date.today) 
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name') 
    remarks = fields.Text(string="Remarks")
    terms=fields.Text('Terms and conditions')
    revision_no = fields.Char(' Rev No')
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Sorry....You Can\'t Delete'))
        return super(PrakrutiSalesReturn, self).unlink()
    
    
    '''
    While selecting dispatch no it will extract data from Dispatch Screen 
    '''
    def onchange_dispatch_no(self, cr, uid, ids, dispatch_no, context=None):
        process_type = self.pool.get('prakruti.dispatch').browse(cr, uid, dispatch_no, context=context)
        result = {
            'dispatch_date': process_type.dispatch_date,
            'order_no': process_type.order_no.id,
            'order_date': process_type.order_date,
            'company_id': process_type.company_id.id,
            'dispatch_to':process_type.dispatch_to.id,
            'dispatch_id': process_type.dispatch_id.id,
            'requested_id': process_type.requested_id.id,
            'order_id': process_type.order_id.id,
            'quotation_id': process_type.quotation_id.id,
            'product_type_id':process_type.product_type_id.id,
            'reference_no':process_type.reference_no,
            'reference_date':process_type.reference_date,
            'terms':process_type.terms,
            'remarks':process_type.remarks,  
            'revision_no':process_type.revision_no
                }
        return {'value': result}  
    
    
    @api.onchange('return_type')
    def onchange_return_type(self):
        if self.return_type == 'from_dispatch':
            self.invoice_no = False
            self.invoice_date = False
            self.dispatch_no = False
            self.dispatch_date = False
            self.order_no = False
            self.order_date = False
            self.dispatch_to = False
            self.company_id = False
            
        else:
            self.invoice_no = False
            self.invoice_date = False
            self.dispatch_no = False
            self.dispatch_date = False
            self.order_no = False
            self.order_date = False
            self.dispatch_to = False
            self.company_id = False
    
    '''
    This button helps to list out the data from dispatch screen
    '''
    @api.one
    @api.multi
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            if temp.return_type == 'from_dispatch':
                cr.execute('''SELECT product_id,uom_id,specification_id,scheduled_qty,scheduled_date,material_type,unit_price,description,ordered_qty,dispatched_qty,status,accepted_qty,rejected_qty FROM prakruti_dispatch INNER JOIN prakruti_dispatch_line ON prakruti_dispatch.id=prakruti_dispatch_line.main_id 
                    WHERE prakruti_dispatch_line.main_id = CAST(%s as integer) and (status = 'rejected' or status = 'par_reject') ''',((temp.dispatch_no.id),))
                for item in cr.dictfetchall():
                    product_id=item['product_id']
                    uom_id=item['uom_id']
                    specification_id=item['specification_id']
                    material_type=item['material_type']
                    description =item['description']
                    ordered_qty=item['ordered_qty']
                    scheduled_qty=item['scheduled_qty']
                    scheduled_date=item['scheduled_date']
                    dispatched_qty=item['dispatched_qty']
                    unit_price=item['unit_price']
                    rejected_qty=item['rejected_qty']
                    status =item['status']
                    accepted_qty=item['accepted_qty']
                    erp_id = self.pool.get('prakruti.sales_return_items').create(cr,uid, {
                        'product_id':product_id,
                        'uom_id':uom_id,
                        'specification_id':specification_id,
                        'material_type':material_type,
                        'description':description,
                        'ordered_qty':ordered_qty,
                        'scheduled_date':scheduled_date,
                        'scheduled_qty':scheduled_qty,
                        'dispatched_qty':dispatched_qty,
                        'unit_price':unit_price,
                        'rejected_qty':rejected_qty,
                        'main_id':temp.id,
                        'status':status,
                        'accepted_qty':accepted_qty
                            })
                cr.execute("UPDATE  prakruti_sales_return SET flag_count_accept =2 WHERE prakruti_sales_return.id = cast(%s as integer)",((temp.id),))
            elif temp.return_type == 'return_by_customer':
                cr.execute('''SELECT product_id,uom_id,specification_id,description,quantity FROM prakruti_sales_invoice INNER JOIN prakruti_sales_invoice_line ON prakruti_sales_invoice.id=prakruti_sales_invoice_line.main_id WHERE prakruti_sales_invoice_line.main_id = CAST(%s as integer)''',((temp.invoice_no.id),))
                for item in cr.dictfetchall():
                    product_id=item['product_id']
                    uom_id=item['uom_id']
                    specification_id=item['specification_id']
                    description =item['description']
                    quantity=item['quantity']
                    ordered_qty=item['quantity']
                    erp_id = self.pool.get('prakruti.sales_return_items').create(cr,uid, {
                        'product_id':product_id,
                        'uom_id':uom_id,
                        'specification_id':specification_id,
                        'description':description,
                        'rejected_qty':quantity,
                        'ordered_qty':quantity,
                        'main_id':temp.id
                            })
                cr.execute("UPDATE  prakruti_sales_return SET flag_count_accept =2 WHERE prakruti_sales_return.id = cast(%s as integer)",((temp.id),))
            return {}
   
    '''
    This button helps to delete the data in prakruti_sales_return_items
    '''
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''DELETE FROM prakruti_sales_return_items WHERE prakruti_sales_return_items.main_id = (%s)''', ((temp.id),))
            cr.execute("UPDATE  prakruti_sales_return SET flag_count_accept =1 WHERE prakruti_sales_return.id = cast(%s as integer)",((temp.id),))
        return {}
    
    
    '''
    Pulls the data to Sales GRN screen
    '''
    @api.one
    @api.multi 
    def return_to_grn(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            ebsl_id = self.pool.get('prakruti.sales_return_grn').create(cr,uid, {
                'order_no':temp.order_no.id,
                'order_date':temp.order_date,
                'customer_id':temp.dispatch_to.id,
                'company_id':temp.company_id.id,
                'product_type_id':temp.product_type_id.id,
                'dispatch_id':temp.dispatch_id.id,
                'order_id':temp.order_id.id,
                'quotation_id':temp.quotation_id.id,
                'requested_id':temp.requested_id.id,
                'return_type':temp.return_type,
                'state':'grn',  
                'terms':temp.terms,
                'reference_date':temp.reference_date,
                'reference_no':temp.reference_no,   
                'revision_no':temp.revision_no,
                'remarks':temp.remarks
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.sales_return_grn_line').create(cr,uid, {
                    'product_id':item.product_id.id,
                    'uom_id':item.uom_id.id,
                    'specification_id':item.specification_id.id,
                    'material_type':item.material_type,
                    'description':item.description,
                    'quantity':item.rejected_qty,
                    'rejected_qty':item.rejected_qty,
                    'status':item.status,
                    'grn_line_id': ebsl_id
                    })
            cr.execute("UPDATE prakruti_sales_return SET state = 'grn' WHERE prakruti_sales_return.id = cast(%s as integer)",((temp.id),))
        return {}
  
class PrakrutiSalesReturnItems(models.Model):
    _name = 'prakruti.sales_return_items'
    _table = 'prakruti_sales_return_items'
    _description = 'Sales Return Items'
    
    main_id = fields.Many2one('prakruti.sales_return',string="Grid ID")
    product_id  = fields.Many2one('product.product', string="Product Name",required= True)
    uom_id = fields.Many2one('product.uom',string="UOM")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    material_type= fields.Selection([('extraction','Extraction'),('formulation','Formulation')], string= 'Material Type', default= 'extraction')
    description = fields.Text(string="Description")
    ordered_qty = fields.Float('Ordered Qty',digits=(6,3))
    unit_price=fields.Float(string="Unit Price",digits=(6,3))
    scheduled_date = fields.Date('Scheduled Date')
    scheduled_qty = fields.Float('Scheduled Qty',digits=(6,3))
    dispatched_qty = fields.Float('Dispatched Qty',digits=(6,3))
    remarks = fields.Text(string="Remarks")
    return_type =fields.Selection([
        ('from_dispatch','FROM DISPATCH'),
        ('return_by_customer','Return By Customer')
       ],default='from_dispatch', string= 'Type')
    state =fields.Selection([
        ('draft','Draft'),
        ('sent_to_qc','Sent To Quality Check'),
        ('sent_to_dispatch','Sent to Dispatch'),
        ('qc_done','QC Done'),
        ('invoice','Invoiced'),
        ('return','returned')
        ], string= 'States',default='draft', invisible= True)
    status = fields.Selection([
		('accepted', 'Accepted'),
		('par_reject', 'Par. Rejected'),
		('rejected','Rejected')
		], string= 'Status',default='rejected')
    accepted_qty = fields.Float(string= 'Accept. Qty.', readonly= True,digits=(6,3))
    rejected_qty = fields.Float(string= 'Reject/Returned Qty.', readonly= True,digits=(6,3))
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')