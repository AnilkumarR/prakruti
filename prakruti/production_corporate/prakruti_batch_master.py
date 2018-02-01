'''
Company : EBSL
Author: Induja
Module: Batch Master
Class 1: PrakrutiBatchMaster
Table 1 : prakruti_batch_master
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
import re
import logging
from openerp.exceptions import ValidationError
from datetime import timedelta
from openerp.tools import email_re, email_split
import json


#########################################################################################################


class PrakrutiBatchMaster(models.Model):
    _name = 'prakruti.batch_master'
    _table = 'prakruti_batch_master'
    _description = 'Batch Master '
    _order= "id desc"
    _rec_name="batch_no"
    
    metal_inspection = fields.Selection(related='subplant_id.metal_inspection', string="Metal Inspection",store=1)    
    inspection = fields.Selection(related='subplant_id.inspection', string="Inspection Details",store=1)    
    tablet_coating = fields.Selection(related='subplant_id.tablet_coating', string="Coating Preparation",store=1)    
    compression = fields.Selection(related='subplant_id.compression', string="Compression",store=1)    
    final_drying = fields.Selection(related='subplant_id.final_drying',  string="Final Drying",store=1)
    semi_drying = fields.Selection(related='subplant_id.semi_drying', string="Semi Drying",store=1)    
    granulation = fields.Selection(related='subplant_id.granulation', string="Granulation",store=1)    
    preparation_of_binder = fields.Selection(related='subplant_id.preparation_of_binder', string="Preparation of Binder",store=1)
    filtration = fields.Selection(related='subplant_id.filtration', string="Filtration",store=1)    
    milling = fields.Selection(related='subplant_id.milling', string="Milling",store=1)
    blending = fields.Selection(related='subplant_id.blending', string="Blending",store=1)
    sieving = fields.Selection(related='subplant_id.sieving', string="Sieving",store=1)
    coating = fields.Selection(related='subplant_id.coating', string="Coating",store=1)
    packing =  fields.Selection(related='subplant_id.packing', string="Packing",store=1)
    coding =  fields.Selection(related='subplant_id.coding', string="Coding",store=1)
    filling =  fields.Selection(related='subplant_id.filling', string="Filling",store=1)
    solvent_name = fields.Selection(related='subplant_id.solvent_name', string="Solvent Name",store=1)
    ph_control_buffer = fields.Selection(related='subplant_id.ph_control_buffer', string="pH control buffer action ",store=1)
    preparation_syrup = fields.Selection(related='subplant_id.preparation_syrup', string="Syrup Preparation",store=1)
    addition_preservative = fields.Selection(related='subplant_id.addition_preservative', string="Addition of Preservative",store=1)
    autoclave = fields.Selection(related='subplant_id.autoclave', string="Autoclave",store=1)
    api_addition = fields.Selection(related='subplant_id.api_addition', string="API Addition",store=1)
    soak_raw_material = fields.Selection(related='subplant_id.soak_raw_material', string="Soak Raw Material",store=1)
    other_ingredient_addition = fields.Selection(related='subplant_id.other_ingredient_addition',string="Other Ingredient Addition",store=1)
    heat_sterilization = fields.Selection(related='subplant_id.heat_sterilization',string="Heat Sterilization",store=1)
    magnetic_particle_seperation = fields.Selection(related='subplant_id.magnetic_particle_seperation',string="Magnetic Particle Seperation",store=1)
    spray_drying_chart = fields.Selection(related='subplant_id.spray_drying_chart',string="Spray Drying Chart",store=1)
    water_striiping_chart = fields.Selection(related='subplant_id.water_striiping_chart',string="Water Strriping Chart",store=1)
    charcolisation_chart = fields.Selection(related='subplant_id.charcolisation_chart',string="Charcolisation Chart",store=1)
    maturation_crystalization = fields.Selection(related='subplant_id.maturation_crystalization',string="Maturation & Crystalization",store=1)
    spent_cooling_unloading = fields.Selection(related='subplant_id.spent_cooling_unloading',string="Spent Cooling & Unloading",store=1)
    spent_stripping = fields.Selection(related='subplant_id.spent_stripping',string="Spent Stripping",store=1)
    stirring = fields.Selection(related='subplant_id.stirring',string="Stirring",store=1)
    evaporation = fields.Selection(related='subplant_id.evaporation',string="Evaporation",store=1)
    concentration = fields.Selection(related='subplant_id.concentration',string="Concentartion",store=1)
    bleaching = fields.Selection(related='subplant_id.bleaching',string="Bleaching",store=1)
    precipitation = fields.Selection(related='subplant_id.precipitation',string="Precipitation",store=1)
    extraction_new = fields.Selection(related='subplant_id.extraction_new',string="Extraction",store=1)
    pulverisation = fields.Selection(related='subplant_id.pulverisation',string="Pulverisation",store=1)
    drying_chart = fields.Selection(related='subplant_id.drying_chart',string="Drying Chart",store=1)
    plant_type = fields.Selection(related='subplant_id.plant_type',string='Plant Type',store=1)
    blow_off = fields.Selection(related='subplant_id.blow_off', string="Blow Off",store=1)
    washing = fields.Selection(related='subplant_id.washing', string="Washing",store=1)
    hexane_recover = fields.Selection(related='subplant_id.hexane_recover', string="Hexane Recovery",store=1)
    extract_solution = fields.Selection([('yes','Yes'),('no','No')],default='yes',string="Extract Solution")
    addition_of_ingredients=fields.Selection([('yes','Yes'),('no','No')], string="Addition Of Ingredients", default='yes')
    
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Sub Plant",required="True")    
    batch_name=fields.Char(string='Batch Name',required="True")
    batch_no=fields.Char(string='Batch No',required="True" )
    batch_allocation_date=fields.Datetime(string='Batch Allocation Date', default=fields.Date.today)
    batch_end_date=fields.Datetime(string='Batch End Date')
    batch_capacity=fields.Float(string='Batch Capacity',required="True",digits=(6,3))
    batch_allocated_by = fields.Selection([('free', 'Free'),('extraction', 'Extraction'),('syrup','Syrup'),('tablet','Tablet'),('formulation','Formulation'),],string='Batch Allocated By',default='free')
    is_batch_closed = fields.Selection([('open', 'Open'),('close', 'Closed')],string='Batch Status',default='open')
    batch_allocated_flag = fields.Integer('Is Allocated',default=0,readonly=True)
    email_template=fields.Char(compute='send_mail',store=True)
    insert_flag = fields.Integer(string= 'Field Insert',default=0,readonly=1)
    insert_into_bom = fields.Char(string='Inserted Or Not',compute='_on_saving_the_record')
    bmr_no = fields.Char(string = 'BMR No')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    
    #Added as per to keep the track that for which Slip Number this Batch is Created 
    #By Karan on 20170921
    slip_id = fields.Many2one('prakruti.production_slip',string= 'Slip No')
    
    formulation_type=fields.Selection(related='subplant_id.formulation_type', string="Formulation Type",store=1) 
    extract_solution_lotion = fields.Selection(related='subplant_id.extract_solution_lotion', string="Extract Solution",store=1)
   
    addition_of_solution = fields.Selection(related='subplant_id.addition_of_solution', string="Addition Of Solution",store=1)
    other_ingredient_addition_lotion = fields.Selection(related='subplant_id.other_ingredient_addition_lotion', string="Other Ingredient Addition",store=1)
    volume_make_up =fields.Selection(related='subplant_id.volume_make_up', string="Volume Make Up",store=1)
    filling_lotion = fields.Selection(related='subplant_id.filling_lotion', string="Filling",store=1) 
    post_precipitation =fields.Selection(related='subplant_id.post_precipitation', string="Post Precipitation",store=1)
    filtration_b =fields.Selection(related='subplant_id.filtration_b', string="Filtration B",store=1)
    ph_adjustment =fields.Selection(related='subplant_id.ph_adjustment', string="PH Adjustment",store=1)
    
    batch_closed_flag = fields.Integer(string="Batch Closed Flag",default=0)
    #This flag will be updated from the PTN so that the batch will not display if the Inward is Done,will be also set to 1 and is used as a domain filter in the PTN
    #Dated : 2017/11/14 By Karan
    is_ptn_done = fields.Integer(string="PTN Closed Flag",default=0) 
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
                context = {}
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.batch_no
            code = record.batch_allocated_by                    
            name_code = "%s : %s" % (name,code)
            res.append((record.id, name_code))
        return res
    
    '''
    Production Screen Update 
    ''' 
    @api.one
    @api.multi
    def refresh_production(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute('''  UPDATE 
                                prakruti_production AS b 
                            SET 
                                pulverisation = a.pulverisation,
                                extraction_new = a.extraction_new,
                                precipitation = a.precipitation,
                                bleaching = a.bleaching,
                                filtration = a.filtration,
                                concentration = a.concentration,
                                evaporation = a.evaporation,
                                spent_cooling_unloading = a.spent_cooling_unloading,
                                maturation_crystalization = a.maturation_crystalization,
                                water_striiping_chart = a.water_striiping_chart,
                                charcolisation_chart = a.charcolisation_chart,
                                spray_drying_chart = a.spray_drying_chart,
                                drying_chart = a.drying_chart,
                                milling = a.milling,
                                sieving = a.sieving,
                                magnetic_particle_seperation = a.magnetic_particle_seperation,
                                blending = a.blending,
                                heat_sterilization = a.heat_sterilization,
                                spent_stripping = a.spent_stripping,
                                stirring = a.stirring,       
                                blow_off = a.blow_off,
                                washing = a.washing,
                                hexane_recover = a.hexane_recover,
                                post_precipitation = a.post_precipitation,
                                filtration_b = a.filtration_b,
                                ph_adjustment = a.ph_adjustment
                            FROM(
                                SELECT 
                                    pulverisation,
                                    extraction_new,
                                    precipitation,
                                    bleaching,
                                    filtration,
                                    concentration,
                                    evaporation,
                                    spent_cooling_unloading,
                                    maturation_crystalization,
                                    water_striiping_chart,
                                    charcolisation_chart,
                                    spray_drying_chart,
                                    drying_chart,
                                    milling,
                                    sieving,
                                    magnetic_particle_seperation,
                                    blending,
                                    heat_sterilization,
                                    spent_stripping,
                                    stirring,         
                                    blow_off,
                                    washing,
                                    hexane_recover,
                                    post_precipitation,
                                    filtration_b,
                                    ph_adjustment,
                                    id 
                                FROM 
                                    prakruti_batch_master 
                                WHERE  
                                    id= %s 
                                ) AS a 
                            WHERE 
                                a.id = b.batch_id''',((temp.id),))
            cr.execute('''  UPDATE 
                                prakruti_syrup_production AS b 
                            SET 
                                pulverisation = a.pulverisation,
                                extract_solution = a.extract_solution,
                                soak_raw_material = a.soak_raw_material,
                                extraction_new = a.extraction_new,
                                autoclave = a.autoclave,
                                addition_preservative = a.addition_preservative,
                                preparation_syrup = a.preparation_syrup,
                                ph_control_buffer = a.ph_control_buffer,
                                solvent_name = a.solvent_name,
                                filling = a.filling,
                                coding = a.coding,
                                packing = a.packing,
                                other_ingredient_addition = a.other_ingredient_addition,
                                filtration = a.filtration
                            FROM(
                                SELECT 
                                    pulverisation,
                                    extract_solution,
                                    soak_raw_material,
                                    extraction_new,
                                    autoclave,
                                    addition_preservative,
                                    preparation_syrup,
                                    ph_control_buffer,
                                    solvent_name,
                                    filling,
                                    coding,
                                    packing,
                                    other_ingredient_addition,
                                    filtration,
                                    id 
                                FROM 
                                    prakruti_batch_master 
                                WHERE  
                                    id= %s 
                                ) AS a 
                            WHERE 
                                a.id = b.batch_id''',((temp.id),))
            cr.execute('''  UPDATE 
                                prakruti_tablet_production AS b 
                            SET 
                                sieving = a.sieving,
                                preparation_of_binder = a.preparation_of_binder,
                                granulation = a.granulation,
                                semi_drying = a.semi_drying,
                                final_drying = a.final_drying,
                                milling = a.milling,
                                blending = a.blending,
                                compression = a.compression,
                                tablet_coating = a.tablet_coating,
                                coating = a.coating,
                                inspection = a.inspection,
                                packing = a.packing,
                                metal_inspection = a.metal_inspection
                            FROM(
                                SELECT 
                                    sieving,
                                    preparation_of_binder,
                                    granulation,
                                    semi_drying,
                                    final_drying,
                                    milling,
                                    blending,
                                    compression,
                                    tablet_coating,
                                    coating,
                                    inspection,
                                    packing,
                                    metal_inspection,
                                    id 
                                FROM 
                                    prakruti_batch_master 
                                WHERE  
                                    id= %s 
                                ) AS a 
                            WHERE 
                                a.id = b.batch_id''',((temp.id),))
            cr.execute('''  UPDATE 
                                prakruti_powder_production AS b 
                            SET 
                                sieving = a.sieving,
                                preparation_of_binder = a.preparation_of_binder,
                                granulation = a.granulation,
                                semi_drying = a.semi_drying,
                                final_drying = a.final_drying,
                                milling = a.milling,
                                api_addition = a.api_addition,
                                blending = a.blending,
                                compression = a.compression,
                                coating = a.coating,
                                tablet_coating = a.tablet_coating,
                                inspection = a.inspection,
                                metal_inspection = a.metal_inspection,
                                packing = a.packing
                            FROM(
                                SELECT 
                                    sieving,
                                    preparation_of_binder,
                                    granulation,
                                    semi_drying,
                                    final_drying,
                                    milling,
                                    api_addition,
                                    coating,
                                    blending,
                                    compression,
                                    tablet_coating,
                                    inspection,
                                    metal_inspection,
                                    packing,
                                    id 
                                FROM 
                                    prakruti_batch_master 
                                WHERE  
                                    id= %s 
                                ) AS a 
                            WHERE 
                                a.id = b.batch_id''',((temp.id),))
        return {}
    
    
    
    
    def onchange_batch_name(self, cr, uid, ids, batch_name, context=None):
        '''
        Batch name should be in this format
        '''
        if batch_name == False:
            return {
                'value': {
                    'batch_name': False
                }
            }

        if re.match("^[ A-Za-z0-9]", batch_name) != None:
            batch_name = batch_name.strip()
            batch_name = batch_name.upper()

            return {
                'value': {
                    'batch_name': batch_name
                }
            }
        
    def onchange_batch_no(self, cr, uid, ids, batch_no, context=None):
        '''
        Batch No should be in this format
        ''' 
        if batch_no == False:
            return {
                'value': {
                    'batch_no': False
                }
            }

        if re.match("^[ A-Za-z0-9]", batch_no) != None:
            batch_no = batch_no.strip()
            batch_no = batch_no.upper()

            return {
                'value': {
                    'batch_no': batch_no
                }
            }
        
        
      
    def onchange_subplant_id(self, cr, uid, ids, subplant_id, context=None):
        '''
        when we select subplant it will automatically extract data from sub plant
        '''
        slip_number = []
        slip_id = ''        
        cr.execute('''  SELECT 
                                prakruti_production_slip.id AS slip_id,
                                prakruti_production_slip.slip_no AS slip_no,
                                prakruti_production_slip_line.product_id AS subplant_id,
                                prakruti_production_slip_line.description AS subplant_name
                        FROM
                                prakruti_production_slip JOIN	
                                prakruti_production_slip_line ON	
                                prakruti_production_slip_line.main_id = prakruti_production_slip.id JOIN	
                                prakruti_sub_plant ON	
                                prakruti_sub_plant.subplant_id = prakruti_production_slip_line.product_id
                        WHERE
                                prakruti_sub_plant.id = CAST(%s AS INTEGER)''', ((subplant_id),))        
        for record in cr.dictfetchall():
            slip_id = record['slip_id']
            slip_number.append((slip_id))
        print 'SLIP NUMBER',slip_number
        return {'value' :{
            'slip_id': slip_id
            }}
    
    
    @api.one
    @api.constrains('slip_id','subplant_id')
    def _check_slip_id(self):
        '''
        This method checks the number of Slip Number associated with this Subplant if Yes than will list it out else will throw an Error
        '''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        slip_number = []
        slip_list = []
        slip_id = ''
        slip_no = ''
        cr.execute('''  SELECT 
                                prakruti_production_slip.id AS slip_id,
                                prakruti_production_slip.slip_no AS slip_no,
                                prakruti_production_slip_line.product_id AS subplant_id,
                                prakruti_production_slip_line.description AS subplant_name
                        FROM
                                prakruti_production_slip JOIN	
                                prakruti_production_slip_line ON	
                                prakruti_production_slip_line.main_id = prakruti_production_slip.id JOIN	
                                prakruti_sub_plant ON
                                prakruti_sub_plant.subplant_id = prakruti_production_slip_line.product_id
                        WHERE
                                prakruti_sub_plant.id = CAST(%s AS INTEGER)''', ((self.subplant_id.id),))        
        for record in cr.dictfetchall():
            slip_id = record['slip_id']
            slip_no = record['slip_no']
            slip_number.append((slip_id))
            slip_list.append((slip_no))
        #if self.slip_id.id not in slip_number:
            #raise ValidationError(_('Wrong Slip Number Selected...!\nSlip Number\'s which belongs to particularly this Subplant are as follows : \n\n\n%s')%(json.dumps(slip_list)))
        
    
    @api.one
    @api.multi
    def _on_saving_the_record(self):
        '''
        while saving the record this will insert data in to Bill of material, syrup, tablet screens based on plant type
        '''
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        for temp in self:
            if temp.insert_flag == 0:
                if temp.plant_type == 'extraction':
                    insert_into_bom = self.pool.get('prakruti.bill_of_material').create(cr,uid,{
                        'subplant_id':temp.subplant_id.id,
                        'batch_id':temp.id,
                        'actual_batch_size':temp.batch_capacity
                        })
                elif temp.plant_type == 'syrup':
                    insert_into_syrup_bom = self.pool.get('prakruti.syrup').create(cr,uid,{
                        'subplant_id':temp.subplant_id.id,
                        'batch_no':temp.id,
                        'actual_batch_size':temp.batch_capacity
                        })
                elif temp.plant_type == 'tablet':
                    insert_into_tablet_bom = self.pool.get('prakruti.tablet').create(cr,uid,{
                        'subplant_id':temp.subplant_id.id,
                        'batch_no':temp.id,
                        'actual_batch_size':temp.batch_capacity
                        })
                elif temp.plant_type == 'formulation':
                    insert_into_syrup_bom = self.pool.get('prakruti.powder').create(cr,uid,{
                        'subplant_id':temp.subplant_id.id,
                        'batch_no':temp.id,
                        'actual_batch_size':temp.batch_capacity, 
                        'formulation_type':temp.formulation_type
                        })
            cr.execute('''update prakruti_batch_master set insert_flag =1 where id=%s ''', ((temp.id),))
        return {}
    
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('name_uniq', 'unique (batch_no)', 'Batch No Should be Unique!'),
    ]    
    
    '''
    batch allocation date can't be < than current date
    '''
    @api.one
    @api.constrains('batch_allocation_date')
    def _check_batch_allocation_date(self):
        if self.batch_allocation_date < fields.Date.today():
            raise ValidationError(
                "Batch Allocation Date can't be less than current date!")  
        
        
    '''
    batch end date can't be < than current date
    '''
    @api.one
    @api.constrains('batch_end_date')
    def _check_batch_end_date(self):
        if self.batch_end_date < fields.Date.today():
            raise ValidationError(
                "Batch End Date can't be less than current date!")
    
    
    '''
    It will send the mail automatically while saving the record
    '''
    def send_mail(self, cr, uid, ids, context=None):
        for temp in self.browse(cr, uid, ids, context={}):
            template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Manage Batch')],context=context)[0]
            email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            print 'template_idtemplate_idtemplate_idtemplate_id',template_id
        return True