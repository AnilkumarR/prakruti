'''
Company : EBSL
Author: Induja
Module: Production Transfer Note
Class 1: PrakrutiProductionTransferNote
Class 2: PrakrutiDispatchLine
Table 1 & Reference Id: prakruti_production_transfer_note ,grid_id
Table 2 & Reference Id: prakruti_dispatch_line,main_id
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


#########################################################################################################


class PrakrutiProductionTransferNote(models.Model):
    _name = 'prakruti.production_transfer_note'
    _table = 'prakruti_production_transfer_note'
    _description = 'PTN'
    _order= "id desc"
    _rec_name="ptn_no" 
    
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
                                CAST(EXTRACT (month FROM date) AS integer) AS month,
                                CAST(EXTRACT (year FROM date) as integer) as year ,
                                id 
                          FROM
                                prakruti_production_transfer_note 
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
            cr.execute('''SELECT autogenerate_prakruti_production_transfer_note(%s)''', ((temp.id),)  ) # Database function: autogenerate_prakruti_production_transfer_note
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_prakruti_production_transfer_note'];
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
                style_format[record.id] = 'PTN\\'+str(auto_gen) +'/'+str(display_present_year)+'-'+str(dispay_year)
            cr.execute('''UPDATE 
                                prakruti_production_transfer_note 
                          SET 
                                ptn_no =%s 
                          WHERE 
                                id=%s ''', ((style_format[record.id]),(temp.id),)  )
        return style_format
    
    grid_id = fields.One2many('prakruti.production_transfer_note_line', 'main_id',string='Grid')
    
    
    batch_no = fields.Many2one('prakruti.batch_master',string='Batch No', required=1)
    
    ptn_no = fields.Char(string='PTN No',default='New',readonly=1)
    date=fields.Date(string='Date', default=fields.Date.today,required=1)
    
    dept_from = fields.Many2one('res.company','From Department', required=1)
    dept_to = fields.Many2one('res.company','To Department', required=1)
    
    doc_no = fields.Char(' Doc No')
    rev_no = fields.Char(' Rev No')
    
    prepared_by= fields.Many2one('res.users',string="Prepared By",required=1, default=lambda self: self.env.user)
    store_incharge= fields.Many2one('res.users',string="Store Incharge",required=1, default=lambda self: self.env.user)
    approved_by= fields.Many2one('res.users',string="Approved By",required=1, default=lambda self: self.env.user)
    
    ref_if_any = fields.Char('Ref If Any')
    remarks = fields.Char('Remarks')
    
    state =fields.Selection([
        ('ptn', 'Production Transfer Note draft'),
        ('inward','Production Transfer Note Inward'),
        ('qc_check','Quality Control Pending'),
        ('approved','Quality Control Approved'),
        ('rejected','Quality Control Rejected'),
        ('done','Production Transfer Note Done'),
        ('destruction','Destruction Note')
        ],default= 'ptn', string= 'Status')
    
    pt_no = fields.Char('PTN No', compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating ID',default= 0)
    
    extraction_display_flag = fields.Integer(string="Extraction Displayed",default=0)
    extraction_delete_flag = fields.Integer(string="Extraction Deleted",default=0)
    
    syrup_display_flag = fields.Integer(string="Syrup Displayed",default=0)
    syrup_delete_flag = fields.Integer(string="Syrup Deleted",default=0)
    
    tablet_display_flag = fields.Integer(string="Tablet Displayed",default=0)
    tablet_delete_flag = fields.Integer(string="Tablet Deleted",default=0)
    
    powder_display_flag = fields.Integer(string="Powder Displayed",default=0)
    powder_delete_flag = fields.Integer(string="Powder Deleted",default=0)
    
    qc_ptn_no = fields.Char(string='QC PTN No')   
    bmr_no = fields.Char(string = 'BMR No')
    
    company_id = fields.Many2one('res.company',string= 'Company', default = lambda self: self.env.user.company_id.id)    
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly = 1,default='-')
    
    formulation_type=fields.Selection([('powder','Powder'),('lotion','Lotion')],string='Formulation Type')
    batch_allocated_by = fields.Selection([('extraction', 'Extraction'),('syrup','Syrup'),('tablet','Tablet'),('formulation','Formulation')],string='Batch Allocated By')
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            raise UserError(_('Can\'t Delete'))
        return super(PrakrutiProductionTransferNote, self).unlink() 
    '''
    date can't be < than current date
    '''
    @api.one
    @api.constrains('date')
    def _check_date(self):
        if self.date <  fields.Date.today():
            raise ValidationError(
                "Can\'t Select Back Date") 
        
    '''
    Listing the products from extraction
    '''    
    @api.one
    @api.multi
    def action_list_products_for_extraction(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''SELECT production_transfer_note_action_list_product_extraction(%s,%s)''', ((temp.id),(temp.batch_no.id),))
        return {}
    '''
    Listing the products from tablet
    '''
    @api.one
    @api.multi
    def action_list_products_for_tablet(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''SELECT production_transfer_note_action_list_product_tablet(%s,%s)''', ((temp.id),(temp.batch_no.id),))
        return {}
    '''
    Listing the products from syrup
    '''
    @api.one
    @api.multi
    def action_list_products_for_syrup(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''SELECT production_transfer_note_action_list_product_syrup(%s,%s)''', ((temp.id),(temp.batch_no.id),))
        return {}
        
    '''
    Listing the products from powder
    '''    
    @api.one
    @api.multi
    def action_list_products_for_powder(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute('''SELECT production_transfer_note_action_list_product_powder(%s,%s)''', ((temp.id),(temp.batch_no.id),))
        return {}
    '''
    deleting the products 
    '''
    @api.one
    @api.multi
    def action_delete_products_for_extraction(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_production_transfer_note_line WHERE main_id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_production_transfer_note SET extraction_display_flag = 0,extraction_delete_flag = 1,syrup_display_flag = 0,syrup_delete_flag = 0,powder_display_flag = 0,powder_delete_flag = 0,tablet_display_flag = 0,tablet_delete_flag = 0 WHERE prakruti_production_transfer_note.id = %s",((temp.id),))
        return {}
    '''
    deleting the products 
    '''
    @api.one
    @api.multi
    def action_delete_products_for_syrup(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_production_transfer_note_line WHERE main_id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_production_transfer_note SET syrup_display_flag = 0,syrup_delete_flag = 1,extraction_display_flag = 0,powder_display_flag = 0,powder_delete_flag = 0,extraction_delete_flag = 0,tablet_display_flag = 0,tablet_delete_flag = 0 WHERE prakruti_production_transfer_note.id = %s",((temp.id),))
        return {}
    '''
    deleting the products 
    '''
    @api.one
    @api.multi
    def action_delete_products_for_tablet(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_production_transfer_note_line WHERE main_id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_production_transfer_note SET tablet_display_flag = 0,tablet_delete_flag = 1,powder_display_flag = 0,powder_delete_flag = 0,syrup_display_flag = 0,syrup_delete_flag = 0,extraction_display_flag = 0,extraction_delete_flag = 0 WHERE prakruti_production_transfer_note.id = %s",((temp.id),))
        return {}
    '''
    deleting the products 
    '''
    @api.one
    @api.multi
    def action_delete_products_for_powder(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_production_transfer_note_line WHERE main_id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_production_transfer_note SET powder_display_flag = 0,powder_delete_flag = 1,tablet_display_flag = 0,tablet_delete_flag = 0,syrup_display_flag = 0,syrup_delete_flag = 0,extraction_display_flag = 0,extraction_delete_flag = 0 WHERE prakruti_production_transfer_note.id = %s",((temp.id),))
        return {}
    
    
    '''
    While selecting batch no it will extract data from batch master Screen 
    ''' 
    def onchange_batch_no(self, cr, uid, ids, batch_no, context=None):
        process_type = self.pool.get('prakruti.batch_master').browse(cr, uid, batch_no, context=context)
        result = {
            'batch_allocated_by': process_type.batch_allocated_by,
            'bmr_no': process_type.bmr_no,
            'formulation_type':process_type.formulation_type
            }
        return {'value': result}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_batch_no the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_batch_no(cr, uid, [], vals['batch_no'])
        if onchangeResult.get('value') or onchangeResult['value'].get('batch_allocated_by','bmr_no'):
            vals['batch_allocated_by'] = onchangeResult['value']['batch_allocated_by']
            vals['bmr_no'] = onchangeResult['value']['bmr_no']
        return super(PrakrutiProductionTransferNote, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiProductionTransferNote, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.batch_no.id
        onchangeResult = self.onchange_batch_no(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('batch_allocated_by','bmr_no'):
            vals['batch_allocated_by'] = onchangeResult['value']['batch_allocated_by']
            vals['bmr_no'] = onchangeResult['value']['bmr_no']
        return super(PrakrutiProductionTransferNote, self).write(cr, uid, ids, vals, context=context)
    
    '''
    pulling data to inward 
    '''    
    @api.one
    @api.multi
    def action_to_inward(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            cr.execute("SELECT count(id) as no_of_line FROM prakruti_production_transfer_note_line WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                no_of_line = line['no_of_line']            
            cr.execute("SELECT count(distinct(product_id)) as no_of_product_line FROM prakruti_production_transfer_note_line WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                no_of_product_line = line['no_of_product_line']
            if no_of_line == no_of_product_line:
                ebsl_id = self.pool.get('prakruti.production_inward').create(cr,uid, {
                    'qc_ptn_no':temp.qc_ptn_no,
                    'inward_no':temp.ptn_no,
                    'batch_no':temp.batch_no.id,
                    'date':temp.date,
                    'dept_from':temp.dept_from.id,
                    'prepared_by':temp.prepared_by.id,
                    'store_incharge':temp.store_incharge.id,
                    'company_id':temp.company_id.id,
                    'approved_by':temp.approved_by.id,
                    'formulation_type':temp.formulation_type,
                    'batch_allocated_by':temp.batch_allocated_by,
                    'bmr_no':temp.bmr_no
                    })
                for item in temp.grid_id:
                    erp_id = self.pool.get('prakruti.production_inward_line').create(cr,uid, {
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'description':item.description,
                        'specification_id':item.specification_id.id,
                        'packing_style':item.packing_style,
                        'packing_qty':item.packing_qty,
                        'total_output_qty':item.total_output_qty,
                        'accepted_qty':item.accepted_qty,
                        'rejected_qty':item.rejected_qty,
                        'test_result':item.test_result,    
                        'qc_status': item.qc_status,
                        'remarks':item.remarks,
                        'main_id':ebsl_id
                    })
            else:
                raise UserError(_('Can\'t Proceed, Since Product line is having Duplicate Entries else Please Enter Some Products'))
            cr.execute("UPDATE  prakruti_production_transfer_note SET state = 'inward' WHERE prakruti_production_transfer_note.id = cast(%s as integer)",((temp.id),))
        return {}
    '''
    Button action
    '''
    def action_ptn_product_id_transfer(self, cr, uid, ids, context=None):
        prakruti_production_transfer_note = self.browse(cr, uid, ids[0], context=context)
        for temp in prakruti_production_transfer_note:
            return {
                'name': ('Additional Output'),
                'view_type':'form',
                'view_mode':'form',
                'res_model': 'prakruti.production_transfer_note_wizard',
                'view_id':False,
                'type':'ir.actions.act_window',
                'target':'new',
                'context': {
                            'default_ptn_id':prakruti_production_transfer_note.id,
                            'default_batch_no':prakruti_production_transfer_note.batch_no.id,
                            'default_ptn_no':prakruti_production_transfer_note.ptn_no,
                            }, 
                
                }
  
    
    
class PrakrutiPTNLine(models.Model):
    _name = 'prakruti.production_transfer_note_line'
    _table = "prakruti_production_transfer_note_line"
    _description = 'Production Transfer Note Line '

    
    main_id = fields.Many2one('prakruti.production_transfer_note',string="Grid", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product Name")
    uom_id = fields.Many2one('product.uom',string="UOM")
    description = fields.Text(string="Description")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    packing_style=fields.Float(string='Packing Style',digits=(6,3))
    packing_qty=fields.Float(string='Packing Qty',digits=(6,3))
    total_output_qty=fields.Float(string='Total Output Qty',digits=(6,3))
    accepted_qty = fields.Float(string = "Accepted.Qty",digits=(6,3))
    rejected_qty = fields.Float(string = "Reject Qty" ,digits=(6,3))
    test_result=fields.Char(string='Test Result')
    qc_status=fields.Selection([('approved','Approved'),('rejected','Rejected')],string='QC status')
    remarks=fields.Char(string='Remarks')
    
   
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        cr.execute('SELECT  product_uom.id AS uom_id,product_uom.name,product_template.name as description FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id=cast(%s as integer)', ((product_id),))
        for values in cr.dictfetchall():
            uom_id = values['uom_id']
            description = values['description']
            return {'value' :{ 'uom_id': uom_id,'description':description }}