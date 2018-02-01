'''
Company : EBSL
Author: Induja
Module: Production Transfer Note QC
Class 1: PrakrutiProductionTransferNoteQC
Class 2: PrakrutiProductionTransferNoteQCLine
Table 1 & Reference Id: prakruti_production_transfer_note_qc ,grid_id
Table 2 & Reference Id: prakruti_production_transfer_note_qc_line,main_id
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
import pdb


#########################################################################################################


class PrakrutiProductionTransferNoteQC(models.Model):
    _name = 'prakruti.production_transfer_note_qc'
    _table = 'prakruti_production_transfer_note_qc'
    _description = 'Production Transfer Note QC'
    _order= "id desc"
    _rec_name="ptn_no"
    
    
    grid_id = fields.One2many('prakruti.production_transfer_note_qc_line', 'main_id',string='Grid')
    ptn_no = fields.Char(string='PTN No',readonly=1)
    batch_no = fields.Many2one('prakruti.batch_master',string='Batch No',readonly=1)
    qc_date=fields.Date(string='QC Date', default=fields.Date.today)
    checked_by= fields.Many2one('res.users',string="Checked By")
    remarks=fields.Char(string='Remarks')
    flag_count_reject = fields.Integer('Rejected Line',default= 0)
    date=fields.Date(string='PTN/Inward Date')
    state = fields.Selection([
        ('qc_check','Quality Control Draft'),
        ('to_ha','Quality Control HA'),
        ('approved','Quality Control Approved'),
        ('rejected','Quality Control Rejected'),
        ('done','Production Transfer Note Done')],default= 'qc_check', string= 'Status')    
    report_status = fields.Selection([
        ('attached','AR Attached'),
        ('not_attached','AR Not Attached')], string= 'Report Status',help='If AR is not attached than the request will be send to Higher Approval...',readonly=1)
    
    formulation_type=fields.Selection([('powder','Powder'),('lotion','Lotion')],string='Formulation Type')
    batch_allocated_by = fields.Selection([('extraction', 'Extraction'),('syrup','Syrup'),('tablet','Tablet'),('formulation','Formulation')],string='Batch Allocated By')
    company_id = fields.Many2one('res.company', string = 'Company',default=lambda self: self.env.user.company_id,required="True")
    
    _defaults = {
        'checked_by': lambda s, cr, uid, c:uid,
        }
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            raise UserError(_('Record Can\'t be Deleted'))
        return super(PrakrutiProductionTransferNoteQC, self).unlink()
    '''
    QC date can't be < than current date
    '''
    @api.one
    @api.constrains('qc_date')
    def _check_qc_date(self):
        if self.qc_date <  fields.Date.today():
            raise ValidationError(
                "Can\'t Select Back Date") 
    
    '''
    Pulls the data to inward
    '''
    @api.one
    @api.multi 
    def action_to_inward(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute("SELECT count(id) AS status_marked FROM prakruti_production_transfer_note_qc_line WHERE (qc_status = 'approved' OR qc_status = 'rejected') AND main_id  = %s",((temp.id),))
            for item in cr.dictfetchall():
                status_marked = item['status_marked']   
            cr.execute('''SELECT count(id) AS total_line FROM prakruti_production_transfer_note_qc_line WHERE main_id =%s''',((temp.id),))
            for line_t in cr.dictfetchall():
                total_line=line_t['total_line']    
            if total_line == status_marked:   
                cr.execute('''SELECT count(id) AS ar_entry_line FROM prakruti_production_transfer_note_qc_line WHERE main_id =%s AND ar_id > 0''',((temp.id),))
                for ar_line in cr.dictfetchall():
                    ar_entry_line = ar_line['ar_entry_line']                
                if ar_entry_line > 0:
                    cr.execute("UPDATE prakruti_production_transfer_note_qc SET report_status = 'attached' WHERE id = %s",((temp.id),))
                    for line in temp.grid_id:
                        if line.rejected_qty:
                            cr.execute("UPDATE prakruti_production_transfer_note_qc SET flag_count_reject = 2,state = 'rejected' WHERE id = %s",((temp.id),))
                            cr.execute("UPDATE prakruti_production_inward SET state = 'rejected' WHERE prakruti_production_inward.inward_no = %s",((temp.ptn_no),))
                            cr.execute("UPDATE prakruti_production_transfer_note SET state = 'rejected' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.ptn_no),))
                        elif line.accepted_qty:                    
                            cr.execute('''  UPDATE 
                                                prakruti_production_inward_line AS b 
                                            SET 
                                                qc_status =a.qc_status,
                                                accepted_qty =a.accepted_qty,
                                                state = 'qc_check',
                                                specification_id = a.specification_id
                                            FROM(
                                                SELECT 
                                                    main_id,
                                                    product_id,
                                                    accepted_qty,
                                                    qc_status,
                                                    specification_id,
                                                    common_inward_line_id 
                                                FROM 
                                                    prakruti_production_transfer_note_qc_line 
                                                WHERE 
                                                    main_id= %s 
                                                ) AS a 
                                            WHERE 
                                                a.product_id = b.product_id AND 
                                                a.common_inward_line_id = b.id''' ,((temp.id),))                    
                            cr.execute("UPDATE prakruti_production_transfer_note_qc SET state = 'approved' WHERE id = CAST(%s AS INTEGER)",((temp.id),))
                            cr.execute("UPDATE prakruti_production_inward SET state = 'approved' WHERE prakruti_production_inward.inward_no = %s",((temp.ptn_no),))
                            cr.execute("UPDATE prakruti_production_transfer_note SET state = 'approved' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.ptn_no),))
                        else:
                            raise UserError(_('Please Enter Qty...'))
                else:
                    cr.execute("UPDATE prakruti_production_transfer_note_qc SET report_status = 'not_attached' WHERE id = %s",((temp.id),))
                    for line in temp.grid_id:
                        if line.rejected_qty:
                            cr.execute("UPDATE prakruti_production_transfer_note_qc SET flag_count_reject = 2,state = 'rejected' WHERE id = %s",((temp.id),))
                            cr.execute("UPDATE prakruti_production_inward SET state = 'rejected' WHERE prakruti_production_inward.inward_no = %s",((temp.ptn_no),))
                            cr.execute("UPDATE prakruti_production_transfer_note SET state = 'rejected' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.ptn_no),))
                        elif line.accepted_qty:
                            cr.execute("UPDATE prakruti_production_transfer_note_qc SET flag_count_reject = 2 WHERE id = %s",((temp.id),))
                            #raise UserError(_('AR Report is not Attached\nPlease send the request to Higher Approval...'))
                        else:
                            raise UserError(_('Please Enter Qty...'))
            else:
                raise UserError(_('Please Enter Accepted Qty\nPlease Check Status'))
        return True 
    '''
    Pulls the data to PTN  HA 
    '''
    @api.one
    @api.multi
    def action_to_ha(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ha_id = self.pool.get('prakruti.production_transfer_note_ha').create(cr,uid, {
                'ptn_no':temp.ptn_no,
                'date':temp.date,
                'batch_no':temp.batch_no.id,
                'remarks':temp.remarks,
                'checked_by':temp.checked_by.id,
                'company_id':temp.company_id.id,
                'formulation_type':temp.formulation_type,
                'report_status':temp.report_status,
                'batch_allocated_by':temp.batch_allocated_by
                })
            for item in temp.grid_id:
                ha_line_id = self.pool.get('prakruti.production_transfer_note_ha_line').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description': item.description,
                    'specification_id': item.specification_id.id,
                    'ar_id':item.ar_id.id,
                    'mrg_quantity': item.mrg_quantity,
                    'accepted_qty': item.accepted_qty,
                    'rejected_qty':item.rejected_qty,
                    'qc_status':item.qc_status,
                    'common_inward_line_id':item.common_inward_line_id,
                    'main_id':ha_id
                })
            cr.execute("UPDATE prakruti_production_transfer_note_qc SET state = 'to_ha',flag_count_reject = 3 WHERE prakruti_production_transfer_note_qc.id = cast(%s as integer)",((temp.id),))
            cr.execute("UPDATE prakruti_production_inward SET state = 'qc_check' WHERE prakruti_production_inward.inward_no = %s",((temp.ptn_no),))
            cr.execute("UPDATE prakruti_production_transfer_note SET state = 'qc_check' WHERE prakruti_production_transfer_note.ptn_no = %s",((temp.ptn_no),))
        return {}
    
    '''
    Update to AR Status 
    //Updated on 20171226
    '''
    @api.one
    @api.multi 
    def action_update_ar_status(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        #pdb.set_trace()
        for temp in self:
            cr.execute('''SELECT count(id) AS ar_entry_line FROM prakruti_production_transfer_note_qc_line WHERE main_id =%s AND ar_id > 0''',((temp.id),))
            for ar_line in cr.dictfetchall():
                ar_entry_line = ar_line['ar_entry_line']
                
                if ar_entry_line > 0:
                    cr.execute("UPDATE prakruti_production_transfer_note_qc SET report_status = 'attached' WHERE id = %s",((temp.id),))
                    
                    cr.execute("UPDATE prakruti_production_transfer_note_ha_line AS b SET ar_id =a.ar_id,specification_id=a.specification_id FROM( SELECT ar_id,common_inward_line_id,product_id,specification_id  FROM prakruti_production_transfer_note_qc_line  WHERE  main_id= %s ) AS a  WHERE a.product_id = b.product_id AND  a.common_inward_line_id = b.common_inward_line_id ",((temp.id),))
                    
                    cr.execute("UPDATE prakruti_production_transfer_note_ha AS b SET report_status =a.report_status FROM ( SELECT report_status,ptn_no,batch_no  FROM prakruti_production_transfer_note_qc  WHERE  id=%s ) AS a WHERE a.batch_no = b.batch_no AND  a.ptn_no = b.ptn_no ",((temp.id),))
                    
                   
        return True 
    
class PrakrutiProductionTransferNoteQCLine(models.Model):
    _name = 'prakruti.production_transfer_note_qc_line'
    _table = "prakruti_production_transfer_note_qc_line"
    _description = 'Production Transfer Note QC Line Grid'


    main_id = fields.Many2one('prakruti.production_transfer_note_qc',string="Grid", ondelete='cascade') 
    product_id = fields.Many2one('product.product', string="Product", required=True)
    uom_id = fields.Many2one('product.uom',string="UOM",required=True)
    description = fields.Text(string="Description")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    mrg_quantity = fields.Float(string = "MFG.Qty",digits=(6,3))
    accepted_qty = fields.Float(string = "Accepted.Qty",digits=(6,3))
    rejected_qty = fields.Float(string = "Reject Qty", compute='_compute_rejected_qty',store=True,digits=(6,3))
    qc_status=fields.Selection([('approved','Approved'),('rejected','Rejected')],string='Status',default='rejected')
    test_result=fields.Char(string='Test Result')
    remarks=fields.Char(string='Remarks')
    common_inward_line_id=fields.Integer(string='Common Inward Line ID')    
    ar_id = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")  
    
    '''
    Negative value validation
    '''
    @api.one
    @api.constrains('mrg_quantity')
    def _check_mrg_quantity(self):
        if self.mrg_quantity < 0:
            raise ValidationError(
                "Quantity Can\'t Be Negative or Zero")  
    '''
    Rejected Qty calculation 
    '''
    @api.depends('mrg_quantity','accepted_qty','qc_status')
    def _compute_rejected_qty(self):
        for order in self:
            rejected_qty = 0.0            
            order.update({                
                'rejected_qty': order.mrg_quantity - order.accepted_qty 
            })
            
    @api.onchange('qc_status')
    def onchange_qc_status(self):
        if self.qc_status == 'approved':
            self.accepted_qty = self.mrg_quantity
            self.rejected_qty = 0.0
            self.test_result = None
        elif not self.qc_status:
            self.accepted_qty = 0.0
            self.test_result = None
        elif self.qc_status == 'rejected':
            self.rejected_qty = self.mrg_quantity
            self.accepted_qty = 0.0
            self.test_result = None
        else:
            self.accepted_qty = 0.0
            self.test_result = None 
            
    @api.onchange('rejected_qty','accepted_qty')
    def onchange_mrg_quantity(self):
        if self.accepted_qty == self.mrg_quantity:
            self.qc_status = 'approved'
            self.test_result = 'PASS'
        else:
            self.qc_status = 'rejected'
            self.test_result = 'FAIL'
            
    


    