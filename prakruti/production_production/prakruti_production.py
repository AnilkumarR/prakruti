'''
Company : EBSL
Author: Induja
Module: Extraction Production
Class 1: PrakrutiProduction
Class 2: PrakrutiProductionPulverization
Class 3 : PrakrutiProductionExtraction
Class 4 : PrakrutiProductionPrecipitation
Class 5 : PrakrutiProductionBleaching
Class 6 : PrakrutiProductionFiltration
Class 7 : PrakrutiProductionConcentration
Class 8 : PrakrutiProductionEvaporation
Class 9 : PrakrutiProductionStrippingAndPurging
Class 10 : PrakrutiProductionCoolingAndUnloading
Class 11 : PrakrutiProductionMaturationAndCrystalization
Class 12 : PrakrutiProductionStirringAndSettling
Class 13 : PrakrutiProductionWaterStripping
Class 14 : PrakrutiProductionCharcolization
Class 15 : PrakrutiProductionSprayDrying
Class 16: PrakrutiProductionMilling
Class 17: PrakrutiProductionSieving
Class 18 : PrakrutiProductionMagneticParticleSeparation
Class 19 : PrakrutiProductionBlending
Class 20 : PrakrutiProductionHeatSterilization
Class 21 : PrakrutiProductionPacking
Class 22: PrakrutiProductionBreakdown
Class 23 : PrakrutiExtractionDrying
Class 24: PrakrutiBlowOff
Class 25: PrakrutiWashingLine
Class 26 : PrakrutiHexaneRecoveryLine
Table & Reference id : prakruti_production
Table 1 & Reference Id: prakruti_production_pulverization ,pulverization_id,pulverization_production_id
Table 2 & Reference Id: prakruti_production_extraction,extraction_id,extraction_production_id
Table 3 & Reference Id: prakruti_production_precipitation ,precipitation_id,precipitation_production_id
Table 4 & Reference Id: prakruti_production_bleaching,bleaching_id,bleaching_production_id
Table 5 & Reference Id: prakruti_production_filtration ,filtration_id,filtration_production_id
Table 6 & Reference Id: prakruti_production_concentration,concentration_id,concentration_production_id
Table 7 & Reference Id: prakruti_production_evaporation ,evaporation_id,evaporation_production_id
Table 8 & Reference Id: prakruti_production_stripping_purging,stripping_purging_id,stripping_production_id
Table 9 & Reference Id: prakruti_production_cooling_unloading ,cooling_unloading_id,cooling_production_id
Table 10 & Reference Id: prakruti_production_maturation_crystalization,maturation_id,maturation_production_id
Table 11 & Reference Id: prakruti_production_stirring_settling ,stirring_settling_id,stirring_production_id
Table 12 & Reference Id: prakruti_production_water_stripping,water_stripping_id,water_stripping_production_id
Table 13 & Reference Id: prakruti_production_charcolization ,charcoalization_id,charcolization_production_id
Table 14 & Reference Id: prakruti_production_spray_drying,spray_drying_id,spray_production_id
Table 15 & Reference Id: prakruti_production_milling ,milling_id,milling_production_id
Table 16 & Reference Id: prakruti_production_sieving,sieving_id,sieving_production_id
Table 17 & Reference Id: prakruti_production_magnetic_particle_separation ,magnetic_separation_id,magnetic_production_id
Table 18 & Reference Id: prakruti_production_blending,blending_id,blending_production_id
Table 19 & Reference Id: prakruti_production_heat_sterilization ,heat_sterilization_id,sterilization_production_id
Table 20 & Reference Id: prakruti_production_packing,packing_id,packing_production_id
Table 21 & Reference Id: prakruti_production_breakdown,breakdown_grid_id,breakdown_production_id
Table 22 & Reference Id: prakruti_production_drying ,drying_id,extraction_drying_id
Table 23 & Reference Id: prakruti_blow_off_line,blow_off_id,blow_off_line
Table 24 & Reference Id: prakruti_washing_line ,washing_id,washing_line
Table 25 & Reference Id: prakruti_hexane_recovery_line,hexane_recovery_id,hexane_recovery_line

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


class PrakrutiProduction(models.Model):
    _name='prakruti.production'
    _table ='prakruti_production'
    _description='Extraction Production'
    _order= 'id desc'
    _rec_name= 'subplant_id'
    
    pulverization_production_id = fields.One2many('prakruti.production_pulverization','pulverization_id',string='Pulverization Grid')
    extraction_production_id = fields.One2many('prakruti.production_extraction','extraction_id',string='Extraction Grid')
    precipitation_production_id = fields.One2many('prakruti.production_precipitation','precipitation_id',string='Precipitation Grid')
    bleaching_production_id = fields.One2many('prakruti.production_bleaching','bleaching_id',string='Bleaching Grid')
    filtration_production_id = fields.One2many('prakruti.production_filtration','filtration_id',string='Filtration Grid')
    concentration_production_id = fields.One2many('prakruti.production_concentration','concentration_id',string='Concentration Grid')    
    evaporation_production_id = fields.One2many('prakruti.production_evaporation','evaporation_id',string='Evaporation Grid')
    stripping_production_id = fields.One2many('prakruti.production_stripping_purging','stripping_purging_id',string='Stripping Purging Grid')
    cooling_production_id = fields.One2many('prakruti.production_cooling_unloading','cooling_unloading_id',string='Cooling Unloading Grid')    
    maturation_production_id = fields.One2many('prakruti.production_maturation_crystalization','maturation_id',string='maturation Grid')
    stirring_production_id = fields.One2many('prakruti.production_stirring_settling','stirring_settling_id',string='stirring Settling Grid')    
    water_stripping_production_id = fields.One2many('prakruti.production_water_stripping','water_stripping_id',string='Water Stripping Grid')
    charcolization_production_id = fields.One2many('prakruti.production_charcolization','charcoalization_id',string='Charcoalization Grid')
    spray_production_id = fields.One2many('prakruti.production_spray_drying','spray_drying_id',string='Spray Drying Grid')    
    milling_production_id = fields.One2many('prakruti.production_milling','milling_id',string='Milling Grid')
    sieving_production_id = fields.One2many('prakruti.production_sieving','sieving_id',string='Sieving Grid')
    magnetic_production_id = fields.One2many('prakruti.production_magnetic_particle_separation','magnetic_separation_id',string='Magnetic Separation Grid')    
    blending_production_id = fields.One2many('prakruti.production_blending','blending_id',string='Blending Grid')
    sterilization_production_id = fields.One2many('prakruti.production_heat_sterilization','heat_sterilization_id',string='Heat Sterilization Grid')
    packing_production_id=fields.One2many('prakruti.production_packing','packing_id',string='Packing')
    breakdown_production_id = fields.One2many('prakruti.production_breakdown','breakdown_grid_id',string='Break Down Grid')
    extraction_drying_id = fields.One2many('prakruti.production_drying','drying_id',string='Drying Grid')
    blow_off_line=fields.One2many('prakruti.blow_off_line','blow_off_id',string='Blow Off Line')
    washing_line = fields.One2many('prakruti.washing_line','washing_id',string='Washing Line')
    hexane_recovery_line = fields.One2many('prakruti.hexane_recovery_line','hexane_recovery_id',string='Hexane Recovery Line')
    total_extract_charged = fields.Float(string='Total Extract Charged(Ltr)',compute= '_compute_extract_charged',store=True,digits=(6,3))
    total_semi_concentrate = fields.Float(string='Total Semi Concentrate(Ltr)',compute= '_compute_semi_concentrate',store=True,digits=(6,3))
    total_solvent_recovered = fields.Float(string='Total Solvent Recovered(Ltr)',compute= '_compute_total_solvent',store=True,digits=(6,3))
    total_extract_charged_eve = fields.Float(string='Total Extract Charged(Ltr)',compute= '_compute_extract_charged_eve',store=True,digits=(6,3))
    total_semi_concentrate_eve = fields.Float(string='Total Semi Concentrate(Ltr)',compute= '_compute_semi_concentrate_eve',store=True,digits=(6,3))
    total_solvent_recovered_eve = fields.Float(string='Total Solvent Recovered(Ltr)',compute= '_compute_total_solvent_eve',store=True,digits=(6,3))
    total_input_qty = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty',store=True,digits=(6,3))
    total_output_qty = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty',store=True,digits=(6,3))  
    total_input_qty_si = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty_si',store=True,digits=(6,3))
    total_output_qty_si = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty_si',store=True,digits=(6,3)) 
    total_input_qty_ms = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty_ms',store=True,digits=(6,3))
    total_output_qty_ms = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty_ms',store=True,digits=(6,3)) 
    total_input_qty_bl = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty_bl',store=True,digits=(6,3))
    total_output_qty_bl = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty_bl',store=True,digits=(6,3)) 
    total_input_qty_hs = fields.Float(string='Total Input Qty',compute= '_compute_total_input_qty_hs',store=True,digits=(6,3))
    total_output_qty_hs = fields.Float(string='Total Output Qty',compute= '_compute_total_output_qty_hs',store=True,digits=(6,3))
    drying_chart=fields.Selection([('yes','Yes'),('no','No')], string="Drying Chart", default='yes')
    pulverisation=fields.Selection([('yes','Yes'),('no','No')], string="Pulverisation")
    extraction_new=fields.Selection([('yes','Yes'),('no','No')], string="Extraction")
    precipitation=fields.Selection([('yes','Yes'),('no','No')], string="Precipitation")
    bleaching=fields.Selection([('yes','Yes'),('no','No')], string="Bleaching")    
    filtration=fields.Selection([('yes','Yes'),('no','No')], string="Filtration", default='yes')
    concentration=fields.Selection([('yes','Yes'),('no','No')], string="Concentration", default='yes')
    evaporation=fields.Selection([('yes','Yes'),('no','No')], string="Evaporation", default='yes')    
    spent_cooling_unloading=fields.Selection([('yes','Yes'),('no','No')], string="Spent Cooling & Loading", default='yes')
    maturation_crystalization=fields.Selection([('yes','Yes'),('no','No')], string="Maturation & Crystalization", default='yes')
    water_striiping_chart=fields.Selection([('yes','Yes'),('no','No')], string="Water Strriping Chart", default='yes')    
    charcolisation_chart=fields.Selection([('yes','Yes'),('no','No')], string="Charcolisation Chart", default='yes')
    spray_drying_chart=fields.Selection([('yes','Yes'),('no','No')], string="Spray Drying Chart", default='yes')
    milling=fields.Selection([('yes','Yes'),('no','No')], string="Milling", default='yes')    
    sieving=fields.Selection([('yes','Yes'),('no','No')], string="Sieving", default='yes')
    magnetic_particle_seperation=fields.Selection([('yes','Yes'),('no','No')], string="Magnetic Particle Seperation", default='yes')
    blending=fields.Selection([('yes','Yes'),('no','No')], string="Blending", default='yes')    
    heat_sterilization=fields.Selection([('yes','Yes'),('no','No')], string="Heat Sterilization", default='yes')
    spent_stripping=fields.Selection([('yes','Yes'),('no','No')], string="Spent Stripping", default='yes')
    stirring=fields.Selection([('yes','Yes'),('no','No')], string="Stirring", default='yes') 
    blow_off=fields.Selection([('yes','Yes'),('no','No')], string="Blow Off", default='yes')
    washing=fields.Selection([('yes','Yes'),('no','No')], string="Washing", default='yes')
    hexane_recover=fields.Selection([('yes','Yes'),('no','No')], string="Hexane Recovery", default='yes')   
    remarks = fields.Text(string='Remarks')
    bmr_no = fields.Char(string = 'BMR No')
    batch_allocation_date=fields.Datetime(string='Batch Allocation Date', default=fields.Date.today)
    batch_end_date=fields.Datetime(string='Batch End Date') 
    status = fields.Selection([('batch_alloted','Batch Alloted')],string="Status",readonly=1)
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant",required=1)
    batch_id = fields.Many2one('prakruti.batch_master',string='Batch No',required=1)
    batch_size= fields.Float(string='Batch Size', required=1,digits=(6,3))
    production_date= fields.Date(string = 'Production Date', default= fields.Date.today, required=1)
    production_name = fields.Selection([('extraction', 'Extraction')],string='Production Type',default='extraction')
    category_type=fields.Selection([('buffer', 'Buffer'),('non_buffer', 'Non Buffer')],string='Category ',default='buffer', required=1)    
    created_by =fields.Many2one('res.users','Created By')
    
    revise_status = fields.Selection([('revise_extraction','Revise Extraction'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    assay_line = fields.One2many('prakruti.rm_assay','production_id',string='RM Assay Grid')
    flag_display_product = fields.Integer(default=0)    
    flag_delete_product = fields.Integer(default=0)   
    
    #added by karan for print out on 20170911
    company_id=fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id,required="True")
    #added by induja  on 20180103
    post_precipitation=fields.Selection([('yes','Yes'),('no','No')], string="Post Precipitation", default='yes')
    filtration_b=fields.Selection([('yes','Yes'),('no','No')], string="Filtration B", default='yes')
    ph_adjustment=fields.Selection([('yes','Yes'),('no','No')], string="PH Adjustment", default='yes')
    checked_by = fields.Many2one('res.users',string='Checked By')
    ph_adjustment_line = fields.One2many('prakruti.production_ph_adjustment','ph_adjustment_id',string='Ph Adjustment Grid')
    precipitation_post_line = fields.One2many('prakruti.production_post_precipitation','precipitation_post_id',string='Post Precipitation Grid')
    filtrationb_line = fields.One2many('prakruti.production_filtration_b','filtrationb_id',string='Filtration B Grid')
    
    
    
    
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
    This Button helps for Revision
    '''
    @api.one
    @api.multi
    def revise_extraction(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            ebsl_id = self.pool.get('prakruti.production').create(cr,uid, {
                'drying_chart':temp.drying_chart,
                'pulverisation':temp.pulverisation,
                'extraction_new':temp.extraction_new,
                'precipitation':temp.precipitation,
                'bleaching':temp.bleaching,
                'filtration':temp.filtration,
                'concentration':temp.concentration,
                'evaporation':temp.evaporation,
                'spent_cooling_unloading':temp.spent_cooling_unloading,
                'maturation_crystalization':temp.maturation_crystalization,
                'water_striiping_chart':temp.water_striiping_chart,
                'charcolisation_chart':temp.charcolisation_chart,
                'spray_drying_chart':temp.spray_drying_chart,
                'milling':temp.milling,
                'post_precipitation':temp.post_precipitation,
                'filtration_b':temp.filtration_b,
                'ph_adjustment':temp.ph_adjustment,
                'sieving':temp.sieving,
                'magnetic_particle_seperation':temp.magnetic_particle_seperation,
                'blending':temp.blending,
                'heat_sterilization':temp.heat_sterilization,
                'spent_stripping':temp.spent_stripping,
                'stirring':temp.stirring,
                'blow_off':temp.blow_off,
                'washing':temp.washing,
                'hexane_recover':temp.hexane_recover,
                'remarks':temp.remarks,
                'bmr_no':temp.bmr_no,
                'batch_allocation_date':temp.batch_allocation_date,
                'batch_end_date':temp.batch_end_date,
                'status':'',
                'subplant_id':temp.subplant_id.id,
                'batch_id':temp.batch_id.id,
                'batch_size':temp.batch_size,
                'production_date':temp.production_date,
                'production_name':temp.production_name,
                'category_type':temp.category_type,
                'created_by':temp.created_by.id,
                'checked_by':temp.checked_by.id,
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
                production = self.pool.get('prakruti.rm_assay').create(cr,uid, {
                    'material_id': item.material_id.id,
                    'rm_assay': item.rm_assay,
                    'rm_assay_output': item.rm_assay_output,
                    'output_yield': item.output_yield,
                    #'rm_assay_output_o': item.rm_assay_output_o,
                    #'rm_assay_t': item.rm_assay_t,
                    #'rm_assay_output_t': item.rm_assay_output_t,
                    'production_id': ebsl_id
                    })
            for item in temp.pulverization_production_id:
                pulverization = self.pool.get('prakruti.production_pulverization').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'qty_charge_pulverizer': item.qty_charge_pulverizer,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'qty_powder': item.qty_powder,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'pulverization_id': ebsl_id
                    })
            for item in temp.extraction_production_id:
                extraction = self.pool.get('prakruti.production_extraction').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'equipment': item.equipment.id,
                    'from_time': item.from_time,
                    'to_time': item.to_time,
                    'fresh': item.fresh,
                    'recd': item.recd,
                    'counter_current_ext_no': item.counter_current_ext_no,
                    'qty': item.qty,
                    'total': item.total,
                    'extract_qty_ltr': item.extract_qty_ltr,
                    'tds_per': item.tds_per,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'extraction_id': ebsl_id
                    })
            for item in temp.precipitation_production_id:
                precipitation = self.pool.get('prakruti.production_precipitation').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'extract_charged': item.extract_charged,
                    'precipitation_start': item.precipitation_start,
                    'precipitation_end': item.precipitation_end,
                    'ph_value': item.ph_value,
                    'consumable': item.consumable,
                    'filtration_start': item.filtration_start,
                    'filtration_end': item.filtration_end,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'precipitation_id': ebsl_id
                    })
            for item in temp.ph_adjustment_id:
                pulverization = self.pool.get('prakruti.production_ph_adjustment').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'solvent_name': item.solvent_name,
                    'solvent_qty': item.solvent_qty,
                    'start_time': item.start_time,
                    'ph_value': item.ph_value,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'pulverization_id': ebsl_id
                    })
            for item in temp.precipitation_post_id:
                pulverization = self.pool.get('prakruti.production_post_precipitation').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'solvent_consumed': item.solvent_consumed,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'pulverization_id': ebsl_id
                    })
            for item in temp.filtrationb_id:
                pulverization = self.pool.get('prakruti.production_filtration_b').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'input_qty': item.input_qty,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'output_qty': item.output_qty,
                    'done_by': item.done_by,
                    'temperature': item.temperature,
                    'solvent_qty': item.solvent_qty,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'pulverization_id': ebsl_id
                    })
            for item in temp.bleaching_production_id:
                bleaching = self.pool.get('prakruti.production_bleaching').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'heating_start_time': item.heating_start_time,
                    'bleaching_agent_qty': item.bleaching_agent_qty,
                    'bleaching_agent_name': item.bleaching_agent_name,
                    'temperature': item.temperature,
                    'heating_stop_time': item.heating_stop_time,
                    'cooling_start_time': item.cooling_start_time,
                    'cooling_end_time': item.cooling_end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'bleaching_id': ebsl_id
                    })
            for item in temp.filtration_production_id:
                filtration = self.pool.get('prakruti.production_filtration').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'no_of_filter_plates': item.no_of_filter_plates,
                    'start_time': item.start_time,
                    'water_wash_start_time': item.water_wash_start_time,
                    'water_wash_end_time': item.water_wash_end_time,
                    'end_time': item.end_time,
                    'done_by': item.done_by,
                    'machine_id': item.machine_id.id,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'filtration_id': ebsl_id
                    })
            for item in temp.concentration_production_id:
                concentration = self.pool.get('prakruti.production_concentration').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'qty_charged_lts': item.qty_charged_lts,
                    'temperature': item.temperature,
                    'qty_recovered_solvent': item.qty_recovered_solvent,
                    'qty_concentrate_collected': item.qty_concentrate_collected,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'concentration_id': ebsl_id
                    })
            for item in temp.evaporation_production_id:
                evaporation = self.pool.get('prakruti.production_evaporation').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'equipment_code': item.equipment_code.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'qty_charged_lts': item.qty_charged_lts,
                    'temperature': item.temperature,
                    'qty_recovered_solvent': item.qty_recovered_solvent,
                    'qty_concentrate_collected': item.qty_concentrate_collected,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'evaporation_id': ebsl_id
                    })
            for item in temp.stripping_production_id:
                stripping_purging = self.pool.get('prakruti.production_stripping_purging').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'stripping_start_time': item.stripping_start_time,
                    'stripping_end_time': item.stripping_end_time,
                    'purging_start_time': item.purging_start_time,
                    'purging_end_time': item.purging_end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'machine_id': item.machine_id.id,
                    'stripping_purging_id': ebsl_id
                    })
            for item in temp.cooling_production_id:
                cooling_unloading = self.pool.get('prakruti.production_cooling_unloading').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'spent_cooling_start_time': item.spent_cooling_start_time,
                    'spent_cooling_end_time': item.spent_cooling_end_time,
                    'spent_unloading_start_time': item.spent_unloading_start_time,
                    'spent_unloading_end_time': item.spent_unloading_end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'cooling_unloading_id': ebsl_id
                    })
            for item in temp.maturation_production_id:
                maturation_crystalization = self.pool.get('prakruti.production_maturation_crystalization').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'weight_oleoresin': item.weight_oleoresin,
                    'volume_ethyl_added': item.volume_ethyl_added,
                    'volume_crystal_solvent': item.volume_crystal_solvent,
                    'adding_mixing_start_time': item.adding_mixing_start_time,
                    'adding_mixing_end_time': item.adding_mixing_end_time,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'maturation_id': ebsl_id
                    })
            for item in temp.stirring_production_id:
                stirring_settling = self.pool.get('prakruti.production_stirring_settling').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'qty_solvent': item.qty_solvent,
                    'qty_solvent_recovered': item.qty_solvent_recovered,
                    'qty_solvent_used': item.qty_solvent_used,
                    'stirring_start_time': item.stirring_start_time,
                    'stirring_end_time': item.stirring_end_time,
                    'settling_start_time': item.settling_start_time,
                    'settling_end_time': item.settling_end_time,
                    'separation_start_time': item.separation_start_time,
                    'separation_end_time': item.separation_end_time,
                    'done_by': item.done_by,
                    'machine_id': item.machine_id.id,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'stirring_settling_id': ebsl_id
                    })
            for item in temp.water_stripping_production_id:
                water_stripping = self.pool.get('prakruti.production_water_stripping').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'from_time': item.from_time,
                    'to_time': item.to_time,
                    'qty_water_charged': item.qty_water_charged,
                    'temperature': item.temperature,
                    'vaccum': item.vaccum,
                    'qty_distilled_water': item.qty_distilled_water,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'water_stripping_id': ebsl_id
                    })
            for item in temp.charcolization_production_id:
                charcolization = self.pool.get('prakruti.production_charcolization').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'from_time': item.from_time,
                    'to_time': item.to_time,
                    'qty_charged': item.qty_charged,
                    'temperature': item.temperature,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'charcoalization_id': ebsl_id
                    })
            for item in temp.spray_production_id:
                spray_drying = self.pool.get('prakruti.production_spray_drying').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'from_time': item.from_time,
                    'to_time': item.to_time,
                    'qty_charged': item.qty_charged,
                    'temperature_inlet': item.temperature_inlet,
                    'temperature_outlet': item.temperature_outlet,
                    'dried_qty': item.dried_qty,
                    'done_by': item.done_by,
                    'machine_id': item.machine_id.id,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'spray_drying_id': ebsl_id
                    })
            for item in temp.milling_production_id:
                milling = self.pool.get('prakruti.production_milling').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'batch_no': item.batch_no,
                    'lot_no': item.lot_no,
                    'mesh_id': item.mesh_id.id,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'return_qty': item.return_qty,
                    'done_by': item.done_by,
                    'machine_id': item.machine_id.id,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'milling_id': ebsl_id
                    })
            for item in temp.sieving_production_id:
                sieving = self.pool.get('prakruti.production_sieving').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'batch_no': item.batch_no,
                    'lot_no': item.lot_no,
                    'sieve_id': item.sieve_id.id,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'return_qty': item.return_qty,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'sieving_id': ebsl_id
                    })
            for item in temp.magnetic_production_id:
                magnetic_particle_separation = self.pool.get('prakruti.production_magnetic_particle_separation').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'batch_no': item.batch_no,
                    'lot_no': item.lot_no,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'magnetic_separation_id': ebsl_id
                    })
            for item in temp.blending_production_id:
                blending = self.pool.get('prakruti.production_blending').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'batch_no': item.batch_no,
                    'batch_capacity': item.batch_capacity,
                    'batch_id': item.batch_id.id,
                    'lot_no': item.lot_no,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'machine_id': item.machine_id.id,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'blending_id': ebsl_id
                    })
            for item in temp.sterilization_production_id:
                heat_sterilization = self.pool.get('prakruti.production_heat_sterilization').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'input_qty': item.input_qty,
                    'output_qty': item.output_qty,
                    'done_by': item.done_by,
                    'machine_id': item.machine_id.id,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'heat_sterilization_id': ebsl_id
                    })
            for item in temp.packing_production_id:
                packing = self.pool.get('prakruti.production_packing').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'std_time': item.std_time,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'packing_style': item.packing_style,
                    'no_of_packing': item.no_of_packing,
                    'machine_id': item.machine_id.id,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'packing_id': ebsl_id
                    })
            for item in temp.breakdown_production_id:
                breakdown = self.pool.get('prakruti.production_breakdown').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'machine_id': item.machine_id.id,
                    'breakdown_id': item.breakdown_id.id,
                    'running_hours': item.running_hours,
                    'breakdown_hours': item.breakdown_hours,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'breakdown_grid_id': ebsl_id
                    })
            for item in temp.extraction_drying_id:
                drying = self.pool.get('prakruti.production_drying').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'std_time': item.std_time,
                    'qty_charged': item.qty_charged,
                    'from_time': item.from_time,
                    'to_time': item.to_time,
                    'temperature_inlet': item.temperature_inlet,
                    'temperature_outlet': item.temperature_outlet,
                    'dried_qty': item.dried_qty,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'drying_id': ebsl_id
                    })
            for item in temp.blow_off_line:
                blow_off = self.pool.get('prakruti.blow_off_line').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temperature': item.temperature,
                    'quantity': item.quantity,
                    'purity_percent': item.purity_percent,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'blow_off_id': ebsl_id
                    })
            for item in temp.washing_line:
                washing = self.pool.get('prakruti.washing_line').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'temperature': item.temperature,
                    'quantity': item.quantity,
                    'solvent': item.solvent,
                    'done_by': item.done_by,
                    'checked_by': item.checked_by,
                    'machine_id': item.machine_id.id,
                    'remarks': item.remarks,
                    'washing_id': ebsl_id
                    })
            for item in temp.hexane_recovery_line:
                hexane_recovery = self.pool.get('prakruti.hexane_recovery_line').create(cr,uid, {
                    'process_id': item.process_id.id,
                    'shift_id': item.shift_id.id,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'quantity': item.quantity,
                    'temperature': item.temperature,
                    'vacuum': item.vacuum,
                    'hexane_recover': item.hexane_recover,
                    'residue': item.residue,
                    'done_by': item.done_by,
                    'machine_id': item.machine_id.id,
                    'checked_by': item.checked_by,
                    'remarks': item.remarks,
                    'hexane_recovery_id': ebsl_id
                    })
            cr.execute('''UPDATE prakruti_production SET revise_status = 'revise_extraction',is_revise = 'True' WHERE id = %s''',((temp.id),))
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
                    cr.execute('''SELECT revise_production (%s,%s,%s)''',((temp.id),(temp.batch_id.id),(temp.subplant_id.subplant_id.id),))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 
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
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete, Since the Batch is Alloted'))
        return super(PrakrutiProduction, self).unlink()
    
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
            'precipitation': process_type.precipitation,
            'bleaching': process_type.bleaching,
            'filtration': process_type.filtration,
            'concentration': process_type.concentration,
            'evaporation': process_type.evaporation,
            'spent_cooling_unloading': process_type.spent_cooling_unloading,
            'maturation_crystalization': process_type.maturation_crystalization,
            'water_striiping_chart': process_type.water_striiping_chart,
            'charcolisation_chart': process_type.charcolisation_chart,
            'spray_drying_chart': process_type.spray_drying_chart,
            'drying_chart': process_type.drying_chart,
            'milling': process_type.milling,
            'sieving': process_type.sieving,
            'magnetic_particle_seperation': process_type.magnetic_particle_seperation,
            'blending': process_type.blending,
            'heat_sterilization':process_type.heat_sterilization,
            'spent_stripping':process_type.spent_stripping,
            'stirring':process_type.stirring,
            'bmr_no': process_type.bmr_no,            
            'blow_off':process_type.blow_off,
            'washing':process_type.washing,
            'post_precipitation':process_type.post_precipitation,
            'filtration_b':process_type.filtration_b,
            'ph_adjustment':process_type.ph_adjustment,
            'hexane_recover':process_type.hexane_recover
            }
        return {'value': result}
    
    '''
    calculation for Total Extract charged
    '''
    @api.depends('concentration_production_id.qty_charged_lts')
    def _compute_extract_charged(self):
        for order in self:
            extract_charged = 0.0
            for line in order.concentration_production_id:
                extract_charged += line.qty_charged_lts 
                order.update({
                        'total_extract_charged': extract_charged
                        })
    '''
    calculation for Total semi concentrate
    '''            
    @api.depends('concentration_production_id.qty_concentrate_collected')
    def _compute_semi_concentrate(self):
        for order in self:
            semi_concentrate = 0.0
            for line in order.concentration_production_id:
                semi_concentrate += line.qty_concentrate_collected 
                order.update({
                        'total_semi_concentrate': semi_concentrate
                        })
    '''
    calculation for Total solvent recovered
    '''            
    @api.depends('concentration_production_id.qty_recovered_solvent')
    def _compute_total_solvent(self):
        for order in self:
            total_solvent = 0.0
            for line in order.concentration_production_id:
                total_solvent += line.qty_recovered_solvent 
                order.update({
                        'total_solvent_recovered': total_solvent
                        })
    
    '''
    calculation for Total Extract charged evaporation
    '''
    @api.depends('evaporation_production_id.qty_charged_lts')
    def _compute_extract_charged_eve(self):
        for order in self:
            extract_charged_eve = 0.0
            for line in order.evaporation_production_id:
                extract_charged_eve += line.qty_charged_lts 
                order.update({
                        'total_extract_charged_eve': extract_charged_eve
                        })
    '''
    calculation for Total semi concentrate evaporation
    '''            
    @api.depends('evaporation_production_id.qty_concentrate_collected')
    def _compute_semi_concentrate_eve(self):
        for order in self:
            semi_concentrate_eve = 0.0
            for line in order.evaporation_production_id:
                semi_concentrate_eve += line.qty_concentrate_collected 
                order.update({
                        'total_semi_concentrate_eve': semi_concentrate_eve
                        })
    '''
    calculation for Total solvent recovered evaporation
    '''             
    @api.depends('evaporation_production_id.qty_recovered_solvent')
    def _compute_total_solvent_eve(self):
        for order in self:
            total_solvent_eve = 0.0
            for line in order.evaporation_production_id:
                total_solvent_eve += line.qty_recovered_solvent 
                order.update({
                        'total_solvent_recovered_eve': total_solvent_eve
                        })
    '''
    calculation for Total input qty
    '''            
    @api.depends('milling_production_id.input_qty')
    def _compute_total_input_qty(self):
        for order in self:
            input_qty_mi = 0.0
            for line in order.milling_production_id:
                input_qty_mi += line.input_qty 
                order.update({
                        'total_input_qty': input_qty_mi
                        })
    '''
    calculation for Total output qty
    '''             
    @api.depends('milling_production_id.output_qty')
    def _compute_total_output_qty(self):
        for order in self:
            output_qty_mi = 0.0
            for line in order.milling_production_id:
                output_qty_mi += line.output_qty 
                order.update({
                        'total_output_qty': output_qty_mi
                        })
    '''
    calculation for Total input qty sieving
    '''            
    @api.depends('sieving_production_id.input_qty')
    def _compute_total_input_qty_si(self):
        for order in self:
            input_qty_si = 0.0
            for line in order.sieving_production_id:
                input_qty_si += line.input_qty 
                order.update({
                        'total_input_qty_si': input_qty_si
                        })
    '''
    calculation for Total output qty sieving
    '''            
    @api.depends('sieving_production_id.output_qty')
    def _compute_total_output_qty_si(self):
        for order in self:
            output_qty_si = 0.0
            for line in order.sieving_production_id:
                output_qty_si += line.output_qty 
                order.update({
                        'total_output_qty_si': output_qty_si
                        })
        
    '''
    calculation for Total input qty Magnetic production
    ''' 
                
    @api.depends('magnetic_production_id.input_qty')
    def _compute_total_input_qty_ms(self):
        for order in self:
            input_qty_ms = 0.0
            for line in order.magnetic_production_id:
                input_qty_ms += line.input_qty 
                order.update({
                        'total_input_qty_ms': input_qty_ms
                        })
    '''
    #calculation for Total output qty Magnetic production
    '''             
    @api.depends('magnetic_production_id.output_qty')
    def _compute_total_output_qty_ms(self):
        for order in self:
            output_qty_ms = 0.0
            for line in order.magnetic_production_id:
                output_qty_ms += line.output_qty 
                order.update({
                        'total_output_qty_ms': output_qty_ms
                        })
                
    '''
    calculation for Total input qty blending
    '''              
    @api.depends('blending_production_id.input_qty')
    def _compute_total_input_qty_bl(self):
        for order in self:
            input_qty_bl = 0.0
            for line in order.blending_production_id:
                input_qty_bl += line.input_qty 
                order.update({
                        'total_input_qty_bl': input_qty_bl
                        })
    '''
    calculation for Total output qty blending
    '''             
    @api.depends('blending_production_id.output_qty')
    def _compute_total_output_qty_bl(self):
        for order in self:
            output_qty_bl = 0.0
            for line in order.blending_production_id:
                output_qty_bl += line.output_qty 
                order.update({
                        'total_output_qty_bl': output_qty_bl
                        })

    '''
    calculation for Total input qty Sterilization
    '''             
    @api.depends('sterilization_production_id.input_qty')
    def _compute_total_input_qty_hs(self):
        for order in self:
            input_qty_hs = 0.0
            for line in order.sterilization_production_id:
                input_qty_hs += line.input_qty 
                order.update({
                        'total_input_qty_hs': input_qty_hs
                        })
                
    '''
    calculation for Total output qty Sterilization
    ''' 
    @api.depends('sterilization_production_id.output_qty')
    def _compute_total_output_qty_hs(self):
        for order in self:
            output_qty_hs = 0.0
            for line in order.sterilization_production_id:
                output_qty_hs += line.output_qty 
                order.update({
                        'total_output_qty_hs': output_qty_hs
                        })
    '''
    allocating batch no 
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
            cr.execute("UPDATE prakruti_batch_master AS b SET batch_allocated_by = 'extraction',batch_allocated_flag = 1 FROM(SELECT batch_id FROM prakruti_production WHERE  id= %s ) AS a WHERE a.batch_id = b.id",((temp.id),))
            cr.execute("UPDATE prakruti_production SET status = 'batch_alloted' WHERE id = %s",((temp.id),))
        return {}
     
    
    #_sql_constraints = [        
        #('production_uniq_with_batch_date','unique(batch_id,production_date)', 'This production Batch is already Entered for this Date. Please check and retry !'),       
        #('production_uniq_with_batch_subplant_date','unique(subplant_id,batch_id,production_date)', 'This batch is already in Use. Please check and retry !'),   
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
                                prakruti_bill_of_material_line.material_id,
                                prakruti_bill_of_material.batch_id 
                            FROM 
                                prakruti_bill_of_material_line INNER JOIN 
                                prakruti_bill_of_material ON 
                                prakruti_bill_of_material_line.main_id = prakruti_bill_of_material.id  
                            WHERE 
                                prakruti_bill_of_material.batch_id =%s''',((temp.batch_id.id),))
            for line in cr.dictfetchall():
                material_id = line['material_id']
                grid_line_entry = self.pool.get('prakruti.rm_assay').create(cr,uid,{
                    'material_id':material_id,
                    'production_id':temp.id
                    })
            cr.execute('UPDATE prakruti_production SET flag_display_product = 1,flag_delete_product = 0 WHERE prakruti_production.id = %s',((temp.id),))
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
            cr.execute("DELETE FROM prakruti_rm_assay WHERE prakruti_rm_assay.production_id = %s", ((temp.id),))
            cr.execute("UPDATE prakruti_production SET flag_delete_product = 1,flag_display_product = 0 WHERE prakruti_production.id = %s",((temp.id),))
        return {}
    
