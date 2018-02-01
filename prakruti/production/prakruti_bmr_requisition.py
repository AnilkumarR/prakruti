'''
Company : EBSL
Author: Induja
Module: BMR Requisition
Class 1: PrakrutiBMRRequisition
Table 1  : prakruti_bmr_requisition 
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
'''

# -*- coding: utf-8 -*-
from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime,timedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
import re
import logging

class PrakrutiBMRRequisition(models.Model):
    _name = 'prakruti.bmr_requisition'
    _table = 'prakruti_bmr_requisition'
    _description = 'BMR Requisition'
    _order= "id desc"
    _rec_name= 'product_id' 
    
    
  
    '''Auto genereation function
    'Format: BMR\AUTO GENERATE NO\FINANCIAL YEAR
    Example: BMR\0455\17-18
    Updated By : Induja
    Updated On : 20170824
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
                                CAST(EXTRACT (month FROM start_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM start_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_bmr_requisition 
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
                cr.execute('''SELECT autogenerate_bmr_requisition(%s)''', ((temp.id),)  ) # DATABASE FUNCTION :autogenerate_bmr_requisition
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_bmr_requisition'];
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
                    style_format[record.id] = 'BMR'+'\\'+str(auto_gen)+'\\'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE 
                                    prakruti_bmr_requisition 
                              SET 
                                    bmr_no =%s 
                              WHERE 
                                    id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
        
    
    slip_no = fields.Char(string = 'Slip No',readonly=1)
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip No',help='Production Slip Number',readonly=1)
    product_id = fields.Many2one('product.product',string = 'Product Name',readonly=1)
    batch_size = fields.Float(string= 'Batch Size',digits = (6,3))
    request_id = fields.Many2one('res.users',string = 'Request Raised By')
    status = fields.Selection([('request','BMR Request'),('batch_master','Sent To Batch Master')],default='request')
    
    bmr_no = fields.Char(string = 'BMR No',readonly=1,default='New')    
    bmr_number= fields.Char('BMR No', compute= '_get_auto')
    auto_no= fields.Integer('Auto')
    req_no_control_id= fields.Integer('Auto Generating id', default= 0)
    
    start_date = fields.Date(string="Start",readonly=1,default=fields.Date.today())
    finish = fields.Datetime(string="Finish",readonly=1)
    requisition_type = fields.Selection([('new','New'),('re_process','Re-Process')],default='new',string= 'Requisition Type')    
    batch_name=fields.Char(string='Batch Name')
    batch_no=fields.Char(string='Batch No')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'start': datetime.now(),
        'request_id': lambda s, cr, uid, c:uid
        }
    
    '''
    Pulls the data to batch master
    '''    
    @api.one
    @api.multi 
    def raise_batch_master(self):
        subplant_id = 0
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            if temp.requisition_type == 'new':
                cr.execute("SELECT prakruti_sub_plant.id as subplant_id FROM prakruti_sub_plant INNER JOIN prakruti_bmr_requisition ON prakruti_bmr_requisition.product_id =  prakruti_sub_plant.subplant_id WHERE prakruti_bmr_requisition.id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    subplant_id = line['subplant_id']
                if subplant_id:
                    ebsl_id = self.pool.get('prakruti.batch_master').create(cr,uid,{
                        'bmr_no':temp.bmr_no,
                        'subplant_id':subplant_id,
                        'batch_name':'New',
                        'batch_no': 'New',
                        'batch_capacity':temp.batch_size
                        })
                    cr.execute("UPDATE prakruti_bmr_requisition set status = 'batch_master' WHERE id = %s",((temp.id),))
                    cr.execute("UPDATE prakruti_bmr_requisition set finish = now() WHERE id = %s",((temp.id),))
            elif temp.requisition_type == 're_process':
                cr.execute("SELECT prakruti_sub_plant.id as subplant_id FROM prakruti_sub_plant INNER JOIN prakruti_bmr_requisition ON prakruti_bmr_requisition.product_id =  prakruti_sub_plant.subplant_id WHERE prakruti_bmr_requisition.id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    subplant_id = line['subplant_id']
                if subplant_id:
                    ebsl_id = self.pool.get('prakruti.batch_master').create(cr,uid,{
                        'bmr_no':temp.bmr_no,
                        'subplant_id':subplant_id,
                        'batch_name':temp.batch_name + ' - RP',
                        'batch_no': temp.batch_no + ' - RP',
                        'batch_capacity':temp.batch_size
                        })
                    cr.execute("UPDATE prakruti_bmr_requisition set status = 'batch_master' WHERE id = %s",((temp.id),))
                    cr.execute("UPDATE prakruti_bmr_requisition set finish = now() WHERE id = %s",((temp.id),))
            else:
                raise UserError(_('Please create a Subplant or Product of these particular Batch in Subplant...'))
        return {}