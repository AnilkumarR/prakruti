'''
Company : EBSL
Author: Induja
Module: Credit Note
Class 1: PrakrutiCreditNote
Class 2: CreditNoteLine
Table 1 & Reference Id: prakruti_credit_note ,order_line
Table 2 & Reference Id: prakruti_credit_note_line,line_id
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
from openerp.tools import email_re, email_split



class PrakrutiCreditNote(models.Model):
    _name='prakruti.credit.note'
    _table='prakruti_credit_note'
    _order='id desc'
    _rec_name='credit_note_no' 
    
    
  
    '''Auto genereation function
    'Format: CN\AUTO GENERATE NO\FINANCIAL YEARres
    Example: CN\0455\17-18
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
                                CAST(EXTRACT (month FROM credit_date) AS integer) AS month ,
                                CAST(EXTRACT (year FROM credit_date) AS integer) AS year ,
                                id 
                         FROM 
                                prakruti_credit_note 
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
                        
                cr.execute('''SELECT autogenerate_credit_note(%s)''', ((temp.id),)  ) 
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_credit_note'];
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
                    style_format[record.id] = 'CN\\'+str(auto_gen) +'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE 
                                    prakruti_credit_note 
                              SET 
                                    credit_note_no =%s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format   
    
    order_line = fields.One2many('prakruti.credit.note.line','line_id',string='Order Line')
    credit_note_no = fields.Char(string= 'Credit Note No.',readonly=1)
    credit_date = fields.Date(string= 'Date', default=fields.Date.today)
    sales_return_id = fields.Many2one('prakruti.sales_return',string = 'Select Return')
    customer_id = fields.Many2one('res.partner',string = 'Customer Name')
    dispatch_to = fields.Many2one('res.partner', string='Dispatch To')
    notes = fields.Text(string= 'Notes')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal',store=True,digits=(6,3))
    cdt_no = fields.Char(compute= '_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0) 
    flag_count_accept = fields.Integer('Accepted Line is There',default= 1)
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            raise UserError(_('Sorry....You Can\'t Delete'))
        return super(PrakrutiCreditNote, self).unlink() 
    '''
    While selecting Return no it will extract data from Sales return Screen 
    '''
    
    def onchange_sales_return_id(self, cr, uid, ids, sales_return_id, context=None):
        process_type = self.pool.get('prakruti.sales_return').browse(cr, uid, sales_return_id, context=context)
        result = {
            'customer_id': process_type.dispatch_to,
            'dispatch_to':process_type.dispatch_to
            
                }
        return {'value': result}
       
    
    '''
   Listing products from Sales Return
    '''
    @api.one
    @api.multi
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''SELECT product_id,uom_id,material_type,rejected_qty,unit_price FROM prakruti_sales_return INNER JOIN prakruti_sales_return_items ON prakruti_sales_return.id=prakruti_sales_return_items.main_id WHERE prakruti_sales_return_items.main_id =CAST(%s as integer)''',((temp.sales_return_id.id),))
            for item in cr.dictfetchall():
                product_id=item['product_id']
                uom_id=item['uom_id']
                rejected_qty=item['rejected_qty']
                unit_price =item['unit_price'] 
                grid_down = self.pool.get('prakruti.credit.note.line').create(cr,uid, {
                    'product_id':product_id,
                    'uom_id':uom_id,
                    'rejected_qty':rejected_qty,
                    'unit_price':unit_price,
                    'line_id':temp.id,
                            
                        })
                cr.execute("UPDATE  prakruti_credit_note SET flag_count_accept =2 WHERE prakruti_credit_note.id = cast(%s as integer)",((temp.id),))
                
            return {}
    '''
    Deleting from Sales Return
    '''
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''DELETE FROM prakruti_credit_note_line WHERE prakruti_credit_note_line.line_id = (%s)''', ((temp.id),))
            cr.execute("UPDATE  prakruti_credit_note SET flag_count_accept =1 WHERE prakruti_credit_note.id = cast(%s as integer)",
                                   ((temp.id),))
        return {}
    '''
    Calculation for Sub total
    '''
    @api.depends('order_line.rejected_qty','order_line.unit_price')
    def _compute_subtotal(self):
        for order in self:
            subtotal  = total_amount=0.0
            for line in order.order_line:
                total_amount += line.rejected_qty * line.unit_price
                order.update({
                    'subtotal': total_amount
                    })
    
    '''
    Sending mail
    '''
    def send_mail_quotation(self, cr, uid, ids, context=None):
        for temp in self.browse(cr, uid, ids, context={}):
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Credit Note')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            print 'template_idtemplate_idtemplate_id',template_id
        return True
    
class CreditNoteLine(models.Model):
    _name = 'prakruti.credit.note.line'
    _table = "prakruti_credit_note_line"
    
    line_id = fields.Many2one('prakruti.credit.note')    
    product_id = fields.Many2one('product.product',string= 'Product Name')
    uom_id = fields.Many2one('product.uom',string= 'Units')
    rejected_qty = fields.Float(string= 'Qty.',digits=(6,3))
    unit_price = fields.Float(string= 'Amount',digits=(6,3))
    total = fields.Float(string= 'Total',compute='_compute_price_total',store=True,digits=(6,3))
    
    '''
    Calculation for total
    '''
    @api.depends('rejected_qty', 'unit_price')
    def _compute_price_total(self):
        for order in self:
            total = 0.0            
            order.update({                
                'total': order.rejected_qty * order.unit_price 
            })