class PrakrutiProductionPulverization(models.Model):
    _name ='prakruti.production_pulverization'
    _table = 'prakruti_production_pulverization'
    _description = 'Production Pulverisation'
        
    pulverization_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")    
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    qty_charge_pulverizer =  fields.Float(string='Qty RM Charged to pulverizer',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    qty_powder= fields.Float(string='Qty of Powder obtained(Kg)',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, pulverization_id)', 'Process Name must be Unique for Pulverization')
        #]  
        
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
    
    #def _check_qty_charge_pulverizer(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_charge_pulverizer <= 0:
                #return False
            #return True
    
    #def _check_qty_powder(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_powder <= 0:
                #return False
            #return True
       
    #_constraints = [        
        #(_check_qty_charge_pulverizer,'Qty Charge Pulveriser cannot be negative or zero!',['qty_charge_pulverizer']),
        #(_check_qty_powder,'Qty Powder cannot be negative or zero!',['qty_powder'])       
    #]
    
    
class PrakrutiProductionExtraction(models.Model):
    _name ='prakruti.production_extraction'
    _table = 'prakruti_production_extraction'
    _description = 'Production Extraction'
        
    extraction_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")  
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')  
    equipment = fields.Many2one('prakruti.machine',string='Equipment')
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    fresh = fields.Char(string='Fresh')
    recd = fields.Char(string='Recd')
    counter_current_ext_no = fields.Char(string='Counter Current Ext No.')
    qty = fields.Float(string='Qty(Ltr)',digits=(6,3))
    total = fields.Float(string='Total(Ltr)',digits=(6,3))
    extract_qty_ltr= fields.Float('Extract Qty Ltr',digits=(6,3))
    tds_per = fields.Float(string='%TDS',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')    
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, extraction_id)', 'Process Name must be Unique for Extraction')
        #]
        
    #@api.one
    #@api.constrains('from_time')
    #def _check_from_time(self):
        #if self.from_time < fields.Date.today():
            #raise ValidationError(
                #"From date can't be less than current date!")  
        
    #@api.one
    #@api.constrains('total')
    #def _check_total(self):
        #if self.total <= 0:
            #raise ValidationError(
                #"Total ltr cannot be negative or zero!'")  
        
    #@api.one
    #@api.constrains('to_time')
    #def _check_to_time(self):
        #if self.to_time < self.from_time:
            #raise ValidationError(
                #"End Date can't be less than From date!")
    
    
    
    #def _check_qty(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty <= 0:
                #return False
            #return True
        
    #def _check_extract_qty(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.extract_qty_ltr <= 0:
                #return False
            #return True
        
    #_constraints = [        
        #(_check_qty,'Qty  cannot be negative or zero!',['qty']),
        #(_check_extract_qty,'Extract Qty  cannot be negative or zero!',['extract_qty_ltr'])
    #]
    
  
class PrakrutiProductionPrePrecipitation(models.Model):
    _name='prakruti.production_precipitation'
    _table = 'prakruti_production_precipitation'
    _description = 'Production Pre Precipitation'
        
    precipitation_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    extract_charged= fields.Float(string='Extract Charged',digits=(6,3))
    precipitation_start = fields.Datetime(string='Precipitation Start')
    precipitation_end = fields.Datetime(string='Precipitation End')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    ph_value = fields.Float(string='pH',digits=(6,3))
    consumable = fields.Char(string='Consumable')
    filtration_start = fields.Datetime(string='Filtration Start')
    filtration_end = fields.Datetime(string='Filtration End')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, precipitation_id)', 'Process Name must be Unique for Precipitation')
        #]
        
    #@api.one
    #@api.constrains('precipitation_start')
    #def _check_precipitation_start(self):
        #if self.precipitation_start < fields.Date.today():
            #raise ValidationError(
                #"Precipitation Start  can't be less than Current date!")
        
    #@api.one
    #@api.constrains('precipitation_end')
    #def _check_precipitation_end(self):
        #if self.precipitation_end < self.precipitation_start:
            #raise ValidationError(
                #"Precipitation End  can't be less than Precipitation Start !")
        
    #@api.one
    #@api.constrains('filtration_start')
    #def _check_filtration_start(self):
        #if self.filtration_start < fields.Date.today():
            #raise ValidationError(
                #"Filtration Start  can't be less than Current date!")
        
    #@api.one
    #@api.constrains('filtration_end')
    #def _check_filtration_end(self):
        #if self.filtration_end < self.filtration_start:
            #raise ValidationError(
                #"Filtration End  can't be less than Filtration Start !")
    
          
    #def _check_extract_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.extract_charged <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_extract_charged, 'Extract Charged cannot be negative or zero !', ['extract_charged']),
        #]
    
    
        
