'''
Company : EBSL
Author: Induja
Module: Material Rejected Store
Class 1: PrakrutiRejectedMaterialStore
Class 2: PrakrutiRejectedMaterialStoreLine
Table 1 & Reference Id: prakruti_material_rejected_store ,qc_check_line
Table 2 & Reference Id: prakruti_rejected_material_store_line,qc_check_line_id
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
'''


# -*- coding: utf-8 -*-
from openerp import models, fields, api,_
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

class PrakrutiRejectedMaterialStore(models.Model):
    _name =  'prakruti.material_rejected_store'
    _table = 'prakruti_material_rejected_store'
    _description = 'Material Rejected Store '
    _order="id desc"
    _rec_name= "grn_no"
    
    qc_check_line = fields.One2many('prakruti.rejected_material_store_line','qc_check_line_id')
    checked_by = fields.Many2one('res.users',string = 'Checked By')
    rejection_date = fields.Date('Rejection Date', default=fields.Date.today)
    grn_no = fields.Char(string= 'GRN/Dispatch/PTN No', readonly=1)
    po_no = fields.Char('Order No', readonly=1)
    grn_date = fields.Date('GRN/Dispatch/PTN Date', readonly=1)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=1)
    order_date = fields.Date('Order Date', readonly=1)
    store_incharge = fields.Many2one('res.users', string="Store Incharge")
    quality_incharge = fields.Many2one('res.users', string="Quality Incharge")
    coming_from = fields.Selection([('sales','Sales'),('purchase','Purchase'),('production','Production')],default= 'sales', string = "Type")
    location_id= fields.Many2one('prakruti.stock_location','Store Location')
    remarks = fields.Text(string="Remarks") 
    product_id = fields.Many2one('product.product', related='qc_check_line.product_id', string='Product Name')
    batch_id = fields.Many2one('prakruti.batch_master',string='Batch No',readonly=1)
    bmr_no = fields.Char(string = 'BMR No')   
    reference_no= fields.Char(string='Ref No')
    revision_no = fields.Char(' Rev No')
    terms=fields.Text('Terms and conditions')
    reference_date= fields.Date(string='Ref Date')
    state =fields.Selection([
        ('draft','Material Draft'),
        ('reprocess','Material Reprocessed'),
        ('destruction_note','Material Destructed'),
        ('to_scrap','Material Scrapped'),
        ('rejection_note','Material Rejection Note'),
        ('material_return','Material Return'),
        ('material_outward','Material Outward')
        ],default= 'draft', string= 'Status', readonly=1) 
    company_address = fields.Many2one('res.company',string='Company Address', readonly= "True" )   
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete record went to further process'))
        return super(PrakrutiRejectedMaterialStore, self).unlink()
    
    
    '''
    pulling data to BMR Requistion
    ''' 
    @api.one
    @api.multi
    def do_reprocess(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''  SELECT 
                                prakruti_bmr_requisition.slip_no,
                                prakruti_bmr_requisition.product_id,
                                prakruti_batch_master.batch_capacity,
                                prakruti_batch_master.batch_no,
                                prakruti_batch_master.batch_name 
                            FROM 
                                prakruti_material_rejected_store join 
                                prakruti_batch_master on 
                                prakruti_material_rejected_store.batch_id = prakruti_batch_master.id join 
                                prakruti_bmr_requisition on 
                                prakruti_batch_master.bmr_no = prakruti_bmr_requisition.bmr_no	
                            where 
                                prakruti_material_rejected_store.id = %s AND 
                                prakruti_material_rejected_store.batch_id = %s AND 
                                prakruti_material_rejected_store.bmr_no = %s''',((temp.id),(temp.batch_id.id),(temp.bmr_no),))
            for item in cr.dictfetchall():
                slip_no = item['slip_no']
                product_id = item['product_id']
                batch_capacity = item['batch_capacity']
                batch_no = item['batch_no']
                batch_name = item['batch_name']
            bmr_requisition_entry = self.pool.get('prakruti.bmr_requisition').create(cr,uid,{
                'requisition_type':'re_process',
                'slip_no':slip_no,
                'product_id':product_id,
                'batch_size':batch_capacity,
                'batch_name':batch_name,
                'batch_no':batch_no
                })
            cr.execute("UPDATE prakruti_material_rejected_store SET state = 'reprocess' WHERE prakruti_material_rejected_store.id = cast(%s as integer)",((temp.id),))
        return {}
    
    '''
    Puling data to destruction note & Scrap
    ''' 
    @api.one
    @api.multi
    def to_destruction(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if temp.coming_from == 'sales':
                to_destruct = self.pool.get('prakruti.sales_scrap').create(cr,uid, {
                    'grn_no':temp.grn_no,
                    'order_no':temp.order_no.id,
                    'checked_by':temp.checked_by.id,
                    'order_date':temp.order_date,
                    'grn_date':temp.grn_date,
                    'remarks':temp.remarks,
                    'coming_from':temp.coming_from,
                    'terms':temp.terms,
                    'company_id':temp.company_address.id,
                    'reference_date':temp.reference_date,
                    'reference_no':temp.reference_no,   
                    'revision_no':temp.revision_no
                    })
                for item in temp.qc_check_line:
                    grid_values = self.pool.get('prakruti.sales_scrap_line').create(cr,uid, {
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'description': item.description,
                        'quantity':item.quantity,
                        'remarks':item.remarks,
                        'scrap_line_id':to_destruct
                    })            
            elif temp.coming_from == 'purchase':
                to_destruct_note = self.pool.get('prakruti.sales_scrap').create(cr,uid, {
                    'grn_no':temp.grn_no,
                    'po_no':temp.po_no,
                    'checked_by':temp.checked_by.id,
                    'order_date':temp.order_date,
                    'grn_date':temp.grn_date,
                    'remarks':temp.remarks,
                    'terms':temp.terms,
                    'reference_date':temp.reference_date,
                    'reference_no':temp.reference_no,   
                    'revision_no':temp.revision_no,
                    'company_id':temp.company_address.id,
                    'coming_from':temp.coming_from
                    })
                for item in temp.qc_check_line:
                    grid_values = self.pool.get('prakruti.sales_scrap_line').create(cr,uid, {
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'description': item.description,
                        'quantity':item.quantity,
                        'remarks':item.remarks,
                        'scrap_line_id':to_destruct_note
                    })            
            elif temp.coming_from == 'production':
                to_destruction_note = self.pool.get('prakruti.destruction_note').create(cr,uid, {
                    'inward_no':temp.grn_no,
                    'po_no':temp.po_no,
                    'checked_by':temp.checked_by.id,
                    'order_date':temp.order_date,
                    'grn_date':temp.grn_date,
                    'remarks':temp.remarks,
                    'coming_from':temp.coming_from
                    })
                for item in temp.qc_check_line:
                    grid_values = self.pool.get('prakruti.destruction_note_line').create(cr,uid, {
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'description': item.description,
                        'quantity':item.quantity,
                        'remarks':item.remarks,
                        'main_id':to_destruction_note
                    })       
            cr.execute("UPDATE  prakruti_material_rejected_store SET state = 'destruction_note' WHERE prakruti_material_rejected_store.id = cast(%s as integer)",((temp.id),))
        return {}
    
class PrakrutiRejectedMaterialStoreLine(models.Model):
    _name = 'prakruti.rejected_material_store_line'
    _table = 'prakruti_rejected_material_store_line'
    _description = 'Material Rejected Store Line'
    
    qc_check_line_id = fields.Many2one('prakruti.material_rejected_store', ondelete='cascade')    
    product_id = fields.Many2one('product.product',string='Product Name')
    uom_id = fields.Many2one('product.uom',string='UOM')
    description = fields.Text(string='Description')
    quantity = fields.Float('Return Qty.',digits=(6,3))
    remarks = fields.Text(string="Remarks")