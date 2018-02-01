'''
Company : EBSL
Author: Induja
Module: Production Transfer Note HA
Class 1: PrakrutiProductionTransferNoteHA
Class 2: PrakrutiProductionTransferNoteHALine
Table 1 & Reference Id: prakruti_production_transfer_note_ha ,grid_id
Table 2 & Reference Id: prakruti_production_transfer_note_ha_line,main_id
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


class PrakrutiProductionTransferNoteHA(models.Model):
    _name = 'prakruti.production_transfer_note_ha'
    _table = 'prakruti_production_transfer_note_ha'
    _description = 'Production Transfer Note HA'
    _rec_name="ptn_no"
    _order= "id desc"
    
    grid_id = fields.One2many('prakruti.production_transfer_note_ha_line', 'main_id',string='Grid')
    ptn_no = fields.Char(string='PTN No',readonly=1)
    batch_no = fields.Many2one('prakruti.batch_master',string='Batch No')
    qc_date=fields.Date(string='QC Date', default=fields.Date.today)
    checked_by= fields.Many2one('res.users',string="Checked By")
    remarks=fields.Char(string='Remarks')
    date=fields.Date(string='PTN/Inward Date')    
    state = fields.Selection([
                            ('ha_check','Quality Control HA Draft'),
                            ('approved','Quality Control Approved'),
                            ('rejected','Quality Control Rejected'),
                            ('done','Production Transfer Note Done')],default= 'ha_check', string= 'Status')    
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
            raise UserError(_('Can\'t Delete'))
        return super(PrakrutiProductionTransferNoteHA, self).unlink()
    '''
    pulls the data to inward
    ''' 
    @api.one
    @api.multi 
    def action_to_inward(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute(''' SELECT count(id) as status_marked FROM prakruti_production_transfer_note_ha_line WHERE (qc_status = 'approved' OR qc_status = 'rejected') AND  main_id =%s''',((temp.id),))
            for item in cr.dictfetchall():
                status_marked=item['status_marked']   
            cr.execute(''' SELECT count(id) as total_line FROM prakruti_production_transfer_note_ha_line WHERE main_id =%s''',((temp.id),))
            for line in cr.dictfetchall():
                total_line=line['total_line']    
            if total_line == status_marked:
                for l in temp.grid_id:
                    if l.ar_id.id:
                        cr.execute("SELECT ptn_ha_to_inward(%s,%s)",((temp.id),(temp.ptn_no),))
                        cr.execute("UPDATE prakruti_production_transfer_note_ha SET report_status = 'attached' WHERE id = %s",((temp.id),))
                    else:
                        cr.execute("SELECT ptn_ha_to_inward(%s,%s)",((temp.id),(temp.ptn_no),))
                        cr.execute("UPDATE prakruti_production_transfer_note_ha SET report_status = 'not_attached' WHERE id = %s",((temp.id),))
                        #raise UserError(_('Please attach the AR Report...'))
            else:
                raise UserError(_('Please Enter Accepted Qty\nPlease Check Status'))
        return True 
   
  
    
class PrakrutiProductionTransferNoteHALine(models.Model):
    _name = 'prakruti.production_transfer_note_ha_line'
    _table = "prakruti_production_transfer_note_ha_line"
    _description = 'Production Transfer Note HA Line'

    main_id = fields.Many2one('prakruti.production_transfer_note_ha',string="Grid", ondelete='cascade')  
    product_id = fields.Many2one('product.product', string="Product", required=1)
    uom_id = fields.Many2one('product.uom',string="UOM",required=1)
    description = fields.Text(string="Description")
    specification_id = fields.Many2one('product.specification.main', string = "Specification")
    mrg_quantity = fields.Float(string = "MFG.Qty",digits=(6,3))
    accepted_qty = fields.Float(string = "Accepted.Qty",digits=(6,3))
    rejected_qty = fields.Float(string = "Reject Qty",digits=(6,3))
    qc_status=fields.Selection([('approved','Approved'),('rejected','Rejected')],string='Status',default='rejected')
    test_result=fields.Char(string='Test Result')
    remarks=fields.Char(string='Remarks')
    common_inward_line_id=fields.Integer(string='Common Inward Line ID')     
    ar_id = fields.Many2one('prakruti.specification.ar.no', string = "AR No.")  
    
    
    '''
    Accepted qty Validation
    '''
    @api.one
    @api.constrains('accepted_qty')
    def _check_accepted_qty(self):
        if self.accepted_qty > self.mrg_quantity:
            raise ValidationError(
                "Please Check Quantity") 
    '''
    Accepted qty Validation
    '''
    @api.one
    @api.constrains('accepted_qty')
    def _check_accepted_qtyt_amount(self):
        if self.accepted_qty < 0 :
            raise ValidationError(
                "Please Check Quantity") 
    '''
    Rejected qty Validation
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



    


    