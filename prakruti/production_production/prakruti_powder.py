'''
Company : EBSL
Author: Induja
Module: Powder 
Class 1: PrakrutiPowder
Class 2: PrakrutiPowderline
C;ass 3 : PrakrutiPowderlinePacking
Table 1 & Reference Id: prakruti_powder ,grid_id,grid_id1
Table 2 & Reference Id: prakruti_powder_line,main_id
Table 3 & Reference Id: prakruti_powder_line_packing,packing_id
Updated By: Induja
Updated Date & Version: 20170828 ,0.1
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


#########################################################################################################


class PrakrutiPowder(models.Model):
    _name = 'prakruti.powder'
    _table = 'prakruti_powder'
    _description = 'Powder '
    _order = 'id desc'
    _rec_name = 'subplant_id'
    
    
    grid_id = fields.One2many('prakruti.powder_line','main_id')
    grid_id1 = fields.One2many('prakruti.powder_line_packing','packing_id')
    date= fields.Date(string = 'Date',default=fields.Date.today, required=True)
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant ",required=True)
    
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No', required=True)
    actual_batch_size =fields.Float(string='Actual Batch Size', required=True)
    date= fields.Date(string = 'Date',default=fields.Date.today, required=True)
    assay_per = fields.Float(string='% Assay',digits=(6,3))
    label_claim= fields.Char(string='Label Claim')
    material_issued_by = fields.Many2one('res.users',string='Material Issued By',readonly=True)
    material_checked_by = fields.Many2one('res.users',string='Material Checked By',readonly=True)
    material_recieved_by = fields.Many2one('res.users',string='Material Recieved By',readonly=True)
    material_requested_by = fields.Many2one('res.users',string='Material Requested By')
    mrn_no = fields.Char(string = 'MRN No.')
    mrn_date_time = fields.Datetime('MRN Date & Time', default=fields.Date.today)
    is_duplicate = fields.Boolean(string= 'Is a Duplicate',default=False,readonly=True)
    duplicate_flag = fields.Char(string= 'Duplicate Flag',default=0,readonly=True)
    existing_batch_no = fields.Integer(string= 'Existing Batch No.',default=0,readonly=True)
    dept_id = fields.Many2one('res.company','Department')
    std_batch_size_id = fields.Many2one('prakruti.standard_product',string='Std Batch Size')
    flag_display_product = fields.Integer(default=0)    
    flag_delete_product = fields.Integer(default=0)    
    flag_display_product1 = fields.Integer(default=0)    
    flag_delete_product1 = fields.Integer(default=0)
    readonly_flag = fields.Integer(default=0,string="Read Only Field")
    flag_count = fields.Char(string= ' Update Flag',default=0,readonly=True)
    grn_line = fields.One2many('prakruti.powder_bom_grn_list_line', 'powder_id',string='GRN line')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    
    formulation_type=fields.Selection([('powder','Powder'),('lotion','Lotion')],string='Formulation Type', default='powder')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    
    
    
    state = fields.Selection([
                ('draft','Draft'),
                ('sent_stores','Requested To Stores'),
                ('issued_quant','Quantity Issued'),
                
                ('extra_issue','Extra Quantity Request'),
                ('extra_quantity_issued','Extra Quantity Issued'),#new
                
                ('packing_request','Packing Material Request'),
                ('packing_material_issued','Packing Material Issued'),#new
                
                #('issued_pack','Issued Extra Packing'),
                #('issued_extra_packing','Extra Packing Issued'),#new
                ('extra_packing_issue','Extra Packing Material Request'),
                ('extra_packing_issued','Extra Packing Material Issued')#new
                ], string= 'Status',default='draft')    
    packing_material_request_flag = fields.Integer(default = 0)
    
    '''
    Can't delete this record
    '''
    @api.multi
    def unlink(self):
        for v in self:
            if v.state != 'draft':
                raise UserError(_('Can\'t Delete'))
        return super(PrakrutiPowder, self).unlink()
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'material_requested_by': lambda s, cr, uid, c:uid,
        'material_recieved_by': lambda s, cr, uid, c:uid,
        'material_checked_by': lambda s, cr, uid, c:uid
        }
    '''
   Negative value validation
    '''
    def _check_batch_size(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.actual_batch_size <= 0:
                return False
            return True
        
    _constraints = [        
        (_check_batch_size,'Actual Batch Size cannot be negative or zero!',['actual_batch_size'])
        ]
    '''
   Listing  the Products
    '''
    @api.one
    @api.multi 
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("SELECT product_id,description,uom_id,prakruti_standard_product_line.standard_value as std_value FROM prakruti_standard_product_line INNER JOIN prakruti_standard_product ON prakruti_standard_product_line.standard_line_id = prakruti_standard_product.id INNER JOIN prakruti_powder ON prakruti_standard_product.subplant_id = prakruti_powder.subplant_id AND prakruti_standard_product.id = prakruti_powder.std_batch_size_id WHERE prakruti_powder.id = %s",((temp.id),))
            for line in cr.dictfetchall():
                product_id = line['product_id']
                description = line['description']
                uom_id = line['uom_id']
                std_qty = line['std_value']
                actual_qty = line['std_value']
                grid_line_entry = self.pool.get('prakruti.powder_line').create(cr,uid,{
                    'product_id':product_id,
                    'description':description,
                    'uom_id':uom_id,
                    'std_wgt':std_qty,
                    'actual_weight':actual_qty,
                    'main_id':temp.id
                    })
            cr.execute('UPDATE prakruti_powder SET flag_display_product = 1 WHERE prakruti_powder.id = %s',((temp.id),))
            cr.execute("UPDATE prakruti_powder SET flag_delete_product = 0 WHERE prakruti_powder.id = %s",((temp.id),))
        return {}    
    '''
    Deleting the Products
    '''        
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_powder_line WHERE prakruti_powder_line.main_id = %s", ((temp.id),))
            cr.execute("UPDATE  prakruti_powder SET flag_delete_product = 1 WHERE prakruti_powder.id = %s",((temp.id),))
            cr.execute('UPDATE prakruti_powder SET flag_display_product = 0 WHERE prakruti_powder.id = %s',((temp.id),))
        return {}
    '''
    Listing the Packing Products
    '''
    @api.one
    @api.multi 
    def action_list_packing_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("SELECT product_id,description,uom_id,prakruti_standard_product_line.standard_value as std_value FROM prakruti_standard_product_line INNER JOIN prakruti_standard_product ON prakruti_standard_product_line.standard_line_id = prakruti_standard_product.id INNER JOIN prakruti_powder ON prakruti_standard_product.subplant_id = prakruti_powder.subplant_id AND prakruti_standard_product.id = prakruti_powder.std_batch_size_id WHERE prakruti_powder.id = %s",((temp.id),))
            for line in cr.dictfetchall():
                product_id = line['product_id']
                description = line['description']
                uom_id = line['uom_id']
                std_qty = line['std_value']
                actual_qty = line['std_value']
                grid_line_entry = self.pool.get('prakruti.powder_line_packing').create(cr,uid,{
                    'product_id':product_id,
                    'description':description,
                    'uom_id':uom_id,
                    'std_wgt':std_qty,
                    'actual_weight':actual_qty,
                    'packing_id':temp.id
                    })
            cr.execute('UPDATE prakruti_powder SET flag_display_product1 = 1 WHERE prakruti_powder.id = %s',((temp.id),))
            cr.execute("UPDATE prakruti_powder SET flag_delete_product1 = 0 WHERE prakruti_powder.id = %s",((temp.id),))
        return {}    
    '''
    Deleting the Packing Product
    '''        
    @api.one
    @api.multi
    def action_delete_packing_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_powder_line_packing WHERE prakruti_powder_line_packing.packing_id = %s", ((temp.id),))
            cr.execute("UPDATE  prakruti_powder SET flag_delete_product1 = 1 WHERE prakruti_powder.id = %s",((temp.id),))
            cr.execute('UPDATE prakruti_powder SET flag_display_product1 = 0 WHERE prakruti_powder.id = %s',((temp.id),))
        return {}
    '''
    Avoiding to do duplicate from the existing type
    '''
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Forbbiden to duplicate'), _('It Is not possible to duplicate from here...'))
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as batch no, standard batch size,etc.
    '''
    def onchange_subplant_id(self, cr, uid, ids, subplant_id, context=None):
        batch_no = 0
        std_batch_size = 0
        formulation_type = ''
        cr.execute('SELECT prakruti_batch_master.subplant_id,prakruti_batch_master.batch_name,prakruti_batch_master.id as batch_no,prakruti_batch_master.batch_capacity as std_batch_size,prakruti_batch_master.formulation_type as formulation_type FROM prakruti_batch_master WHERE prakruti_batch_master.subplant_id=cast(%s as integer)', ((subplant_id),))
        for line in cr.dictfetchall():
            batch_no = line['batch_no']
            std_batch_size = line['std_batch_size']
            formulation_type = line['formulation_type']
        return {'value' :{
                'batch_no':batch_no,
                'std_batch_size':std_batch_size,
                'formulation_type':formulation_type,
                          }}
        
    '''
    While selecting the product it will load by defaults whatever values are required for that particular from batch Master
    ''' 
    def onchange_batch_id(self, cr, uid, ids, batch_no, context=None):
        process_type = self.pool.get('prakruti.batch_master').browse(cr, uid, batch_no, context=context)
        result = {
            'std_batch_size': process_type.batch_capacity,
            'formulation_type':process_type.formulation_type
            }
        return {'value': result}
    
    '''
    Pulls the data to store Request
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
            if temp.existing_batch_no != temp.batch_no.id:
                print 'BATCH ID',temp.batch_no.id
                print 'COPIED BATCH NUMBER',temp.existing_batch_no
                cr.execute("SELECT count(id) as no_of_line,count(actual_weight) as actual_count  FROM prakruti_powder_line WHERE main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    actual_count = line['actual_count']
                    no_of_line = line['no_of_line']
                if actual_count == no_of_line:
                    #Store Request Entry
                    request_id =  self.pool.get('prakruti.store_request').create(cr,uid, {
                        'date':temp.date,
                        'batch_no':temp.batch_no.id,
                        'powder_bom_id':temp.id,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'store_request_no':'From Production',
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id                        
                        })
                    for item in temp.grid_id:
                        request_line_id = self.pool.get('prakruti.store_request_item').create(cr,uid, {
                            'product_id':item.product_id.id,
                            'description':item.description,
                            'extra_readonly_flag':1,
                            'requested_quantity':item.actual_weight,
                            'uom_id':item.uom_id.id,
                            'grid_common_id':item.id,
                            'main_id':request_id
                            })
                    #Store Approve Entry
                    approve_id =  self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                        'date':temp.date,
                        'batch_no':temp.batch_no.id,
                        'powder_bom_id':temp.id,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id                        
                        })
                    for item in temp.grid_id:
                        approve_line_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                            'product_id':item.product_id.id,
                            'description':item.description,
                            'extra_readonly_flag':1,
                            'requested_quantity':item.actual_weight,
                            'approved_quantity':item.actual_weight,
                            'uom_id':item.uom_id.id,
                            'grid_common_id':item.id,
                            'main_id':approve_id
                            })
                    #Store Issue Entry
                    issue_id =  self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'date':temp.date,
                        'batch_no':temp.batch_no.id,
                        'powder_bom_id':temp.id,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'subplant_id':temp.subplant_id.id                        
                        })
                    for item in temp.grid_id:
                        issue_line_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                            'product_id':item.product_id.id,
                            'description':item.description,
                            'extra_readonly_flag':1,
                            'requested_quantity':item.actual_weight,
                            'approved_quantity':item.actual_weight,
                            'uom_id':item.uom_id.id,
                            'grid_common_id_bom':item.id,
                            'main_id':issue_id
                            })
                    cr.execute("update prakruti_powder set readonly_flag = 1 where id=%s",((temp.id),))
                    cr.execute("update prakruti_powder_line set readonly_grid = 1 where main_id=%s",((temp.id),))
                    cr.execute("update prakruti_powder set state ='sent_stores' where id=%s",((temp.id),))
                    cr.execute("update prakruti_powder set flag_count = 1 where id=%s",((temp.id),))
                else:
                    raise UserError(_('Oops...! Please Enter Actual Qty'))
            else:
                raise UserError(_('Oops...! Please Select different Batch Number'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales BOM Powder')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    
    '''
    Pulls the packing  material data to store Request
    '''
    @api.one
    @api.multi 
    def request_packing_material_issue(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            if temp.existing_batch_no != temp.batch_no.id:
                print 'BATCH ID',temp.batch_no.id
                print 'COPIED BATCH NUMBER',temp.existing_batch_no
                if len(temp.grid_id1) != 0:
                    #Store Request Entry
                    request_id =  self.pool.get('prakruti.store_request').create(cr,uid, {
                        'date':temp.date,
                        'powder_packing_bom_id':temp.id,
                        'powder_bom_id':0,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'store_request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Request Entry
                    approve_id =  self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                        'date':temp.date,
                        'powder_packing_bom_id':temp.id,
                        'powder_bom_id':0,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Request Entry
                    issue_id =  self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'date':temp.date,
                        'powder_packing_bom_id':temp.id,
                        'powder_bom_id':0,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'subplant_id':temp.subplant_id.id
                        })
                    for line in temp.grid_id1:
                        request_line_id = self.pool.get('prakruti.store_request_item').create(cr,uid, {
                            'product_id':line.product_id.id,
                            'description':line.description,
                            'extra_readonly_flag':1,
                            'uom_id':line.uom_id.id,
                            'requested_quantity':line.actual_weight,
                            'grid_common_id':line.id,
                            'main_id':request_id
                            })
                        approve_line_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                            'product_id':line.product_id.id,
                            'description':line.description,
                            'extra_readonly_flag':1,
                            'uom_id':line.uom_id.id,
                            'requested_quantity':line.actual_weight,
                            'grid_common_id':line.id,
                            'main_id':approve_id
                            })
                        issue_line_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                            'product_id':line.product_id.id,
                            'description':line.description,
                            'extra_readonly_flag':1,
                            'uom_id':line.uom_id.id,
                            'requested_quantity':line.actual_weight,
                            'approved_quantity':line.actual_weight,
                            'grid_common_id_bom':line.id,
                            'main_id':issue_id
                            })
                else:
                    raise UserError(_('Oops...! Please Enter Packing Details To Proceed Further'))
                cr.execute("update prakruti_powder_line_packing set readonly_grid = 1 where packing_id=%s",((temp.id),))
                cr.execute("update prakruti_powder set state ='packing_request' where id=%s",((temp.id),))
                cr.execute("update prakruti_powder set flag_count =2,packing_material_request_flag = 0 where id=%s",((temp.id),))
            else:
                raise UserError(_('Oops...! Please Select different Batch Number'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales Powder Packing')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    '''
    Pulls the extra issue material to store requst
    '''
    @api.one
    @api.multi 
    def request_to_stores_for_extra_issue(self):
        product_id = 0
        description = ''
        uom_id = 0
        extra_qty = 0
        extra_bom_id = 0
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
            if temp.existing_batch_no != temp.batch_no.id:
                print 'BATCH ID',temp.batch_no.id
                print 'COPIED BATCH NUMBER',temp.existing_batch_no
                cr.execute("SELECT extra_qty as extra_count FROM prakruti_powder_line WHERE extra_qty > 0 AND main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    extra_count = line['extra_count']
                if extra_count:
                    #Store Request Entry
                    request_id =  self.pool.get('prakruti.store_request').create(cr,uid, {
                        'date':temp.date,
                        'powder_bom_id':temp.id,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'store_request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Approve Entry
                    approve_id =  self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                        'date':temp.date,
                        'powder_bom_id':temp.id,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Issue Entry
                    issue_id =  self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'date':temp.date,
                        'powder_bom_id':temp.id,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'powder_packing_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'subplant_id':temp.subplant_id.id
                        })
                    cr.execute("SELECT product_id,description,uom_id,extra_qty,prakruti_powder_line.id FROM prakruti_powder_line WHERE extra_qty > 0 AND main_id = %s",((temp.id),))
                    for item in cr.dictfetchall():
                        product_id = item['product_id']
                        description = item['description']
                        uom_id = item['uom_id']
                        extra_qty = item['extra_qty']
                        extra_bom_id = item['id']
                        request_line_id = self.pool.get('prakruti.store_request_item').create(cr,uid, {
                            'style_flag':1,
                            'packing_flag':1,
                            'product_id':product_id,
                            'description':description,
                            'uom_id':uom_id,
                            'requested_quantity':extra_qty,
                            'grid_common_id':extra_bom_id,
                            'main_id':request_id
                            })
                        approve_line_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                            'style_flag':1,
                            'packing_flag':1,
                            'product_id':product_id,
                            'description':description,
                            'uom_id':uom_id,
                            'requested_quantity':extra_qty,
                            'grid_common_id':extra_bom_id,
                            'main_id':approve_id
                            })
                        issue_line_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                            'style_flag':1,
                            'packing_flag':1,
                            'product_id':product_id,
                            'description':description,
                            'uom_id':uom_id,
                            'requested_quantity':extra_qty,
                            'approved_quantity':extra_qty,
                            'grid_common_id_bom':extra_bom_id,
                            'main_id':issue_id
                            })
                else:
                    raise UserError(_('Oops...! Please Enter Extra Required Qty'))
                cr.execute("update prakruti_powder set state ='extra_issue' where id=%s",((temp.id),))
                cr.execute("update prakruti_powder set flag_count = 3 where id=%s",((temp.id),))
                # UPDATE STATE BEFORE PACKING
                if temp.state == 'issued_quant':
                    cr.execute("update prakruti_powder set packing_material_request_flag = 2 where id=%s",((temp.id),))
                else:
                    cr.execute("update prakruti_powder set packing_material_request_flag = 0 where id=%s",((temp.id),))
            else:
                raise UserError(_('Oops...! Please Select different Batch Number'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales Powder Extra')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    
    '''
    Pulls the extra issue Packing  material to store requst
    '''
    @api.one
    @api.multi 
    def request_to_stores_for_extra_issue_packing(self):
        product_id = 0
        description = ''
        uom_id = 0
        requested_quantity = 0
        packing_extra_id = 0
        extra_issued_packing = 0
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
            if temp.existing_batch_no != temp.batch_no.id:
                print 'BATCH ID',temp.batch_no.id
                print 'COPIED BATCH NUMBER',temp.existing_batch_no
                cr.execute("SELECT count(id) as extra_count FROM prakruti_powder_line_packing WHERE (extra_qty > 0 OR extra_issued_weight >0) AND packing_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    extra_count = line['extra_count']
                if extra_count:
                    #Store Request Entry
                    request_id =  self.pool.get('prakruti.store_request').create(cr,uid, {
                        'date':temp.date,
                        'powder_packing_bom_id':temp.id,
                        'powder_bom_id':0,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'store_request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Approve Entry
                    approve_id =  self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                        'date':temp.date,
                        'powder_packing_bom_id':temp.id,
                        'powder_bom_id':0,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'state':'issue',
                        'subplant_id':temp.subplant_id.id
                        })
                    #Store Issue Entry
                    issue_id =  self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'date':temp.date,
                        'powder_packing_bom_id':temp.id,
                        'powder_bom_id':0,
                        'tablet_bom_id':0,
                        'syrup_bom_id':0,
                        'extraction_bom_id':0,
                        'syrup_packing_bom_id':0,                
                        'tablet_packing_bom_id':0,
                        'request_no':'From Production',
                        'batch_no':temp.batch_no.id,
                        'dept_id':temp.dept_id.id,
                        'coming_from':'Powder BOM',
                        'subplant_id':temp.subplant_id.id
                        })
                    cr.execute("SELECT product_id,description,uom_id,extra_qty,prakruti_powder_line_packing.id,extra_issued_weight FROM prakruti_powder_line_packing WHERE (extra_qty > 0 OR extra_issued_weight >0) AND packing_id = %s",((temp.id),))
                    for item in cr.dictfetchall():
                        product_id = item['product_id']
                        description = item['description']
                        uom_id = item['uom_id']
                        requested_quantity = item['extra_qty']
                        packing_extra_id = item['id']
                        extra_issued_packing = item['extra_issued_weight']
                        request_line_id = self.pool.get('prakruti.store_request_item').create(cr,uid, {
                                'style_flag':1,
                                'packing_flag':1,
                                'product_id':product_id,
                                'description':description,
                                'uom_id':uom_id,
                                'requested_quantity':requested_quantity,
                                'grid_common_id':packing_extra_id,
                                'extra_issued_packing':extra_issued_packing,
                                'main_id':request_id
                                })
                        approve_line_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                                'style_flag':1,
                                'packing_flag':1,
                                'product_id':product_id,
                                'description':description,
                                'uom_id':uom_id,
                                'requested_quantity':requested_quantity,
                                'grid_common_id':packing_extra_id,
                                'extra_issued_packing':extra_issued_packing,
                                'main_id':approve_id
                                })
                        issue_line_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                                'style_flag':1,
                                'packing_flag':1,
                                'product_id':product_id,
                                'description':description,
                                'uom_id':uom_id,
                                'requested_quantity':requested_quantity,
                                'approved_quantity':requested_quantity,
                                'grid_common_id_bom':packing_extra_id,
                                'extra_issued_packing':extra_issued_packing,
                                'main_id':issue_id
                                })
                else:
                    raise UserError(_('Oops...! Please Enter Extra Packing Qty'))
                cr.execute("update prakruti_powder set state ='extra_packing_issue' where id=%s",((temp.id),))
                cr.execute("update prakruti_powder set flag_count = 4 where id=%s",((temp.id),))
            else:
                raise UserError(_('Oops...! Please Select different Batch Number'))
            #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Sales Powder Extra Packing')],context=context)[0]
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        return {}
    '''
    Duplicate Bom
    '''
    @api.one
    @api.multi
    def duplicate_bom(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            d_request = self.pool.get('prakruti.powder').create(cr,uid, {
                'date':temp.date,
                'subplant_id':temp.subplant_id.id,
                'batch_no':temp.batch_no.id,
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
                'existing_batch_no':temp.batch_no.id
                })
            for item in temp.grid_id:
                grid_values = self.pool.get('prakruti.powder_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'composition': item.composition,
                    'description':item.description,
                    'uom_id':item.uom_id.id,
                    'std_wgt': item.std_wgt,
                    'material_weight': item.material_weight,
                    'issued_weight': item.issued_weight,
                    'extra_qty': item.extra_qty,
                    'actual_weight': item.actual_weight,
                    'weighed_by': item.weighed_by.id,
                    'checked_by': item.checked_by.id,
                    'grn_no': item.grn_no.id,
                    'ar_no': item.ar_no.id,
                    'weight_return': item.weight_return,
                    'extra_issued_qty': item.extra_issued_qty,
                    'readonly_grid': item.readonly_grid,
                    'extra_flag': item.extra_flag,
                    'grn_list':item.grn_list,
                    'main_id': d_request
                    })
            for item in temp.grid_id1:
                grid_values2 = self.pool.get('prakruti.powder_line_packing').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'composition': item.composition,
                    'description':item.description,
                    'uom_id':item.uom_id.id,
                    'std_wgt': item.std_wgt,
                    'material_weight': item.material_weight,
                    'issued_weight': item.issued_weight,
                    'extra_qty': item.extra_qty,
                    'actual_weight': item.actual_weight,
                    'weighed_by': item.weighed_by.id,
                    'checked_by': item.checked_by.id,
                    'grn_no': item.grn_no.id,
                    'grn_list':item.grn_list,
                    'ar_no': item.ar_no.id,
                    'weight_returned': item.weight_returned,
                    'extra_issued_qty': item.extra_issued_qty,
                    'readonly_grid': item.readonly_grid,
                    'extra_flag': item.extra_flag,
                    'packing_id': d_request
                    })
        return {} 
    
    
    def action_formulation_product_id(self, cr, uid, ids, context=None):
        prakruti_powder = self.browse(cr, uid, ids[0], context=context)
        for temp in prakruti_powder:
            return {
                'name': ('Additional Output'),
                'view_type':'form',
                'view_mode':'form',
                'res_model': 'prakruti.formulation_wizard',
                'view_id':False,
                'type':'ir.actions.act_window',
                'target':'new',
                'context': {
                            'default_formulation_bom_id':prakruti_powder.id,
                            'default_batch_no':prakruti_powder.batch_no.id,
                            'default_subplant_id':prakruti_powder.subplant_id.id,
                            }, 
                
                }
    
    def action_formulation_packing_product_id(self, cr, uid, ids, context=None):
        prakruti_powder = self.browse(cr, uid, ids[0], context=context)
        for temp in prakruti_powder:
            return {
                'name': ('Additional Output'),
                'view_type':'form',
                'view_mode':'form',
                'res_model': 'prakruti.formulation_packing_wizard',
                'view_id':False,
                'type':'ir.actions.act_window',
                'target':'new',
                'context': {
                            'default_formulation_packing_bom_id':prakruti_powder.id,
                            'default_batch_no':prakruti_powder.batch_no.id,
                            'default_subplant_id':prakruti_powder.subplant_id.id,
                            }, 
                
                }
                
    
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
            cr.execute("SELECT weight_return  FROM prakruti_powder_line WHERE main_id = %s",((temp.id),))  
            for line in cr.dictfetchall():
                weight_return = line['weight_return']
            #cr.execute("SELECT weight_returned  FROM prakruti_powder_line_packing WHERE packing_id = %s",((temp.id),)) 
            #for line in cr.dictfetchall():
                #weight_returned = line['weight_returned']
                if weight_return > 0:
                    cr.execute("SELECT issued_weight,weight_return,extra_issued_qty  FROM prakruti_powder_line WHERE main_id = %s",((temp.id),))
                    for line in cr.dictfetchall():
                        issued_weight = line['issued_weight']
                        weight_return = line['weight_return']
                        extra_issued_qty = line['extra_issued_qty']
                    if (issued_weight >= weight_return) or (extra_issued_qty>=weight_return):
                        cr.execute('''UPDATE 
                                            prakruti_store_issue_item as a 
                                    SET 
                                            qty_returned= b.weight_return
                                    FROM (
                                            SELECT 
                                                    weight_return,
                                                    product_id,
                                                    prakruti_powder_line.issue_common_id,
                                                    prakruti_powder_line.id 
                                            FROM    prakruti_powder_line JOIN 
                                                    prakruti_powder ON 
                                                    prakruti_powder_line.main_id=prakruti_powder.id 
                                            WHERE 
                                                    main_id=%s
                                            )as b 
                                    WHERE 
                                            b.id=a.grid_common_id_bom AND 
                                            a.product_id=b.product_id AND 
                                            a.id=b.issue_common_id ''' ,((temp.id),))  
                    else:
                        raise UserError(_('Returned qty cannot be greater than Issued Or extra issued Weight'))
                #elif weight_returned > 0:
                    #cr.execute("SELECT issued_weight,weight_returned,extra_issued_weight  FROM prakruti_powder_line WHERE main_id = %s",((temp.id),))
                    #for line in cr.dictfetchall():
                        #issued_weight = line['issued_weight']
                        #weight_returned = line['weight_returned']
                        #extra_issued_weight = line['extra_issued_weight']
                    #if (issued_weight >= weight_returned) or (extra_issued_weight>=weight_returned):
                        #cr.execute('''UPDATE 
                                            #prakruti_store_issue_item as a 
                                    #SET 
                                            #qty_returned= b.weight_returned
                                    #FROM (
                                            #SELECT 
                                                    #weight_returned,
                                                    #product_id,
                                                    #prakruti_powder_line_packing.id 
                                            #FROM    prakruti_powder_line_packing JOIN 
                                                    #prakruti_powder ON 
                                                    #prakruti_powder_line_packing.packing_id=prakruti_powder.id 
                                            #WHERE 
                                                    #packing_id=%s
                                            #)as b 
                                    #WHERE 
                                            #b.id=a.grid_common_id_bom AND 
                                            #a.product_id=b.product_id ''' ,((temp.id),))  
                    #else:
                        #raise UserError(_('Returned qty cannot be greater than Issued Or extra issued Weight')) 
                else:
                    raise UserError(_('Returned qty cannot be -Ve or  0'))
        return {}
                
    
    @api.one
    @api.multi 
    def packing_return_to_stores(self):
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
            if len(temp.grid_id1) != 0 :
                cr.execute("SELECT weight_returned  FROM prakruti_powder_line_packing WHERE packing_id = %s",((temp.id),)) 
                for line in cr.dictfetchall():
                    weight_returned = line['weight_returned']
                    if weight_returned > 0:
                        cr.execute("SELECT issued_weight,weight_returned,extra_issued_weight  FROM prakruti_powder_line_packing WHERE packing_id = %s",((temp.id),))
                        for line in cr.dictfetchall():
                            issued_weight = line['issued_weight']
                            weight_returned = line['weight_returned']
                            extra_issued_weight = line['extra_issued_weight']
                        if (issued_weight >= weight_returned) or (extra_issued_weight>=weight_returned):
                            cr.execute('''UPDATE 
                                                prakruti_store_issue_item as a 
                                        SET 
                                                qty_returned= b.weight_returned
                                        FROM (
                                                SELECT 
                                                        weight_returned,
                                                        product_id,
                                                        prakruti_powder_line_packing.issue_common_id, 
                                                        prakruti_powder_line_packing.id 
                                                FROM    prakruti_powder_line_packing JOIN 
                                                        prakruti_powder ON 
                                                        prakruti_powder_line_packing.packing_id=prakruti_powder.id 
                                                WHERE 
                                                        packing_id=%s
                                                )as b 
                                        WHERE 
                                                b.id=a.grid_common_id_bom AND 
                                                a.product_id=b.product_id AND 
                                                a.id=b.issue_common_id ''' ,((temp.id),))  
                        else:
                            raise UserError(_('Returned qty cannot be greater than Issued Or extra issued Weight')) 
                    else:
                        raise UserError(_('Returned qty cannot be -Ve or  0'))
            else:
                raise UserError(_('Please Select the Packing Material...'))
        return {}
    
    
    
    