class PrakrutiProductionBleaching(models.Model):
    _name='prakruti.production_bleaching'
    _table = 'prakruti_production_bleaching'
    _description = 'Production Bleaching'
    
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    heating_start_time = fields.Datetime(string='Heating Start Time')
    bleaching_agent_qty = fields.Float(string='Bleaching Agent Qty Used',digits=(6,3))
    bleaching_agent_name = fields.Char(string='Bleaching Agent Name')
    temperature = fields.Float(string='Temperature',digits=(6,3))
    heating_stop_time = fields.Datetime(string='Heating Stop Time')
    cooling_start_time = fields.Datetime(string='Cooling Start Time')
    cooling_end_time = fields.Datetime(string='Cooling End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')    
    bleaching_id = fields.Many2one('prakruti.production')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, bleaching_id)', 'Process Name must be Unique for Bleaching')
        #]
        
    #@api.one
    #@api.constrains('bleaching_agent_qty')
    #def _check_bleaching_agent_qty(self):
        #if self.bleaching_agent_qty < 0:
            #raise ValidationError(
                #"Bleaching Agent Qty Used  can't be Negative!")
        
    #@api.one
    #@api.constrains('heating_start_time')
    #def _check_heating_start_time(self):
        #if self.heating_start_time < fields.Date.today():
            #raise ValidationError(
                #"Heating Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('heating_stop_time')
    #def _check_heating_stop_time(self):
        #if self.heating_stop_time < self.heating_start_time:
            #raise ValidationError(
                #"Heating End Time can't be less than Heating Start Time  !")
        
    #@api.one
    #@api.constrains('cooling_start_time')
    #def _check_cooling_start_time(self):
        #if self.cooling_start_time < fields.Date.today():
            #raise ValidationError(
                #"Cooling Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('cooling_end_time')
    #def _check_cooling_end_time(self):
        #if self.cooling_end_time < self.cooling_start_time:
            #raise ValidationError(
                #"Cooling End Time can't be less than Cooling Start Time  !")
    
