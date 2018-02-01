'''
Company : EBSL
Author: Induja
Module: Syrup Production
Class 1: PrakrutiSyrupProduction
Class 2: PrakrutiProductionSyrupPulverization
Class 3 : PrakrutiSyrupExtractSolution
Class 4 : PrakrutiSoakRawMaterial
Class 5 : PrakrutiSyrupExtraction
Class 6 : PrakrutiSyrupFiltration
Class 7 : PrakrutiSyrupAutoclave
Class 8 : PrakrutiAdditionPreservative
Class 9 : PrakrutiPreparationSyrup
Class 10 : PrakrutiOtherIngredientAddition
Class 11 : PrakrutiPhControlBufferAction
Class 12 : PrakrutiSolventName
Class 13 : PrakrutiFilling
Class 14 : PrakrutiCoding
Class 15 : PrakrutiPacking
Class 16: PrakrutiProductionBreakdownSyrup
Table 1 & Reference Id: prakruti_syrup_production 
Table 2 & Reference Id: prakruti_production_syrup_pulverization,pulverization_id,pulverization_production_syrup_id
Table 3 & Reference Id: prakruti_syrup_extract_solution ,extract_solution_id,extract_solution_syrup_id
Table 4 & Reference Id: prakruti_soak_raw_material,soak_raw_material_id,soak_raw_material_syrup_id
Table 5 & Reference Id: prakruti_syrup_extraction ,syrup_extraction_id,extraction_syrup_id
Table 6 & Reference Id: prakruti_syrup_filtration,syrup_filtration_id,filtration_syrup_id
Table 7 & Reference Id: prakruti_syrup_autoclave ,syrup_autoclave_id,autoclave_syrup_id
Table 8 & Reference Id: prakruti_addition_preservative,addition_preservative_id,addition_preservative_syrup_id
Table 9 & Reference Id: prakruti_preparation_syrup ,preparation_syrup_id,syrup_preparation_id
Table 10 & Reference Id: prakruti_other_ingredient_addition,prakruti_other_ingredient_addition,other_ingredient_addition_syrup_id
Table 11 & Reference Id: prakruti_ph_control_buffer_action ,prakruti_ph_control_buffer_action,ph_control_buffer_action_syrup_id
Table 12 & Reference Id: prakruti_solvent_name,prakruti_solvent_name,solvent_name_syrup_id
Table 13 & Reference Id: prakruti_filling ,prakruti_filling,filling_syrup_id
Table 14 & Reference Id: prakruti_coding,coding_id,coding_syrup_id
Table 15 & Reference Id: prakruti_packing ,packing_id,packing_syrup_id
Table 16 & Reference Id: prakruti_production_breakdown_syrup,breakdown_grid_id,breakdown_production_id

Updated By: Induja
Updated Date & Version: 20170823 ,0.1
'''





# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
import openerp
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize, image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
from openerp import tools
from datetime import timedelta
from openerp.osv import osv,fields
from openerp import models, fields, api, _
from openerp.tools.translate import _
import sys, os, urllib2, urlparse
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import email, re
from datetime import datetime
from datetime import date, timedelta
from lxml import etree
import cgi
import logging
import lxml.html
import lxml.html.clean as clean
import openerp.pooler as pooler
import random
import re
import socket
import threading
import time
from openerp.tools import image_resize_image_big
from openerp.tools import amount_to_text
from openerp.tools.amount_to_text import amount_to_text_in 
from openerp.tools.amount_to_text import amount_to_text_in_without_word_rupees 

######################################################################################

