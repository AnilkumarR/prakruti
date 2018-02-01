'''
Company : EBSL
Author: Induja
Module: Sub Plant
Class 1: PrakrutiSubPlant
Table 1 : prakruti_sub_plant 
Updated By: Induja
Updated Date & Version: 20170824 ,0.1
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


#########################################################################################################


class PrakrutiSubPlant(models.Model):
    _name = 'prakruti.sub_plant'
    _table = 'prakruti_sub_plant'
    _description = 'Sub Plant '
    _order= "id desc"
    _rec_name="subplant_id"
   
   
    subplant_id= fields.Many2one('product.product', string="Name",required="True")
    subplant_code=fields.Char(string='Code',required="True")
    main_plant_id=fields.Many2one('prakruti.main_plant',string='Main Plant',required="True")
    description=fields.Text(string='Description')
    plant_type=fields.Selection([('extraction','Extraction'),('syrup','Syrup'),('tablet','Tablet'),('formulation','Formulation')],string='Plant Type', default='extraction')
    formulation_type=fields.Selection([('powder','Powder'),('lotion','Lotion')],string='Formulation Type', default='powder')
    drying_chart=fields.Selection([('yes','Yes'),('no','No')], string="Drying Chart", default='yes',required="True")
    pulverisation=fields.Selection([('yes','Yes'),('no','No')], string="Pulverisation", default='yes',required="True")
    extraction_new=fields.Selection([('yes','Yes'),('no','No')], string="Extraction", default='yes',required="True")
    precipitation=fields.Selection([('yes','Yes'),('no','No')], string="Precipitation", default='yes',required="True")
    bleaching=fields.Selection([('yes','Yes'),('no','No')], string="Bleaching", default='yes',required="True")
    concentration=fields.Selection([('yes','Yes'),('no','No')], string="Concentartion", default='yes',required="True")
    evaporation=fields.Selection([('yes','Yes'),('no','No')], string="Evaporation", default='yes',required="True")
    stirring=fields.Selection([('yes','Yes'),('no','No')], string="Stirring", default='yes',required="True")
    spent_stripping=fields.Selection([('yes','Yes'),('no','No')], string="Spent Stripping", default='yes',required="True")
    spent_cooling_unloading=fields.Selection([('yes','Yes'),('no','No')], string="Spent Cooling & Unloading", default='yes',required="True")
    maturation_crystalization=fields.Selection([('yes','Yes'),('no','No')], string="Maturation & Crystalization", default='yes',required="True")
    water_striiping_chart=fields.Selection([('yes','Yes'),('no','No')], string="Water Strriping Chart", default='yes',required="True")
    charcolisation_chart=fields.Selection([('yes','Yes'),('no','No')], string="Charcolisation Chart", default='yes',required="True")
    spray_drying_chart=fields.Selection([('yes','Yes'),('no','No')], string="Spray Drying Chart", default='yes',required="True")
    magnetic_particle_seperation=fields.Selection([('yes','Yes'),('no','No')], string="Magnetic Particle Seperation", default='yes',required="True")
    blending=fields.Selection([('yes','Yes'),('no','No')], string="Blending", default='yes',required="True")
    heat_sterilization=fields.Selection([('yes','Yes'),('no','No')], string="Heat Sterilization", default='yes',required="True")
    other_ingredient_addition = fields.Selection([('yes','Yes'),('no','No')], string="Other Ingredient Addition",default='yes',required="True")
    extract_solution = fields.Selection([('yes','Yes'),('no','No')], string="Extract Solution", default='yes',required="True")
    soak_raw_material =fields.Selection([('yes','Yes'),('no','No')], string="Soak Raw Material", default='yes',required="True")
    api_addition=fields.Selection([('yes','Yes'),('no','No')], string="API Addition", default='yes',required="True")
    autoclave = fields.Selection([('yes','Yes'),('no','No')], string="Autoclave", default='yes',required="True")
    addition_preservative = fields.Selection([('yes','Yes'),('no','No')], string="Addition of Preservative", default='yes',required="True")
    preparation_syrup = fields.Selection([('yes','Yes'),('no','No')], string="Syrup Preparation", default='yes',required="True")
    ph_control_buffer = fields.Selection([('yes','Yes'),('no','No')], string="pH control buffer action ", default='yes',required="True")
    solvent_name= fields.Selection([('yes','Yes'),('no','No')], string="Solvent Name", default='yes',required="True")
    filling =  fields.Selection([('yes','Yes'),('no','No')], string="Filling", default='yes',required="True")
    coding =  fields.Selection([('yes','Yes'),('no','No')], string="Coding", default='yes',required="True")
    packing =  fields.Selection([('yes','Yes'),('no','No')], string="Packing", default='yes',required="True")
    coating = fields.Selection([('yes','Yes'),('no','No')], string="Coating", default='yes',required="True")
    sieving=fields.Selection([('yes','Yes'),('no','No')], string="Sieving", default='yes',required="True")
    blending=fields.Selection([('yes','Yes'),('no','No')], string="Blending", default='yes',required="True")
    milling=fields.Selection([('yes','Yes'),('no','No')], string="Milling", default='yes',required="True")
    filtration = fields.Selection([('yes','Yes'),('no','No')], string="Filtration", default='yes',required="True")
    preparation_of_binder= fields.Selection([('yes','Yes'),('no','No')], string="Preparation of Binder", default='yes',required="True")
    granulation = fields.Selection([('yes','Yes'),('no','No')], string="Granulation", default='yes',required="True")
    semi_drying = fields.Selection([('yes','Yes'),('no','No')], string="Semi Drying", default='yes',required="True")
    final_drying = fields.Selection([('yes','Yes'),('no','No')], string="Final Drying", default='yes',required="True")
    compression = fields.Selection([('yes','Yes'),('no','No')], string="Compression", default='yes',required="True")
    tablet_coating = fields.Selection([('yes','Yes'),('no','No')], string="Tablet Coating Preparation", default='yes',required="True")
    inspection =fields.Selection([('yes','Yes'),('no','No')], string="Inspection Details", default='yes',required="True")
    metal_inspection=fields.Selection([('yes','Yes'),('no','No')], string="Metal Inspection", default='yes',required="True")
    blow_off=fields.Selection([('yes','Yes'),('no','No')], string="Blow Off", default='yes')
    washing=fields.Selection([('yes','Yes'),('no','No')], string="Washing", default='yes')
    hexane_recover=fields.Selection([('yes','Yes'),('no','No')], string="Hexane Recovery", default='yes')    
    plant_allocated_flag = fields.Integer(string='Plant Allocated flag', default=0)
    addition_of_ingredients=fields.Selection([('yes','Yes'),('no','No')], string="Addition Of Ingredients", default='yes')
    extract_solution_lotion = fields.Selection([('yes','Yes'),('no','No')], string="Extract Solution", default='yes',required="True")
    addition_of_solution = fields.Selection([('yes','Yes'),('no','No')], string="Addition Of Solution", default='yes',required="True")
    other_ingredient_addition_lotion = fields.Selection([('yes','Yes'),('no','No')], string="Other Ingredient Addition", default='yes',required="True")
    volume_make_up = fields.Selection([('yes','Yes'),('no','No')], string="Volume Make Up", default='yes',required="True")
    filling_lotion = fields.Selection([('yes','Yes'),('no','No')], string="Filling", default='yes',required="True")   
    
    primary_raw_material_id = fields.Many2one('product.product',string = 'Primary Raw Material')
    primary_raw_material_name = fields.Char(related = 'primary_raw_material_id.name_template',string = 'Primary Raw Material',store = 1)  
    post_precipitation=fields.Selection([('yes','Yes'),('no','No')], string="Post Precipitation", default='yes',required="True")
    filtration_b=fields.Selection([('yes','Yes'),('no','No')], string="Filtration B", default='yes',required="True")
    ph_adjustment=fields.Selection([('yes','Yes'),('no','No')], string="PH Adjustment", default='yes',required="True")
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id,required="True")
    
    @api.onchange('plant_type')
    def onchange_plant(self):
        self.formulation_type = ''
    
    
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as subplant code and description etc.
    '''   
    def onchange_subplant_id(self, cr, uid, ids, subplant_id, context=None):
        cr.execute('SELECT  product_uom.id AS uom_id,product_uom.name,product_template.name as description,product_template.code as subplant_code FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id=cast(%s as integer)', ((subplant_id),))
        for values in cr.dictfetchall():
            subplant_code = values['subplant_code']
            description = values['description']
            return {'value' :{ 'subplant_code': subplant_code,'description':description }}
        
        
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_subplant_id the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_subplant_id(cr, uid, [], vals['subplant_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('subplant_code','description'):
            vals['subplant_code'] = onchangeResult['value']['subplant_code']
            vals['description'] = onchangeResult['value']['description']
        return super(PrakrutiSubPlant, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiSubPlant, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.subplant_id.id
        onchangeResult = self.onchange_subplant_id(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('subplant_code','description'):
            vals['subplant_code'] = onchangeResult['value']['subplant_code']
            vals['description'] = onchangeResult['value']['description']
        return super(PrakrutiSubPlant, self).write(cr, uid, ids, vals, context=context)
    '''
    The Name which will be entered shoud be unique, that means same Nmae must not be entered more than one 
    '''
    _sql_constraints = [
        ('prakruti_sub_plant_uniq', 'unique (subplant_id,main_plant_id)',
         'This Sub Plant is already Entered. Please Check !')
        ]
    
    
    