class PrakrutiProductionFiltration(models.Model):
    _name='prakruti.production_filtration'
    _table = 'prakruti_production_filtration'
    _description = 'Production Filtration A'
        
    filtration_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    no_of_filter_plates = fields.Float(string='No of Filter Plates',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    water_wash_start_time = fields.Datetime(string='Water Wash Start Time')
    water_wash_end_time = fields.Datetime(string='Water Wash End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    end_time = fields.Datetime(string='End Time')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')    
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, filtration_id)', 'Process Name must be Unique for Filteration')
        #]
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
    
        
    #@api.one
    #@api.constrains('water_wash_start_time')
    #def _check_water_wash_start_time(self):
        #if self.water_wash_start_time < fields.Date.today():
            #raise ValidationError(
                #" Water Wash Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('water_wash_end_time')
    #def _check_water_wash_end_time(self):
        #if self.water_wash_end_time < self.water_wash_start_time:
            #raise ValidationError(
                #" Water Wash End Time can't be less than Water Wash Start time!")
        
        
        
        
class PrakrutiProductionConcentration(models.Model):
    _name='prakruti.production_concentration'
    _table = 'prakruti_production_concentration'
    _description = 'Production Concentration'
    
    concentration_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    qty_charged_lts= fields.Float(string='Qty Charged Lts',digits=(6,3))
    temperature = fields.Float(string='Temperature',digits=(6,3))
    qty_recovered_solvent = fields.Float(string='Qty of Recovered Solvent Lts',digits=(6,3))
    qty_concentrate_collected = fields.Float(string='Qty of Concentrate Collected',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, concentration_id)', 'Process Name must be Unique for Concentration')
        #]
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
    
        
    #@api.one
    #@api.constrains('water_wash_start_time')
    #def _check_water_wash_start_time(self):
        #if self.water_wash_start_time < fields.Date.today():
            #raise ValidationError(
                #" Water Wash Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('water_wash_end_time')
    #def _check_water_wash_end_time(self):
        #if self.water_wash_end_time < self.water_wash_start_time:
            #raise ValidationError(
                #" Water Wash End Time can't be less than Water Wash Start time!")
    
    #def _check_qty_charged_lts(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_charged_lts <= 0:
                #return False
            #return True
        
    #def _check_qty_recovered_solvent(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_recovered_solvent <= 0:
                #return False
            #return True
        
    #def _check_qty_concentrate_collected(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_concentrate_collected <= 0:
                #return False
            #return True
        
    #def _check_total_extract_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.total_extract_charged <= 0:
                #return False
            #return True
        
    #def _check_total_semi_concentrate(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.total_semi_concentrate <= 0:
                #return False
            #return True
        
    #def _check_total_solvent_recovered(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.total_solvent_recovered <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_qty_charged_lts, 'Qty Charged Liters cannot be negative or zero !', ['qty_charged_lts']),
       #(_check_total_extract_charged, 'Total Extract Charged Liters cannot be negative or zero !', ['total_extract_charged']),
       #(_check_total_semi_concentrate, 'Total semi concentrate cannot be negative or zero !', ['total_semi_concentrate']),
       #(_check_total_solvent_recovered, 'Total solvent recovered cannot be negative or zero !', ['total_solvent_recovered']),
       #(_check_qty_recovered_solvent, ' Recovered solvent cannot be negative or zero !', ['qty_recovered_solvent']),
       #(_check_qty_concentrate_collected, 'Concentrate collected cannot be negative or zero !', ['qty_concentrate_collected']),
        #]
    
