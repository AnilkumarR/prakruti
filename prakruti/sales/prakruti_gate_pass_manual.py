'''
Company : EBSL
Author: Induja
Module: Manual Gate Pass
Class 1: PrakrutiGatePassManual
Class 2: PrakrutiGatePassLineManual
Table 1 & Reference Id: prakruti_gate_pass_manual ,grid_id
Table 2 & Reference Id: prakruti_gate_pass_manual_line,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''# -*- coding: utf-8 -*-
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
######################################################################################

class PrakrutiGatePassManual(models.Model):
    _name= 'prakruti.gate_pass_manual'
    _table= 'prakruti_gate_pass_manual'
    _description= 'Manual Gate Pass' 
    _order= 'id desc'
    _rec_name= 'pass_no'
    
    
  
    '''Auto genereation function
    'Format: PPPL/GP/GROUP CODE/AUTO GENERATE NO\FINANCIAL YEAR
    Example: PPPL/GP/EXFG/0455/17-18
    Updated By : Induja
    Updated On : 20170823
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
            cr.execute('''SELECT cast(EXTRACT (month FROM pass_date) AS integer) AS month ,cast(EXTRACT (year FROM pass_date) AS integer) AS year ,id FROM prakruti_gate_pass_manual WHERE id=%s''',((temp.id),))
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
                cr.execute('''select autogenerate_manual_gate_pass_no(%s)''', ((temp.id),)  ) # Database Function:autogenerate_manual_gate_pass_no
                result = cr.dictfetchall()
                parent_invoice_id = 0
                for value in result: parent_invoice_id = value['autogenerate_manual_gate_pass_no'];
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
                    style_format[record.id] = 'PPPL/GP-'+str(auto_gen) +'/'+str(display_present_year)+'-'+str(dispay_year)
                cr.execute('''UPDATE prakruti_gate_pass_manual SET pass_no =%s WHERE id=%s ''', ((style_format[record.id]),(temp.id),)  )
            return style_format
    
      
    grid_id= fields.One2many('prakruti.gate_pass_manual_line', 'main_id',string= 'Grid')     
    pass_no= fields.Char(string='Gate Pass No.', default= 'New', readonly=True)
    pass_date= fields.Date('Date', default= fields.Date.today)   
    company_id= fields.Many2one('res.company', string= "Company",default=lambda self: self.env.user.company_id)
    gp_no= fields.Char('Pass No', compute= '_get_auto')
    auto_no= fields.Integer('Auto')
    req_no_control_id= fields.Integer('Auto Generating id', default= 0)     
    vendor_id= fields.Many2one('res.partner', string= "Vendor Name")    
    remarks= fields.Text(string= "Remarks")
    coming_from =fields.Char(string= 'Coming From')
    movement_type = fields.Selection([('inward','Inward'),('outward','Outward')],default='inward',string= 'Type Of Movement')
    local_vendor = fields.Char(string="Local Vendor If Not Exist(s)") 
    product_name = fields.Char(related='grid_id.product_name', string='Product Name')  
    
    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')
    
    _defaults = {
        'company_id': _default_company
        }
    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete...'))
        return super(PrakrutiGatePassManual, self).unlink() 
    
class PrakrutiGatePassLineManual(models.Model):
    _name= 'prakruti.gate_pass_manual_line'
    _table= 'prakruti_gate_pass_manual_line'
    _description= 'Manual Gate Pass Line' 
    
    main_id = fields.Many2one('prakruti.gate_pass_manual', string= "Grid Line")
    product_name= fields.Char(string= "Product Name")
    quantity= fields.Float(string= 'Qty.',digits=(6,3))
    remarks= fields.Text(string= "Remarks")