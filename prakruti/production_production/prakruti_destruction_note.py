'''
Company : EBSL
Author: Induja
Module: Destruction Note
Class 1: PrakrutiDestructionNote
Class 2: PrakrutiDestructionNoteLine
Table 1 & Reference Id: prakruti_destruction_note ,grid_id
Table 2 & Reference Id: prakruti_destruction_note_line,main_id
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


######################################################################################


class PrakrutiDestructionNote(models.Model):
    _name='prakruti.destruction_note'
    _table ='prakruti_destruction_note'
    _description = 'Destruction Note'
    _rec_name = 'grn_no'
    _order = 'id desc'
    
    grid_id = fields.One2many('prakruti.destruction_note_line', 'main_id',string='Grid')
    state = fields.Selection([('destruction','Destruction'),
                              ('to_scrap','Scrap'),
                             ],default= 'destruction', string= 'Status')
    destruction_date = fields.Date(string='Destruction Date', default=fields.Date.today)
    ptn_no = fields.Char(string='PTN No.')
    batch_no = fields.Char(string='Batch No')
    grn_no = fields.Char('GRN No', readonly=True)
    grn_date = fields.Date('GRN Date', readonly=True)
    po_no = fields.Char('Order No', readonly=True)
    order_no = fields.Many2one('prakruti.sales_order', string='Order No',readonly=True)
    order_date = fields.Date('Order Date', readonly=True)
    checked_by  = fields.Many2one('res.users', string='Checked By')
    remarks = fields.Text(string="Remarks")
    coming_from = fields.Selection([('sales','Sales'),('purchase','Purchase'),('production','Production')],default= 'sales', string = "Coming From",readonly=True)
    inward_no = fields.Char(string='PTN/Inward No',readonly=1)
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    
    
    
    '''
    destruction date can't be < than current date
    '''
    @api.one
    @api.constrains('destruction_date')
    def _check_accepted_qty(self):
        if self.destruction_date < fields.Date.today():
            raise ValidationError(
                "Please Check Date") 
    '''
    pulls the data to scrap
    '''
    
    @api.one
    @api.multi 
    def destruct_to_scrap(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            to_scrap_procuction = self.pool.get('prakruti.sales_scrap').create(cr,uid,{
                'grn_no':temp.inward_no,
                'grn_date':temp.grn_date,
                'order_date':temp.order_date,
                'state':'scrap',
                'coming_from':temp.coming_from
                })
            for item in temp.grid_id:
                grid_values = self.pool.get('prakruti.sales_scrap_line').create(cr,uid, {
                    'product_id':item.product_id.id,
                    'uom_id':item.uom_id.id,
                    'description':item.description,
                    'quantity':item.quantity,
                    'remarks':item.remarks,
                    'scrap_line_id':to_scrap_procuction
                    })
        cr.execute("UPDATE prakruti_destruction_note SET state = 'to_scrap' WHERE prakruti_destruction_note.id = cast(%s as integer)", ((temp.id),))
        return {}
    
    
class PrakrutiDestructionNoteLine(models.Model):
    _name='prakruti.destruction_note_line'
    _table ='prakruti_destruction_note_line'
    _description = 'Destruction Note Line'
    
    main_id = fields.Many2one('prakruti.destruction_note',string="Grid")
    product_id = fields.Many2one('product.product', string='Product Name',readonly=1)
    description= fields.Text(string='Description',readonly=1)
    uom_id = fields.Many2one('product.uom',string="UOM",readonly=1)
    quantity = fields.Float('Qty.',readonly=1,digits=(6,3))
    remarks = fields.Text(string="Remarks",readonly=1)