class PrakrutiProductionEvaporation(models.Model):
    _name='prakruti.production_evaporation'
    _table = 'prakruti_production_evaporation'
    _description = 'Production Evaporation'
    
    evaporation_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    equipment_code = fields.Many2one('prakruti.machine',string='Equipment')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    qty_charged_lts= fields.Float(string='Qty Charged Lts',digits=(6,3))
    temperature = fields.Float(string='Temperature',digits=(6,3))
    qty_recovered_solvent = fields.Float(string='Qty of Recovered Solvent Lts',digits=(6,3))
    qty_concentrate_collected = fields.Float(string='Qty of Concentrate Collected',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, evaporation_id)', 'Process Name must be Unique for Evaporation')
        #]
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
    
    #def _check_qty_charged_liters(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_charged_lts <= 0:
                #return False
            #return True
        
    
        
    #def _check_qty_recovered_solvent(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_recovered_solvent <= 0:
                #return False
            #return True
        
    #def _check_qty_concentrate_collected(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_concentrate_collected <= 0:
                #return False
            #return True
        
    #def _check_total_extract_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.total_extract_charged <= 0:
                #return False
            #return True
        
    #def _check_total_semi_concentrate(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.total_semi_concentrate <= 0:
                #return False
            #return True
        
    #def _check_total_solvent_recovered(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.total_solvent_recovered <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_qty_charged_liters, 'Qty Charged Liters cannot be negative or zero !', ['qty_charged_lts']),
       #(_check_total_extract_charged, 'Total Extract Charged Liters cannot be negative or zero !', ['total_extract_charged']),
       #(_check_total_semi_concentrate, 'Total semi concentrate cannot be negative or zero !', ['total_semi_concentrate']),
       #(_check_total_solvent_recovered, 'Total solvent recovered cannot be negative or zero !', ['total_solvent_recovered']),
       #(_check_qty_recovered_solvent, ' Recovered solvent cannot be negative or zero !', ['qty_recovered_solvent']),
       #(_check_qty_concentrate_collected, 'Concentrate collected cannot be negative or zero !', ['qty_concentrate_collected']),
        #]
    
    