class PrakrutiSyrupProduction(models.Model):
    _name='prakruti.syrup_production'
    _table ='prakruti_syrup_production'
    _description='Syrup Production'
    _order= 'id desc'
    _rec_name= 'subplant_id'    
    
    pulverization_production_syrup_id = fields.One2many('prakruti.production_syrup_pulverization','pulverization_id',string='Pulverization Grid')
    extract_solution_syrup_id= fields.One2many('prakruti.syrup_extract_solution','extract_solution_id',string='Extract Solution Grid') 
    soak_raw_material_syrup_id=fields.One2many('prakruti.soak_raw_material','soak_raw_material_id',string='Soak Raw Material Grid') 
    extraction_syrup_id=fields.One2many('prakruti.syrup_extraction','syrup_extraction_id',string='Extraction Grid') 
    filtration_syrup_id=fields.One2many('prakruti.syrup_filtration','syrup_filtration_id',string='Filtration Grid')
    autoclave_syrup_id=fields.One2many('prakruti.syrup_autoclave','syrup_autoclave_id',string='Autoclave Grid')
    addition_preservative_syrup_id=fields.One2many('prakruti.addition_preservative','addition_preservative_id',string='Addition Preservative Grid')
    syrup_preparation_id=fields.One2many('prakruti.preparation_syrup','preparation_syrup_id',string='Preparartion Syrup Grid')
    other_ingredient_addition_syrup_id=fields.One2many('prakruti.other_ingredient_addition','other_ingredient_addition_id',string='Other Ingredient Addition Grid')
    ph_control_buffer_action_syrup_id=fields.One2many('prakruti.ph_control_buffer_action','ph_control_buffer_action_id',string='Ph Control Buffer Action')
    solvent_name_syrup_id=fields.One2many('prakruti.solvent_name','solvent_name_id',string='Solvent Name')
    filling_syrup_id=fields.One2many('prakruti.filling','filling_id',string='Filling')
    coding_syrup_id=fields.One2many('prakruti.coding','coding_id',string='Coding')
    packing_syrup_id=fields.One2many('prakruti.packing','packing_id',string='Packing')
    breakdown_production_id = fields.One2many('prakruti.production_breakdown_syrup','breakdown_grid_id',string='Break Down Grid')    
    total_weight_before = fields.Float(string='Total Weight Before',compute= '_compute_total_weight_before',store=True,digits=(6,3))
    total_weight_after = fields.Float(string='Total  Weight After',compute= '_compute_total_weight_after',store=True,digits=(6,3))
    total_volume_before_pe = fields.Float(string='Total Volume Before',compute= '_compute_total_volume_before_pe',store=True,digits=(6,3))
    total_volume_after_pe = fields.Float(string='Total  Volume After',compute= '_compute_total_volume_after_pe',store=True,digits=(6,3))
    total_weight_before_ex = fields.Float(string='Total Weight Before',compute= '_compute_total_weight_before_ex',store=True,digits=(6,3))
    total_volume_before_ps = fields.Float(string='Total Volume Before',compute= '_compute_total_volume_before_ps',store=True,digits=(6,3))
    total_volume_after_ps = fields.Float(string='Total  Volume After',compute= '_compute_total_volume_after_ps',store=True,digits=(6,3))
    total_volume_before_vu = fields.Float(string='Total Volume Before',compute= '_compute_total_volume_before_vu',store=True,digits=(6,3))
    total_volume_after_vu = fields.Float(string='Total  Volume After',compute= '_compute_total_volume_after_vu',store=True,digits=(6,3))
    pulverisation=fields.Selection([('yes','Yes'),('no','No')], string="Pulverisation", default='yes',required="True")
    extract_solution = fields.Selection([('yes','Yes'),('no','No')], string="Extract Solution", default='yes',required="True")
    soak_raw_material =fields.Selection([('yes','Yes'),('no','No')], string="Soak Raw Material", default='yes',required="True")
    extraction_new=fields.Selection([('yes','Yes'),('no','No')], string="Extraction", default='yes',required="True")    
    autoclave = fields.Selection([('yes','Yes'),('no','No')], string="Autoclave", default='yes',required="True")
    addition_preservative = fields.Selection([('yes','Yes'),('no','No')], string="Addition of Preservative", default='yes',required="True")
    preparation_syrup = fields.Selection([('yes','Yes'),('no','No')], string="Syrup Preparation", default='yes',required="True")    
    ph_control_buffer = fields.Selection([('yes','Yes'),('no','No')], string="pH control buffer action ", default='yes',required="True")
    solvent_name= fields.Selection([('yes','Yes'),('no','No')], string="Solvent Name", default='yes',required="True")
    filling =  fields.Selection([('yes','Yes'),('no','No')], string="Filling", default='yes',required="True")
    coding =  fields.Selection([('yes','Yes'),('no','No')], string="Coding", default='yes',required="True")
    packing =  fields.Selection([('yes','Yes'),('no','No')], string="Packing", default='yes',required="True")
    other_ingredient_addition = fields.Selection([('yes','Yes'),('no','No')], string="Other Ingredient Addition",default='yes',required="True")
    filtration = fields.Selection([('yes','Yes'),('no','No')], string="Filtration", default='yes',required="True")
    batch_allocation_date=fields.Datetime(string='Batch Allocation Date', default=fields.Date.today)
    batch_end_date=fields.Datetime(string='Batch End Date')
    subplant_id = fields.Many2one('prakruti.sub_plant', string='Sub Plant', required=True)
    batch_id = fields.Many2one('prakruti.batch_master',string='Batch No',required=True)
    batch_size= fields.Float(string='Batch Size', required=True,digits=(6,3))
    standard_time=fields.Datetime(string='Standard Time')
    date= fields.Date(string = 'Date', default= fields.Date.today, required=True)    
    created_by =fields.Many2one('res.users','Created By')
    remarks = fields.Text(string='Remarks')
    production_name = fields.Selection([('syrup','Syrup')],string='Production Type',default='syrup')
    status = fields.Selection([('batch_alloted','Batch Alloted')],string="Status",readonly="True")
    bmr_no = fields.Char(string = 'BMR No')
    revise_status = fields.Selection([('revise_syrup','Revise Syrup'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    assay_line = fields.One2many('prakruti.syrup_rm_assay','production_syrup_id',string='RM Assay Grid')
    flag_display_product = fields.Integer(default=0)    
    flag_delete_product = fields.Integer(default=0)      
    
    #added by karan for print out on 20170911
    company_id=fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id,required="True")
    
    
    
    total_output_yeild = fields.Float(string='Total Output Quantity',digits=(6,3))
    available_qty = fields.Float(string='Available Qty',digits=(6,3))
    total_assay_output = fields.Float(string='Output Quantity',compute = '_compute_output_qty')
    
    
    @api.depends('assay_line.rm_assay_output')
    def _compute_output_qty(self):
        for val in self:
            total_output_yeild = total = available_qty = 0.0
            for line in val.assay_line:
                total += line.rm_assay_output
                val.update({
                    'total_output_yeild' : total,
                    'available_qty' : total
                    })
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')
        
    _defaults={
        'created_by': lambda s, cr, uid, c:uid,
        'revise_id': lambda s, cr, uid, c:uid,
        'company_id':_default_company,   
        }
     
    '''
    This Button helps for Revision
    '''
    @api.one
    @api.multi
    def revise_syrup(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ebsl_id = self.pool.get('prakruti.syrup_production').create(cr,uid, {
                'pulverisation':temp.pulverisation,
                'extract_solution':temp.extract_solution,
                'soak_raw_material':temp.soak_raw_material,
                'extraction_new':temp.extraction_new,
                'autoclave':temp.autoclave,
                'addition_preservative':temp.addition_preservative,
                'preparation_syrup':temp.preparation_syrup,
                'ph_control_buffer':temp.ph_control_buffer,
                'solvent_name':temp.solvent_name,
                'filling':temp.filling,
                'coding':temp.coding,
                'packing':temp.packing,
                'other_ingredient_addition':temp.other_ingredient_addition,
                'filtration':temp.filtration,
                'batch_allocation_date':temp.batch_allocation_date,
                'batch_end_date':temp.batch_end_date,
                'subplant_id':temp.subplant_id.id,
                'batch_id':temp.batch_id.id,
                'batch_size':temp.batch_size,
                'standard_time':temp.standard_time,
                'date':temp.date,
                'created_by':temp.created_by.id,
                'remarks':temp.remarks,
                'production_name':temp.production_name,
                'status':'',
                'bmr_no':temp.bmr_no,
                'total_output_yeild':temp.total_output_yeild,
                'available_qty':temp.available_qty,
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,                
                'revise_flag': 1
                })
            for item in temp.assay_line:
                production_syrup = self.pool.get('prakruti.syrup_rm_assay').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'rm_assay': item.rm_assay,
                    'rm_assay_output': item.rm_assay_output,
                    #'rm_assay_o': item.rm_assay_o,
                    #'rm_assay_output_o': item.rm_assay_output_o,
                    #'rm_assay_t': item.rm_assay_t,
                    #'rm_assay_output_t': item.rm_assay_output_t,
                    'production_syrup_id': ebsl_id
                    })
            for item in temp.pulverization_production_syrup_id:
                pulverization = self.pool.get('prakruti.production_syrup_pulverization').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'weight_before': item.weight_before,
                    'weight_after': item.weight_after,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'pulverization_id': ebsl_id
                    })
            for item in temp.extract_solution_syrup_id:
                extract_solution = self.pool.get('prakruti.syrup_extract_solution').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'name_of_extract': item.name_of_extract,
                    'name_of_solvent': item.name_of_solvent,
                    'solvent_name': item.solvent_name,
                    'machine_id': item.machine_id.id,
                    'qty_of_extract_charged': item.qty_of_extract_charged,
                    'qty_of_solvent_charged': item.qty_of_solvent_charged,
                    'qty_of_solvent': item.qty_of_solvent,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'volume_before': item.volume_before,
                    'volume_after': item.volume_after,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'extract_solution_id': ebsl_id
                    })
            for item in temp.soak_raw_material_syrup_id:
                soak_raw_material = self.pool.get('prakruti.soak_raw_material').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'name_of_solvent': item.name_of_solvent,
                    'solvent_name': item.solvent_name,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'qty_charged': item.qty_charged,
                    'solvent_charged': item.solvent_charged,
                    'charged_solvent': item.charged_solvent,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'soak_raw_material_id': ebsl_id
                    })
            for item in temp.extraction_syrup_id:
                syrup_extraction = self.pool.get('prakruti.syrup_extraction').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'weight_before': item.weight_before,
                    'solvent_charged': item.solvent_charged,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'syrup_extraction_id': ebsl_id
                    })
            for item in temp.filtration_syrup_id:
                syrup_filtration = self.pool.get('prakruti.syrup_filtration').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'volume_collected': item.volume_collected,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'syrup_filtration_id': ebsl_id
                    })
            for item in temp.autoclave_syrup_id:
                syrup_autoclave = self.pool.get('prakruti.syrup_autoclave').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'syrup_autoclave_id': ebsl_id
                    })
            for item in temp.addition_preservative_syrup_id:
                addition_preservative = self.pool.get('prakruti.addition_preservative').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'quantity': item.quantity,
                    'name_of_preservative': item.name_of_preservative,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'addition_preservative_id': ebsl_id
                    })
            for item in temp.syrup_preparation_id:
                preparation_syrup = self.pool.get('prakruti.preparation_syrup').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'quantity_of_sugar': item.quantity_of_sugar,
                    'volume_before': item.volume_before,
                    'volume_after': item.volume_after,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'preparation_syrup_id': ebsl_id
                    })
            for item in temp.other_ingredient_addition_syrup_id:
                other_ingredient_addition = self.pool.get('prakruti.other_ingredient_addition').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'ingredient_name': item.ingredient_name,
                    'quantity': item.quantity,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'other_ingredient_addition_id': ebsl_id
                    })
            for item in temp.ph_control_buffer_action_syrup_id:
                ph_control_buffer_action = self.pool.get('prakruti.ph_control_buffer_action').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'ingredient_name': item.ingredient_name.id,
                    'quantity': item.quantity,
                    'ph_before': item.ph_before,
                    'ph_after': item.ph_after,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'ph_control_buffer_action_id': ebsl_id
                    })
            for item in temp.solvent_name_syrup_id:
                solvent_name = self.pool.get('prakruti.solvent_name').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'name_of_solvent': item.name_of_solvent,
                    'machine_id': item.machine_id.id,
                    'volume_added': item.volume_added,
                    'volume_before': item.volume_before,
                    'volume_after': item.volume_after,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'solvent_name_id': ebsl_id
                    })
            for item in temp.filling_syrup_id:
                filling = self.pool.get('prakruti.filling').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'no_of_bottles_filled': item.no_of_bottles_filled,
                    'no_of_bottles_rejected': item.no_of_bottles_rejected,
                    'total_bottles_accepted': item.total_bottles_accepted,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'filling_id': ebsl_id
                    })
            for item in temp.coding_syrup_id:
                coding = self.pool.get('prakruti.coding').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'no_of_units_code': item.no_of_units_code,
                    'no_of_units_rejected': item.no_of_units_rejected,
                    'total_units_accepted': item.total_units_accepted,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'coding_id': ebsl_id
                    })
            for item in temp.packing_syrup_id:
                packing = self.pool.get('prakruti.packing').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'packing_style': item.packing_style,
                    'no_of_packing': item.no_of_packing,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'packing_id': ebsl_id
                    })
            for item in temp.breakdown_production_id:
                breakdown = self.pool.get('prakruti.production_breakdown_syrup').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'machine_id': item.machine_id.id,
                    'date': item.date,
                    'breakdown_id': item.breakdown_id.id,
                    'running_hours': item.running_hours,
                    'breakdown_hours': item.breakdown_hours,
                    'remarks': item.remarks,
                    'checked_by': item.checked_by,
                    'breakdown_grid_id': ebsl_id
                    })
            cr.execute('''UPDATE prakruti_syrup_production SET revise_status = 'revise_syrup',is_revise = 'True' WHERE id = %s''',((temp.id),))
        return {}  
    
    '''
    After doing changes in table 2 click this to visible Revise button and to update the changes in the screen
    '''
    
    @api.one
    @api.multi
    def revise_done(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context' 
        revise_done_by = False
        error_message = ''
        for temp in self:
            if temp.revise_remarks:
                if temp.revise_id:  
                    cr.execute('''SELECT revise_syrup_production  (%s,%s,%s)''',((temp.id),(temp.batch_id.id),(temp.subplant_id.subplant_id.id),))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete, Since the Batch is Alloted'))
        return super(PrakrutiSyrupProduction, self).unlink()    
    
    
    '''
    While selecting batch no it will extract data from Batch master Screen 
    '''     
    def onchange_batch_id(self, cr, uid, ids, batch_id, context=None):
        process_type = self.pool.get('prakruti.batch_master').browse(cr, uid, batch_id, context=context)
        result = {
            'batch_size': process_type.batch_capacity,
            'batch_allocation_date': process_type.batch_allocation_date,
            'batch_end_date': process_type.batch_end_date,
            'pulverisation': process_type.pulverisation,
            'extraction_new': process_type.extraction_new,
            'extract_solution':process_type.extract_solution,
            'soak_raw_material':process_type.soak_raw_material,
            'filtration':process_type.filtration,
            'autoclave':process_type.autoclave,
            'addition_preservative':process_type.addition_preservative,
            'preparation_syrup':process_type.preparation_syrup,
            'ph_control_buffer':process_type.ph_control_buffer,
            'solvent_name':process_type.solvent_name,
            'filling':process_type.filling,
            'coding':process_type.coding,
            'packing':process_type.packing,
            'other_ingredient_addition':process_type.other_ingredient_addition,
            'bmr_no': process_type.bmr_no
            }
        return {'value': result}
    '''
    Allocating batch No
    ''' 
    @api.one
    @api.multi
    def allocate_batch_no(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}   
            cr.execute("UPDATE prakruti_batch_master AS b SET batch_allocated_by = 'syrup',batch_allocated_flag = 1 FROM(SELECT batch_id FROM prakruti_syrup_production WHERE  id= %s ) AS a WHERE a.batch_id = b.id",((temp.id),))
            cr.execute("UPDATE prakruti_syrup_production SET status = 'batch_alloted' WHERE id = %s",((temp.id),))
        return {}
    '''
    calculation for Total Weight Before
    '''
    @api.depends('pulverization_production_syrup_id.weight_before')
    def _compute_total_weight_before(self):
        for order in self:
            weight_before = 0.0
            for line in order.pulverization_production_syrup_id:
                weight_before += line.weight_before 
                order.update({
                        'total_weight_before': weight_before
                        })
    '''
    calculation for Total Weight After
    '''
    @api.depends('pulverization_production_syrup_id.weight_after')
    def _compute_total_weight_after(self):
        for order in self:
            weight_after = 0.0
            for line in order.pulverization_production_syrup_id:
                weight_after += line.weight_after 
                order.update({
                        'total_weight_after': weight_after
                        })
    '''
    calculation for Total Volume before Extract Solution
    '''
    @api.depends('extract_solution_syrup_id.volume_before')
    def _compute_total_volume_before_pe(self):
        for order in self:
            volume_before_pe = 0.0
            for line in order.extract_solution_syrup_id:
                volume_before_pe += line.volume_before 
                order.update({
                        'total_volume_before_pe': volume_before_pe
                        })
    '''
    calculation for Total Volume After Extract Solution
    '''
    @api.depends('extract_solution_syrup_id.volume_after')
    def _compute_total_volume_after_pe(self):
        for order in self:
            volume_after_pe = 0.0
            for line in order.extract_solution_syrup_id:
                volume_after_pe += line.volume_after 
                order.update({
                        'total_volume_after_pe': volume_after_pe
                        })
    '''
    calculation for Total Weight Before Extraction Syrup
    '''
    @api.depends('extraction_syrup_id.weight_before')
    def _compute_total_weight_before_ex(self):
        for order in self:
            weight_before_ex = 0.0
            for line in order.extraction_syrup_id:
                weight_before_ex += line.weight_before 
                order.update({
                        'total_weight_before_ex': weight_before_ex
                        })
    
    '''
    calculation for Total Volume before Syruo prepration
    '''
    @api.depends('syrup_preparation_id.volume_before')
    def _compute_total_volume_before_ps(self):
        for order in self:
            volume_before_ps = 0.0
            for line in order.syrup_preparation_id:
                volume_before_ps += line.volume_before 
                order.update({
                        'total_volume_before_ps': volume_before_ps
                        })
    
    '''
    calculation for Total Volume After Syruo prepration
    '''
    @api.depends('syrup_preparation_id.volume_after')
    def _compute_total_volume_after_ps(self):
        for order in self:
            volume_after_ps = 0.0
            for line in order.syrup_preparation_id:
                volume_after_ps += line.volume_after 
                order.update({
                        'total_volume_after_ps': volume_after_ps
                        })
    '''
    calculation for Total Volume Before Solvent name
    '''
    @api.depends('solvent_name_syrup_id.volume_before')
    def _compute_total_volume_before_vu(self):
        for order in self:
            volume_before_vu = 0.0
            for line in order.solvent_name_syrup_id:
                volume_before_vu += line.volume_before 
                order.update({
                        'total_volume_before_vu': volume_before_vu
                        })
    
    '''
    calculation for Total Volume After solvent name
    '''
    @api.depends('solvent_name_syrup_id.volume_after')
    def _compute_total_volume_after_vu(self):
        for order in self:
            volume_after_vu = 0.0
            for line in order.solvent_name_syrup_id:
                volume_after_vu += line.volume_after 
                order.update({
                        'total_volume_after_vu': volume_after_vu
                        })
   
    
    
    #_sql_constraints = [        
        #('production_uniq_with_batch_date','unique(batch_id,date)', 'This production Batch is already Entered for this Date. Please check and retry !'),       
        #('production_uniq_with_batch_subplant_date','unique(subplant_id,batch_id,date)', 'This batch is already in Use. Please check and retry !'),   
        #('production_uniq_with_batch_subplant','unique(subplant_id,batch_id)', 'This Subplant is already allocated to this Batch. Please check and retry !')
        #]
        
    # Added by induja on 20170905 for reports
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
            cr.execute('''  SELECT 
                                    prakruti_syrup_line.product_id,
                                    prakruti_syrup.batch_no 
                            FROM 	
                                    prakruti_syrup_line INNER JOIN 
                                    prakruti_syrup ON 
                                    prakruti_syrup_line.main_id=prakruti_syrup.id 
                            WHERE 
                                    prakruti_syrup.batch_no=%s
	''',((temp.batch_id.id),))
            for line in cr.dictfetchall():
                product_id = line['product_id']
                grid_line_entry = self.pool.get('prakruti.syrup_rm_assay').create(cr,uid,{
                    'product_id':product_id,
                    'production_syrup_id':temp.id
                    })
            cr.execute('UPDATE prakruti_syrup_production SET flag_display_product = 1 WHERE prakruti_syrup_production.id = %s',((temp.id),))
            cr.execute("UPDATE  prakruti_syrup_production SET flag_delete_product = 0 WHERE prakruti_syrup_production.id = %s",((temp.id),))
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
            cr.execute("DELETE FROM prakruti_syrup_rm_assay WHERE prakruti_syrup_rm_assay.production_syrup_id = %s", ((temp.id),))
            cr.execute("UPDATE  prakruti_syrup_production SET flag_delete_product = 1 WHERE prakruti_syrup_production.id = %s",((temp.id),))
            cr.execute('UPDATE prakruti_syrup_production SET flag_display_product = 0 WHERE prakruti_syrup_production.id = %s',((temp.id),))
        return {} 
    
class PrakrutiProductionSyrupPulverization(models.Model):
    _name ='prakruti.production_syrup_pulverization'
    _table = 'prakruti_production_syrup_pulverization'
    _description = 'Syrup Pulverisation'
    
    pulverization_id = fields.Many2one('prakruti.syrup_production') 
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')    
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    weight_before=fields.Float(string='Weight Before',digits=(6,3))
    weight_after=fields.Float(string='Weight After',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_weight_before(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.weight_before <= 0:
                #return False
            #return True
        
    #def _check_weight_after(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.weight_after <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_weight_before, 'Weight before cannot be negative or zero !', ['weight_before']),
       #(_check_weight_after, 'Weight after cannot be negative or zero !', ['weight_after']),
        #]
     
    
class PrakrutiSyrupExtractSolution(models.Model):
    _name ='prakruti.syrup_extract_solution'
    _table = 'prakruti_syrup_extract_solution'
    _description = 'Syrup Extract solution'
         
    extract_solution_id = fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    name_of_extract = fields.Char( string='Name Of Extract')
    name_of_solvent = fields.Char( string='Name Of Solvent 1')
    solvent_name = fields.Char( string='Name Of Solvent 2')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    qty_of_extract_charged=fields.Float(string='Qty of Extract Charged',digits=(6,3))
    qty_of_solvent_charged=fields.Float(string='Qty of Solvent Charged 1',digits=(6,3))
    qty_of_solvent=fields.Float(string='Qty of Solvent Charged 2',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    volume_before=fields.Float(string='Volume Before',digits=(6,3))
    volume_after=fields.Float(string='Volume After',digits=(6,3))
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('volume_before')
    #def _check_volume_before(self):
        #if self.volume_before < 0:
            #raise ValidationError(
                #"Volume Before can't be Negative !")  
        
    #@api.one
    #@api.constrains('volume_after')
    #def _check_volume_after(self):
        #if self.volume_after < 0:
            #raise ValidationError(
                #"Volume After can't be Negative !")  
        
    #@api.one
    #@api.constrains('qty_of_solvent_charged')
    #def _check_qty_of_solvent_charged(self):
        #if self.qty_of_solvent_charged <= 0:
            #raise ValidationError(
                #"Qty of Solvent Charged 1 can't be Negative !")  
        
    #@api.one
    #@api.constrains('qty_of_solvent')
    #def _check_qty_of_solvent(self):
        #if self.qty_of_solvent <= 0:
            #raise ValidationError(
                #"Qty of Solvent Charged 2 can't be Negative !")  
    
    #def _check_extract_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_of_extract_charged <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_extract_charged, 'Extract Charged cannot be negative or zero !', ['qty_of_extract_charged']),
        #]
    
class PrakrutiSoakRawMaterial(models.Model):
    _name ='prakruti.soak_raw_material'
    _table = 'prakruti_soak_raw_material'
    _description = 'Syrup Soak raw material'
     
    soak_raw_material_id = fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    name_of_solvent = fields.Char( string='Name Of Solvent 1')
    solvent_name = fields.Char( string='Name Of Solvent 2')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    qty_charged=fields.Float(string='Qty  Charged',digits=(6,3))
    solvent_charged=fields.Float(string='Solvent Charged 1',digits=(6,3))
    charged_solvent=fields.Float(string='Solvent Charged 2',digits=(6,3))
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('solvent_charged')
    #def _check_solvent_charged(self):
        #if self.solvent_charged <= 0:
            #raise ValidationError(
                #"Solvent Charged 1 can't be Negative or 0!")  
        
    #@api.one
    #@api.constrains('charged_solvent')
    #def _check_charged_solvent(self):
        #if self.charged_solvent <= 0:
            #raise ValidationError(
                #"Solvent Charged 2 can't be Negative or 0!")  
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_qty_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_charged <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_qty_charged, 'Qty Charged cannot be negative or zero !', ['qty_charged']),
        #]
     
    
class PrakrutiSyrupExtraction(models.Model):
    _name ='prakruti.syrup_extraction'
    _table = 'prakruti_syrup_extraction'
    _description = 'Syrup Extraction '
    
    syrup_extraction_id=fields.Many2one('prakruti.syrup_production') 
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    weight_before=fields.Float(string='Weight Before',digits=(6,3))
    solvent_charged=fields.Float(string='Solvent Charged',digits=(6,3))
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks') 
        
    #@api.one
    #@api.constrains('solvent_charged')
    #def _check_solvent_charged(self):
        #if self.solvent_charged < 0:
            #raise ValidationError(
                #"Solvent Charged can't be Negative !")  
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_weight_before(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.weight_before <= 0:
                #return False
            #return True
        
    #_constraints = [
       #(_check_weight_before, 'Weight cannot be negative or zero !', ['weight_before'])
        #]
     
     
    
class PrakrutiSyrupFiltration(models.Model):
    _name ='prakruti.syrup_filtration'
    _table = 'prakruti_syrup_filtration'
    _description = 'Syrup Filtration '
    
    syrup_filtration_id=fields.Many2one('prakruti.syrup_production') 
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    volume_collected=fields.Float(string='Volume Collected',digits=(6,3))
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")

class PrakrutiSyrupAutoclave(models.Model):
    _name ='prakruti.syrup_autoclave'
    _table = 'prakruti_syrup_autoclave'
    _description = 'Syrup Autoclave '
    
    syrup_autoclave_id=fields.Many2one('prakruti.syrup_production') 
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks') 
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
class PrakrutiAdditionPreservative(models.Model):
    _name ='prakruti.addition_preservative'
    _table = 'prakruti_addition_preservative'
    _description = 'Syrup Addition Preservative '
    
    addition_preservative_id=fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True") 
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    quantity=fields.Char( string='Quantity')
    name_of_preservative=fields.Char( string='Name of Preservative')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks') 
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_quantity(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.quantity <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_quantity, 'Extract Charged cannot be negative or zero !', ['quantity']),
        #]
     
     

class PrakrutiPreparationSyrup(models.Model):
    _name ='prakruti.preparation_syrup'
    _table = 'prakruti_preparation_syrup'
    _description = 'Syrup Preparation '
    
    preparation_syrup_id=fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    quantity_of_sugar=fields.Char( string='Qty of Sugar')
    volume_before=fields.Float(string='Volume Before',digits=(6,3))
    volume_after=fields.Float(string='Volume After',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks') 
        
    #@api.one
    #@api.constrains('volume_after')
    #def _check_volume_after(self):
        #if self.volume_after <= 0:
            #raise ValidationError(
                #"Volume After can't be Negative or 0 !")  
        
    #@api.one
    #@api.constrains('volume_before')
    #def _check_volume_before(self):
        #if self.volume_before < 0:
            #raise ValidationError(
                #"Volume Before can't be Negative or 0!")  
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_quantity_of_sugar(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.quantity_of_sugar <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_quantity_of_sugar, 'Please enter Qty of Sugar Required !', ['quantity_of_sugar']),
        #]
     
     

class PrakrutiOtherIngredientAddition(models.Model):
    _name ='prakruti.other_ingredient_addition'
    _table = 'prakruti_other_ingredient_addition'
    _description = 'Syrup Other Ingredient Addition '
    
    other_ingredient_addition_id=fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    ingredient_name=fields.Many2one('product.product', string='Ingredient Name')
    quantity=fields.Char( string='Quantity')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks') 
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_quantity(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.quantity <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_quantity, 'Extract Charged cannot be negative or zero !', ['quantity']),
        #]
     
     

class PrakrutiPhControlBufferAction(models.Model):
    _name ='prakruti.ph_control_buffer_action'
    _table = 'prakruti_ph_control_buffer_action'
    _description = 'Syrup Ph Buffer Action '
    
    ph_control_buffer_action_id=fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    ingredient_name=fields.Many2one('product.product', string='Ingredient Name')
    quantity=fields.Char( string='Quantity')
    ph_before=fields.Float(string='PH Before',digits=(6,3))
    ph_after=fields.Float(string='PH After',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks') 
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
    #def _check_quantity(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.quantity <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_quantity, 'Extract Charged cannot be negative or zero !', ['quantity']),
        #]
     
     
    
class PrakrutiSolventName(models.Model):
    _name ='prakruti.solvent_name'
    _table = 'prakruti_solvent_name'
    _description = 'Syrup Solvent Name '
    
    solvent_name_id=fields.Many2one('prakruti.syrup_production') 
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    name_of_solvent = fields.Char( string='Name Of Solvent')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    volume_added=fields.Char( string='Volume Added')
    volume_before=fields.Float(string='Volume Before',digits=(6,3))
    volume_after=fields.Float(string='Volume After',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('volume_added')
    #def _check_volume_added(self):
        #if self.volume_added <= 0:
            #raise ValidationError(
                #"Volume Added can't be Negative or 0 !")  
        
    #@api.one
    #@api.constrains('volume_before')
    #def _check_volume_before(self):
        #if self.volume_before <= 0:
            #raise ValidationError(
                #"Volume Before can't be Negative or 0 !")  
        
    #@api.one
    #@api.constrains('volume_after')
    #def _check_volume_after(self):
        #if self.volume_after <= 0:
            #raise ValidationError(
                #"Volume After can't be Negative or 0 !")  
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
class PrakrutiFilling(models.Model):
    _name ='prakruti.filling'
    _table = 'prakruti_filling'
    _description = 'Syrup Filling '
    
    filling_id=fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')    
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    no_of_bottles_filled=fields.Char( string='No of Bottles Filled')
    no_of_bottles_rejected=fields.Float(string='No of Bottles Rejected',digits=(6,3))
    total_bottles_accepted=fields.Float(string='Total Bottles Accepted',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('no_of_bottles_filled')
    #def _check_no_of_bottles_filled(self):
        #if self.no_of_bottles_filled < 0:
            #raise ValidationError(
                #"No of Bottles Filled can't be Negative  !")  
        
    #@api.one
    #@api.constrains('no_of_bottles_rejected')
    #def _check_no_of_bottles_rejected(self):
        #if self.no_of_bottles_rejected < 0:
            #raise ValidationError(
                #"No of Bottles Rejected can't be Negative !")  
        
    #@api.one
    #@api.constrains('total_bottles_accepted')
    #def _check_total_bottles_accepted(self):
        #if self.total_bottles_accepted < 0:
            #raise ValidationError(
                #"Total Bottles Accepted can't be Negative  !")   
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")

class PrakrutiCoding(models.Model):
    _name ='prakruti.coding'
    _table = 'prakruti_coding'
    _description = 'Syrup Coding '
    
    coding_id=fields.Many2one('prakruti.syrup_production') 
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    no_of_units_code=fields.Char( string='No of Units Code')
    no_of_units_rejected=fields.Float(string='No of Units Rejected',digits=(6,3))
    total_units_accepted=fields.Float(string='Total Units Accepted',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('no_of_units_rejected')
    #def _check_no_of_units_rejected(self):
        #if self.no_of_units_rejected < 0:
            #raise ValidationError(
                #"No of Units Rejected can't be Negative  !")  
        
    #@api.one
    #@api.constrains('total_units_accepted')
    #def _check_total_units_accepted(self):
        #if self.total_units_accepted < 0:
            #raise ValidationError(
                #"Total Units Accepted can't be Negative  !")  
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    
class PrakrutiPacking(models.Model):
    _name ='prakruti.packing'
    _table = 'prakruti_packing'
    _description = 'Syrup Packing '
    
    packing_id=fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    std_time = fields.Char( string='Standard Time')
    packing_style=fields.Text( string='Packing Style')
    no_of_packing=fields.Float( string='No of Packing',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
     
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #"Start date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #"End Date can't be less than start date!")
    #def _check_no_of_packing(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.no_of_packing <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_no_of_packing, 'No of Packing cannot be negative or zero !', ['no_of_packing']),
        #]
    
    
class PrakrutiProductionBreakdownSyrup(models.Model):
    _name = 'prakruti.production_breakdown_syrup'
    _table = 'prakruti_production_breakdown_syrup'
    _description = 'Production Breakdown Syrup  '
    
    breakdown_grid_id = fields.Many2one('prakruti.syrup_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    machine_id=fields.Many2one('prakruti.machine',string='Machine')
    date=fields.Date(string='Date', default=fields.Date.today)
    breakdown_id=fields.Many2one('prakruti.breakdown_item',string='Break Down Item')
    running_hours=fields.Char(string='Running Hours')
    breakdown_hours=fields.Char(string='Break Down Hours')
    remarks=fields.Text(string='Remarks')
    checked_by = fields.Char(string='Checked By')
       
class PrakrutiProductionSyrupRMAssay(models.Model):
    _name ='prakruti.syrup_rm_assay'
    _table = 'prakruti_syrup_rm_assay'
    _description = 'Production Syrup RM Assay'
    
    production_syrup_id = fields.Many2one('prakruti.syrup_production')
    product_id = fields.Many2one('product.product', string='Product Name')
    rm_assay = fields.Float(string="RM Assay%" , digits=(6,3))
    rm_assay_output = fields.Float(string="Output Quantity" , digits=(6,3)) 
    #rm_assay_o = fields.Float(string="RM Assay1%" , digits=(6,3))
    #rm_assay_output_o = fields.Float(string="RM Assay Output1" , digits=(6,3))
    #rm_assay_t = fields.Float(string="RM Assay2%" , digits=(6,3))
    #rm_assay_output_t = fields.Float(string="RM Assay Output2" , digits=(6,3))   