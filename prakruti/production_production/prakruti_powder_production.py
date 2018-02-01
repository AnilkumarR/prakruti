'''
Company : EBSL
Author: Induja
Module: Powder Production
Class 1: PrakrutiPowderProduction
Class 2: PrakrutiPowderProductionSeiving
Class 3 : PrakrutiPowderProductionBinder
Class 4 : PrakrutiPowderProductionGranulation
Class 5 : PrakrutiPowderProductionSemiDrying
Class 6 : PrakrutiPowderProductionFinalDrying
Class 7 : PrakrutiPowderProductionMilling
Class 8 : PrakrutiPowderProductionAPIAddition
Class 9 : PrakrutiPowderProductionBlending
Class 10 : PrakrutiPowderProductionCompression
Class 11 : PrakrutiPowderProductionCoatingPreparation
Class 12 : PrakrutiPowderProductionCoating
Class 13 : PrakrutiPowderProductionPowderInspection
Class 15 : PrakrutiPowderProductionMetalDetection
Class 16: PrakrutiPowderProductionBreakdown
Class 17 : PrakrutiPowderProductionPacking
Table 1 & Reference Id: prakruti_powder_production 
Table 2 & Reference Id: prakruti_powder_production_sieving,sieving_id,powder_sieving_id
Table 3 & Reference Id: prakruti_powder_production_binder ,binder_id,powder_binder_id
Table 4 & Reference Id: prakruti_powder_production_granulation ,granulation_id,powder_granulation_id
Table 5 & Reference Id: prakruti_powder_production_semi_drying,semi_drying_id,powder_semi_drying_id
Table 6 & Reference Id: prakruti_powder_production_final_drying ,final_drying_id,powder_final_drying_id
Table 7 & Reference Id: prakruti_powder_production_milling,milling_id,powder_milling_id
Table 8 & Reference Id: prakruti_powder_production_api_addition ,api_addition_id,powder_api_addition_id
Table 9 & Reference Id: prakruti_powder_production_blending,blending_id,powder_blending_id
Table 10 & Reference Id: prakruti_powder_production_compression ,compression_id,powder_compression_id   
Table 11 & Reference Id: prakruti_powder_production_coating_preparation,coating_preparation_id,powder_coating_preparation_id
Table 12 & Reference Id: prakruti_powder_production_coating ,coating_id,powder_coating_id
Table 13 & Reference Id: prakruti_powder_production_inspection,inspection_id,powder_inspection_id
Table 14 & Reference Id: prakruti_powder_production_metal_detection,metal_detection_id,powder_metal_inspection_id
Table 15 & Reference ID : prakruti_powder_production_packing,packing_id,powder_packing_id
Table 16 & Reference id : prakruti_production_powder_breakdown,breakdown_grid_id,breakdown_production_id
Updated By: Induja
Updated Date & Version: 20170828 ,0.1
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


class PrakrutiPowderProduction(models.Model):
    _name='prakruti.powder_production'
    _table ='prakruti_powder_production'
    _description='Formulation Production'
    _order= 'id desc'
    _rec_name= 'subplant_id'
    
    
    powder_sieving_id = fields.One2many('prakruti.powder_production_sieving','sieving_id',string='Sieving Grid')
    powder_binder_id = fields.One2many('prakruti.powder_production_binder','binder_id',string='Binder Grid')
    powder_granulation_id = fields.One2many('prakruti.powder_production_granulation','granulation_id',string='Granulation Grid')
    powder_semi_drying_id = fields.One2many('prakruti.powder_production_semi_drying','semi_drying_id',string='Semi Drying Grid')
    powder_final_drying_id = fields.One2many('prakruti.powder_production_final_drying','final_drying_id',string='Final Drying Grid')
    powder_milling_id = fields.One2many('prakruti.powder_production_milling','milling_id',string='Milling Grid')
    powder_api_addition_id = fields.One2many('prakruti.powder_production_api_addition','api_addition_id',string='Addition Grid')
    powder_blending_id = fields.One2many('prakruti.powder_production_blending','blending_id',string='Blending Grid')
    powder_compression_id = fields.One2many('prakruti.powder_production_compression','compression_id',string='Compression Grid')
    powder_coating_preparation_id = fields.One2many('prakruti.powder_production_coating_preparation','coating_preparation_id',string='Coating Preparation Grid')
    powder_coating_id = fields.One2many('prakruti.powder_production_coating','coating_id',string='Coating Grid')
    powder_inspection_id = fields.One2many('prakruti.powder_production_inspection','inspection_id',string='Inspection Grid')
    powder_metal_inspection_id = fields.One2many('prakruti.powder_production_metal_detection','metal_detection_id',string='Metal Detection Grid')
    powder_packing_id = fields.One2many('prakruti.powder_production_packing','packing_id',string='Packing Grid')
    breakdown_production_id = fields.One2many('prakruti.production_powder_breakdown','breakdown_grid_id',string='Break Down Grid')    
    #total_weight_before_si = fields.Float(string='Total Weight Before',compute= '_compute_total_weight_before_si',store=True,digits=(6,3))#i
    #total_weight_after_si = fields.Float(string='Total  Weight After',compute= '_compute_total_weight_after_si',store=True,digits=(6,3))#i
    total_weight_before_mi = fields.Float(string='Total Weight Before',compute= '_compute_total_weight_before_mi',store=True,digits=(6,3))#i
    total_weight_after_mi = fields.Float(string='Total  Weight After',compute= '_compute_total_weight_after_mi',store=True,digits=(6,3))#i
    total_input_qty_pc = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty_pc',store=True,digits=(6,3))#i
    total_output_qty_pc = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty_pc',store=True,digits=(6,3))#i
    total_input_qty_c = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty_c',store=True,digits=(6,3))#i
    total_output_qty_c = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty_c',store=True,digits=(6,3))#i     
    sieving=fields.Selection([('yes','Yes'),('no','No')], string="Sieving", default='yes',required="True")
    preparation_of_binder= fields.Selection([('yes','Yes'),('no','No')], string="Preparation of Binder", default='yes',required="True")
    granulation = fields.Selection([('yes','Yes'),('no','No')], string="Granulation", default='yes',required="True")
    semi_drying = fields.Selection([('yes','Yes'),('no','No')], string="Semi Drying", default='yes',required="True")
    final_drying = fields.Selection([('yes','Yes'),('no','No')], string="Final Drying", default='yes',required="True")
    milling=fields.Selection([('yes','Yes'),('no','No')], string="Milling", default='yes',required="True")
    api_addition=fields.Selection([('yes','Yes'),('no','No')], string="API Addition", default='yes',required="True")
    blending=fields.Selection([('yes','Yes'),('no','No')], string="Blending", default='yes',required="True")
    compression = fields.Selection([('yes','Yes'),('no','No')], string="Compression\Capsule Filling", default='yes',required="True")
    tablet_coating = fields.Selection([('yes','Yes'),('no','No')], string="Powder Coating Preparation", default='yes',required="True")
    coating = fields.Selection([('yes','Yes'),('no','No')], string="Coating", default='yes',required="True")
    inspection =fields.Selection([('yes','Yes'),('no','No')], string="Inspection Details", default='yes',required="True")
    metal_inspection=fields.Selection([('yes','Yes'),('no','No')], string="Metal Inspection", default='yes',required="True")
    packing =  fields.Selection([('yes','Yes'),('no','No')], string="Packing", default='yes',required="True")
    batch_allocation_date=fields.Datetime(string='Batch Allocation Date', default=fields.Date.today)
    batch_end_date=fields.Datetime(string='Batch End Date')
    subplant_id = fields.Many2one('prakruti.sub_plant', string='Sub Plant', required=True)
    batch_id = fields.Many2one('prakruti.batch_master',string='Batch No',required=True)
    batch_size= fields.Float(string='Batch Size', required=True,digits=(6,3))
    date= fields.Date(string = 'Date', default= fields.Date.today, required=True)
    created_by =fields.Many2one('res.users','Created By')
    total_input_qty = fields.Float(string='Total Input Qty',digits=(6,3))#i
    total_output_qty = fields.Float(string='Total Output Qty',digits=(6,3))#i
    remarks = fields.Text(string='Remarks')
    production_name = fields.Selection([('formulation','Formulation')],string='Production Type',default='formulation')    
    status = fields.Selection([('batch_alloted','Batch Alloted')],string="Status",readonly="True")
    total_time_c = fields.Datetime(string='Total Time')
    bmr_no = fields.Char(string = 'BMR No')
    revise_status = fields.Selection([('revise_powder','Revise Powder'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    assay_line = fields.One2many('prakruti.powder_rm_assay','production_powder_id',string='RM Assay Grid')
    addition_of_ingredients_line=fields.One2many('prakruti.powder_production_addition_of_ingredients','addition_of_ingredients_id',string='Addition Of Ingredients Grid')
    extract_solution_line = fields.One2many('prakruti.lotion_extract_solution','extract_solution_id',string='Extract  Solution Grid')    
    addition_of_solution_line = fields.One2many('prakruti.lotion_addition_of_solution','addition_of_solution_id',string='Addition Of Solution Grid')     
    other_ingredient_addition_line = fields.One2many('prakruti.lotion_other_ingredient_addition','other_ingredient_addition_id',string='Other Ingredient Addition Grid')     
    volume_make_up_line = fields.One2many('prakruti.lotion_volume_make_up','volume_make_up_id',string='Volume Make Up Grid')     
    filling_line = fields.One2many('prakruti.lotion_filling','filling_id',string='Filling Grid') 
    extract_solution_lotion = fields.Selection([('yes','Yes'),('no','No')], string="Extract Solution", default='yes',required="True")
    addition_of_solution = fields.Selection([('yes','Yes'),('no','No')], string="Addition Of Solution", default='yes',required="True")
    other_ingredient_addition_lotion = fields.Selection([('yes','Yes'),('no','No')], string="Other Ingredient Addition", default='yes',required="True")
    volume_make_up = fields.Selection([('yes','Yes'),('no','No')], string="Volume Make Up", default='yes',required="True")
    filling_lotion = fields.Selection([('yes','Yes'),('no','No')], string="Filling", default='yes',required="True")   
    flag_display_product = fields.Integer(default=0)    
    flag_delete_product = fields.Integer(default=0)      
    
    #added by karan for print out on 20170911
    company_id=fields.Many2one('res.company','Company')
    
    formulation_type=fields.Selection([('powder','Powder'),('lotion','Lotion')],string='Formulation Type')
    
    
    
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
    def revise_powder(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ebsl_id = self.pool.get('prakruti.powder_production').create(cr,uid, {
                'sieving':temp.sieving,
                'preparation_of_binder':temp.preparation_of_binder,
                'granulation':temp.granulation,
                'semi_drying':temp.semi_drying,
                'final_drying':temp.final_drying,
                'milling':temp.milling,
                'api_addition':temp.api_addition,
                'blending':temp.blending,
                'compression':temp.compression,
                'tablet_coating':temp.tablet_coating,
                'coating':temp.coating,
                'inspection':temp.inspection,
                'metal_inspection':temp.metal_inspection,
                'packing':temp.packing,
                'batch_allocation_date':temp.batch_allocation_date,
                'batch_end_date':temp.batch_end_date,
                'subplant_id':temp.subplant_id.id,
                'batch_id':temp.batch_id.id,
                'batch_size':temp.batch_size,
                'date':temp.date,
                'created_by':temp.created_by.id,
                'total_input_qty':temp.total_input_qty,
                'total_output_qty':temp.total_output_qty,
                'remarks':temp.remarks,
                'production_name':temp.production_name,
                'status':'',
                'total_time_c':temp.total_time_c,
                'total_output_yeild':temp.total_output_yeild,
                'available_qty':temp.available_qty,
                'bmr_no':temp.bmr_no,
                'revise_status':temp.revise_status,
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,                
                'revise_flag': 1
                })
            for item in temp.assay_line:
                production_powder = self.pool.get('prakruti.powder_rm_assay').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'rm_assay': item.rm_assay,
                    'rm_assay_output': item.rm_assay_output,
                    #'rm_assay_o': item.rm_assay_o,
                    #'rm_assay_output_o': item.rm_assay_output_o,
                    #'rm_assay_t': item.rm_assay_t,
                    #'rm_assay_output_t': item.rm_assay_output_t,
                    'production_powder_id': ebsl_id
                    })
            for item in temp.powder_sieving_id:
                sieving = self.pool.get('prakruti.powder_production_sieving').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'date': item.date,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'ingredient_name': item.ingredient_name.id,
                    'sieve_id': item.sieve_id.id,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'sieving_id': ebsl_id
                    })
            for item in temp.powder_binder_id:
                binder = self.pool.get('prakruti.powder_production_binder').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'solvent': item.solvent,
                    'solvent1': item.solvent1,
                    'equipment_code': item.equipment_code.id,
                    'binding_agent': item.binding_agent,
                    'qty_solvent_1kg': item.qty_solvent_1kg,
                    'qty_solvent_2kg': item.qty_solvent_2kg,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'qty_binder_solution': item.qty_binder_solution,
                    'temperature': item.temperature,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'binder_id': ebsl_id
                    })
            for item in temp.powder_granulation_id:
                granulation = self.pool.get('prakruti.powder_production_granulation').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'stage_id': item.stage_id.id,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'qty_used': item.qty_used,
                    'impellar': item.impellar,
                    'chopper': item.chopper,
                    'temperature': item.temperature,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'granulation_id': ebsl_id
                    })
            for item in temp.powder_semi_drying_id:
                semi_drying = self.pool.get('prakruti.powder_production_semi_drying').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'inlet': item.inlet,
                    'exhaust': item.exhaust,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'semi_drying_id': ebsl_id
                    })
            for item in temp.powder_final_drying_id:
                final_drying = self.pool.get('prakruti.powder_production_final_drying').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'inlet_air_flow': item.inlet_air_flow,
                    'duration': item.duration,
                    'lod_of_granules': item.lod_of_granules,
                    'inlet': item.inlet,
                    'exhaust': item.exhaust,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'final_drying_id': ebsl_id
                    })
            for item in temp.powder_milling_id:
                milling = self.pool.get('prakruti.powder_production_milling').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'ingredient_name': item.ingredient_name,
                    'mesh_id': item.mesh_id,
                    'weight_before': item.weight_before,
                    'weight_after': item.weight_after,
                    'rejection': item.rejection,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'milling_id': ebsl_id
                    })
            for item in temp.powder_api_addition_id:
                api_addition = self.pool.get('prakruti.powder_production_api_addition').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'ingredient_name': item.ingredient_name,
                    'quantity': item.quantity,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temperature': item.temperature,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'api_addition_id': ebsl_id
                    })
            for item in temp.powder_blending_id:
                blending = self.pool.get('prakruti.powder_production_blending').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'date': item.date,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'blending_rpm': item.blending_rpm,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'blending_id': ebsl_id
                    })
            for item in temp.powder_compression_id:
                compression = self.pool.get('prakruti.powder_production_compression').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'qty_for_compression': item.qty_for_compression,
                    'qty_after_compression': item.qty_after_compression,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'compression_id': ebsl_id
                    })
            for item in temp.powder_coating_preparation_id:
                coating_preparation = self.pool.get('prakruti.powder_production_coating_preparation').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'equipment_code': item.equipment_code.id,
                    'qty_coating_material': item.qty_coating_material,
                    'qty_solvent': item.qty_solvent,
                    'solvent_qty': item.solvent_qty,
                    'temperature': item.temperature,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'coating_material_name': item.coating_material_name,
                    'solvent_name': item.solvent_name,
                    'name_solvent': item.name_solvent,
                    'standard_time': item.standard_time,
                    'coating_preparation_id': ebsl_id
                    })
            for item in temp.powder_coating_id:
                coating = self.pool.get('prakruti.powder_production_coating').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'pan_speed': item.pan_speed,
                    'spray_rate': item.spray_rate,
                    'powder_bed_temp': item.powder_bed_temp,
                    'automization_pressure': item.automization_pressure,
                    'inlet': item.inlet,
                    'exhaust': item.exhaust,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'coating_id': ebsl_id
                    })
            for item in temp.powder_inspection_id:
                inspection = self.pool.get('prakruti.powder_production_inspection').create(cr,uid, { 
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'total_coated': item.total_coated,
                    'rejected_powder': item.rejected_powder,
                    'rejected_percentage': item.rejected_percentage,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'inspection_id': ebsl_id
                    })
            for item in temp.powder_metal_inspection_id:
                metal_detection = self.pool.get('prakruti.powder_production_metal_detection').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'equipment_code': item.equipment_code.id,
                    'total_coated': item.total_coated,
                    'rejected_powder': item.rejected_powder,
                    'rejected_percentage': item.rejected_percentage,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'metal_detection_id': ebsl_id
                    })
            for item in temp.powder_packing_id:
                packing = self.pool.get('prakruti.powder_production_packing').create(cr,uid, { 
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'packing_style': item.packing_style,
                    'packing_qty': item.packing_qty,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'packing_id': ebsl_id
                    })
            for item in temp.breakdown_production_id:
                breakdown = self.pool.get('prakruti.production_powder_breakdown').create(cr,uid, {
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
            for item in temp.addition_of_ingredients_line:
                addition_of_ingredients = self.pool.get('prakruti.powder_production_addition_of_ingredients').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'standard_time': item.standard_time,
                    'date': item.date,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'ingredient_added': item.ingredient_added.id,
                    'remarks': item.remarks,
                    'total_qty': item.total_qty,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'addition_of_ingredients_id': ebsl_id
                    })
            for item in temp.extract_solution_line:
                sieving = self.pool.get('prakruti.lotion_extract_solution').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'name_of_extract': item.name_of_extract,
                    'name_of_solvent': item.name_of_solvent,
                    'stage_id': item.stage_id.id,
                    'machine_id': item.machine_id.id,
                    'qty_of_extract_charged': item.qty_of_extract_charged,
                    'qty_of_solvent_charged': item.qty_of_solvent_charged,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'volume_before': item.volume_before,
                    'volume_after': item.volume_after,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'extract_solution_id': ebsl_id
                    })
            for item in temp.addition_of_solution_line:
                sieving = self.pool.get('prakruti.lotion_addition_of_solution').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'qty_solvent': item.qty_solvent,
                    'name_of_solvent': item.name_of_solvent,
                    'stage_id': item.stage_id.id,
                    'machine_id': item.machine_id.id,
                    'qty_of_extract_charged': item.qty_of_extract_charged,
                    'qty_of_solvent_charged': item.qty_of_solvent_charged,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'volume_before': item.volume_before,
                    'volume_after': item.volume_after,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'addition_of_solution_id': ebsl_id
                    })
            for item in temp.other_ingredient_addition_line:
                sieving = self.pool.get('prakruti.lotion_other_ingredient_addition').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'material_id': item.material_id.id,
                    'stage_id': item.stage_id.id,
                    'machine_id': item.machine_id.id,
                    'quantity': item.quantity,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temp_pressure_ph': item.temp_pressure_ph,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'other_ingredient_addition_id': ebsl_id
                    })
            for item in temp.volume_make_up_line:
                sieving = self.pool.get('prakruti.lotion_volume_make_up').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'stage_id': item.stage_id.id,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'volume_before': item.volume_before,
                    'volume_after': item.volume_after,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'volume_make_up_id': ebsl_id
                    })
            for item in temp.filling_line:
                sieving = self.pool.get('prakruti.lotion_volume_make_up').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'machine_id': item.machine_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'no_of_bottles_filled': item.no_of_bottles_filled,
                    'no_of_bottles_rejected': item.no_of_bottles_rejected,
                    'total_bottles_accepted': item.total_bottles_accepted,
                    'checked_by': item.checked_by,
                    'done_by': item.done_by,
                    'filling_id': ebsl_id
                    })
            cr.execute('''UPDATE prakruti_powder_production SET revise_status = 'revise_powder',is_revise = 'True' WHERE id = %s''',((temp.id),))
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
                    cr.execute('''SELECT revise_powder_production  (%s,%s,%s)''',((temp.id),(temp.batch_id.id),(temp.subplant_id.subplant_id.id),))
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
        return super(PrakrutiPowderProduction, self).unlink()    
    
    '''
    While selecting batch no it will extract data from Batch master Screen 
    '''
    
    def onchange_batch_id(self, cr, uid, ids, batch_id, context=None):
        process_type = self.pool.get('prakruti.batch_master').browse(cr, uid, batch_id, context=context)
        result = {
            'batch_size': process_type.batch_capacity,
            'batch_allocation_date': process_type.batch_allocation_date,
            'batch_end_date': process_type.batch_end_date,
            'bmr_no': process_type.bmr_no,
            'formulation_type':process_type.formulation_type,
            'sieving': process_type.sieving,
            'preparation_of_binder': process_type.preparation_of_binder,
            'granulation':process_type.granulation,
            'semi_drying':process_type.semi_drying,
            'final_drying':process_type.final_drying,
            'milling':process_type.milling,
            'blending':process_type.blending,
            'compression':process_type.compression,
            'tablet_coating':process_type.tablet_coating,
            'coating':process_type.coating,
            'inspection':process_type.inspection,
            'packing':process_type.packing,
            'metal_inspection':process_type.metal_inspection,
            'extract_solution_lotion':process_type.extract_solution_lotion,
            'addition_of_solution':process_type.addition_of_solution,
            'other_ingredient_addition_lotion':process_type.other_ingredient_addition_lotion,
            'volume_make_up':process_type.volume_make_up,
            'filling_lotion':process_type.filling_lotion,
            
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
            cr.execute("UPDATE prakruti_batch_master AS b SET batch_allocated_by = 'formulation',batch_allocated_flag = 1 FROM(SELECT batch_id FROM prakruti_powder_production WHERE  id= %s ) AS a WHERE a.batch_id = b.id",((temp.id),))
            cr.execute("UPDATE prakruti_powder_production SET status = 'batch_alloted' WHERE id = %s",((temp.id),))
        return {}
    '''
    calculation for Total Weight Before Sieving
    '''
    @api.depends('powder_sieving_id.weight_before')
    def _compute_total_weight_before_si(self):
        for order in self:
            weight_before_si = 0.0
            for line in order.powder_sieving_id:
                weight_before_si += line.weight_before 
                order.update({
                        'total_weight_before_si': weight_before_si
                        })
    '''
    calculation for Total Weight After Sieving
    '''
    @api.depends('powder_sieving_id.weight_after')
    def _compute_total_weight_after_si(self):
        for order in self:
            weight_after_si = 0.0
            for line in order.powder_sieving_id:
                weight_after_si += line.weight_after 
                order.update({
                        'total_weight_after_si': weight_after_si
                        })
    '''
    calculation for Total Weight Before Milling
    '''
    @api.depends('powder_milling_id.weight_before')
    def _compute_total_weight_before_mi(self):
        for order in self:
            weight_before_mi = 0.0
            for line in order.powder_milling_id:
                weight_before_mi += line.weight_before 
                order.update({
                        'total_weight_before_mi': weight_before_mi
                        })
    '''
    calculation for Total Weight After Milling
    '''
    @api.depends('powder_milling_id.weight_after')
    def _compute_total_weight_after_mi(self):
        for order in self:
            weight_after_mi = 0.0
            for line in order.powder_milling_id:
                weight_after_mi += line.weight_after 
                order.update({
                        'total_weight_after_mi': weight_after_mi
                        })
    
    '''
    calculation for Total input Qty Coating Preparation
    '''
    @api.depends('powder_coating_preparation_id.input_qty')
    def _compute_total_input_qty_pc(self):
        for order in self:
            input_qty_pc = 0.0
            for line in order.powder_coating_preparation_id:
                input_qty_pc += line.input_qty 
                order.update({
                        'total_input_qty_pc': input_qty_pc
                        })
    '''
    calculation for Total o/pqty Coating preparation
    '''
    @api.depends('powder_coating_preparation_id.output_qty')
    def _compute_total_output_qty_pc(self):
        for order in self:
            output_qty_pc = 0.0
            for line in order.powder_coating_preparation_id:
                output_qty_pc += line.output_qty 
                order.update({
                        'total_output_qty_pc': output_qty_pc
                        })
    '''
    calculation for Total input qty Coating
    '''
    @api.depends('powder_coating_id.input_qty')
    def _compute_total_input_qty_c(self):
        for order in self:
            input_qty_c = 0.0
            for line in order.powder_coating_id:
                input_qty_c += line.input_qty 
                order.update({
                        'total_input_qty_c': input_qty_c
                        })
    '''
    calculation for Total o/p Qty coating
    '''
    @api.depends('powder_coating_id.output_qty')
    def _compute_total_output_qty_c(self):
        for order in self:
            output_qty_c = 0.0
            for line in order.powder_coating_id:
                output_qty_c += line.output_qty 
                order.update({
                        'total_output_qty_c': output_qty_c
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
                                    prakruti_powder_line.product_id,
                                    prakruti_powder.batch_no 
                            FROM 	
                                    prakruti_powder_line INNER JOIN 
                                    prakruti_powder ON 
                                    prakruti_powder_line.main_id=prakruti_powder.id 
                            WHERE 
                                    prakruti_powder.batch_no=%s''',((temp.batch_id.id),))
            for line in cr.dictfetchall():
                product_id = line['product_id']
                grid_line_entry = self.pool.get('prakruti.powder_rm_assay').create(cr,uid,{
                    'product_id':product_id,
                    'production_powder_id':temp.id
                    })
            cr.execute('UPDATE prakruti_powder_production SET flag_display_product = 1 WHERE prakruti_powder_production.id = %s',((temp.id),))
            cr.execute("UPDATE  prakruti_powder_production SET flag_delete_product = 0 WHERE prakruti_powder_production.id = %s",((temp.id),))
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
            cr.execute("DELETE FROM prakruti_powder_rm_assay WHERE prakruti_powder_rm_assay.production_powder_id = %s", ((temp.id),))
            cr.execute("UPDATE  prakruti_powder_production SET flag_delete_product = 1 WHERE prakruti_powder_production.id = %s",((temp.id),))
            cr.execute('UPDATE prakruti_powder_production SET flag_display_product = 0 WHERE prakruti_powder_production.id = %s',((temp.id),))
        return {}
    