class PrakrutiProductionStrippingAndPurging(models.Model):
    _name='prakruti.production_stripping_purging'
    _table = 'prakruti_production_stripping_purging'
    _description = 'Production Stripping Purging'
        
    stripping_purging_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    stripping_start_time = fields.Datetime(string='Stripping Start Time')
    stripping_end_time = fields.Datetime(string='Stripping End Time')
    purging_start_time = fields.Datetime(string='Purging Start Time')
    purging_end_time = fields.Datetime(string='Purging End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, stripping_purging_id)', 'Process Name must be Unique for Stripping And Purging')
        #]
        
    #@api.one
    #@api.constrains('stripping_start_time')
    #def _check_stripping_start_time(self):
        #if self.stripping_start_time < fields.Date.today():
            #raise ValidationError(
                #" Stripping Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('stripping_end_time')
    #def _check_stripping_end_time(self):
        #if self.stripping_end_time < self.stripping_start_time:
            #raise ValidationError(
                #"Stripping End Time can't be less than Stripping Start time!")
        
    #@api.one
    #@api.constrains('purging_start_time')
    #def _check_purging_start_time(self):
        #if self.purging_start_time < fields.Date.today():
            #raise ValidationError(
                #" Purging Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('purging_end_time')
    #def _check_purging_end_time(self):
        #if self.purging_end_time < self.purging_start_time:
            #raise ValidationError(
                #" Purging End Time can't be less than Purging Start Time!")
    
class PrakrutiProductionCoolingAndUnloading(models.Model):
    _name='prakruti.production_cooling_unloading'
    _table = 'prakruti_production_cooling_unloading'
    _description = 'Production Cooling & Unloading'
        
    cooling_unloading_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    spent_cooling_start_time = fields.Datetime(string='Spent Cooling Start Time')
    spent_cooling_end_time = fields.Datetime(string='Spent Cooling End Time')
    spent_unloading_start_time = fields.Datetime(string='Spent Unloading Start Time')
    spent_unloading_end_time = fields.Datetime(string='Spent Unloading End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, cooling_unloading_id)', 'Process Name must be Unique for Cooling')
        #]
        
    #@api.one
    #@api.constrains('spent_cooling_start_time')
    #def _check_spent_cooling_start_time(self):
        #if self.spent_cooling_start_time < fields.Date.today():
            #raise ValidationError(
                #" Spent Cooling Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('spent_cooling_end_time')
    #def _check_spent_cooling_end_time(self):
        #if self.spent_cooling_end_time < self.spent_cooling_start_time:
            #raise ValidationError(
                #"Spent Cooling End Time can't be less than Spent Cooling Start time!")
        
    #@api.one
    #@api.constrains('spent_unloading_start_time')
    #def _check_spent_unloading_start_time(self):
        #if self.spent_unloading_start_time < fields.Date.today():
            #raise ValidationError(
                #" Spent Unloading Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('spent_unloading_end_time')
    #def _check_spent_unloading_end_time(self):
        #if self.spent_unloading_end_time < self.spent_unloading_start_time:
            #raise ValidationError(
                #" Spent Unloading End Time can't be less than Spent Unloading Start Time!")

class PrakrutiProductionMaturationAndCrystalization(models.Model):
    _name='prakruti.production_maturation_crystalization'
    _table = 'prakruti_production_maturation_crystalization'
    _description = 'Production Maturation Crystalization'
    
    maturation_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    weight_oleoresin = fields.Float(string='Weight of the oleoresin in kg',digits=(6,3))
    volume_ethyl_added = fields.Char(string='Crystallization Solvent Name')
    volume_crystal_solvent = fields.Float(string='Volume of crystalization Solvent',digits=(6,3))
    adding_mixing_start_time = fields.Datetime(string='Adding & Mixing Start Time')
    adding_mixing_end_time = fields.Datetime(string='Adding & Mixing End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    output_qty = fields.Float(string='Output Qty',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, maturation_id)', 'Process Name must be Unique for Crystalization')
        #]
        
    #@api.one
    #@api.constrains('adding_mixing_start_time')
    #def _check_adding_mixing_start_time(self):
        #if self.adding_mixing_start_time < fields.Date.today():
            #raise ValidationError(
                #" Adding & Mixing  Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('adding_mixing_end_time')
    #def _check_adding_mixing_end_time(self):
        #if self.adding_mixing_end_time < self.adding_mixing_start_time:
            #raise ValidationError(
                #" Adding & Mixing  End Time can't be less than Adding & Mixing  Start Time!")
        
    #@api.one
    #@api.constrains('volume_ethyl_added')
    #def _check_volume_ethyl_added(self):
        #if self.volume_ethyl_added <= 0:
            #raise ValidationError(
                #" Volume of Ethyl Alcohol added can't be Negative!")
    
    #def _check_weight_oleoresin(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.weight_oleoresin <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_weight_oleoresin, 'Please Enter the weight of oleoresin needed!', ['weight_oleoresin']),
        #]
    
