'''
Company : EBSL
Author : Karan
Module : Product Specification AR Number
Class 1 : SpecificationARNoGenerator
Class 2 : SpecificationARNoGeneratorLine

Table 1 & Reference Id : prakruti_specification_ar_no,ar_line
Table 2 & Reference Id : prakruti_specification_ar_no_line,line_id

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

from openerp.exceptions import ValidationError

class SpecificationARNoGenerator(models.Model):
    _name = 'prakruti.specification.ar.no'
    _table = 'prakruti_specification_ar_no'
    _description = 'AR Number'
    _rec_name = 'ar_number'
    _order = 'id desc'
    
    ar_line = fields.One2many('prakruti.specification.ar.no.line','line_id',string= 'A.R Line')
    specification_id = fields.Many2one('product.specification.main',string= 'Specification Name')
    scientific_name= fields.Char(string= 'Scientific Name',readonly=True)
    product_id = fields.Many2one('product.product',string= 'Product Name',readonly=True)
    ar_number = fields.Char(string= 'A.R Number')
    display_product = fields.Integer(string= 'Is Product Displayed',default=0)        
    status = fields.Selection([('draft','Draft'),('assign','Assigned')],string= 'Status',default= 'draft',readonly=True)
    company_id= fields.Many2one('res.company',string= 'Company ID',default=lambda self: self.env.user.company_id)
    customer_name= fields.Many2one('res.partner', string= 'Customer Name')
    date= fields.Date(string= 'Date', default= fields.Date.today)
    mfd_date= fields.Date(string= 'M.F.D Date')
    expiry_date= fields.Date(string= 'Expiry Date')
    country_of_origin=fields.Char( string= 'Country of origin')
    batch_no=fields.Char(string='Batch No')
    batch_size=fields.Char(string='Batch Size')
    dispatch_qty=fields.Char(string='Dispatch Qty')
    plant_part_used= fields.Char(string= 'Plant Part Used')
    sample_qty=fields.Char(string='Sample Qty')
    remarks=fields.Text(string='Remarks')
    issue_date= fields.Date(string= 'Issue Date')
    effective_date= fields.Date(string= 'Effective Date')
    review_date= fields.Date(string= 'Review Date')
    doc_no= fields.Char(string= 'Doc No')
    rev_no= fields.Char(string= 'Rev No') 
    parameter = fields.Text(related='ar_line.parameter', string='Parameter')
    rm_assay = fields.Float(string="RM Assay%" , digits=(6,3))
    
    
    @api.one
    @api.constrains('rm_assay')
    def _check_rm_assay(self):
        if self.rm_assay <= 0:
            raise ValidationError(
                "RM Assay% !!! Can't be Negative OR 0 ")
        
        
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
    To store or to insert the readonly fields which is required for readonly fields
    '''
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_specification_id(cr, uid, [], vals['specification_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('scientific_name','product_id'):
            vals['product_id'] = onchangeResult['value']['product_id']
            vals['scientific_name'] = onchangeResult['value']['scientific_name']
        return super(SpecificationARNoGenerator, self).create(cr, uid, vals, context=context)
    
    '''
    To update the readonly fields which is required for readonly fields
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(SpecificationARNoGenerator, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            spec_type=record.specification_id.id
        onchangeResult = self.onchange_specification_id(cr, uid, ids, spec_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('scientific_name','product_id'):
            vals['product_id'] = onchangeResult['value']['product_id']
            vals['scientific_name'] = onchangeResult['value']['scientific_name']
        return super(SpecificationARNoGenerator, self).write(cr, uid, ids, vals, context=context)
    
    '''
    The AR Number must be unique
    '''
    _sql_constraints = [
    ('ar_unique', 'unique(ar_number)','A.R Number must be Unique !')
    ]
    
    '''
    The AR number will set to null if the specification is changed
    '''
    @api.onchange('specification_id')
    def onchange_spec_id(self):
        self.ar_number = ' '
    
    '''
    When on changing the specification the Scientific name and the product will displayed
    '''
    def onchange_specification_id(self, cr, uid, ids, specification_id, context=None):
        line = self.pool.get('product.specification.main').browse(cr, uid, specification_id, context=context)
        result = {
            'scientific_name':line.scientific_name,
            'product_id':line.product_id.id
            }
        return {'value': result}
    
    '''
    It will list the specification details from specification table based on the specification name
    '''
    @api.one
    @api.multi
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("SELECT CAST((product_specification.parameter_category ,product_specification.parameter_value)AS character varying) AS parameter,specification_table.specification_id,specification,protocol FROM product_specification INNER JOIN specification_table ON product_specification.id = specification_table.specification_id INNER JOIN product_specification_main ON specification_table.specification_line = product_specification_main.id INNER JOIN prakruti_specification_ar_no ON product_specification_main.id = prakruti_specification_ar_no.specification_id WHERE prakruti_specification_ar_no.id = CAST(%s AS INTEGER)",((temp.id),))
            for item in cr.dictfetchall():
                parameter=item['parameter']
                protocol=item['protocol']
                specification=item['specification']
                grid_down = self.pool.get('prakruti.specification.ar.no.line').create(cr,uid, {
                    'parameter':parameter,
                    'protocol':protocol,
                    'specification':specification,
                    'line_id':temp.id,
                        })
            cr.execute("UPDATE prakruti_specification_ar_no SET display_product = '1' WHERE id = CAST(%s AS INTEGER)",((temp.id),))
        return {}
    
    '''
    It will delete the specification list
    '''
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_specification_ar_no_line WHERE prakruti_specification_ar_no_line.line_id = CAST(%s AS INTEGER)", ((temp.id),))
            cr.execute("UPDATE prakruti_specification_ar_no SET display_product = '0' WHERE id = CAST(%s AS INTEGER)",((temp.id),))
        return {}
    
    '''
    The status will update to Assigned
    '''
    @api.one
    @api.multi
    def assign_no(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            if temp.ar_number:
                cr.execute("UPDATE prakruti_specification_ar_no SET status = 'assign' WHERE id = CAST(%s AS INTEGER)",((temp.id),))
            else:
                raise UserError(_('Please Enter A.R Number !'))
        return {}
    
class SpecificationARNoGeneratorLine(models.Model):
    _name = 'prakruti.specification.ar.no.line'
    _table = 'prakruti_specification_ar_no_line'
    _description = 'AR Number Line'
    
    line_id = fields.Many2one('prakruti.specification.ar.no',string= 'Line ID',ondelete='cascade')
    parameter= fields.Text(string="Parameter")
    specification= fields.Text(string= 'Specification')
    protocol= fields.Text(string= 'Protocol')
    result= fields.Text(string= 'Result')
    
    