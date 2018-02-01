'''
Company : EBSL
Author : Karan
Module : Batch Wise Alloaction
Class 1 : batch_wise_allocation
Class 2 : PurchaseRequisitionLine
Table 1 & Reference Id : batch_wise_allocation,main_id
Table 2 & Reference Id : batch_wise_allocation_line,batch_allocation_line_id
Updated By : Karan 
Updated Date & Version : 2017/08/29 & 0.1
'''


# -*- coding: utf-8 -*-
from openerp.tools import image_resize_image_big
from openerp.exceptions import ValidationError
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

class batch_wise_allocation(models.TransientModel):
    _name = 'batch.wise_allocation'
    _table = 'batch_wise_allocation'
    _description = 'Batch Wise Allocation'
    
    main_id=  fields.One2many('batch.wise_allocation_line','batch_allocation_line_id',string= 'Allocation Line ID')       
    product_id= fields.Many2one('product.product', string="Product",readonly=1)
    uom_id = fields.Many2one('product.uom',string="UOM",readonly=1)
    store_qty= fields.Float(string= 'Store Qty',readonly=1)
    dispatched_qty= fields.Float(string= 'Dispatch Qty',readonly=1)
    dispatch_line_id = fields.Integer(string= 'Dispatch Line ID')
    
    '''
    Approve the batch for particular product
    '''
    @api.one
    @api.multi
    def action_approve(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        total_line = 0        
        packing_enter_line = 0
        for temp in self:
            cr.execute(''' select count(id) as total_line from batch_wise_allocation_line where batch_allocation_line_id = %s''',((temp.id),))
            for line in cr.dictfetchall():
                total_line = line['total_line']
            cr.execute(''' select count(id) as packing_enter_line from batch_wise_allocation_line where batch_allocation_line_id = %s and length(packing_details) > 0''',((temp.id),))
            for line in cr.dictfetchall():
                packing_enter_line = line['packing_enter_line']
            if packing_enter_line == total_line:
                for item in temp.main_id:
                    if item.dispatch_qty > item.available_qty:
                        raise UserError(_('Your Dispatch Qty is %s for the Batch [ %s ] and the Stock Availability is %s') %(item.dispatch_qty,item.batch_id.batch_no,item.available_qty))
                cr.execute('''  UPDATE 
                                    prakruti_dispatch_line 
                                SET
                                    batch_list = b.batch_list,
                                    batch_wise_dispatch = b.batch_wise_dispatch,
                                    packing_details = b.packing_details,
                                    dispatched_qty = b.dispatched_qty
                                FROM(
                                    SELECT
                                        array_to_string(array_agg(batch_wise_allocation_line.batch_name),',') AS batch_list,
                                        array_to_string(array_agg(batch_wise_allocation_line.packing_details),',') AS packing_details,
                                        sum(coalesce(batch_wise_allocation_line.dispatch_qty,0)) AS dispatched_qty,
                                        array_to_string(array_agg(batch_wise_allocation_line.batch_name),',') || '|' ||
                                        array_to_string(array_agg(batch_wise_allocation_line.batch_size),',') || '|' ||
                                        array_to_string(array_agg(batch_wise_allocation_line.batch_qty),',') || '|' ||
                                        array_to_string(array_agg(batch_wise_allocation_line.dispatch_qty),',') || '|' ||
                                        array_to_string(array_agg(batch_wise_allocation_line.packing_details),',') AS batch_wise_dispatch,
                                        batch_wise_allocation.product_id,
                                        batch_wise_allocation.uom_id,
                                        batch_wise_allocation.dispatch_line_id
                                    FROM
                                        batch_wise_allocation_line JOIN
                                        batch_wise_allocation ON
                                        batch_wise_allocation_line.batch_allocation_line_id = batch_wise_allocation.id
                                    WHERE
                                        batch_wise_allocation_line.batch_allocation_line_id =%s
                                    GROUP BY
                                        batch_wise_allocation.product_id,
                                        batch_wise_allocation.uom_id,
                                        batch_wise_allocation.dispatch_line_id
                                    ) AS b
                                WHERE
                                    b.product_id = prakruti_dispatch_line.product_id AND
                                    b.dispatch_line_id = prakruti_dispatch_line.id
                            ''',((temp.id),))
                
                cr.execute('''  INSERT INTO prakruti_dispatch_batch_list_line(product_id,uom_id,dispatched_qty,batch_no,batch_size,batch_qty,packing_details,dispatch_id,send_to_invoice_flag)
                                SELECT 
                                    batch_wise_allocation.product_id,
                                    batch_wise_allocation.uom_id,
                                    batch_wise_allocation_line.dispatch_qty,
                                    batch_wise_allocation_line.batch_id,
                                    batch_wise_allocation_line.batch_size,
                                    batch_wise_allocation_line.batch_qty,
                                    batch_wise_allocation_line.packing_details,
                                    prakruti_dispatch_line.main_id,
                                    0 AS send_to_invoice_flag
                                FROM
                                    batch_wise_allocation JOIN
                                    batch_wise_allocation_line ON
                                    batch_wise_allocation.id = batch_wise_allocation_line.batch_allocation_line_id JOIN
                                    prakruti_dispatch_line ON
                                    prakruti_dispatch_line.id = batch_wise_allocation.dispatch_line_id
                                WHERE 
                                    batch_wise_allocation.id = %s ''',((temp.id),))
                
            else:
                raise UserError(_('Oops Somewere You Missed Out Packing Details...'))
        return {}


class batch_wise_allocation_line(models.TransientModel):
    _name = 'batch.wise_allocation_line'
    _table = 'batch_wise_allocation_line'
    _description = 'Batch Wise Allocation Line'
    
    batch_allocation_line_id= fields.Many2one('batch.wise_allocation', string="Batch Allocation ID")
    batch_id= fields.Many2one('prakruti.batch_master',string= 'Batch No',required=1)
    batch_name=fields.Char('Batch Name')
    batch_size= fields.Float('Batch Size')
    batch_qty=fields.Float('Batch Qty')
    available_qty=fields.Float('Available Qty')
    dispatch_qty= fields.Float('Dispatch Qty')
    packing_details= fields.Char('Packing Details')
    '''
    Its a ORM Insert Method, Its is used because whenever we run the on_change_batch the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''
    def create(self, cr, uid, vals, context=None):
        batch_values = self.on_change_batch(cr, uid, [], vals['batch_id'])
        if batch_values.get('value') or batch_values['value'].get('batch_size','batch_qty','available_qty'):
            vals['batch_size'] = batch_values['value']['batch_size']
            vals['batch_qty'] = batch_values['value']['batch_qty']
            vals['available_qty'] = batch_values['value']['available_qty']
        return super(batch_wise_allocation_line, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(batch_wise_allocation_line, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.batch_id.id
        batch_values = self.on_change_batch(cr, uid, ids, store_type)
        if batch_values.get('value') or batch_values['value'].get('batch_size','batch_qty','available_qty'):
            vals['batch_size'] = batch_values['value']['batch_size']
            vals['batch_qty'] = batch_values['value']['batch_qty']
            vals['available_qty'] = batch_values['value']['available_qty']
        return super(batch_wise_allocation_line, self).write(cr, uid, ids, vals, context=context)
    '''
    While changing the batch no it will load by defaults whatever values are required for that particular Batch no such as Batch Qty, Batch Size,Batch name, Available Qty,etc.
    '''
    def on_change_batch(self, cr, uid, ids, batch_id, context=None):
        cr.execute('''  select
                            case
                                when
                                    prakruti_batch_master.batch_allocated_by = 'extraction' then prakruti_production.total_output_yeild
                                when
                                    prakruti_batch_master.batch_allocated_by = 'tablet' then prakruti_tablet_production.total_output_yeild
                                when
                                    prakruti_batch_master.batch_allocated_by = 'syrup' then prakruti_syrup_production.total_output_yeild
                                when
                                    prakruti_batch_master.batch_allocated_by = 'formulation' then prakruti_powder_production.total_output_yeild
                                end as 
                            batch_qty,
                            case
                                when
                                    prakruti_batch_master.batch_allocated_by = 'extraction' then prakruti_production.available_qty
                                when
                                    prakruti_batch_master.batch_allocated_by = 'tablet' then prakruti_tablet_production.available_qty
                                when
                                    prakruti_batch_master.batch_allocated_by = 'syrup' then prakruti_syrup_production.available_qty
                                when
                                    prakruti_batch_master.batch_allocated_by = 'formulation' then prakruti_powder_production.available_qty
                                end as 
                            available_qty,
                            prakruti_batch_master.batch_capacity as batch_size,
                            prakruti_batch_master.batch_no as batch_name
                        from
                            prakruti_batch_master left join
                            prakruti_production on
                            prakruti_batch_master.id = prakruti_production.batch_id left join
                            prakruti_syrup_production on
                            prakruti_batch_master.id = prakruti_syrup_production.batch_id left join
                            prakruti_tablet_production on
                            prakruti_batch_master.id = prakruti_tablet_production.batch_id left join
                            prakruti_powder_production on
                            prakruti_batch_master.id = prakruti_powder_production.batch_id
                        where
                            prakruti_batch_master.id =  cast(%s AS INTEGER)''', ((batch_id),))
        for machine in cr.dictfetchall():
            batch_qty = machine['batch_qty']
            batch_size = machine['batch_size']
            batch_name = machine['batch_name']
            available_qty = machine['available_qty']
            result = {
                'batch_qty': batch_qty,
                'batch_size': batch_size,
                'batch_name': batch_name,
                'available_qty': available_qty
                }
            return {'value': result}