class PrakrutiPowderline(models.Model):
    _name = 'prakruti.powder_line'
    _table = 'prakruti_powder_line'
    _description = 'Powder Line'
    
    main_id = fields.Many2one('prakruti.powder', ondelete='cascade')
    product_id=fields.Many2one('product.product', string="Ingredient Name",required="True")
    description = fields.Text(string = "Description", required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.',readonly=True)
    std_wgt = fields.Float(string='Std. Weight',digits=(6,3))
    composition = fields.Float(string='Composition per 10ml',digits=(6,3))
    material_weight = fields.Float(string='Material Weight',digits=(6,3))
    actual_weight = fields.Float(string='Actual Weight', required="True",digits=(6,3))
    weighed_by=fields.Many2one('res.users','Weighed By')
    checked_by=fields.Many2one('res.users','Checked By')
    issued_weight = fields.Float(string='Issued Weight',digits=(6,3))
    extra_qty =fields.Float(string='Extra Req Weight',digits=(6,3))
    extra_issued_qty =fields.Float(string='Extra Weight',digits=(6,3))
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.',readonly=True)
    extra_flag = fields.Integer(string='Extra Flag',default=0)
    readonly_grid = fields.Integer(string='Grid Readonly',default=0)
    weight_return = fields.Float(string='Weight Returned',digits=(6,3))
    grn_list = fields.Text(string= 'GRN Nos',readonly=1,default='.')
    issue_common_id = fields.Integer('Grid common ID')
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    _sql_constraints=[
        ('unique_product_id','unique(product_id,main_id)', 'Item(s) should be Unique')
        ]
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'weighed_by': lambda s, cr, uid, c:uid,
        'checked_by': lambda s, cr, uid, c:uid        
        }
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as batch no, standard batch size,etc.
    ''' 
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = 0
        description = ''
        std_wgt = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description,case when prakruti_standard_product.standard_value >0 then prakruti_standard_product.standard_value else 0 end as std_wgt FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id LEFT JOIN prakruti_standard_product ON product_product.id = prakruti_standard_product.product_name WHERE product_product.id = cast(%s as integer)', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
            std_wgt = line['std_wgt']
        return {'value' :{
                'uom_id':uom_id,
                'description':description,
                'std_wgt':std_wgt,
                'actual_weight':std_wgt
                          }}
    '''
    Negative values validation
    ''' 
    def _check_material_weight(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.material_weight <= 0:
                return False
            return True
        
    def _check_actual_weight(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.actual_weight <= 0:
                return False
            return True
    
    
    
    _constraints = [        
        (_check_material_weight,'Material Weight cannot be negative or zero!',['material_weight']),
        (_check_actual_weight,'Actual Weight cannot be negative or zero!',['actual_weight'])        
        ]
    
class PrakrutiPowderlinePacking(models.Model):
    _name = 'prakruti.powder_line_packing'
    _table = 'prakruti_powder_line_packing'
    _description = 'Powder Packing Line'
    
    packing_id = fields.Many2one('prakruti.powder', ondelete='cascade')
    product_id=fields.Many2one('product.product', string="Packing Material",required="True")
    description = fields.Text(string = "Description", required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.',readonly=True)
    std_wgt = fields.Float(string='Std. Weight',digits=(6,3))
    composition = fields.Float(string='No. of Packings',digits=(6,3))
    material_weight = fields.Float(string='Material Weight',digits=(6,3))
    actual_weight = fields.Float(string='Actual Weight', required="True",digits=(6,3))
    weighed_by=fields.Many2one('res.users','Weighed By')
    checked_by=fields.Many2one('res.users','Checked By')
    issued_weight = fields.Float(string='Packing Weight',digits=(6,3))
    extra_qty =fields.Float(string='Extra Req Weight',digits=(6,3))
    extra_issued_qty =fields.Float(string='Extra Weight',digits=(6,3))
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.',readonly=True)
    extra_flag = fields.Integer(string='Extra Flag',default=0)
    readonly_grid = fields.Integer(string='Grid Readonly',default=0)
    weight_returned = fields.Float(string='Weight Returned',digits=(6,3))
    extra_no_of_packing = fields.Float(string='Extra No. of Packings',digits=(6,3))#
    extra_issued_weight = fields.Float(string='Extra Packing Weight',digits=(6,3))#
    extra_issued_packing = fields.Float(string='Extra Packing',digits=(6,3))#
    grn_list = fields.Text(string= 'GRN Nos',readonly=1,default='.')
    issue_common_id = fields.Integer('Grid common ID')
    '''
    The product which will be entered shoud be unique, that means same product must not be entered more than one 
    '''
    _sql_constraints=[
        ('unique_product_id','unique(product_id,packing_id)', 'Item(s) should be Unique')
        ]
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'weighed_by': lambda s, cr, uid, c:uid,
        'checked_by': lambda s, cr, uid, c:uid        
        }
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as batch no, standard batch size,etc.
    '''  
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        uom_id = 0
        description = ''
        std_wgt = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description,case when prakruti_standard_product.standard_value >0 then prakruti_standard_product.standard_value else 0 end as std_wgt FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id LEFT JOIN prakruti_standard_product ON product_product.id = prakruti_standard_product.product_name WHERE product_product.id = cast(%s as integer)', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
            std_wgt = line['std_wgt']
        return {'value' :{
                'uom_id':uom_id,
                'description':description,
                'std_wgt':std_wgt,
                'actual_weight':std_wgt
                          }}
    
    '''
    Negative value validation
    '''
    def _check_material_weight(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.material_weight <= 0:
                return False
            return True
        
    def _check_actual_weight(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.actual_weight <= 0:
                return False
            return True
        
    def _check_weight(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.actual_weight < temp.material_weight:
                return False
            return True
        
    def _check_packing(self, cr, uid, ids):
        lines = self.browse(cr, uid, ids)
        for temp in lines:
            if temp.composition <= 0:
                return False
            return True
    
    
    _constraints = [        
        (_check_material_weight,'Material Weight cannot be negative or zero!',['material_weight']),
        (_check_actual_weight,'Actual Weight cannot be negative or zero!',['actual_weight']),
        (_check_weight,'Actual Weight cannot be less than Material weight!',['actual_weight']),
        (_check_packing,'Please Enter No of Packings!',['composition']),
        ]
    
class PrakrutiPowderBOMGrnListLine(models.Model):
    _name = 'prakruti.powder_bom_grn_list_line'
    _table = 'prakruti_powder_bom_grn_list_line'
    _description = 'Powder BOM GRN Line'
    
    powder_id = fields.Many2one('prakruti.powder',string="Powder BOM ID")
    
    product_id  = fields.Many2one('product.product', string="Product",readonly=1,required=1)
    grn_id= fields.Many2one('prakruti.grn_inspection_details',string= 'GRN No',readonly=1)
    received_qty=fields.Float('Received Qty',readonly=1,default=0)
    issued_qty = fields.Float('Issued Qty',digits=(6,3),readonly=1,default=0)   
    extra_issued_qty =fields.Float(string='Extra Qty',digits=(6,3),readonly=1,default=0)   
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3),readonly=1,default=0)
    packing_per_qty = fields.Float(string= 'Packing Per Qty',digits=(6,3),readonly=1,default=0)
    extra_issued_packing =fields.Float(string='(+)Extra Packing',default=0,digits=(6,3),readonly=1) 
    remarks = fields.Text(string="Remarks")