class PrakrutiPowderProductionSeiving(models.Model):
    _name='prakruti.powder_production_sieving'
    _table ='prakruti_powder_production_sieving'
    _description='Powder Production Sieving'
    
    sieving_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    date = fields.Datetime(string='Date')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    ingredient_name=fields.Many2one('product.product', string='Ingredient Name')
    sieve_id = fields.Many2one('prakruti.sieve_master',string='Seive Size')
    input_qty= fields.Float(string='Total Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Total Output Qty',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('rejection')
    #def _check_rejection(self):
        #if self.rejection < 0:
            #raise ValidationError(
                #"Rejection can't be Negative !")  
        
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
        #for temp in lines:
            #if temp.weight_before <= 0:
                #return False
            #return True
        
    #def _check_weight_after(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for temp in lines:
            #if temp.weight_after <= 0:
                #return False
            #return True
        
        
    #_constraints = [
        
        #(_check_weight_before,'Weight before cannot be negative or zero!',['weight_before']),
        #(_check_weight_after,'Weight after cannot be negative or zero!',['weight_after']),
        #]
    
    
class PrakrutiPowderProductionBinder(models.Model):
    _name='prakruti.powder_production_binder'
    _table ='prakruti_powder_production_binder'
    _description='Powder Production Binder'
    
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    solvent = fields.Char(string='Name Of Solvent 1')
    solvent1 = fields.Char(string='Name Of Solvent 2')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    binding_agent = fields.Char(string='Binding Agent')
    qty_solvent_1kg = fields.Float(string='Qty of solvent 1(KG)',digits=(6,3))
    qty_solvent_2kg = fields.Float(string='Qty of solvent 2(KG)',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    qty_binder_solution = fields.Float(string='Qty of Binder Solution',digits=(6,3))
    temperature = fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    binder_id = fields.Many2one('prakruti.powder_production')
        
    #@api.one
    #@api.constrains('qty_solvent_1kg')
    #def _check_qty_solvent_1kg(self):
        #if self.qty_solvent_1kg <= 0:
            #raise ValidationError(
                #"Qty of solvent 1(KG) can't be Negative or 0!") 
        
    #@api.one
    #@api.constrains('qty_solvent_2kg')
    #def _check_qty_solvent_2kg(self):
        #if self.qty_solvent_2kg <= 0:
            #raise ValidationError(
                #"Qty of solvent 2(KG)can't be Negative or 0!") 
        
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
    
    #def _check_qty_binder(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for temp in lines:
            #if temp.qty_binder_solution <= 0:
                #return False
            #return True
        
        
    #_constraints = [
        
        #(_check_qty_binder,'Qty of binder solution cannot be negative or zero!',['qty_binder_solution']),
        #]
    
    
class PrakrutiPowderProductionGranulation(models.Model):
    _name='prakruti.powder_production_granulation'
    _table ='prakruti_powder_production_granulation'
    _description='Powder Production Granulation'
    
    granulation_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    stage_id = fields.Many2one('prakruti.stage', string='Stage')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    qty_used = fields.Float(string='Qty Used',digits=(6,3))
    impellar = fields.Selection([('slow','Slow'),('fast','Fast')],string='Impellar')
    chopper = fields.Selection([('slow','Slow'),('fast','Fast')],string='Chopper')
    temperature = fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
        
    #@api.one
    #@api.constrains('qty_used')
    #def _check_qty_used(self):
        #if self.qty_used <= 0:
            #raise ValidationError(
                #"Qty Used can't be Negative or 0!") 
        
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
    
    
class PrakrutiPowderProductionSemiDrying(models.Model):
    _name='prakruti.powder_production_semi_drying'
    _table ='prakruti_powder_production_semi_drying'
    _description='Powder Production Semi drying'
        
    semi_drying_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    inlet =fields.Float(string='Temp Inlet',digits=(6,3))
    exhaust =fields.Float(string='Temp Exhaust',digits=(6,3))
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
    
class PrakrutiPowderProductionFinalDrying(models.Model):
    _name='prakruti.powder_production_final_drying'
    _table ='prakruti_powder_production_final_drying'
    _description='Powder Production Final Drying'
        
    final_drying_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    inlet_air_flow =fields.Float(string='Inlet Air Flow',digits=(6,3))
    duration = fields.Datetime(string='Duration of Time')
    lod_of_granules= fields.Char(string='LOD of granules')
    inlet =fields.Float(string='Temp Inlet',digits=(6,3))
    exhaust =fields.Float(string='Temp Exhaust',digits=(6,3))
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
    
class PrakrutiPowderProductionMilling(models.Model):
    _name='prakruti.powder_production_milling'
    _table ='prakruti_powder_production_milling'
    _description='Powder Production Milling'
     
    milling_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    ingredient_name=fields.Many2one('product.product', string='Ingredient Name')
    mesh_id = fields.Many2one('prakruti.mesh_master',string='Mesh Size')
    weight_before= fields.Float(string='Weight Before',digits=(6,3))
    weight_after= fields.Float(string='Weight After',digits=(6,3))
    rejection=fields.Float(string='Rejection',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
    #@api.one
    #@api.constrains('rejection')
    #def _check_rejection(self):
        #if self.rejection <= 0:
            #raise ValidationError(
                #"Rejection  can't be Negative or 0!") 
        
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
        #for temp in lines:
            #if temp.weight_before <= 0:
                #return False
            #return True
        
    #def _check_weight_after(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for temp in lines:
            #if temp.weight_after <= 0:
                #return False
            #return True
        
        
    #_constraints = [
        
        #(_check_weight_before,'Weight before cannot be negative or zero!',['weight_before']),
        #(_check_weight_after,'Weight after cannot be negative or zero!',['weight_after']),
        #]
    
    
    
class PrakrutiPowderProductionAPIAddition(models.Model):
    _name='prakruti.powder_production_api_addition'
    _table ='prakruti_powder_production_api_addition'
    _description='Powder Production API Addition'
    
    api_addition_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    ingredient_name=fields.Many2one('product.product', string='Ingredient Name')
    quantity = fields.Float(string='Quantity',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temperature = fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
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
        #for temp in lines:
            #if temp.quantity <= 0:
                #return False
            #return True
        
        
    #_constraints = [
        
        #(_check_quantity,'Qty cannot be negative or zero!',['quantity']),
        #]
    
class PrakrutiPowderProductionBlending(models.Model):
    _name='prakruti.powder_production_blending'
    _table ='prakruti_powder_production_blending'
    _description='Powder Production Blending'
    
    blending_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    date = fields.Datetime(string='Date ')
    start_time = fields.Datetime(string='Time Start ')
    end_time = fields.Datetime(string='Time End ')
    blending_rpm = fields.Float(string='Blending RPM')
    input_qty = fields.Float(string='Total Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Total Output Qty',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #"Input Qty can't be Negative or 0!") 
    
    
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #"Output Qty  can't be Negative or 0!") 
        
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
    
class PrakrutiPowderProductionCompression(models.Model):
    _name='prakruti.powder_production_compression'
    _table ='prakruti_powder_production_compression'
    _description='Powder Production Compression'
        
    compression_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    qty_for_compression = fields.Float(string='Qty Before',digits=(6,3))
    qty_after_compression= fields.Float(string='Qty After',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time ')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
    #@api.one
    #@api.constrains('qty_for_compression')
    #def _check_qty_for_compression(self):
        #if self.qty_for_compression <= 0:
            #raise ValidationError(
                #"Qty Taken for Compression can't be Negative or 0!") 
    
    
    #@api.one
    #@api.constrains('qty_after_compression')
    #def _check_qty_after_compression(self):
        #if self.qty_after_compression <= 0:
            #raise ValidationError(
                #"Qty After Compression can't be Negative or 0!") 
        
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
    
class PrakrutiPowderProductionCoatingPreparation(models.Model):
    _name='prakruti.powder_production_coating_preparation'
    _table ='prakruti_powder_production_coating_preparation'
    _description='Powder Production Coating Preparation'
        
    coating_preparation_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    qty_coating_material = fields.Float(string='Quantity Of Coating Material',digits=(6,3))
    qty_solvent = fields.Float(string='Quantity Of Solvent 1',digits=(6,3))
    solvent_qty = fields.Float(string='Quantity Of Solvent 2',digits=(6,3))
    temperature = fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    start_time = fields.Datetime(string='Start Time ')
    end_time = fields.Datetime(string='End Time ')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')    
    coating_material_name = fields.Char(string='Coating Material name')
    solvent_name=fields.Char(string=' Solvent Name 1')
    name_solvent=fields.Char(string=' Solvent Name 2')
    standard_time = fields.Char(string='Std Time')
    
    
    #@api.one
    #@api.constrains('qty_coating_material')
    #def _check_qty_coating_material(self):
        #if self.qty_coating_material <= 0:
            #raise ValidationError(
                #"Quantity Of Coating Material can't be Negative or 0!") 
    
    
    #@api.one
    #@api.constrains('qty_solvent')
    #def _check_qty_solvent(self):
        #if self.qty_solvent <= 0:
            #raise ValidationError(
                #"Quantity Of Solvent 1 can't be Negative or 0!") 
    
    
    #@api.one
    #@api.constrains('solvent_qty')
    #def _check_solvent_qty(self):
        #if self.solvent_qty <= 0:
            #raise ValidationError(
                #"Quantity Of Solvent 2 can't be Negative or 0!") 
    

    
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #"Input Qty can't be Negative or 0!") 
    
    
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #"Output Qty  can't be Negative or 0!") 
        
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

class PrakrutiPowderProductionCoating(models.Model):
    _name='prakruti.powder_production_coating'
    _table ='prakruti_powder_production_coating'
    _description='Powder Production Coating'
        
    coating_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time ')
    end_time = fields.Datetime(string='End Time')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    pan_speed = fields.Float(string='Pan Speed',digits=(6,3))
    spray_rate = fields.Float(string='Spray Rate',digits=(6,3))
    powder_bed_temp = fields.Float(string='Powder BED Temp',digits=(6,3))
    automization_pressure = fields.Float(string='Automization Pressure',digits=(6,3))
    inlet =fields.Float(string='Temp Inlet',digits=(6,3))
    exhaust =fields.Float(string='Temp Exhaust',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #"Input Qty can't be Negative or 0!") 
    
    
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #"Output Qty  can't be Negative or 0!") 
        
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

class PrakrutiPowderProductionInspection(models.Model):
    _name='prakruti.powder_production_inspection'
    _table ='prakruti_powder_production_inspection'  
    _description='Powder Production Inspection'
    
    inspection_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    total_coated = fields.Float(string='Total Coated Powder in Kg',digits=(6,3))
    rejected_powder = fields.Float(string='Rejected Powder',digits=(6,3))
    rejected_percentage = fields.Float(string='Rejection%',digits=(6,3))
    start_time = fields.Datetime(string='Start Time ')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
    #@api.one
    #@api.constrains('total_coated')
    #def _check_total_coated(self):
        #if self.total_coated <= 0:
            #raise ValidationError(
                #"Total Coated Powder in Kg can't be Negative or 0!") 
        
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
    
class PrakrutiPowderProductionMetalDetection(models.Model):
    _name='prakruti.powder_production_metal_detection'
    _table ='prakruti_powder_production_metal_detection'    
    _description='Powder Production Metal'
    
    metal_detection_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    total_coated = fields.Float(string='Total Coated Powder in Kg',digits=(6,3))
    rejected_powder = fields.Float(string='Rejected Powder',digits=(6,3))
    rejected_percentage = fields.Float(string='Rejection%',digits=(6,3))
    start_time = fields.Datetime(string='Start Time ')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
    #@api.one
    #@api.constrains('total_coated')
    #def _check_total_coated(self):
        #if self.total_coated <= 0:
            #raise ValidationError(
                #"Total Coated Powder in Kg can't be Negative or 0!") 
        
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
    
    
   
    
class PrakrutiPowderProductionPacking(models.Model):
    _name='prakruti.powder_production_packing'
    _table ='prakruti_powder_production_packing'   
    _description='Powder Production Packing' 
        
    packing_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    packing_style =fields.Char(string='Packing style')
    packing_qty =fields.Float(string='Packing Qty',digits=(6,3))
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time ')
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
    
    #def _check_packing_qty(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for temp in lines:
            #if temp.packing_qty <= 0:
                #return False
            #return True
        
        
    #_constraints = [
        
        #(_check_packing_qty,'Please Enter Packing Qty!',['packing_qty']),
        #]
    
class PrakrutiPowderProductionBreakdown(models.Model):
    _name = 'prakruti.production_powder_breakdown'
    _table = 'prakruti_production_powder_breakdown'
    _description = 'Production Powder Breakdown  '
    
    breakdown_grid_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    machine_id=fields.Many2one('prakruti.machine',string='Machine')
    date=fields.Date(string='Date', default=fields.Date.today)
    breakdown_id=fields.Many2one('prakruti.breakdown_item',string='Break Down Item')
    running_hours=fields.Char(string='Running Hours')
    breakdown_hours=fields.Char(string='Break Down Hours')
    remarks=fields.Text(string='Remarks')
    checked_by = fields.Char(string='Checked By')
       
class PrakrutiProductionSyrupRMAssay(models.Model):
    _name ='prakruti.powder_rm_assay'
    _table = 'prakruti_powder_rm_assay'
    _description = 'Production Syrup RM Assay'
    
    production_powder_id = fields.Many2one('prakruti.powder_production')
    product_id = fields.Many2one('product.product', string='Product Name')
    rm_assay = fields.Float(string="RM Assay%" , digits=(6,3))
    rm_assay_output = fields.Float(string="Output Quantity" , digits=(6,3)) 
    #rm_assay_o = fields.Float(string="RM Assay1%" , digits=(6,3))
    #rm_assay_output_o = fields.Float(string="RM Assay Output1" , digits=(6,3))
    #rm_assay_t = fields.Float(string="RM Assay2%" , digits=(6,3))
    #rm_assay_output_t = fields.Float(string="RM Assay Output2" , digits=(6,3))
    
    
    
class PrakrutiPowderProductionadditionOfIngredients(models.Model):
    _name='prakruti.powder_production_addition_of_ingredients'
    _table ='prakruti_powder_production_addition_of_ingredients'   
    _description='Powder Production Addition of Ingredients' 
        
    addition_of_ingredients_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    standard_time = fields.Char(string='Standard Time')
    date = fields.Datetime(string='Date ')
    start_time = fields.Datetime(string='Start Time ')
    end_time = fields.Datetime(string='End Time')
    ingredient_added =fields.Many2one('product.product', string='Ingredient Added')
    total_qty = fields.Float(string='Total Qty',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    remarks = fields.Text(string='Remarks')
    
    
class PrakrutiLotionExtractSolution(models.Model):
    _name ='prakruti.lotion_extract_solution'
    _table = 'prakruti_lotion_extract_solution'
    _description = 'Preparation of Extract solution'
         
    extract_solution_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Code',required="True")
    std_time = fields.Char( string='Standard Time')
    name_of_extract = fields.Char( string='Name Of Extract')
    name_of_solvent = fields.Char( string='Name Of Solvent')
    stage_id = fields.Many2one('prakruti.stage', string='Stage')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment Code')
    qty_of_extract_charged=fields.Float(string='Qty of Extract Charged',digits=(6,3))
    qty_of_solvent_charged=fields.Float(string='Qty of Solvent Charged ',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    volume_before=fields.Float(string='Volume Before',digits=(6,3))
    volume_after=fields.Float(string='Volume After',digits=(6,3))
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    
class PrakrutiLotionAdditionOfSolution(models.Model):
    _name ='prakruti.lotion_addition_of_solution'
    _table = 'prakruti_lotion_addition_of_solution'
    _description = 'Preparation of Addition Of solution'
         
    addition_of_solution_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Code',required="True")
    std_time = fields.Char( string='Standard Time')
    qty_solvent = fields.Char( string='Name Of Solvent 1')
    name_of_solvent = fields.Char( string='Name Of Solvent 2')
    stage_id = fields.Many2one('prakruti.stage', string='Stage')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment Code')
    qty_of_extract_charged=fields.Float(string='Qty of Extract Charged',digits=(6,3))
    qty_of_solvent_charged=fields.Float(string='Qty of Solvent Charged ',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    volume_before=fields.Float(string='Volume Before',digits=(6,3))
    volume_after=fields.Float(string='Volume After',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    
class PrakrutiLotionOtherIngredientAddition(models.Model):
    _name ='prakruti.lotion_other_ingredient_addition'
    _table = 'prakruti_lotion_other_ingredient_addition'
    _description = 'Other Ingredient Addition'
         
    other_ingredient_addition_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Code',required="True")
    std_time = fields.Char( string='Standard Time')
    material_id = fields.Many2one('product.product', string='Ingredient Name')
    stage_id = fields.Many2one('prakruti.stage', string='Stage')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment Code')
    quantity=fields.Float(string='Qty',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temp_pressure_ph=fields.Float(string='Temp/Pressure/PH/RH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    
class PrakrutiLotionVolumeMakeUp(models.Model):
    _name ='prakruti.lotion_volume_make_up'
    _table = 'prakruti_lotion_volume_make_up'
    _description = 'Volume Make Up'
         
    volume_make_up_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Code',required="True")
    std_time = fields.Char( string='Standard Time')
    stage_id = fields.Many2one('prakruti.stage', string='Stage')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment Code')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    volume_before=fields.Float(string='Volume Before',digits=(6,3))
    volume_after=fields.Float(string='Volume After',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    
class PrakrutiLotionFilling(models.Model):
    _name ='prakruti.lotion_filling'
    _table = 'prakruti_lotion_filling'
    _description = 'Filling'
         
    filling_id = fields.Many2one('prakruti.powder_production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Code',required="True")
    std_time = fields.Char( string='Standard Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment Code')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    no_of_bottles_filled=fields.Char( string='No of Bottles Filled')
    no_of_bottles_rejected=fields.Float(string='No of Bottles Rejected',digits=(6,3))
    total_bottles_accepted=fields.Float(string='Total Bottles Accepted',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Checked By')
    