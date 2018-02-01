'''
Company : EBSL
Author : Karan
Module : Contact Master
Class 1 : PrakrutiResCompany
Class 2 : PrakrutiCountryState
Class 3 : ResPartner

Updated By : Karan 
Updated Date & Version : 2017/08/23 & 0.1
'''

from openerp import models, fields, api,_
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



class PrakrutiResCompany(models.Model):
    _inherit = 'res.company'
    _table = 'res_company'
    _description = 'Company'
    
    gstin = fields.Char(string= 'GSTIN')
    
    lut_no = fields.Char(string= 'LUT NO')
    lut_issue_date = fields.Date(string= 'LUT Issue Date')
    lut_expiry_date = fields.Date(string= 'LUT Expiry Date')



class PrakrutiCountryState(models.Model):
    _inherit = 'res.country.state'
    _table = 'res_country_state'
    _description = 'Country State'
    
    state_code = fields.Char(string= 'State Code',help='The State Code which will be enter in Integer Values')


class ResPartner(models.Model):   
    _inherit = 'res.partner'
    _table = 'res_partner'
    _description = 'Contact Master'
    
    pan_no = fields.Char('PAN Number')
    cst_no = fields.Char('CST Number')
    tin_no = fields.Char('TIN Number')
    gst = fields.Char('GST Number')
    vat_no = fields.Char('VAT Number')
    price_unit = fields.Float('Item Prices')
    price_remark =fields.Text('price Remark')
    rating = fields.Selection([('0','Bad'),('1','Fair'),('2','Good'),('3','Verygood'),('4','Excellent')],string= 'Rating')
    description = fields.Text(string='description')
    credit_days = fields.Integer(string='Credit Days')
    credit_limit = fields.Float(string='Credit Limits')
    code = fields.Char(string = 'code')
    type_of_address = fields.Char(string= 'Type of Address')
    delivery_times = fields.Text(string = 'Delivery onTime')
    comments = fields.Text(String = " Comments ")
    active_boxes = fields.Selection([('active','Active'),('deactive','Deactive')],string='Status',default= 'active',required=True)    
    excise_details = fields.Text('Excise Details')
    trade_licence = fields.Selection([
       ('vat', 'VAT'),
       ('pan', 'PAN'),
       ('cst', 'CST'),
       ('tin', 'TIN'),
       ('gst', 'GST')], default='gst',string= 'Trade Licence')       
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The partner name must be unique !'),
        ('code_uniq', 'unique (code)', 'The partner code must be unique !')
    ]
    
    '''
    Only valid letters and Numbers are required
    '''
    def onchange_pan(self, cr, uid, ids,pan_no,context=None):
      if pan_no == False:  
        return 
      if re.match("^[A-Za-z]{5}\d{4}[A-Za-z]{1}$", pan_no) != None:
          pan_no=pan_no.upper()
          return {'value':{'pan_no':pan_no}} 
      else:
          warning_shown = {  
                'title': _("Warning"),  
                'message': _('Enter a valid Pan No'),  
               } 
          return {'value':{
              'pan_no': pan_no,
                  }, 'warning' : warning_shown}
      
    '''
    Only valid letters and Numbers are required
    '''
    def onchange_cst(self, cr, uid, ids,cst_no,context=None):
      if cst_no == False:  
        return 
      if re.match("^[A-Za-z]{5}\d{4}[A-Za-z]{1}$", cst_no) != None:
          cst_no=cst_no.upper()
          return {'value':{'cst_no':cst_no}} 
      else:
          warning_shown = {  
                'title': _("Warning"),  
                'message': _('Enter a valid Pan No'),  
               } 
          return {'value':{
              'cst_no': cst_no,
                  }, 'warning' : warning_shown}
      
    '''
    Only valid letters and Numbers are required
    '''
    def onchange_tin(self, cr, uid, ids,tin_no,context=None):
      if tin_no == False:  
        return 
      if re.match("^[A-Za-z]{5}\d{4}[A-Za-z]{1}$", tin_no) != None:
          tin_no=tin_no.upper()
          return {'value':{'tin_no':tin_no}} 
      else:
          warning_shown = {  
                'title': _("Warning"),  
                'message': _('Enter a valid Pan No'),  
               } 
          return {'value':{
              'tin_no': tin_no,
                  }, 'warning' : warning_shown}	
      
    '''
    Only valid letters and Numbers are required
    '''
    def onchange_vat(self, cr, uid, ids,vat_no,context=None):
      if vat_no == False:   
        return 
      if re.match("^[ A-Za-z0-9-]*$", vat_no) != None:
          return {'value':{'vat_no':vat_no}} 
      else:
          warning_shown = {  
                'title': _("Warning"),  
                'message': _('Enter a valid Tin No'),  
               } 
          return {'value':{
              'vat_no': vat_no,
                  }, 'warning' : warning_shown}
      
      
    '''
    Only valid letters are required
    '''
    def _check_name(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context=context)
        name=obj.name
        if name==False:
            return True
        if re.match("^[ A-Za-z ]*$", name) !=None:
            return True
        else:
            return False
        return True
    
    '''
    Only valid letters are required
    '''
    def _check_fax(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context=context)
        fax=obj.fax
        if fax==False:
            return True
        if re.match("^[ A-Za-z ]*$", fax) !=None:
            return True
        else:
            return False
        return True
    
    '''
    Only valid Numbers are required
    '''
    def _check_phone(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context=context)
        phone=obj.phone
        if phone==False:
            return True
        if re.match("^[0-9+-]*$", phone) !=None:
            return True
        else:
            return False
        return True
    
    '''
    Only valid Numbers are required
    '''
    def _check_mobile(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context=context)
        mobile=obj.mobile
        if mobile==False:
            return True
        if re.match("^[0-9+-]*$", mobile) !=None:
            return True
        else:
            return False
        return True  
    
    '''
    Only valid letters and Numbers are required
    '''
    def _check_pan(self, cr, uid, ids, context=None):

        obj = self.browse(cr, uid, ids[0], context=context)
        pan_no = obj.pan_no
        if pan_no==False:
	  return True
	
        if re.match("^[ A-Za-z0-9-]*$", pan_no) != None:
            return True
	else:
	  return False
        return True 
    
    
    '''
    Only valid letters and Numbers are required
    '''
    def _check_tin(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        tin_no = obj.tin_no
        if tin_no==False:
	  return True
        if re.match("^[ A-Za-z0-9-]*$", tin_no) != None:
            return True
	else:
	  return False
        return True
    
    '''
    Only valid letters and Numbers are required
    '''
    def _check_cst(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        cst_no = obj.cst_no
        if cst_no==False:
	  return True
        if re.match("^[ A-Za-z0-9-]*$", cst_no) != None:
            return True
	else:
	  return False
        return True
    
    '''
    Only valid letters and Numbers are required
    '''
    def _check_vat(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        vat_no = obj.vat_no
        if vat_no==False:
	  return True
        if re.match("^[ A-Za-z0-9-]*$", vat_no) != None:
            return True
	else:
	  return False
        return True
    
    
    '''
    Credit days must not exceed 1000 and should not be less than 0
    '''
    def _check_credit_days(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        credit_days = obj.credit_days
        if(credit_days>1000 or credit_days<0): 
            return False
        return True    
    
    _constraints =[
        (_check_credit_days,'Credit days is too large or too low',['credit_days'])
        ]