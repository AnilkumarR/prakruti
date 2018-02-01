'''
Company : EBSL
Author: Induja
Module: Bill of Material
Class 1: PrakrutiBillOfMaterial
Class 2: PrakrutiBillOfMaterialLine
Table 1 & Reference id: prakruti_bill_of_material,grid_id 
Table 2 & Reference id : prakruti_bill_of_material_line ,main_id
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
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


#########################################################################################################


class PrakrutiBillOfMaterial(models.Model):
    _name = 'prakruti.bill_of_material'
    _table = 'prakruti_bill_of_material'
    _order = 'id desc'
    _description = 'Bill of Material '
    _rec_name = 'subplant_id'
    
    grid_id = fields.One2many('prakruti.bill_of_material_line','main_id')
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant",required=True)
    batch_id= fields.Many2one('prakruti.batch_master',string= 'Batch No', required=True)
    actual_batch_size =fields.Float(string='Actual Batch Size', required=True)
    date= fields.Date(string = 'Date',default=fields.Date.today, required=True)
    assay_per = fields.Float(string='% Assay',digits=(6,3))
    label_claim= fields.Char(string='Label Claim')
    material_issued_by = fields.Many2one('res.users',string='Material Issued By')
    material_checked_by = fields.Many2one('res.users',string='Material Checked By')
    material_recieved_by = fields.Many2one('res.users',string='Material Recieved By')
    material_requested_by = fields.Many2one('res.users',string='Material Requested By')
    mrn_no = fields.Char(string = 'MRN No.')
    mrn_date_time = fields.Datetime('MRN Date & Time', default=fields.Date.today)
    state = fields.Selection([
                ('draft','Bill of Material Draft'),
                ('sent_stores','Requested To Stores'),
                ('issued_quant','BOM Quantity Issued'),
                ('extra_issue','Extra Quantity Required'),
                ('extra_issued','Extra Quantity Issued')], string= 'Status',default='draft')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env.user.company_id,required="True")    
    std_batch_size_id = fields.Many2one('prakruti.standard_product',string='Std Batch Size')
    flag_display_product = fields.Integer(default=0)    
    flag_delete_product = fields.Integer(default=0)    
    readonly_flag = fields.Integer(default=0,string="Read Only Field")
    is_duplicate = fields.Boolean(string= 'Is a Duplicate',default=False,readonly=True)
    duplicate_flag = fields.Char(string= 'Duplicate Flag',default=0,readonly=True)    
    existing_batch_no = fields.Integer(string= 'Existing Batch No.',default=0,readonly=True)                
    dept_id = fields.Many2one('res.company','Department',required = 1)    
    grn_line = fields.One2many('prakruti.extraction_bom_grn_list_line', 'extraction_id',string='GRN line')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')   
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'material_requested_by': lambda s, cr, uid, c:uid,
        'material_recieved_by': lambda s, cr, uid, c:uid,
        'material_checked_by': lambda s, cr, uid, c:uid
        }
    
    '''
    Can't delete this record
    '''
    @api.multi
    def unlink(self):
        for v in self:
            if v.state != 'draft':
                raise UserError(_('Can\'t Delete'))
        return super(PrakrutiBillOfMaterial, self).unlink()

    '''
   If any batch_id, std_batch_size is there for particular subplant then this will automatically dispalys for that particular sub plant
    '''   
    def onchange_subplant_id(self, cr, uid, ids, subplant_id, context=None):
        batch_id = 0
        std_batch_size = 0
        cr.execute('SELECT prakruti_batch_master.subplant_id,prakruti_batch_master.batch_name,prakruti_batch_master.id as batch_id,prakruti_batch_master.batch_capacity as std_batch_size FROM prakruti_batch_master WHERE prakruti_batch_master.subplant_id=cast(%s as integer)', ((subplant_id),))
        for line in cr.dictfetchall():
            batch_id = line['batch_id']
            std_batch_size = line['std_batch_size']
        return {'value' :{
                'batch_id':batch_id,
                'std_batch_size':std_batch_size,
                          }}
    '''
    If any batch_id, std_batch_size is there for particular subplant then this will automatically dispalys for that particular sub plant
    '''    
    
    def onchange_batch_id(self, cr, uid, ids, batch_id, context=None):
        process_type = self.pool.get('prakruti.batch_master').browse(cr, uid, batch_id, context=context)
        result = {
            'std_batch_size': process_type.batch_capacity
            }
        return {'value': result}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_order_no the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''    
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_subplant_id(cr, uid, [], vals['subplant_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('std_batch_size'):
            vals['std_batch_size'] = onchangeResult['value']['std_batch_size']
        return super(PrakrutiBillOfMaterial, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiBillOfMaterial, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.subplant_id.id
        onchangeResult = self.onchange_subplant_id(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('std_batch_size'):
            vals['std_batch_size'] = onchangeResult['value']['std_batch_size']
        return super(PrakrutiBillOfMaterial, self).write(cr, uid, ids, vals, context=context)
    '''
    Avoiding to do duplicate from the existing type
    '''
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Forbbiden to duplicate'), _('Is not possible to duplicate from here...'))
    
    
    '''
    listing the products from standard product
    '''
    @api.one
    @api.multi 
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("SELECT product_id,description,uom_id,prakruti_standard_product_line.standard_value as std_value FROM prakruti_standard_product_line INNER JOIN prakruti_standard_product ON prakruti_standard_product_line.standard_line_id = prakruti_standard_product.id INNER JOIN prakruti_bill_of_material ON prakruti_standard_product.subplant_id = prakruti_bill_of_material.subplant_id AND prakruti_standard_product.id = prakruti_bill_of_material.std_batch_size_id WHERE prakruti_bill_of_material.id = %s",((temp.id),))
            for line in cr.dictfetchall():
                product_id = line['product_id']
                description = line['description']
                uom_id = line['uom_id']
                std_qty = line['std_value']
                actual_qty = line['std_value']
                grid_line_entry = self.pool.get('prakruti.bill_of_material_line').create(cr,uid,{
                    'material_id':product_id,
                    'description':description,
                    'uom_id':uom_id,
                    'std_qty':std_qty,
                    'actual_qty':actual_qty,
                    'main_id':temp.id
                    })
            cr.execute('UPDATE prakruti_bill_of_material SET flag_display_product = 1 WHERE prakruti_bill_of_material.id = %s',((temp.id),))
            cr.execute("UPDATE  prakruti_bill_of_material SET flag_delete_product = 0 WHERE prakruti_bill_of_material.id = %s",((temp.id),))
        return {}    
            
            
    '''
   deleting the products
    '''        
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_bill_of_material_line WHERE prakruti_bill_of_material_line.main_id = %s", ((temp.id),))
            cr.execute("UPDATE  prakruti_bill_of_material SET flag_delete_product = 1 WHERE prakruti_bill_of_material.id = %s",((temp.id),))
            cr.execute('UPDATE prakruti_bill_of_material SET flag_display_product = 0 WHERE prakruti_bill_of_material.id = %s',((temp.id),))
        return {}
    
    
    '''
    validation for -ve values
    '''
    
    def _check_std_batch_size(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.std_batch_size <= 0:
                return False
            return True
  
    def _check_actual_batch_size(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.actual_batch_size <= 0:
                return False
            return True
        
    _constraints = [
        
        (_check_std_batch_size,'Batch Size cannot be negative or zero!',['std_batch_size']),
        (_check_actual_batch_size,'Batch Size cannot be negative or zero!',['actual_batch_size'])
        ]
    '''
    pulls the data to store request
    '''
    @api.one
    @api.multi 
    def request_to_stores(self):
        actual_count = 0
        no_of_line = 0
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            if temp.existing_batch_no != temp.batch_id.id:
                print 'BATCH ID',temp.batch_id.id
                print 'COPIED BATCH NUMBER',temp.existing_batch_no
                cr.execute("SELECT count(id) as no_of_line,count(actual_qty) as actual_count  FROM prakruti_bill_of_material_line WHERE main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    actual_count = line['actual_count']
                    no_of_line = line['no_of_line']
                if actual_count == no_of_line:
                    #Store Request Entry
                    request_id =  self.pool.get('prakruti.store_request').create(cr,uid, {
                        'date':temp.date,
                        'extraction_bom_id':temp.id,
                        'syrup_bom_id':0,
                        'tablet_bom_id':0,
                        'powder_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'store_request_no':'From Production',
                        'batch_no':temp.batch_id.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Extraction BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    for item in temp.grid_id:
                        request_line_id = self.pool.get('prakruti.store_request_item').create(cr,uid, {
                            'product_id':item.material_id.id,
                            'description':item.description,
                            'extra_readonly_flag':1,
                            'uom_id':item.uom_id.id,
                            'requested_quantity':item.actual_qty,
                            'grid_common_id':item.id,
                            'grn_no': item.grn_no.id,
                            'ar_no': item.ar_no.id,
                            'main_id':request_id
                            })
                    #Store Approve Entry
                    approve_id =  self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                        'date':temp.date,
                        'extraction_bom_id':temp.id,
                        'syrup_bom_id':0,
                        'tablet_bom_id':0,
                        'powder_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_id.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Extraction BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    for item in temp.grid_id:
                        approve_line_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                            'product_id':item.material_id.id,
                            'description':item.description,
                            'extra_readonly_flag':1,
                            'uom_id':item.uom_id.id,
                            'requested_quantity':item.actual_qty,
                            'approved_quantity':item.actual_qty,
                            'grid_common_id':item.id,
                            'grn_no': item.grn_no.id,
                            'ar_no': item.ar_no.id,
                            'main_id':approve_id
                            })
                    #Store Issue Entry
                    issue_id =  self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'date':temp.date,
                        'extraction_bom_id':temp.id,
                        'syrup_bom_id':0,
                        'tablet_bom_id':0,
                        'powder_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_id.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Extraction BOM',
                        'subplant_id':temp.subplant_id.id
                        })
                    for item in temp.grid_id:
                        issue_line_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                            'product_id':item.material_id.id,
                            'description':item.description,
                            'extra_readonly_flag':1,
                            'uom_id':item.uom_id.id,
                            'requested_quantity':item.actual_qty,
                            'approved_quantity':item.actual_qty,
                            'grid_common_id_bom':item.id,
                            'grn_no': item.grn_no.id,
                            'ar_no': item.ar_no.id,
                            'main_id':issue_id
                            })                                    
                    cr.execute("update prakruti_bill_of_material set state ='sent_stores' where id=%s",((temp.id),))
                    cr.execute("update prakruti_bill_of_material set readonly_flag = 1 where id=%s",((temp.id),))
                    cr.execute("update prakruti_bill_of_material_line set readonly_grid = 1 where main_id=%s",((temp.id),))
                else:
                    raise UserError(_('Oops...! Please Enter Actual Qty'))
            else:
                raise UserError(_('Oops...! Please Select different Batch Number'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales BOM')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    '''
    pulls the extra isue data to store request
    '''
    @api.one
    @api.multi 
    def request_to_stores_for_extra_issue(self):
        material_id = 0
        description = ''
        uom_id = 0
        requested_quantity = 0
        bom_line_id = 0
        grn_no = 0
        ar_no = 0
        extra_count = 0
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            if temp.existing_batch_no != temp.batch_id.id:
                print 'BATCH ID',temp.batch_id.id
                print 'COPIED BATCH NUMBER',temp.existing_batch_no
                cr.execute("SELECT extra_qty as extra_count FROM prakruti_bill_of_material_line WHERE extra_qty > 0 AND main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    extra_count = line['extra_count']
                if extra_count > 1:
                    #Store Request Entry
                    request_id =  self.pool.get('prakruti.store_request').create(cr,uid, {
                        'date':temp.date,
                        'extraction_bom_id':temp.id,
                        'syrup_bom_id':0,
                        'tablet_bom_id':0,
                        'powder_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'store_request_no':'From Production',
                        'batch_no':temp.batch_id.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Extraction BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Approve Entry
                    approve_id =  self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                        'date':temp.date,
                        'extraction_bom_id':temp.id,
                        'syrup_bom_id':0,
                        'tablet_bom_id':0,
                        'powder_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_id.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Extraction BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Issue Entry
                    issue_id =  self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'date':temp.date,
                        'extraction_bom_id':temp.id,
                        'syrup_bom_id':0,
                        'tablet_bom_id':0,
                        'powder_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_id.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Extraction BOM',
                        'subplant_id':temp.subplant_id.id
                        })
                    cr.execute("SELECT material_id,description,uom_id,extra_qty,prakruti_bill_of_material_line.id,grn_no,ar_no FROM prakruti_bill_of_material_line WHERE extra_qty > 0 AND main_id = %s",((temp.id),))
                    for item in cr.dictfetchall():
                        material_id = item['material_id']
                        description = item['description']
                        uom_id = item['uom_id']
                        requested_quantity = item['extra_qty']
                        bom_line_id = item['id']
                        grn_no = item['grn_no']
                        ar_no = item['ar_no']
                        request_line_id = self.pool.get('prakruti.store_request_item').create(cr,uid, {
                            'style_flag':1,
                            'packing_flag':1,
                            'product_id':material_id,
                            'description':description,
                            'uom_id':uom_id,
                            'requested_quantity':requested_quantity,
                            'grid_common_id':bom_line_id,
                            'main_id':request_id
                            })
                        approve_line_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                            'style_flag':1,
                            'packing_flag':1,
                            'product_id':material_id,
                            'description':description,
                            'uom_id':uom_id,
                            'requested_quantity':requested_quantity,
                            'grid_common_id':bom_line_id,
                            'main_id':approve_id
                            })
                        issue_line_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                            'style_flag':1,
                            'packing_flag':1,
                            'product_id':material_id,
                            'description':description,
                            'uom_id':uom_id,
                            'requested_quantity':requested_quantity,
                            'approved_quantity':requested_quantity,
                            'grid_common_id_bom':bom_line_id,
                            'main_id':issue_id
                            })
                else:
                    raise UserError(_('Please enter Extra Material Required'))
            else:
                raise UserError(_('Oops...! Please Select different Batch Number'))
            cr.execute("update prakruti_bill_of_material set state ='extra_issue' where id=%s",((temp.id),))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales BOM Extra')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    
    '''
    duplicate bill of material
    '''
    @api.one
    @api.multi
    def duplicate_bom(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            ebsl_id = self.pool.get('prakruti.bill_of_material').create(cr,uid, {
                'date':temp.date,
                'subplant_id':temp.subplant_id.id,
                'batch_id':temp.batch_id.id,
                'std_batch_size_id':temp.std_batch_size_id.id,
                'actual_batch_size':temp.actual_batch_size,
                'assay_per':temp.assay_per,
                'label_claim':temp.label_claim,
                'material_issued_by':temp.material_issued_by.id,
                'material_checked_by':temp.material_checked_by.id,
                'material_recieved_by':temp.material_recieved_by.id,
                'material_requested_by':temp.material_requested_by.id,
                'dept_id':temp.dept_id.id,
                'mrn_no':temp.mrn_no,
                'state':'draft',
                'mrn_date_time':temp.mrn_date_time,
                'is_duplicate':'True',
                'readonly_flag':0,
                'duplicate_flag': 1,
                'existing_batch_no':temp.batch_id.id
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.bill_of_material_line').create(cr,uid, {
                    'material_id': item.material_id.id,
                    'description':item.description,
                    'uom_id':item.uom_id.id,
                    'requested_quantity':item.actual_qty,
                    'std_qty': item.std_qty,
                    'actual_qty': item.actual_qty,
                    'grn_no': item.grn_no.id,
                    'ar_no': item.ar_no.id,
                    'issued_qty': item.issued_qty,
                    'extra_issued_qty': item.extra_issued_qty,
                    'qty_returned': item.qty_returned,
                    'remarks': item.remarks,
                    'readonly_grid': item.readonly_grid,
                    'extra_flag': item.extra_flag,
                    'main_id': ebsl_id
                    })
        return {}
    @api.one
    @api.multi 
    def return_to_stores(self):
        actual_count = 0
        no_of_line = 0
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("SELECT qty_returned  FROM prakruti_bill_of_material_line WHERE main_id = %s",((temp.id),)) 
            for line in cr.dictfetchall():
                qty_returned = line['qty_returned']
                if qty_returned > 0:
                    cr.execute("SELECT issued_qty,qty_returned,extra_issued_qty  FROM prakruti_bill_of_material_line WHERE main_id = %s",((temp.id),))
                    for line in cr.dictfetchall():
                        issued_qty = line['issued_qty']
                        qty_returned = line['qty_returned']
                        extra_issued_qty = line['extra_issued_qty']
                    if (issued_qty >= qty_returned) or (extra_issued_qty>=qty_returned):
                        cr.execute('''UPDATE 
                                            prakruti_store_issue_item as a 
                                    SET 
                                            qty_returned= b.qty_returned
                                    FROM (
                                            SELECT 
                                                    qty_returned,
                                                    material_id,
                                                    prakruti_bill_of_material_line.id,
                                                    prakruti_bill_of_material_line.issue_common_id 
                                            FROM    prakruti_bill_of_material_line JOIN 
                                                    prakruti_bill_of_material ON 
                                                    prakruti_bill_of_material_line.main_id=prakruti_bill_of_material.id 
                                            WHERE 
                                                    main_id=%s
                                            )as b 
                                    WHERE 
                                            b.id=a.grid_common_id_bom AND 
                                            a.product_id=b.material_id AND 
                                            a.id=b.issue_common_id''' ,((temp.id),))  
                    else:
                        raise UserError(_('Returned qty cannot be greater than Issued Or extra issued Qty')) 
                else:
                    raise UserError(_('Returned qty cannot be -Ve or  0'))
        return {}
    '''
    Button action
    '''
    def action_extraction_product_id(self, cr, uid, ids, context=None):
        prakruti_bill_of_material = self.browse(cr, uid, ids[0], context=context)
        for temp in prakruti_bill_of_material:
            return {
                'name': ('Additional Output'),
                'view_type':'form',
                'view_mode':'form',
                'res_model': 'prakruti.bill_of_material_wizard',
                'view_id':False,
                'type':'ir.actions.act_window',
                'target':'new',
                'context': {
                            'default_extraction_bom_id':prakruti_bill_of_material.id,
                            'default_batch_id':prakruti_bill_of_material.batch_id.id,
                            'default_subplant_id':prakruti_bill_of_material.subplant_id.id,
                            }, 
                
                }
    
class PrakrutiBillOfMaterialLine(models.Model):
    _name = 'prakruti.bill_of_material_line'
    _table = 'prakruti_bill_of_material_line'
    _description = 'Bill of Material Line '
    
    main_id = fields.Many2one('prakruti.bill_of_material', ondelete='cascade')
    material_id = fields.Many2one('product.product',string='Ingredient Name' ,required="True")
    description = fields.Text(string = "Description",required="True")
    uom_id = fields.Many2one('product.uom',string="UOM",required="True")
    std_qty = fields.Float(string='Std. Qty',digits=(6,3))
    actual_qty = fields.Float(string='Actual Qty', required="True",digits=(6,3))
    extra_qty =fields.Float(string='Extra Req Qty.',digits=(6,3))
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.',readonly=True)
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.',readonly=True)
    issued_qty = fields.Float(string='Issued Qty', readonly=True,digits=(6,3))
    extra_issued_qty =fields.Float(string='Extra Qty',default=0 ,readonly=True,digits=(6,3))
    qty_returned = fields.Float(string='Qty Returned',digits=(6,3))
    remarks = fields.Text(string='Remarks')
    extra_flag = fields.Integer(string='Extra Flag',default=0)
    readonly_grid = fields.Integer(string='Grid Readonly',default=0)
    grn_list = fields.Text(string= 'GRN Nos',readonly=1,default='.')
    issue_common_id = fields.Integer('Grid common ID')
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    _sql_constraints=[
        ('unique_material_id','unique(material_id,main_id)', 'Item(s) should be Unique')
        ]
    @api.one
    @api.constrains('qty_returned')
    def _check_qty_returned(self):
        if self.qty_returned < 0:
            raise ValidationError(
                "Returned Qty !!! Can't be Negative ")
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description, standard qty, actual qty.
    '''
    def onchange_material_id(self, cr, uid, ids, material_id, context=None):
        uom_id = 0
        description = ''
        std_qty = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description,case when prakruti_standard_product.standard_value >0 then prakruti_standard_product.standard_value else 0 end as std_qty FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id LEFT JOIN prakruti_standard_product ON product_product.id = prakruti_standard_product.product_name WHERE product_product.id = cast(%s as integer)', ((material_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
            std_qty = line['std_qty']
        return {'value' :{
                'uom_id':uom_id,
                'description':description,
                'std_qty':std_qty,
                'actual_qty':std_qty
                          }}
    
class PrakrutiExtractionBOMGrnListLine(models.Model):
    _name = 'prakruti.extraction_bom_grn_list_line'
    _table = 'prakruti_extraction_bom_grn_list_line'
    _description = 'Extraction BOM GRN Line'
    
    extraction_id = fields.Many2one('prakruti.bill_of_material',string="Extraction BOM ID")
    
    product_id  = fields.Many2one('product.product', string="Product",readonly=1,required=1)
    grn_id= fields.Many2one('prakruti.grn_inspection_details',string= 'GRN No',readonly=1)
    received_qty=fields.Float('Received Qty',readonly=1,default=0)
    issued_qty = fields.Float('Issued Qty',digits=(6,3),readonly=1,default=0)    
    extra_issued_qty =fields.Float(string='Extra Qty',digits=(6,3),readonly=1,default=0)    
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3),readonly=1,default=0)
    packing_per_qty = fields.Float(string= 'Packing Per Qty',digits=(6,3),readonly=1,default=0)
    extra_issued_packing =fields.Float(string='(+)Extra Packing',default=0,digits=(6,3),readonly=1) 
    remarks = fields.Text(string="Remarks")