class PrakrutiProductionStirringAndSettling(models.Model):
    _name='prakruti.production_stirring_settling'
    _table = 'prakruti_production_stirring_settling'
    _description = 'Production Stiriing Settling'
        
    stirring_settling_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    qty_solvent = fields.Float(string='Qty of solvent used Fresh(AR No)',digits=(6,3))
    qty_solvent_recovered = fields.Float(string='Qty of solvent used Recovered(B.No)',digits=(6,3))
    qty_solvent_used = fields.Float(string='Qty of solvent used (Ltr)',digits=(6,3))
    stirring_start_time = fields.Datetime(string='Stirring Start Time')
    stirring_end_time = fields.Datetime(string='Stirring End Time')
    settling_start_time = fields.Datetime(string='Settling Start Time')
    settling_end_time = fields.Datetime(string='Settling End Time')
    separation_start_time = fields.Datetime(string='Separation Start Time')
    separation_end_time = fields.Datetime(string='Separation End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, stirring_settling_id)', 'Process Name must be Unique for Stirring')
        #]
        
    #@api.one
    #@api.constrains('qty_solvent')
    #def _check_qty_solvent(self):
        #if self.qty_solvent <= 0:
            #raise ValidationError(
                #" Qty of solvent used Fresh(AR No) can't be Negative or 0!")
        
    #@api.one
    #@api.constrains('qty_solvent_recovered')
    #def _check_qty_solvent_recovered(self):
        #if self.qty_solvent_recovered <= 0:
            #raise ValidationError(
                #" Qty of solvent used Recovered(B.No) can't be Negative or 0!")
        
    #@api.one
    #@api.constrains('qty_solvent_used')
    #def _check_qty_solvent_used(self):
        #if self.qty_solvent_used <= 0:
            #raise ValidationError(
                #" Qty of solvent used (Ltr) can't be Negative or 0!")
        
    #@api.one
    #@api.constrains('stirring_start_time')
    #def _check_stirring_start_time(self):
        #if self.stirring_start_time < fields.Date.today():
            #raise ValidationError(
                #" Stirring  Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('stirring_end_time')
    #def _check_stirring_end_time(self):
        #if self.stirring_end_time < self.stirring_start_time:
            #raise ValidationError(
                #" Stirring End Time can't be less than Stirring Start Time!")
        
    #@api.one
    #@api.constrains('settling_start_time')
    #def _check_settling_start_time(self):
        #if self.settling_start_time < fields.Date.today():
            #raise ValidationError(
                #" Separation Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('separation_end_time')
    #def _check_separation_end_time(self):
        #if self.separation_end_time < self.settling_start_time:
            #raise ValidationError(
                #"Separation  End Time can't be less than Separation Start Time!")
    
    
    #def _check_extract_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.extract_charged <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_extract_charged, 'Extract Charged cannot be negative or zero !', ['extract_charged']),
        #]
    
class PrakrutiProductionWaterStripping(models.Model):
    _name = 'prakruti.production_water_stripping'
    _table='prakruti_production_water_stripping'
    _description = 'Production Water Stripping'
        
    water_stripping_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    qty_water_charged = fields.Float(string='Qty Water Charged ltr',digits=(6,3))
    temperature = fields.Float(string='Temperature',digits=(6,3))
    vaccum = fields.Float(string='Vaccum mm Hg',digits=(6,3))
    qty_distilled_water = fields.Float(string='Qty Distilled water',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, water_stripping_id)', 'Process Name must be Unique for Water Stripping')
        #]
        
    #@api.one
    #@api.constrains('from_time')
    #def _check_from_time(self):
        #if self.from_time < fields.Date.today():
            #raise ValidationError(
                #" From Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('to_time')
    #def _check_to_time(self):
        #if self.to_time < self.from_time:
            #raise ValidationError(
                #" To Time can't be less than From time!")
        
    #@api.one
    #@api.constrains('qty_distilled_water')
    #def _check_qty_distilled_water(self):
        #if self.qty_distilled_water < 0:
            #raise ValidationError(
                #"Qty Distilled water can't be Negative!")
    
    
    #def _check_qty_water_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_water_charged <= 0:
                #return False
            #return True
    
     
    #_constraints = [
       #(_check_qty_water_charged, 'Qty Water Charged cannot be negative or zero !', ['qty_water_charged']),
        #]
    
class PrakrutiProductionCharcolization(models.Model):
    _name = 'prakruti.production_charcolization'
    _table = 'prakruti_production_charcolization'
    _description = 'Production Charcolisation'    
        
    charcoalization_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    qty_charged= fields.Float(string='Qty Charged',digits=(6,3))
    temperature = fields.Float(string='Temperature',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, charcoalization_id)', 'Process Name must be Unique for Charcolization')
        #]
        
    #@api.one
    #@api.constrains('from_time')
    #def _check_from_time(self):
        #if self.from_time < fields.Date.today():
            #raise ValidationError(
                #" From Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('to_time')
    #def _check_to_time(self):
        #if self.to_time < self.from_time:
            #raise ValidationError(
                #" To Time can't be less than From time!")
        
    #@api.one
    #@api.constrains('qty_charged')
    #def _check_qty_charged(self):
        #if self.qty_charged < 0:
            #raise ValidationError(
                #"Qty Charged can't be Negative!")
    
    #def _check_qty_charged_lts(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_charged_lts <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_qty_charged_lts, 'Qty Charged Liters cannot be negative or zero !', ['qty_charged_lts']),
        #]
    
class PrakrutiProductionSprayDrying(models.Model):
    _name='prakruti.production_spray_drying'
    _table ='prakruti_production_spray_drying'
    _description = 'Production Spray Drying'
        
    spray_drying_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    qty_charged= fields.Float(string='Qty Charged ltr',digits=(6,3))
    temperature_inlet = fields.Float(string='Temp inlet',digits=(6,3))
    temperature_outlet = fields.Float(string='Temp outlet',digits=(6,3))
    dried_qty = fields.Float(string='Dried Qty kg',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, spray_drying_id)', 'Process Name must be Unique for Spray Drying')
        #]
        
    #@api.one
    #@api.constrains('from_time')
    #def _check_from_time(self):
        #if self.from_time < fields.Date.today():
            #raise ValidationError(
                #" From Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('to_time')
    #def _check_to_time(self):
        #if self.to_time < self.from_time:
            #raise ValidationError(
                #" To Time can't be less than From time!")
        
    #@api.one
    #@api.constrains('qty_charged')
    #def _check_qty_charged(self):
        #if self.qty_charged < 0:
            #raise ValidationError(
                #"Qty Charged can't be Negative!")
    
   
    #def _check_qty_charged(self, cr, uid, ids):
        #lines = self.browse(cr, uid, ids)
        #for line in lines:
            #if line.qty_charged <= 0:
                #return False
            #return True
     
    #_constraints = [
       #(_check_qty_charged, 'Qty Charged  cannot be negative or zero !', ['qty_charged']),
        #]
    
class PrakrutiProductionMilling(models.Model):
    _name='prakruti.production_milling'
    _table ='prakruti_production_milling'
    _description = 'Production Milling'
        
    milling_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    batch_no = fields.Char(string='Batch No')
    lot_no = fields.Char(string='Lot No')
    mesh_id = fields.Many2one('prakruti.mesh_master',string='Mesh Size')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    return_qty= fields.Float(string='Returned Qty',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, milling_id)', 'Process Name must be Unique for Milling')
        #]
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
        
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #" Input Qty can't be Negative or 0 !")
    
        
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #" Output Qty can't be Negative or 0!")
    
class PrakrutiProductionSieving(models.Model):
    _name='prakruti.production_sieving'
    _table ='prakruti_production_sieving'
    _description = 'Production Sieving'
    
    sieving_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    batch_no = fields.Char(string='Batch No')
    lot_no = fields.Char(string='Lot No')
    sieve_id = fields.Many2one('prakruti.sieve_master',string='Seive Size')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    return_qty= fields.Float(string='Returned Qty',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, sieving_id)', 'Process Name must be Unique for Sieving')
        #]
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
        
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #" Input Qty can't be Negative or 0!")
    
        
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #" Output Qty can't be Negative or 0!")

