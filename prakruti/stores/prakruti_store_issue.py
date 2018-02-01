'''
Company : EBSL
Author: Induja
Module: Store Issue
Class 1: PrakrutiStoreIssue
Class 2: PrakrutiStoreIssueItem 
Table 1 & Reference Id: prakruti_store_issue ,grid_id
Table 2 & Reference Id: prakruti_store_issue_item,main_id
Updated By: Induja
Updated Date & Version: 20170823 ,0.1
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
from openerp.exceptions import ValidationError
import re
import logging
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import email, re

class PrakrutiStoreIssue(models.Model):
    _name = 'prakruti.store_issue'
    _table = "prakruti_store_issue"
    _description = 'Store Issue'
    _rec_name = "issue_no"
    _order = 'id desc'
    
    
  
    '''Auto genereation function
    'Format: ST\ISSU\GROUP CODE\AUTO GENERATE NO\FINANCIAL YEAR
    Example: ST\ISSU\FG\0455\17-18
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
            cr.execute('''SELECT 
                                CAST(EXTRACT (month FROM issue_date) AS integer) AS month,
                                CAST(EXTRACT (year FROM issue_date) AS integer) AS year,
                                id 
                          FROM 
                                prakruti_store_issue 
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
            cr.execute('''SELECT autogenerate_store_issue(%s)''', ((temp.id),)  )# Database function:   autogenerate_store_issue 
            result = cr.dictfetchall()
            parent_invoice_id = 0
            for value in result: parent_invoice_id = value['autogenerate_store_issue'];
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
                style_format[record.id] = 'ST\\'+'ISSU\\'+'FG\\'+str(auto_gen) +'/'+str(display_present_year)+'-'+str(dispay_year)
            cr.execute('''UPDATE 
                                prakruti_store_issue 
                          SET 
                                issue_no =%s 
                          WHERE 
                                id=%s ''', ((style_format[record.id]),(temp.id),)  )
        return style_format
    
    
    grid_id = fields.One2many('prakruti.store_issue_item', 'main_id',string='Grid')
    purchase_type= fields.Selection([('extraction','Extraction'),('formulation','Formulation')],'Purchase Type',required=True)
    request_date = fields.Date('Request Date', readonly=True, default=fields.Date.today)
    approved_date = fields.Date('Approved Date',readonly=True, default=fields.Date.today)
    issue_date = fields.Date('Issue Date', required=True, default=fields.Date.today)
    dept_id = fields.Many2one('res.company','Department',readonly=True)
    company_id = fields.Many2one('res.company',string="Company" ,readonly=True)
    request_no = fields.Char(string = "Request No", readonly=True)
    issue_no = fields.Char(string = "Issue No",readonly= True,help= "Its a Issue Number.",)
    requested_by= fields.Many2one('res.users',string="Requested By",required=True)
    approved_by= fields.Many2one('res.users',string="Approved By",readonly=True)
    issued_by= fields.Many2one('res.users',string="Issued By",required=True)
    store_incharge = fields.Many2one('res.users','Store Incharge',readonly=True)
    plant_incharge = fields.Many2one('res.users',string="Plant Incharge",required=True)
    date = fields.Date('Date', required=True, default=fields.Date.today) 
    production_incharge = fields.Many2one('res.users',string="Production Incharge", required= True)
    doc_no = fields.Char(' Doc No')
    rev_no = fields.Char(' Rev No')
    store_issue_no = fields.Char(string = "Issue No",compute='_get_auto')
    auto_no = fields.Integer('Auto')
    req_no_control_id = fields.Integer('Auto Generating id',default= 0)
    remarks = fields.Text(' Remarks ')
    extraction_bom_id = fields.Integer(' Extraction BOM Common id')
    syrup_bom_id = fields.Integer(' Syrup BOM Common id')
    tablet_bom_id = fields.Integer('Tablet BOM Common id')
    powder_bom_id = fields.Integer('Powder BOM Common id')
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')
    store_location_id= fields.Many2one('stock.location','Store Location')    
    syrup_packing_bom_id = fields.Integer(' Syrup Packing BOM Common id')
    tablet_packing_bom_id = fields.Integer(' Tablet Packing BOM Common id')
    powder_packing_bom_id = fields.Integer(' Powder Packing BOM Common id')
    coming_from = fields.Char(string = "Coming From",default='Internal',readonly=True)
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Product",readonly=True)  
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')    
    grn_line = fields.One2many('prakruti.issue_grn_list_line', 'issue_id',string='GRN line')
    status = fields.Selection([
        ('waiting','Store Issue Waiting'),
        ('issue','Store Issued'),
        ('partial_issue','Store Partially Issued'),
        ('extra_issue','Extra Issued'),
        ('return_stock','Return to Stock')],string= 'Status',default='waiting')
    location_id = fields.Many2one('prakruti.stock_location','Store Location')
    revise_status = fields.Selection([('revise_issue','Revise Issue'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    revised_by=fields.Many2one('res.users',string='Revised By')
    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'purchase_type':'extraction',
        'issue_no':'New',
        'requested_by': lambda s, cr, uid, c:uid, #Current login user will display automatically
        'store_incharge': lambda s, cr, uid, c:uid,
        'plant_incharge': lambda s, cr, uid, c:uid,
        'production_incharge': lambda s, cr, uid, c:uid,
        'company_id':_default_company,
        'approved_by': lambda s, cr, uid, c:uid,
        'issued_by': lambda s, cr, uid, c:uid,
        }
    
    
    '''
    Cannot able to delete this record 
    '''
    @api.multi
    def unlink(self):
        for order in self:
            if order.status in ['waiting','partial_issue','issue']:
                raise UserError(_('Can\'t be  Deleted'))
        return super(PrakrutiStoreIssue, self).unlink()
    
    '''
    Issue date can't be < than current date 
    '''
    @api.one
    @api.constrains('issue_date')
    def _check_issue_date(self):
        if self.issue_date < fields.Date.today():
            raise ValidationError(
                "Issue Date Can\'t Take Back Date !!!") 
    '''
    this button helps to update the stock in prakruti_store_issue_line
    '''
    @api.one
    @api.multi
    def check_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute('''  UPDATE 
                                prakruti_store_issue_item 
                            SET 
                                store_qty = a.qty_aval,
                                reserved_qty = a.reserved_qty_aval
                            FROM ( 
                                    SELECT 
                                        prakruti_stock.product_id, 
                                        sum(prakruti_stock.product_qty) as qty_aval,
                                        sum(prakruti_stock.reserved_qty) as reserved_qty_aval,
					prakruti_store_issue.id AS main_id,
					prakruti_store_issue_item.id AS sub_id
                                    FROM 
                                        prakruti_stock JOIN  
                                        prakruti_store_issue_item ON 
                                        prakruti_store_issue_item.product_id = prakruti_stock.product_id JOIN
                                        prakruti_store_issue ON
                                        prakruti_store_issue.id = prakruti_store_issue_item.main_id
                                    WHERE 
                                        prakruti_store_issue_item.main_id = %s 
				    GROUP BY 
					prakruti_stock.product_id,
					prakruti_store_issue.id,
					prakruti_store_issue_item.id
                                    )as a
                            WHERE 
				prakruti_store_issue_item.main_id = a.main_id AND
				prakruti_store_issue_item.id = a.sub_id''',((temp.id),))
            if temp.subplant_id.id:
                cr.execute('''  UPDATE 
                                    prakruti_store_issue_item 
                                SET 
                                    virtual_reserved_qty = a.virtual_reserved_qty
                                FROM ( 
                                        SELECT
                                            prakruti_store_issue.id AS main_id,
                                            prakruti_store_issue_item.id AS sub_id,
                                            sum(coalesce(prakruti_reserved_product.reserved_qty,0) - coalesce(prakruti_reserved_product.consumed_qty,0)) as virtual_reserved_qty,
                                            prakruti_reserved_product.product_id
                                        FROM 
                                            prakruti_reserved_product JOIN
                                            prakruti_store_issue_item ON
                                            prakruti_store_issue_item.product_id = prakruti_reserved_product.product_id JOIN
                                            prakruti_store_issue ON
                                            prakruti_store_issue.id = prakruti_store_issue_item.main_id
                                        WHERE 
                                            prakruti_store_issue_item.main_id = %s AND 
                                            prakruti_reserved_product.subplant_id = %s AND
                                            coalesce(prakruti_reserved_product.reserved_qty,0) - coalesce(prakruti_reserved_product.consumed_qty,0) >= 0.000
                                        GROUP BY 
                                            prakruti_store_issue.id,
                                            prakruti_store_issue_item.id,
                                            prakruti_reserved_product.product_id
                                        )as a
                                WHERE 
                                    prakruti_store_issue_item.main_id = a.main_id AND
                                    prakruti_store_issue_item.id = a.sub_id AND
                                    prakruti_store_issue_item.product_id = a.product_id''',((temp.id),(temp.subplant_id.subplant_id.id),))
                #UPDATING THE SLIP ID WITH THE HELP OF SUBPLANT AND BATCH ID
                cr.execute('''  UPDATE 
                                    prakruti_store_issue_item 
                                SET 
                                    slip_id = a.slip_id
                                FROM ( 
                                        SELECT
                                            prakruti_batch_master.slip_id,
                                            prakruti_batch_master.subplant_id,
                                            prakruti_batch_master.id as batch_id,
                                            prakruti_store_issue.id AS main_id,
                                            prakruti_store_issue_item.id AS sub_id
                                        FROM
					    prakruti_batch_master JOIN
					    prakruti_store_issue ON
					    prakruti_batch_master.id = prakruti_store_issue.batch_no JOIN
					    prakruti_store_issue_item ON
					    prakruti_store_issue_item.main_id = prakruti_store_issue.id
					WHERE
					    prakruti_store_issue_item.main_id = %s AND
					    prakruti_batch_master.subplant_id = %s AND
					    prakruti_batch_master.id = %s
                                        )as a
                                WHERE 
                                    prakruti_store_issue_item.main_id = a.main_id AND
                                    prakruti_store_issue_item.id = a.sub_id AND 
                                    prakruti_store_issue_item.slip_id IS NULL''',((temp.id),(temp.subplant_id.id),(temp.batch_no.id),))
            else:
                cr.execute('''  UPDATE 
                                    prakruti_store_issue_item 
                                SET 
                                    virtual_reserved_qty = a.virtual_reserved_qty
                                FROM ( 
                                        SELECT
                                            prakruti_store_issue.id AS main_id,
                                            prakruti_store_issue_item.id AS sub_id,
                                            sum(coalesce(prakruti_reserved_product.reserved_qty,0) - coalesce(prakruti_reserved_product.consumed_qty,0)) as virtual_reserved_qty
                                        FROM 
                                            prakruti_reserved_product JOIN
                                            prakruti_store_issue_item ON
                                            prakruti_store_issue_item.product_id = prakruti_reserved_product.product_id JOIN
                                            prakruti_store_issue ON
                                            prakruti_store_issue.id = prakruti_store_issue_item.main_id
                                        WHERE 
                                            prakruti_store_issue_item.main_id = %s AND
                                            coalesce(prakruti_reserved_product.reserved_qty,0) - coalesce(prakruti_reserved_product.consumed_qty,0) >= 0.000
                                        GROUP BY 
                                            prakruti_store_issue.id,
                                            prakruti_store_issue_item.id
                                        )as a
                                WHERE 
                                    prakruti_store_issue_item.main_id = a.main_id AND
                                    prakruti_store_issue_item.id = a.sub_id''',((temp.id),))
        return {}
    '''
    This Button helps for Revision(If any changes need to be done in table 2 click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_issue(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            #cr.execute("SELECT subplant_id FROM prakruti_store_issue WHERE id = %s",((temp.id),)) 
            #for line in cr.dictfetchall():
                #subplant_id = line['subplant_id']
            #if temp.subplant_id:
            ebsl_id = self.pool.get('prakruti.store_issue').create(cr,uid, {
                'company_id':temp.company_id.id,
                'coming_from':temp.coming_from,
                'purchase_type':temp.purchase_type,
                'request_date':temp.request_date,
                'approved_date':temp.approved_date,
                'issue_date':temp.issue_date,
                'dept_id':temp.dept_id.id,
                'request_no':temp.request_no,
                'issue_no':temp.issue_no,
                'requested_by':temp.requested_by.id,
                'status':temp.status,
                'approved_by':temp.approved_by.id,
                'issued_by':temp.issued_by.id,
                'store_incharge':temp.store_incharge.id,
                'plant_incharge':temp.plant_incharge.id,
                'date':temp.date,
                'production_incharge':temp.production_incharge.id,
                'doc_no':temp.doc_no,
                'rev_no':temp.rev_no,
                'store_issue_no':temp.store_issue_no,
                'store_location_id':temp.store_location_id.id,
                'revise_status':temp.revise_status,  
                'revise_no':temp.revise_no,
                'is_revise':temp.is_revise,
                'revise_remarks':temp.revise_remarks,
                'revise_remarks_update':temp.revise_remarks_update,
                'revise_id':temp.revise_id.id,  
                'extraction_bom_id':temp.extraction_bom_id,
                'syrup_bom_id':temp.syrup_bom_id,
                'tablet_bom_id':temp.tablet_bom_id,
                'batch_no':temp.batch_no.id,
                'store_location_id':temp.store_location_id.id,                
                'syrup_packing_bom_id':temp.syrup_packing_bom_id,                
                'tablet_packing_bom_id':temp.tablet_packing_bom_id,              
                'subplant_id':temp.subplant_id.id,                    
                'revise_flag': 1
                })
            for item in temp.grid_id:
                erp_id = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                    'product_id': item.product_id.id,
                    'uom_id': item.uom_id.id,
                    'description':item.description,
                    'approved_quantity': item.approved_quantity,
                    'packing_style': item.packing_style,
                    'packing_per_qty':item.packing_per_qty,
                    'remarks':item.remarks, 
                    'grn_no': item.grn_no.id,
                    'ar_no': item.ar_no.id,
                    'extra_issued_qty': item.extra_issued_qty,
                    'style_flag': item.style_flag,
                    'packing_flag': item.packing_flag,
                    'extra_readonly_flag':item.extra_readonly_flag,
                    'extra_issued_packing':item.extra_issued_packing,
                    'grn_list': item.grn_list,
                    'packing_details':item.packing_details,
                    'request_line_id':item.request_line_id,
                    'revise_issue_line':item.revise_issue_line,
                    'issued_quantity':item.issued_quantity,
                    'grid_common_id_bom':item.grid_common_id_bom,
                    'grn_list':item.grn_list,
                    'main_id':ebsl_id
                    })
            cr.execute("UPDATE prakruti_store_issue SET revise_status = 'revise_issue',is_revise = 'True' WHERE id = %s",((temp.id),))
            cr.execute("UPDATE prakruti_store_issue_item SET revise_issue_line = 1 WHERE main_id = %s",((temp.id),))                
            #else:                
                #cr.execute("UPDATE prakruti_store_approve_request SET revise_from_issue = 2,revise_status = 'revise_approval' ,is_revise='True' WHERE request_no = %s",((temp.request_no),))                 
                #cr.execute("UPDATE prakruti_store_issue_item SET revise_issue_line = 1 WHERE main_id = %s",((temp.id),))                

                #cr.execute("UPDATE prakruti_store_approve_request_item as a SET status='approve',revise_issue_line=1 FROM (SELECT request_line_id FROM prakruti_store_issue_item JOIN prakruti_store_issue ON prakruti_store_issue_item.main_id=prakruti_store_issue.id WHERE main_id=%s) as b WHERE a.request_line_id=b.request_line_id ",((temp.id),)) 
                #cr.execute("UPDATE prakruti_store_issue SET revise_status = 'revise_issue',is_revise = 'True' WHERE id = %s",((temp.id),)) 
        return {}
    
    
    
   
    
    
    
    '''
    After doing changes in prakruti_sales_order_item click this to visible Revise button and to update the changes in the screen
    '''
    
    @api.one
    @api.multi
    def revise_done(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context' 
        revise_done_by = False
        line_id = 0
        for temp in self:
            cr.execute("SELECT subplant_id FROM prakruti_store_issue WHERE id = %s",((temp.id),)) 
            for line in cr.dictfetchall():
                subplant_id = line['subplant_id']
            if temp.subplant_id: 
                if temp.revise_remarks:
                    if temp.revise_id:
                        cr.execute("UPDATE prakruti_store_issue_item SET revise_issue_line = 2 WHERE main_id = %s",((temp.id),))
                        cr.execute('''SELECT revise_store_issue(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',((temp.id),(temp.subplant_id.id),(temp.batch_no.id),(temp.extraction_bom_id),(temp.syrup_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_bom_id),(temp.tablet_packing_bom_id),(temp.powder_bom_id),(temp.powder_packing_bom_id),))
                    else:
                        raise UserError(_('Please enter Revised Person...'))
                else:
                    raise UserError(_('Please enter Revise Remarks...'))
            else:
                if temp.revise_remarks:
                    if temp.revise_id:
                        cr.execute("UPDATE prakruti_store_issue_item SET revise_issue_line = 2 WHERE main_id = %s",((temp.id),))
                        cr.execute('''SELECT revise_store_issue_internal AS error_message FROM revise_store_issue_internal(%s,%s)''',((temp.id),(temp.request_no),))
                        for line in cr.dictfetchall():
                            error_message = line['error_message']
                        if error_message == 'Record Cannot be Revised':
                                raise UserError(_('Record...Can\'t Be Revised...\nPlease check Issued Qty...\nPlease Contact Your Administrator...!!!'))
                    else:
                        raise UserError(_('Please enter Revised Person...'))
                else:
                    raise UserError(_('Please enter Revise Remarks...'))
        return {}
    
    
    
    
    '''
    This button helps to issue the product and the stock will deduct after clicking this button 
    '''
    @api.one
    @api.multi
    def UpdateIssueStock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        error_message = ''
        slip_number = []
        entered_slip_no = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            if len(temp.grn_line) == 0 and not temp.doc_no:
                raise UserError(_('Please Enter the Doc No. In the Other Details Tab. If There is No GRN Number For that list of the Product'))
            if len(temp.grn_line) > 0 or temp.doc_no:                    
                cr.execute('''SELECT count(id) as entered_grn_number from prakruti_issue_grn_list_line WHERE grn_id > 0 AND issue_id = %s''',((temp.id),))
                for values in cr.dictfetchall():
                    entered_grn_number = values['entered_grn_number']
                if entered_grn_number == 0:
                    cr.execute('''  INSERT INTO prakruti_issue_grn_list_line(product_id,issued_qty,extra_issued_qty,packing_style,packing_per_qty,extra_issued_packing,issue_id,remarks)
                                    SELECT 
                                        prakruti_store_issue_item.product_id,
                                        sum((coalesce(prakruti_store_issue_item.packing_style,0) * coalesce(prakruti_store_issue_item.packing_per_qty,0)) + coalesce(prakruti_store_issue_item.extra_issued_packing,0)) AS issued_qty,
                                        prakruti_store_issue_item.extra_issued_qty,
                                        prakruti_store_issue_item.packing_style,
                                        prakruti_store_issue_item.packing_per_qty,
                                        prakruti_store_issue_item.extra_issued_packing,
                                        prakruti_store_issue.id AS issue_id,
                                        prakruti_store_issue.doc_no AS remarks
                                    FROM
                                        prakruti_store_issue_item JOIN
                                        prakruti_store_issue ON
                                        prakruti_store_issue.id = prakruti_store_issue_item.main_id
                                    WHERE 
                                        prakruti_store_issue_item.main_id = %s                                    
                                    GROUP BY
                                        prakruti_store_issue_item.product_id,
                                        prakruti_store_issue_item.packing_style,
                                        prakruti_store_issue_item.packing_per_qty,
                                        prakruti_store_issue_item.extra_issued_qty,
                                        prakruti_store_issue_item.extra_issued_packing,
                                        prakruti_store_issue.id,
                                        prakruti_store_issue.doc_no''',((temp.id),))
                cr.execute('''  select
                                    DISTINCT prakruti_reserved_product.slip_id AS slip_id
                                from
                                    prakruti_store_issue INNER JOIN
                                    prakruti_store_issue_item ON
                                    prakruti_store_issue_item.main_id = prakruti_store_issue.id RIGHT JOIN
                                    prakruti_reserved_product ON
                                    prakruti_store_issue_item.product_id = prakruti_reserved_product.product_id 
                                where 
                                    prakruti_store_issue.id = %s AND 
                                    prakruti_reserved_product.slip_id IS NOT NULL''',((temp.id),))
                for line in cr.dictfetchall():
                    slip_id = line['slip_id']
                    slip_number.append((slip_id))
                print 'SLIP NUMBER : ',slip_number
                #WHEN THERE IS MORE THAN THE RESERVED QTY
                cr.execute('''  select
                                    count(prakruti_store_issue_item.id) AS any_more_qty_than_the_reserve_qty
                                from
                                    prakruti_store_issue_item 
                                where	 
                                    prakruti_store_issue_item.main_id = %s AND 
                                    (
                                    (store_qty - coalesce(virtual_reserved_qty,0)) >= ((packing_style * packing_per_qty) + extra_issued_packing) 
                                    OR (store_qty - coalesce(virtual_reserved_qty,0)) >= extra_issued_qty
                                    )''',((temp.id),))
                for line in cr.dictfetchall():
                    any_more_qty_than_the_reserve_qty = line['any_more_qty_than_the_reserve_qty']
                print 'NO OF LINE HAVING MORE QTY THAN RESERVED : ',any_more_qty_than_the_reserve_qty
                #TOTAL NO OF LINE
                cr.execute('''  select
                                    count(id) AS total_line
                                from
                                    prakruti_store_issue_item 
                                where	 
                                    prakruti_store_issue_item.main_id = %s''',((temp.id),))
                for line in cr.dictfetchall():
                    total_line = line['total_line']
                print 'NO OF LINE : ',total_line            
                if any_more_qty_than_the_reserve_qty == total_line:
                    #If the qty is Available but also it have some reserved than deduct from the Reserved
                    cr.execute('''  select 
                                            slip_id AS entered_slip_no
                                    from 
                                            prakruti_store_issue_item 
                                    where 
                                            prakruti_store_issue_item.main_id = %s and slip_id is not null''',((temp.id),))
                    for line in cr.dictfetchall():
                        entered_slip_no = line['entered_slip_no']
                    print 'ENTERED SLIP ID ARE: ',entered_slip_no                
                    if entered_slip_no in slip_number:
                        print '--------4-------------'
                        cr.execute('''  SELECT
                                            issued_quantity AS issue_qty,
                                            extra_issued_qty AS extra_issue_qty
                                        FROM
                                            prakruti_store_issue_item
                                        WHERE
                                            main_id= %s''',((temp.id),))
                        for line in cr.dictfetchall():
                            issue_qty = line['issue_qty']
                            extra_issue_qty = line['extra_issue_qty']
                        if issue_qty:
                            print '--------5-------------'                        
                            #Also update the consumed quantity in the reservation table for the issued Qty
                            cr.execute('''  UPDATE
                                                prakruti_reserved_product
                                            SET
                                                consumed_qty = coalesce(consumed_qty,0) + ((a.packing_style * a.packing_per_qty) + a.extra_issued_packing)
                                            FROM(
                                                SELECT
                                                    prakruti_store_issue_item.slip_id,
                                                    prakruti_store_issue_item.product_id,
                                                    prakruti_store_issue_item.packing_style,
                                                    prakruti_store_issue_item.packing_per_qty,
                                                    prakruti_store_issue_item.extra_issued_packing
                                                FROM
                                                    prakruti_store_issue_item
                                                WHERE
                                                    prakruti_store_issue_item.main_id = %s
                                            ) AS a
                                            WHERE
                                                a.slip_id = prakruti_reserved_product.slip_id AND 
                                                a.product_id = prakruti_reserved_product.product_id''',((temp.id),))
                        else:
                            print '--------6-------------'    
                            #Also update the consumed quantity in the reservation table for the extra Issue Qty
                            cr.execute('''  UPDATE
                                                prakruti_reserved_product
                                            SET
                                                consumed_qty = coalesce(consumed_qty,0) + a.extra_issued_qty
                                            FROM(
                                                SELECT
                                                    prakruti_store_issue_item.slip_id,
                                                    prakruti_store_issue_item.product_id,
                                                    prakruti_store_issue_item.extra_issued_qty
                                                FROM
                                                    prakruti_store_issue_item 
                                                WHERE
                                                    prakruti_store_issue_item.main_id = %s
                                            ) AS a
                                            WHERE
                                                a.slip_id = prakruti_reserved_product.slip_id AND 
                                                a.product_id = prakruti_reserved_product.product_id''',((temp.id),))
                    print '--------1-------------'
                    cr.execute('''  SELECT
                                        issued_quantity AS issue_qty_1,
                                        extra_issued_qty AS extra_issue_qty_1
                                    FROM
                                        prakruti_store_issue_item
                                    WHERE
                                        main_id= %s''',((temp.id),))
                    for line in cr.dictfetchall():
                        issue_qty_1 = line['issue_qty_1']
                        extra_issue_qty_1 = line['extra_issue_qty_1']
                    if issue_qty_1 > 0:
                        print '--------2-------------'
                        cr.execute('''SELECT stock_store_issue(%s)''',((temp.id),))
                    elif extra_issue_qty_1 > 0:
                        print '--------3-------------'
                        cr.execute('''SELECT stock_store_extra_issue(%s)''',((temp.id),))
                else:
                    cr.execute('''  select 
                                            slip_id AS entered_slip_no
                                    from 
                                            prakruti_store_issue_item 
                                    where 
                                            prakruti_store_issue_item.main_id = %s and slip_id is not null''',((temp.id),))
                    for line in cr.dictfetchall():
                        entered_slip_no = line['entered_slip_no']
                    print 'ENTERED SLIP ID ARE: ',entered_slip_no                
                    if entered_slip_no in slip_number:
                        print '--------4-------------'
                        cr.execute('''  SELECT
                                            issued_quantity AS issue_qty,
                                            extra_issued_qty AS extra_issue_qty
                                        FROM
                                            prakruti_store_issue_item
                                        WHERE
                                            main_id= %s''',((temp.id),))
                        for line in cr.dictfetchall():
                            issue_qty = line['issue_qty']
                            extra_issue_qty = line['extra_issue_qty']
                        if issue_qty:
                            print '--------5-------------'                        
                            #Also update the consumed quantity in the reservation table for the issued Qty
                            cr.execute('''  UPDATE
                                                prakruti_reserved_product
                                            SET
                                                consumed_qty = coalesce(consumed_qty,0) + ((a.packing_style * a.packing_per_qty) + a.extra_issued_packing)
                                            FROM(
                                                SELECT
                                                    prakruti_store_issue_item.slip_id,
                                                    prakruti_store_issue_item.product_id,
                                                    prakruti_store_issue_item.packing_style,
                                                    prakruti_store_issue_item.packing_per_qty,
                                                    prakruti_store_issue_item.extra_issued_packing
                                                FROM
                                                    prakruti_store_issue_item
                                                WHERE
                                                    prakruti_store_issue_item.main_id = %s
                                            ) AS a
                                            WHERE
                                                a.slip_id = prakruti_reserved_product.slip_id AND 
                                                a.product_id = prakruti_reserved_product.product_id''',((temp.id),))
                        else:
                            print '--------6-------------'    
                            #Also update the consumed quantity in the reservation table for the extra Issue Qty
                            cr.execute('''  UPDATE
                                                prakruti_reserved_product
                                            SET
                                                consumed_qty = coalesce(consumed_qty,0) + a.extra_issued_qty
                                            FROM(
                                                SELECT
                                                    prakruti_store_issue_item.slip_id,
                                                    prakruti_store_issue_item.product_id,
                                                    prakruti_store_issue_item.extra_issued_qty
                                                FROM
                                                    prakruti_store_issue_item 
                                                WHERE
                                                    prakruti_store_issue_item.main_id = %s
                                            ) AS a
                                            WHERE
                                                a.slip_id = prakruti_reserved_product.slip_id AND 
                                                a.product_id = prakruti_reserved_product.product_id''',((temp.id),))
                        #Also deduct the reserved quantity from the Stock table
                        cr.execute('''  UPDATE
                                            prakruti_stock
                                        SET
                                            reserved_qty = reserved_qty - ((a.packing_style * a.packing_per_qty) + a.extra_issued_packing)
                                        FROM(
                                            SELECT
                                                prakruti_store_issue_item.packing_style,
                                                prakruti_store_issue_item.packing_per_qty,
                                                prakruti_store_issue_item.extra_issued_packing,
                                                prakruti_store_issue_item.product_id,
                                                slip_id,
                                                grn_id
                                            FROM
                                                prakruti_store_issue_item JOIN
                                                prakruti_issue_grn_list_line ON
                                                prakruti_issue_grn_list_line.product_id = prakruti_store_issue_item.product_id
                                            WHERE
                                                prakruti_store_issue_item.main_id = %s AND prakruti_issue_grn_list_line.issue_id = %s
                                        ) AS a
                                        WHERE
                                            a.slip_id = prakruti_stock.slip_id AND 
                                            a.product_id = prakruti_stock.product_id AND 
                                            a.grn_id = prakruti_stock.grn_id''',((temp.id),(temp.id),))
                        cr.execute('''  SELECT
                                            issued_quantity AS issue_qty,
                                            extra_issued_qty AS extra_issue_qty
                                        FROM
                                            prakruti_store_issue_item
                                        WHERE
                                            main_id= %s''',((temp.id),))
                        for line in cr.dictfetchall():
                            issue_qty = line['issue_qty']
                            extra_issue_qty = line['extra_issue_qty']
                        if issue_qty:
                            print '--------7-------------'
                            cr.execute('''SELECT stock_store_issue(%s)''',((temp.id),))
                        elif extra_issue_qty:
                            print '--------8-------------'
                            cr.execute('''SELECT stock_store_extra_issue(%s)''',((temp.id),))
                    else:
                        raise UserError(_('Wrong Slip Number Selected...!\nOR\nQty might be Reserved for Other Production Slip...\nOR\nPlease Click the Check Stock...'))
                cr.execute('''SELECT stock_store AS error_message FROM stock_store(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',((temp.id),(temp.request_no),(temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_bom_id),(temp.powder_packing_bom_id),))                
                for item in cr.dictfetchall():
                    error_message = item['error_message']
                if error_message =='Please Enter Qty':
                    print '--------9-------------'
                    raise UserError(_('Please Enter qty'))
                elif error_message =='Enter Packing Details':
                    print '--------10-------------'
                    raise UserError(_('Enter Packing Details'))
                elif error_message =='Not Enough Stock':
                    print '--------11-------------'
                    raise UserError(_('Not Enough Stock(or)\nNo Any Products To Send For Further Process'))        
                
                #Since Now from the New Update there is no request Number in this screen if the request coming from the production so to update the status in both the approve and request screen we have to go with the BOM ID
                if temp.request_no == 'From Production':
                    cr.execute('''  SELECT
                                        requested_quantity as request_qty
                                    FROM
                                        prakruti_store_issue_item
                                    WHERE
                                        main_id= %s''',((temp.id),))
                    for item in cr.dictfetchall():
                        request_qty = item['request_qty'] 
                    cr.execute('''  SELECT
                                        issued_quantity as issue_qty
                                    FROM
                                        prakruti_store_issue_item
                                    WHERE
                                        main_id= %s''',((temp.id),))
                    for line in cr.dictfetchall():
                        issue_qty = line['issue_qty'] 
                    cr.execute('''  SELECT
                                        extra_issued_qty as extra_isued_qty
                                    FROM
                                        prakruti_store_issue_item
                                    WHERE
                                        main_id= %s''',((temp.id),))
                    for line in cr.dictfetchall():
                        extra_isued_qty = line['extra_isued_qty'] 
                    if (request_qty==issue_qty):
                        cr.execute('''  UPDATE 
                                            prakruti_store_request 
                                        SET 
                                            state = 'issued' 
                                        WHERE 
                                            extraction_bom_id=%s AND
                                            syrup_bom_id =%s AND
                                            tablet_bom_id=%s AND
                                            powder_bom_id=%s AND
                                            syrup_packing_bom_id = %s AND
                                            tablet_packing_bom_id= %s AND
                                            powder_packing_bom_id = %s''',((temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.powder_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_packing_bom_id),))
                        cr.execute('''  UPDATE 
                                            prakruti_store_approve_request 
                                        SET 
                                            state = 'issued' 
                                        WHERE 
                                            extraction_bom_id=%s AND
                                            syrup_bom_id =%s AND
                                            tablet_bom_id=%s AND
                                            powder_bom_id=%s AND
                                            syrup_packing_bom_id = %s AND
                                            tablet_packing_bom_id= %s AND
                                            powder_packing_bom_id = %s''',((temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.powder_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_packing_bom_id),))
                        cr.execute('''  UPDATE 
                                            prakruti_store_issue 
                                        SET 
                                            status = 'issue' 
                                        WHERE 
                                            id = %s''',((temp.id),))
                    elif (request_qty==extra_isued_qty) or (extra_isued_qty>request_qty)or (issue_qty>request_qty):
                        cr.execute('''  UPDATE 
                                            prakruti_store_request 
                                        SET 
                                            state = 'extra_issue' 
                                        WHERE 
                                            extraction_bom_id=%s AND
                                            syrup_bom_id =%s AND
                                            tablet_bom_id=%s AND
                                            powder_bom_id=%s AND
                                            syrup_packing_bom_id = %s AND
                                            tablet_packing_bom_id= %s AND
                                            powder_packing_bom_id = %s''',((temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.powder_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_packing_bom_id),))
                        cr.execute('''  UPDATE 
                                            prakruti_store_approve_request 
                                        SET 
                                            state = 'extra_issue' 
                                        WHERE 
                                            extraction_bom_id=%s AND
                                            syrup_bom_id =%s AND
                                            tablet_bom_id=%s AND
                                            powder_bom_id=%s AND
                                            syrup_packing_bom_id = %s AND
                                            tablet_packing_bom_id= %s AND
                                            powder_packing_bom_id = %s''',((temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.powder_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_packing_bom_id),))
                        cr.execute('''  UPDATE 
                                            prakruti_store_issue 
                                        SET 
                                            status = 'extra_issue' 
                                        WHERE 
                                            id = %s''',((temp.id),))
                    else:
                        cr.execute('''  UPDATE 
                                            prakruti_store_request 
                                        SET 
                                            state = 'partial_issue' 
                                        WHERE 
                                            extraction_bom_id=%s AND
                                            syrup_bom_id =%s AND
                                            tablet_bom_id=%s AND
                                            powder_bom_id=%s AND
                                            syrup_packing_bom_id = %s AND
                                            tablet_packing_bom_id= %s AND
                                            powder_packing_bom_id = %s''',((temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.powder_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_packing_bom_id),))
                        cr.execute('''  UPDATE 
                                            prakruti_store_approve_request 
                                        SET 
                                            state = 'partial_issue' 
                                        WHERE 
                                            extraction_bom_id=%s AND
                                            syrup_bom_id =%s AND
                                            tablet_bom_id=%s AND
                                            powder_bom_id=%s AND
                                            syrup_packing_bom_id = %s AND
                                            tablet_packing_bom_id= %s AND
                                            powder_packing_bom_id = %s''',((temp.extraction_bom_id),(temp.syrup_bom_id),(temp.tablet_bom_id),(temp.powder_bom_id),(temp.syrup_packing_bom_id),(temp.tablet_packing_bom_id),(temp.powder_packing_bom_id),))
                        cr.execute('''  UPDATE 
                                            prakruti_store_issue 
                                        SET 
                                            status = 'partial_issue' 
                                        WHERE 
                                            id = %s''',((temp.id),))
                else:
                    cr.execute('''  SELECT
                                        count(prakruti_store_issue_item.id) as no_of_extra_issue_line
                                    FROM
                                        prakruti_store_issue_item
                                    WHERE
                                        main_id = %s AND
                                        (packing_style * packing_per_qty) + extra_issued_packing > approved_quantity
                                        ''',((temp.id),))
                    for item_line in cr.dictfetchall():
                        no_of_extra_issue_line = item_line['no_of_extra_issue_line']
                    if no_of_extra_issue_line > 0:
                        cr.execute('''  UPDATE 
                                            prakruti_store_issue 
                                        SET 
                                            status = 'extra_issue' 
                                        WHERE 
                                            id = %s''',((temp.id),))
            else:
                raise UserError(_('Please Enter The Selected GRN No...'))
        return {}
    
    
    @api.one
    @api.multi 
    def return_to_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            cr.execute("SELECT count(id) as return_count FROM prakruti_store_issue_item WHERE qty_returned > 0 AND main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                return_count=int(line['return_count'])
            if return_count >= 1:
                cr.execute("SELECT stock_return_issue(%s)", ((temp.id),))
            else:
                raise UserError(_('Return Qty cannot be -ve or o'))   
            cr.execute("UPDATE prakruti_store_issue SET status = 'return_stock' WHERE prakruti_store_issue.id = cast(%s as integer)", ((temp.id),))
        return {}
    
    
class PrakrutiStoreIssueItem(models.Model):
    _name = 'prakruti.store_issue_item'
    _table = "prakruti_store_issue_item"
    _description = 'Store Issue Item'
    
    main_id = fields.Many2one('prakruti.store_issue',string="Main class ID", ondelete='cascade')    
    product_id = fields.Many2one('product.product', string='Product Name')
    uom_id = fields.Many2one('product.uom',string="UOM")
    description = fields.Text(string = "Description")
    batch_no = fields.Char(string = "Batch No",readonly=1)
    approved_quantity = fields.Float(string = "Approved Quantity",readonly=1,digits=(6,3))
    requested_quantity = fields.Float(string = "Req.Quantity", readonly=True,digits=(6,3))
    issued_quantity = fields.Float(string = "Issued Quantity",compute= '_compute_issued_quantity',store=1,digits=(6,3))
    remarks = fields.Text(string="Remarks")    
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3),default=0)
    packing_per_qty = fields.Float(string= 'Packing Per Qty',digits=(6,3),default=0)
    store_qty = fields.Float('Available Stock',digits=(6,3))
    grid_common_id_bom = fields.Integer('Grid common ID')
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.')
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.')
    extra_issued_qty =fields.Float(string='Extra Qty',digits=(6,3))    
    style_flag = fields.Integer(string= 'Style',default=0)
    packing_flag = fields.Integer(string= 'Packing',default=0)
    extra_readonly_flag = fields.Integer(string= 'Extra Flag',default=0)
    extra_issued_packing =fields.Float(string='(+)Extra Packing',default=0,digits=(6,3))
    grn_list = fields.Text(string= 'GRN Nos',readonly=1,default='.')
    packing_details= fields.Char('Packing Details',readonly=1)
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip No')
    reserved_qty = fields.Float(string = 'Reserved Qty',readonly=1,digits=(6,3),default=0)
    revise_issue_line = fields.Integer(string= 'Revised Flag',default=0)
    request_line_id=fields.Integer(string='Grid ID of Request')
    
    virtual_reserved_qty = fields.Float(string = "Reserved Qty",default = 0.000,digits = (6,3),readonly = 1)
    qty_returned = fields.Float(string='Qty Returned',digits=(6,3))
    
    def action_purchase_grn(self, cr, uid, ids, context=None):
        prakruti_store_issue_line = self.browse(cr, uid, ids[0], context=context)
        for temp in prakruti_store_issue_line:
            if temp.store_qty <=0:
                raise UserError(_('Please Check Stock...'))
            else:
                return {
                    'name': ('GRN Number Allocation'),
                    'view_type':'form',
                    'view_mode':'form',
                    'res_model': 'prakruti.grn_store_issue_wizard',
                    'view_id':False,
                    'type':'ir.actions.act_window',
                    'target':'new',
                    'context': {'default_issue_line_id':prakruti_store_issue_line.id,
                                'default_product_id':prakruti_store_issue_line.product_id.id,
                                'default_approved_quantity':prakruti_store_issue_line.approved_quantity,
                                'default_store_qty':prakruti_store_issue_line.store_qty,
                                'default_issue_id':prakruti_store_issue_line.main_id.id
                                }, 
                    }
  
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = False
            self.description = ''
            self.batch_no = ''
            self.remarks = ''
            self.store_qty = 0.0
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description etc.
    '''
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        qty_aval = 0.0
        uom_id = 0
        description = ''
        qty_reserved = 0.0
        purchase_date = False
        last_purchase_vendor_name = False
        uom_name = ''
        last_price = 0
        cr.execute('SELECT product_uom.id AS uom_id, product_uom.name AS uom_name, product_template.name AS description FROM product_uom INNER JOIN product_template ON product_uom.id=product_template.uom_id INNER JOIN product_product ON product_template.id=product_product.product_tmpl_id WHERE product_product.id = cast(%s as integer)', ((product_id),))
        for line in cr.dictfetchall():
            uom_id = line['uom_id']
            description = line['description']
        cr.execute('''SELECT 
                            qty_aval 
                      FROM(
                      SELECT 
                            uom, 
                            product_id, 
                            name, 
                            product_qty as qty_aval 
                            FROM(
                            SELECT 
                                  uom,
                                  product_id, 
                                  name, 
                                  sum(product_qty) as product_qty 
                                  FROM(
                                  SELECT 
                                        product_uom.name as uom,
                                        prakruti_stock.product_id, 
                                        product_product.name_template as name,
                                        prakruti_stock.product_qty
                                  FROM 
                                    product_uom JOIN 
                                    product_template ON 
                                    product_uom.id = product_template.uom_id JOIN 
                                    product_product ON 
                                    product_product.product_tmpl_id = product_template.id JOIN 
                                    prakruti_stock ON 
                                    prakruti_stock.product_id = product_product.id 
                                  WHERE 
                                    product_product.id = CAST(%s as integer)
                                      ) as a group by product_id, name, uom 
                                ) as a 
                            ) AS b 
                        ORDER BY product_id''', ((product_id),))
        for line in cr.dictfetchall():
            qty_aval = line['qty_aval']
        cr.execute('''SELECT                             
                            qty_reserved 
                      FROM(
                      SELECT 
                            reserved_qty as qty_reserved 
                            FROM(
                            SELECT  
                                  sum(reserved_qty) as reserved_qty 
                                  FROM(
                                  SELECT 
                                        prakruti_reserved_product.reserved_qty
                                  FROM
					product_product join				    
					prakruti_reserved_product on
					product_product.id = prakruti_reserved_product.product_id left join
					prakruti_store_issue   on
					prakruti_reserved_product.subplant_id = prakruti_store_issue.subplant_id                                 
                                  WHERE 
					product_product.id = CAST(%s as integer)
                                      ) as a
                                ) as b 
                            ) AS c''', ((product_id),))
        for line in cr.dictfetchall():
            qty_reserved = line['qty_reserved']
        cr.execute('''  SELECT ppl.unit_price AS last_price,ppo.vendor_id AS last_purchase_vendor_name, order_date AS purchase_date FROM prakruti_purchase_order AS ppo INNER JOIN prakruti_purchase_line AS ppl ON ppo.id = ppl.purchase_line_id WHERE ppl.product_id = CAST(%s as integer) and ppo.state = 'order_close' order by ppo.id DESC LIMIT 1''', ((product_id),))
        for line in cr.dictfetchall():
            last_price = line['last_price']
            purchase_date = line['purchase_date']
            last_purchase_vendor_name = line['last_purchase_vendor_name']
        print 'UOM ID',uom_id
        print 'AVAILABLE STOCK',qty_aval
        print 'RESERVED STOCK',qty_reserved
        print 'PRODUCT NAME',description
        print 'VENDOR  NAME',last_purchase_vendor_name
        print 'LAST PRICE',last_price
        return {'value' :{'uom_id':uom_id,
                          'description':description,
                          'store_qty': qty_aval or 0.0,
                          'virtual_reserved_qty': qty_reserved or 0.0
                          }}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''   
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_product(cr, uid, [], vals['product_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('store_qty'):
            vals['store_qty'] = onchangeResult['value']['store_qty']
        return super(PrakrutiStoreIssueItem, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiStoreIssueItem, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        onchangeResult = self.onchange_product(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('store_qty'):
            vals['store_qty'] = onchangeResult['value']['store_qty']
        return super(PrakrutiStoreIssueItem, self).write(cr, uid, ids, vals, context=context)
    '''
    Issued Qty calculation
    '''
    @api.depends('packing_style', 'packing_per_qty','extra_issued_packing')
    def _compute_issued_quantity(self):
        for order in self:
            issued_quantity = 0.0            
            order.update({                
                'issued_quantity': (order.packing_style * order.packing_per_qty) + order.extra_issued_packing
            })
    
    '''
    Issued qty can't be > than Approved Qty
    '''
    #@api.one
    #@api.constrains('issued_quantity')
    #def _check_issued_quantity(self):
        #if ((self.packing_style * self.packing_per_qty) + self.extra_issued_packing) > self.approved_quantity:
            #raise ValidationError(
                #"Issued Qty cannot be more than Approved Qty !")
    
class PrakrutiIssueGrnListLine(models.Model):
    _name = 'prakruti.issue_grn_list_line'
    _table = 'prakruti_issue_grn_list_line'
    _description = 'Issue GRN Line'
    
    _sql_constraints = [        
        ('unique_grn_issue','unique(grn_id, issue_id, product_id)', 'Please Check There Might Be Some GRN No Which Is Already Entered...')
        ]
    
    issue_id = fields.Many2one('prakruti.store_issue',string="Issue ID")
    
    product_id  = fields.Many2one('product.product', string="Product",readonly=1,required=1)
    grn_id= fields.Many2one('prakruti.grn_inspection_details',string= 'GRN No',readonly=1)
    received_qty=fields.Float('Received Qty',readonly=1,default=0)
    issued_qty = fields.Float('Issued Qty',digits=(6,3),readonly=1,default=0)    
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3),readonly=1,default=0)
    packing_per_qty = fields.Float(string= 'Packing Per Qty',digits=(6,3),readonly=1,default=0)
    extra_issued_packing =fields.Float(string='(+)Extra Packing',default=0,digits=(6,3),readonly=1) 
    extra_issued_qty =fields.Float(string='Extra Qty',digits=(6,3),default=0,readonly=1)    
    remarks = fields.Text(string="Remarks")