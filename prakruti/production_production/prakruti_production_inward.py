'''
Company : EBSL
Author: Induja
Module: Production Inward
Class 1: PrakrutiProductionInward
Class 2: PrakrutiProductionInwardLine
Table 1 & Reference Id: prakruti_production_inward ,grid_id
Table 2 & Reference Id: prakruti_production_inward_line,main_id
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


#########################################################################################################


class PrakrutiProductionInward(models.Model):
    _name = 'prakruti.production_inward'
    _table = 'prakruti_production_inward'
    _description = 'Production Inward '
    _order= "id desc"
    _rec_name="inward_no"
     
    grid_id = fields.One2many('prakruti.production_inward_line', 'main_id',string='Grid ID')        
    inward_no = fields.Char(string='PTN/Inward No')
    date=fields.Date(string='PTN/Inward Date')
    batch_no = fields.Many2one('prakruti.batch_master',string='Batch No')
    dept_from = fields.Many2one('res.company','From Department')
    prepared_by= fields.Many2one('res.users',string="Prepared By")
    store_incharge= fields.Many2one('res.users',string="Store Incharge")
    approved_by= fields.Many2one('res.users',string="Approved By")
    remarks = fields.Text(string='Remarks')   
    state = fields.Selection([
                            ('inward','Production Transfer Note Inward'),
                            ('qc_check','Quality Control Pending'),
                            ('approved','Quality Control Approved'),
                            ('rejected','Quality Control Rejected'),
                            ('done','Production Transfer Note Done'),
                             ],default= 'inward', string= 'Status')
    bmr_no = fields.Char(string = 'BMR No') 
    location_id = fields.Many2one('prakruti.stock_location', string= 'Location')
    company_id = fields.Many2one('res.company', string = 'Company',default=lambda self: self.env.user.company_id,required="True")
    
    
    formulation_type=fields.Selection([('powder','Powder'),('lotion','Lotion')],string='Formulation Type')
    batch_allocated_by = fields.Selection([('extraction', 'Extraction'),('syrup','Syrup'),('tablet','Tablet'),('formulation','Formulation')],string='Batch Allocated By')
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            raise UserError(_('Can\'t Delete'))
        return super(PrakrutiProductionInward, self).unlink()
    '''
    Pulls the data to PTN QC
    '''
    @api.one
    @api.multi
    def action_to_qc(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            production_qc = self.pool.get('prakruti.production_transfer_note_qc').create(cr,uid, {
                'ptn_no':temp.inward_no,
                'date':temp.date,
                'batch_no':temp.batch_no.id,
                'formulation_type':temp.formulation_type,
                'batch_allocated_by':temp.batch_allocated_by
                })
            for item in temp.grid_id:
                grid_values = self.pool.get('prakruti.production_transfer_note_qc_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description': item.description,
                    'specification_id': item.specification_id.id,
                    'remarks':item.remarks,
                    'mrg_quantity':item.total_output_qty,
                    'common_inward_line_id':item.id,
                    'main_id':production_qc
                 })
            cr.execute("UPDATE  prakruti_production_inward SET state = 'qc_check' WHERE prakruti_production_inward.id = cast(%s as integer)",((temp.id),))
            cr.execute("UPDATE  prakruti_production_transfer_note SET state = 'qc_check' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.inward_no),))
        return {}              
    '''
    Updating the stock & if it is rejected data will pull to Rejection Store
    '''
    @api.one
    @api.multi 
    def inward_to_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {} 
            cr.execute("SELECT count(id) as accept_count FROM prakruti_production_inward_line WHERE accepted_qty > 0 AND main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                accept_count=int(line['accept_count'])
            if accept_count:
                cr.execute("SELECT stock_inward(%s)", ((temp.id),))
                cr.execute("UPDATE prakruti_production_inward SET state = 'done' WHERE prakruti_production_inward.id = cast(%s as integer)", ((temp.id),))
                cr.execute("UPDATE  prakruti_production_transfer_note SET state = 'done' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.inward_no),))
                cr.execute("UPDATE  prakruti_production_transfer_note_qc SET state = 'done' WHERE prakruti_production_transfer_note_qc.ptn_no = %s",((temp.inward_no),))
                cr.execute("UPDATE  prakruti_production_transfer_note_ha SET state = 'done' WHERE prakruti_production_transfer_note_ha.ptn_no = %s",((temp.inward_no),))
                cr.execute('''  UPDATE 
                                    prakruti_batch_master as a 
                                SET 
                                    batch_closed_flag = 1,
                                    is_ptn_done = 1
                                FROM (
                                    SELECT 
                                        batch_no 
                                    FROM 
                                        prakruti_production_inward 
                                    WHERE 
                                        prakruti_production_inward.batch_no=%s AND
                                        prakruti_production_inward.id=%s
                                    ) as b
                                WHERE 
                                    a.id=b.batch_no ''',((temp.batch_no.id),(temp.id),)) 
            else:
                cr.execute("SELECT count(id) as reject_count FROM prakruti_production_inward_line WHERE qc_status = 'rejected' and rejected_qty > 0 AND main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    reject_count=int(line['reject_count'])
                if reject_count >= 1:
                    material_rejection = self.pool.get('prakruti.material_rejected_store').create(cr,uid,{
                        'grn_no':temp.inward_no,
                        'order_date':temp.date,
                        'grn_date':temp.date,
                        'remarks':temp.remarks,
                        'state':'draft',
                        'coming_from':'production',
                        'batch_id':temp.batch_no.id,
                        'bmr_no':temp.bmr_no
                            })
                    for item in temp.grid_id:
                        grid_values = self.pool.get('prakruti.rejected_material_store_line').create(cr,uid, {
                            'product_id':item.product_id.id,
                            'uom_id':item.uom_id.id,
                            'description':item.description,
                            'quantity':item.rejected_qty,
                            'remarks':item.remarks,
                            'qc_check_line_id':material_rejection
                            })
                cr.execute("UPDATE prakruti_production_inward SET state = 'done' WHERE prakruti_production_inward.id = cast(%s as integer)", ((temp.id),))
                cr.execute("UPDATE prakruti_production_transfer_note SET state = 'done' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.inward_no),))
                cr.execute("UPDATE prakruti_production_transfer_note_qc SET state = 'done' WHERE prakruti_production_transfer_note_qc.ptn_no = %s",((temp.inward_no),))
                cr.execute("UPDATE prakruti_production_transfer_note_ha SET state = 'done' WHERE prakruti_production_transfer_note_ha.ptn_no = %s",((temp.inward_no),))
        return{}
    
class PrakrutiProductionInwardLine(models.Model):
    _name = 'prakruti.production_inward_line'
    _table = "prakruti_production_inward_line"
    _description = 'Production Inward Grid'
   
    main_id = fields.Many2one('prakruti.production_inward',string="Grid", ondelete='cascade') 
    product_id = fields.Many2one('product.product', string="Product", required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    description = fields.Text(string="Description")
    packing_style=fields.Float(string='Packing Style',digits=(6,3))
    accepted_qty = fields.Float(string = "Accepted.Qty",digits=(6,3))
    rejected_qty = fields.Float(string = "Rejected.Qty",digits=(6,3))
    packing_qty=fields.Float(string='Packing Qty',digits=(6,3))
    total_output_qty=fields.Float(string='Total Output Qty',digits=(6,3))
    remarks=fields.Char(string='Remarks')
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    qc_status=fields.Selection([('approved','Approved'),('rejected','Rejected')],string=' QC Status',default= 'rejected')
    state = fields.Selection([
                            ('ptn', 'PTN'),
                            ('inward','Inward'),
                            ('qc_check','QC Check'),
                            ('from_qc','From QC')
                             ],default= 'inward', string= 'Status') 

    