class PrakrutiProductionMagneticParticleSeparation(models.Model):
    _name='prakruti.production_magnetic_particle_separation'
    _table ='prakruti_production_magnetic_particle_separation'
    _description = 'Production Magnetic Particle Seperation'
    
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    start_time = fields.Datetime(string='Start Time ')
    end_time = fields.Datetime(string='End Time')
    batch_no = fields.Char(string='Batch No')
    lot_no = fields.Char(string='Lot No')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    magnetic_separation_id = fields.Many2one('prakruti.production')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, magnetic_separation_id)', 'Process Name must be Unique for Magnetic Seperation')
        #]
    
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
        
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #" Input Qty can't be Negative or 0!")
    
        
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #" Output Qty can't be Negative or 0!")
    
    
class PrakrutiProductionBlending(models.Model):
    _name='prakruti.production_blending'
    _table ='prakruti_production_blending'
    _description = 'Production Blending'
    
    blending_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    batch_no = fields.Char(related = 'batch_id.batch_no',string='Batch No',store = 1)
    batch_capacity = fields.Float(related = 'batch_id.batch_capacity',string='Batch Capacity',store = 1)
    batch_id = fields.Many2one('prakruti.batch_master',string = 'Batch No')
    lot_no = fields.Char(string='Lot No')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, blending_id)', 'Process Name must be Unique for Blending')
        #]
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
        
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #" Input Qty can't be Negative or 0!")
    
        
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #" Output Qty can't be Negative or 0!")
   
class PrakrutiProductionHeatSterilization(models.Model):
    _name='prakruti.production_heat_sterilization'
    _table ='prakruti_production_heat_sterilization'
    _description = 'Production Heat Sterilization'
    
    heat_sterilization_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, heat_sterilization_id)', 'Process Name must be Unique for Heat Sterilization')
        #]
    
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
        
    #@api.one
    #@api.constrains('input_qty')
    #def _check_input_qty(self):
        #if self.input_qty <= 0:
            #raise ValidationError(
                #" Input Qty can't be Negative or 0!")
    
        
    #@api.one
    #@api.constrains('output_qty')
    #def _check_output_qty(self):
        #if self.output_qty <= 0:
            #raise ValidationError(
                #" Output Qty can't be Negative or 0!")
    
class PrakrutiProductionPacking(models.Model):
    _name ='prakruti.production_packing'
    _table = 'prakruti_production_packing'
    _description = 'Production Packing'
    
    packing_id=fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    std_time = fields.Char( string='Standard Time')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    packing_style=fields.Text( string='Packing Style')
    no_of_packing=fields.Float( string='No of Packing',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, packing_id)', 'Process Name must be Unique for Heat Packing')
        #]
        
    #@api.one
    #@api.constrains('start_time')
    #def _check_start_time(self):
        #if self.start_time < fields.Date.today():
            #raise ValidationError(
                #" Start Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('end_time')
    #def _check_end_time(self):
        #if self.end_time < self.start_time:
            #raise ValidationError(
                #" End Time can't be less than Start time!")
    
    
        
class PrakrutiProductionBreakdown(models.Model):
    _name = 'prakruti.production_breakdown'
    _table = 'prakruti_production_breakdown'
    _description = 'Production Breakdown'
    
    breakdown_grid_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    machine_id=fields.Many2one('prakruti.machine',string='Machine')
    breakdown_id=fields.Many2one('prakruti.breakdown_item',string='Break Down Item')
    running_hours=fields.Char(string='Running Hours')
    breakdown_hours=fields.Char(string='Break Down Hours')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    checked_by = fields.Char(string='Solvent Name')
    remarks=fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, breakdown_grid_id)', 'Process Name must be Unique for Breakdown')
        #]

    
class PrakrutiExtractionDrying(models.Model):
    _name = 'prakruti.production_drying'
    _table = 'prakruti_production_drying'
    _description = 'Production Drying'
    
    drying_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    qty_charged= fields.Float(string='Charged Qty(ltr)/No of Tray',digits=(6,3))
    from_time = fields.Datetime(string='Time From')
    to_time = fields.Datetime(string='Time To')
    temperature_inlet = fields.Float(string='Temp inlet',digits=(6,3))
    temperature_outlet = fields.Float(string='Temp outlet',digits=(6,3))
    dried_qty = fields.Float(string='Dried Qty kg',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
    #_sql_constraints=[        
        #('unique_process_id','unique(process_id, drying_id)', 'Process Name must be Unique for Drying')
        #]
    
    #@api.one
    #@api.constrains('dried_qty')
    #def _check_dried_qty(self):
        #if self.dried_qty <= 0:
            #raise ValidationError(
                #" Dried Qty kg can't be Negative or 0!")
    #@api.one
    #@api.constrains('from_time')
    #def _check_from_time(self):
        #if self.from_time < fields.Date.today():
            #raise ValidationError(
                #" From Time can't be less than current time!")
        
    #@api.one
    #@api.constrains('to_time')
    #def _check_to_time(self):
        #if self.to_time < self.from_time:
            #raise ValidationError(
                #" To Time can't be less than From time!")
    
class PrakrutiBlowOff(models.Model):
    _name ='prakruti.blow_off_line'
    _table = 'prakruti_blow_off_line'
    _description = ' Production Blow off Line'
    
    blow_off_id=fields.Many2one('prakruti.production')    
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)    
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temperature = fields.Char(string= 'Temp(C)')
    quantity = fields.Float(string= 'Qty of Aq Solvent(Ltr) Collected')
    purity_percent = fields.Float(string= '\\% \\of Purity')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
class PrakrutiWashingLine(models.Model):
    _name ='prakruti.washing_line'
    _table = 'prakruti_washing_line'
    _description = 'Production Washing Line'
    
    washing_id=fields.Many2one('prakruti.production')    
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")    
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    temperature = fields.Char(string= 'Temp(C)')
    quantity = fields.Float(string= 'Quantity')
    solvent = fields.Float(string= 'Solvent/Material Added')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
class PrakrutiHexaneRecoveryLine(models.Model):
    _name ='prakruti.hexane_recovery_line'
    _table = 'prakruti_hexane_recovery_line'
    _description = 'Production Hexane Recovery Line'
    
    hexane_recovery_id=fields.Many2one('prakruti.production',readonly=1)    
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")    
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    quantity = fields.Float(string= 'Quantity Charged(Ltr)')
    temperature = fields.Char(string= 'Temp(C)')
    vacuum = fields.Char(string= 'Vacuum(mmHg)')
    hexane_recover = fields.Float(string= 'Recovered Hexane(Ltr)')
    residue = fields.Float(string= 'Residue(Kg)')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    checked_by = fields.Char(string='Solvent Name')
    remarks = fields.Text(string='Remarks')
    
class PrakrutiProductionPhAdjustment(models.Model):
    _name ='prakruti.production_ph_adjustment'
    _table = 'prakruti_production_ph_adjustment'
    _description = 'Production PH Adjustment'
    
    ph_adjustment_id=fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    std_time = fields.Char( string='Standard Time')  
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    solvent_name = fields.Char(string='Solvent Name')
    solvent_qty = fields.Float(string='Solvent Qty',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    ph_value = fields.Float(string='pH',digits=(6,3))
    done_by = fields.Char(string='Done By')
    remarks = fields.Text(string='Remarks')
    
    
  
class PrakrutiProductionPostPrecipitation(models.Model):
    _name='prakruti.production_post_precipitation'
    _table = 'prakruti_production_post_precipitation'
    _description = 'Production Post Precipitation'
        
    precipitation_post_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required="True")
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    solvent_consumed = fields.Float(string='Solvent Consumed',digits=(6,3))
    done_by = fields.Char(string='Done By')
    remarks = fields.Text(string='Remarks')
    
class PrakrutiProductionFiltrationB(models.Model):
    _name='prakruti.production_filtration_b'
    _table = 'prakruti_production_filtration_b'
    _description = 'Production Filtration B'
        
    filtrationb_id = fields.Many2one('prakruti.production')
    process_id = fields.Many2one('prakruti.process_order',string='Process Order',required=1)
    shift_id = fields.Many2one('prakruti.shift_assignment',string='Date/Shift')
    std_time = fields.Char(string='Standard Time')
    input_qty = fields.Float(string='Input Qty',digits=(6,3))
    output_qty= fields.Float(string='Output Qty',digits=(6,3))
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    solvent_qty = fields.Float(string='Solvent Qty',digits=(6,3))
    temperature = fields.Float(string='Temperature',digits=(6,3))
    machine_id=fields.Many2one('prakruti.machine',string='Equipment')
    done_by = fields.Char(string='Done By')
    remarks = fields.Text(string='Remarks')
       
class PrakrutiProductionRMAssay(models.Model):
    _name ='prakruti.rm_assay'
    _table = 'prakruti_rm_assay'
    _description = 'Production RM Assay'
    
    production_id = fields.Many2one('prakruti.production')
    material_id = fields.Many2one('product.product', string='Product Name')
    output_yield = fields.Float(string="Output Yield" , digits=(6,3))
    rm_assay = fields.Float(string="Output Assay %" , digits=(6,3))
    rm_assay_output = fields.Float(string="Output Quantity" , digits=(6,3)) 
    #rm_assay_o = fields.Float(string="RM Assay1%" , digits=(6,3))
    #rm_assay_output_o = fields.Float(string="RM Assay Output1" , digits=(6,3))
    #rm_assay_t = fields.Float(string="RM Assay2%" , digits=(6,3))
    #rm_assay_output_t = fields.Float(string="RM Assay Output2" , digits=(6,3))