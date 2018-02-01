'''
Company : EBSL
Author : Karan
Module : Purchase GRN Analysis

Class 1 : ProductSpecificationDefinition
Class 2 : ProductSpecification
Class 2 : ProductSpecificationTable

Table 1 & Reference Id : product_specification_main,specification_table
Table 2 & Reference Id : product_specification
Table 2 & Reference Id : specification_table,specification_line

Updated By : Karan 
Updated Date & Version : 2017/08/23 & 0.1
'''
from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
import re
import logging

class ProductSpecificationDefinition(models.Model):
    _name = 'product.specification.main'
    _table = 'product_specification_main'
    _description = 'Product Specification Definition'
    _rec_name = 'specification_name'
    _order = 'id desc'
    
    specification_table= fields.One2many('specification.table','specification_line',string= 'No.of Specifications')
    product_id = fields.Many2one('product.product',string= "Product Name",required=True)
    specification_sale_status= fields.Boolean('Sale Ok')
    specification_purchase_status= fields.Boolean('Purchase Ok')
    specification_name= fields.Char(string= 'Specification Name', required= True)
    scientific_name= fields.Char(string= 'Scientific Name')
    lab_time= fields.Float(string= 'Lab Report in Hours' ,digits=(6,3))
    customer_name= fields.Many2one('res.partner', string= 'Customer Name')
    common_name= fields.Char(string= 'Common Name')
    plant_part_used= fields.Char(string= 'Plant Part Used')
    preparation_type= fields.Char(string='Preparation Type')
    extraction_ratio= fields.Char(string= 'Extraction Ratio')
    standardization= fields.Char(string= 'Standardization')
    excipients_used= fields.Char(string= 'Excipients Used')
    excipients_details= fields.Char(string= 'Excipients Details')
    specification_product_id= fields.Many2one('product.template',ondelete='cascade', string= 'Product Template ID')
    company_id= fields.Many2one('res.company',ondelete='cascade', string= 'Company ID',default=lambda self: self.env.user.company_id)
    code= fields.Char(string= 'Product Code', readonly=True)
    issue_date= fields.Date(string= 'Issue Date')
    effective_date= fields.Date(string= 'Effective Date')
    review_date= fields.Date(string= 'Review Date')
    extraction_solvent= fields.Char(string= 'Extraction Solvent')
    final_extract_ratio= fields.Char(string= 'Final Extract Ratio')
    common_specification= fields.Boolean('Common Ok')       
    status = fields.Selection([('draft','Draft'),('assign','Assigned')],string= 'Status',default= 'draft',readonly=True)
    doc_no= fields.Char(string= 'Doc No')
    rev_no= fields.Char(string= 'Rev No') 
    specification_id = fields.Many2one('product.specification',related='specification_table.specification_id', string='Specification')
    is_duplicate = fields.Boolean(string= 'Is a Duplicate',default=False,readonly=True)
    duplicate_flag = fields.Char(string= 'Duplicate Flag',default=0,readonly=True) 
    
    '''
    Allowing the user not to do duplication from existing functionality
    '''
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(_('Forbbiden to duplicate'), _('It Is not possible to duplicate from here...'))
    
     
    '''
    Delete functionality will only work if the record is not assign
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.status == 'assign':
                raise UserError(_('Can\'t delete the Record which is Assigned'))
        return super(ProductSpecificationDefinition, self).unlink()
    
    
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'company_id': _default_company
        }
    
    
    _sql_constraints = [
    ('name_uniqueness', 'unique(specification_name)','Specification Name must be Unique !')
    ]
    
    '''
    Product Code will be loaded automatically 
    '''
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        cr.execute('''SELECT code as product_code FROM product_template INNER JOIN product_product ON product_template.id = product_product.product_tmpl_id AND product_product.id = CAST(%s AS INTEGER)''',((product_id),))
        for values in cr.dictfetchall():
            product_code = values['product_code']
            return {
                'value':{
                    'code':product_code
                    }
                }
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product_id the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''    
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_product_id(cr, uid, [], vals['product_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('code'):
            vals['code'] = onchangeResult['value']['code']
        return super(ProductSpecificationDefinition, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(ProductSpecificationDefinition, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        onchangeResult = self.onchange_product_id(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('code'):
            vals['code'] = onchangeResult['value']['code']
        return super(ProductSpecificationDefinition, self).write(cr, uid, ids, vals, context=context)
    
    '''
   Specification Sale Status & Customer Name will be loaded automatically 
    '''
    @api.onchange('specification_sale_status')
    def onchange_sale_status(self):
        if self.specification_sale_status == False:
            self.customer_name = False
    
    @api.onchange('common_specification')
    def onchange_sale_status(self):
        if self.common_specification == True:
            self.specification_sale_status = False
            self.specification_purchase_status = False
            self.customer_name = False
    '''
    Assigning AR No to Product
    ''' 
    @api.one
    @api.multi
    def assign_no(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("UPDATE product_specification_main SET status = 'assign' WHERE id = CAST(%s AS INTEGER)",((temp.id),))
        return {}
    
    
    '''
    Should allow only alphabets and numbers
    '''
    def onchange_check_code(self, cr, uid, ids, code, context=None):
        if code == False: 
            return {

                'value': {
                    'code': False
                }
            }

        if re.match("^[ A-Za-z0-9-]*$", code) != None:
            ''' to strip left and right spaces '''
            code = code.strip()
            code = code.upper()

            return {
                'value': {
                    'code': code
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'code': False
            }, 'warning': warning_shown}
    
    '''
    Should allow only alphabets and numbers
    '''
    def onchange_check_name(self, cr, uid, ids, specification_name, context=None):
        if specification_name == False:  
            return {

                'value': {
                    'specification_name': False
                }
            }

        if re.match("^[ A-Za-z0-9]*$", specification_name) != None:
            ''' to strip left and right spaces '''
            specification_name = specification_name.strip()
            specification_name = specification_name.upper()

            return {
                'value': {
                    'specification_name': specification_name
                }
            }

        else:
            warning_shown = {
                'title': _("Alert"),
                'message': _('Enter only numbers and alphabets'),
            }
            return {'value': {
                'specification_name': False
            }, 'warning': warning_shown}
    
    
    '''
    Duplication of the Records
    '''
    @api.one
    @api.multi
    def duplicate_specification(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            ebsl_id = self.pool.get('product.specification.main').create(cr,uid, {
                'specification_name':'Duplicate',
                'product_id':temp.product_id.id,
                'specification_purchase_status':temp.specification_purchase_status,
                'scientific_name':temp.scientific_name,
                'lab_time':temp.lab_time,
                'customer_name':temp.customer_name.id,
                'common_name':temp.common_name,
                'plant_part_used':temp.plant_part_used,
                'preparation_type':temp.preparation_type,
                'extraction_ratio':temp.extraction_ratio,
                'standardization':temp.standardization,
                'excipients_used':temp.excipients_used,
                'excipients_details':temp.excipients_details,
                'specification_product_id':temp.specification_product_id.id,
                'company_id':temp.company_id.id,
                'code':temp.code,
                'issue_date':temp.issue_date,
                'effective_date':temp.effective_date,
                'review_date':temp.review_date,
                'extraction_solvent':temp.extraction_solvent,
                'final_extract_ratio':temp.final_extract_ratio,
                'common_specification':temp.common_specification,
                'status':temp.status,
                'doc_no':temp.doc_no,
                'rev_no':temp.rev_no,            
                'is_duplicate':'True',
                'duplicate_flag': 1
                })
            for item in temp.specification_table:
                erp_id = self.pool.get('specification.table').create(cr,uid, {
                    'specification_id': item.specification_id.id,
                    'specification': item.specification,
                    'protocol': item.protocol,
                    'remarks': item.remarks,
                    'specification_line': ebsl_id
                    })
        return {} 
    

class ProductSpecification(models.Model):
    _name = 'product.specification'
    _table = 'product_specification'
    _description = 'Product Specification'
    
    parameter_category = fields.Char('Parameter Name', required= True)
    parameter_value = fields.Char('Parameter Value', required= True)#This will be inside square [] bracket
    parameter_name = fields.Text(string= 'Specifications')
    pcal= fields.Text(string= 'Protocols')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
                context = {}
        res = []
        for record in self.browse(cr, uid, ids, context=context):
                parameter_category = record.parameter_category
                parameter_value = record.parameter_value
                description = "%s [%s]" % (parameter_value, record.parameter_category)
                res.append((record.id, description))
        return res
   
class ProductSpecificationTable(models.Model):
    _name = 'specification.table'
    _table = 'specification_table'
    _description = 'Product Specification Table'
    
    specification_line= fields.Many2one('product.specification.main',ondelete='cascade', string="Specifications Line")
    specification_id= fields.Many2one('product.specification',ondelete='cascade', string="Parameters",required= True)
    specification= fields.Text(string= 'Specifications',related='specification_id.parameter_name',store=True)
    protocol= fields.Text(string= 'Protocol',related='specification_id.pcal',store=True)
    remarks= fields.Text(string= 'Remarks')