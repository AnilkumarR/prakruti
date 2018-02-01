'''
Company : EBSL
Author: Induja
Module: Store Approve Request
Class 1: PrakrutiStoreApproveRequest
Class 2: PrakrutiStoreApproveRequestItem
Table 1 & Reference Id: prakruti_store_approve_request ,grid_id
Table 2 & Reference Id: prakruti_store_approve_request_item,main_id
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

class PrakrutiStoreApproveRequest(models.Model):
    _name = 'prakruti.store_approve_request'
    _table = "prakruti_store_approve_request"
    _description = 'Store Approve Request'
    _order='id desc'
    _rec_name = "request_no"
       
    grid_id = fields.One2many('prakruti.store_approve_request_item', 'main_id',string='Grid') 
    purchase_type= fields.Selection([('extraction','Extraction'),('formulation','Formulation')],'Purchase Type')
    request_date = fields.Date('Request Date', readonly=True, default=fields.Date.today)
    approved_date = fields.Date('Approved Date', required=True, default=fields.Date.today)    
    dept_id = fields.Many2one('res.company','Department', readonly=True)
    company_id = fields.Many2one('res.company',string="Company", readonly=True)
    request_no = fields.Char(string = "Request No", readonly=True)    
    requested_by= fields.Many2one('res.users',string="Requested By",readonly=True)    
    approved_by= fields.Many2one('res.users',string="Approved By",required=True)
    store_incharge = fields.Many2one('res.users','Store Incharge',readonly=True)
    plant_incharge = fields.Many2one('res.users',string="Plant Incharge", readonly=True)
    date = fields.Date('Date', default=fields.Date.today, readonly=True) 
    production_incharge = fields.Many2one('res.users',string="Production Incharge", readonly=True)
    doc_no = fields.Char(' Doc No', readonly=True)
    rev_no = fields.Char(' Rev No',readonly=True)    
    state =fields.Selection([
                ('approve','Store Request Approval Draft'),
                ('partial_approve','Store Request Partially Approved'),
                ('issue','Store Issue'),
                ('reject','Rejected'),
                ('partial_issue','Store Partially Issued'),
                ('issued','Store Issued'),
                ('extra_issue','Extra Issued')],default= 'approve', string= 'Status')
    extraction_bom_id = fields.Integer(' Extraction BOM Common id')
    syrup_bom_id = fields.Integer(' Syrup BOM Common id')
    tablet_bom_id = fields.Integer('Tablet BOM Common id')
    batch_no= fields.Many2one('prakruti.batch_master',string= 'Batch No')
    store_location_id= fields.Many2one('stock.location','Store Location')
    syrup_packing_bom_id = fields.Integer(' Syrup Packing BOM Common id')
    tablet_packing_bom_id = fields.Integer(' Tablet Packing BOM Common id')  
    product_id = fields.Many2one('product.product', related='grid_id.product_id', string='Product Name')
    location_id = fields.Many2one('prakruti.stock_location','Store Location')
    revise_status = fields.Selection([('revise_approval','Revise Approval'),('revise_done','Revise Done')],string= 'Revise Status')
    revise_no = fields.Integer(string= '# Of Revision',default=0,readonly=1)
    is_revise = fields.Boolean(string= 'Is Revised',default=0,readonly=1)
    revise_remarks = fields.Text(string= 'Revise Remarks')
    revise_remarks_update = fields.Text(string= 'All Revise Updates',readonly=1,default='-')
    revise_id = fields.Many2one('res.users',string = 'Revised Done By')
    revise_flag = fields.Integer(string= 'Revise Flag',default=0,readonly=1)
    revised_by=fields.Many2one('res.users',string='Revised By')
    
    revise_from_issue = fields.Integer(string= 'Revise from Issue Flag',default=1)
    
    powder_bom_id = fields.Integer('Powder BOM Common id')
    powder_packing_bom_id = fields.Integer(' Powder Packing BOM Common id')
    
    
    coming_from = fields.Char(string = "Coming From")
    subplant_id= fields.Many2one('prakruti.sub_plant', string="Product",readonly=1)
    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner') 
    
    _defaults = {
        'purchase_type':'extraction',
        'requested_by': lambda s, cr, uid, c:uid,
        'store_incharge': lambda s, cr, uid, c:uid,
        'plant_incharge': lambda s, cr, uid, c:uid,
        'production_incharge': lambda s, cr, uid, c:uid,
        'company_id':_default_company,
        'approved_by': lambda s, cr, uid, c:uid,
        'revise_id': lambda s, cr, uid, c:uid 
        }
    
      
    '''
    Cannot able to delete this record 
    '''  
    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ['approve','issue','partial_approve','reject','partial_issue','issued'] or order.coming_from in ['Extraction BOM','Tablet BOM','Syrup BOM','Powder BOM']:
                raise UserError(_('Record Can\'t be Deleted'))
        return super(PrakrutiStoreApproveRequest, self).unlink()  
    
    
    '''
    Approved date can't be < than current date 
    ''' 
    @api.one
    @api.constrains('approved_date')
    def _check_approved_date(self):
        if self.approved_date < fields.Date.today():
            raise ValidationError(
                "Approved Date Can\'t Take Back Date !!!")
        
        
    @api.one
    @api.multi
    def check_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute('''  UPDATE 
                                prakruti_store_approve_request_item 
                            SET 
                                store_qty= qty_aval 
                            FROM ( 
                                SELECT 
                                    product_id,
                                    sum(product_qty) as qty_aval,
                                    id 
                                FROM ( 
                                    SELECT 
                                        prakruti_stock.product_id, 
                                        prakruti_stock.product_qty,
                                        main_id,
                                        prakruti_store_approve_request_item.id 
                                    FROM 
                                        product_template INNER JOIN 
                                        product_product  ON 
                                        product_product.product_tmpl_id = product_template.id INNER JOIN 
                                        prakruti_stock ON 
                                        prakruti_stock.product_id = product_product.id INNER JOIN 
                                        prakruti_store_approve_request_item ON 
                                        prakruti_store_approve_request_item.product_id = prakruti_stock.product_id 
                                    WHERE 
                                        prakruti_store_approve_request_item.main_id = %s
                                      )as a 
                                    GROUP BY product_id,id
                                ) as b 
                            WHERE 
                                b.id = prakruti_store_approve_request_item.id''',((temp.id),))
        return {}
    
    
    
    
    '''
    Pulls the data to Issue Screen
    ''' 
    @api.one
    @api.multi
    def action_to_issue(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        checked_line = 0
        no_of_line = 0
        store_issue = 0
        reject_line = 0
        for temp in self:
            cr = self.env.cr
            uid = self.env.uid
            ids = self.ids
            context = {}
            # MANUAL CLOSE NOT ALLOWED
            cr.execute("SELECT count(id) AS manual_close_line FROM prakruti_store_approve_request_item WHERE status = 'close' AND (approve_flag = 0 OR approve_flag = 1) AND main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                manual_close_line = line['manual_close_line']
            # IF ALL THE ITEMS STATUS ARE CHECKED
            cr.execute("SELECT count(id) AS marked_line FROM prakruti_store_approve_request_item WHERE (status = 'reject' OR status = 'hold' OR status = 'approve' OR status = 'close') AND main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                marked_line = line['marked_line']
            # IF ALL THE ITEMS ARE REJECTED THAN REJECT THE ORDER
            cr.execute("SELECT count(id) AS reject_line FROM prakruti_store_approve_request_item WHERE status = 'reject' AND main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                reject_line = line['reject_line']
            cr.execute("SELECT count(id) AS no_of_line FROM prakruti_store_approve_request_item WHERE main_id = %s",((temp.id),))
            for line in cr.dictfetchall():
                no_of_line = line['no_of_line']
            if manual_close_line >0:
                raise UserError(_('Something Went Wrong...\nYou Can\'t manually close the Order you are only supposed to reject that Particular Item Only...'))
            elif no_of_line != marked_line:
                raise UserError(_('Something Went Wrong...\nPlease Check the Status is Selected or Not...'))
            elif no_of_line == reject_line:
                cr.execute("UPDATE prakruti_store_approve_request SET state = 'reject' WHERE prakruti_store_approve_request.id = cast(%s as integer)",((temp.id),))
                cr.execute("UPDATE prakruti_store_approve_request_item SET approve_flag = 3 WHERE status = 'reject' AND main_id = %s",((temp.id),))
            elif no_of_line != reject_line:
                # IF ALL THE ITEMS ARE REJECTED THAN REJECT THE ORDER
                cr.execute("SELECT count(id) AS reject_line FROM prakruti_store_approve_request_item WHERE status = 'reject' AND main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    reject_line = line['reject_line']
                if reject_line:
                    cr.execute("UPDATE prakruti_store_approve_request_item SET approve_flag = 3 WHERE status = 'reject' AND main_id = %s",((temp.id),)) 
                # IF ALL THE ITEMS ARE NOT REJECTED
                cr.execute("SELECT count(id) AS checked_line FROM prakruti_store_approve_request_item WHERE status = 'approve' AND (approve_flag = 0 OR approve_flag = 1) AND main_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    checked_line = line['checked_line']
                if checked_line:
                    ebsl_id = self.pool.get('prakruti.store_issue').create(cr,uid, {
                        'request_date':temp.request_date,
                        'purchase_type':temp.purchase_type,
                        'request_no':temp.request_no,
                        'dept_id':temp.dept_id.id,
                        'company_id':temp.company_id.id,
                        'store_incharge':temp.store_incharge.id,
                        'plant_incharge':temp.plant_incharge.id,
                        'issued_by':temp.approved_by.id,
                        'requested_by':temp.requested_by.id,
                        'doc_no':temp.doc_no,
                        'date':temp.date,
                        'production_incharge':temp.production_incharge.id,
                        'extraction_bom_id':temp.extraction_bom_id,
                        'syrup_bom_id':temp.syrup_bom_id,
                        'tablet_bom_id':temp.tablet_bom_id,
                        'powder_bom_id':temp.powder_bom_id,
                        'batch_no':temp.batch_no.id,
                        'store_location_id':temp.store_location_id.id,
                        'syrup_packing_bom_id':temp.syrup_packing_bom_id,
                        'powder_packing_bom_id':temp.powder_packing_bom_id,                
                        'tablet_packing_bom_id':temp.tablet_packing_bom_id
                        })
                    cr.execute("SELECT style_flag,packing_flag,product_id,uom_id,description,requested_quantity,approved_quantity,prakruti_store_approve_request_item.remarks,request_line_id,store_qty,grid_common_id,grn_no,ar_no,extra_readonly_flag,extra_issued_packing,prakruti_store_approve_request.id FROM prakruti_store_approve_request_item JOIN prakruti_store_approve_request ON prakruti_store_approve_request.id = prakruti_store_approve_request_item.main_id WHERE (approve_flag = 0 OR approve_flag = 1) AND (approved_quantity <= requested_quantity) AND status = 'approve' AND main_id = %s",((temp.id),))
                    for item in cr.dictfetchall():
                        style_flag = item['style_flag']
                        packing_flag = item['packing_flag']
                        product_id = item['product_id']
                        uom_id = item['uom_id']
                        description = item['description']
                        requested_quantity = item['requested_quantity']
                        approved_quantity = item['approved_quantity']
                        remarks = item['remarks']
                        store_qty = item['store_qty']
                        grid_common_id = item['grid_common_id']
                        grn_no = item['grn_no']
                        ar_no = item['ar_no']
                        extra_readonly_flag = item['extra_readonly_flag']
                        extra_issued_packing = item['extra_issued_packing']
                        request_line_id = item['request_line_id']
                        grid_values = self.pool.get('prakruti.store_issue_item').create(cr,uid, {
                            'style_flag':style_flag,
                            'packing_flag':packing_flag,
                            'product_id':product_id,
                            'uom_id':uom_id,
                            'description':description,
                            'requested_quantity':requested_quantity,
                            'approved_quantity':approved_quantity,
                            'remarks':remarks,
                            'store_qty':store_qty,
                            'grid_common_id_bom':grid_common_id,
                            'grn_no': grn_no,
                            'ar_no': ar_no,
                            'extra_readonly_flag':extra_readonly_flag,
                            'extra_issued_packing':extra_issued_packing,
                            'request_line_id':request_line_id,
                            'main_id':ebsl_id
                            })
                    #UPDATE TOTAL APPROVE QTY
                    cr.execute("UPDATE prakruti_store_approve_request_item SET total_approve_qty = total_approve_qty + approved_quantity WHERE status = 'approve' AND (approve_flag = 1 OR approve_flag = 0) AND main_id = %s",((temp.id),)) 
                    
                    #CHECK IF ANY EXTRA QTY IS ENTERED
                    cr.execute("SELECT COUNT(ID) AS extra_qty_line FROM prakruti_store_approve_request_item WHERE total_approve_qty > requested_quantity AND main_id = %s",((temp.id),))
                    for line in cr.dictfetchall():
                        extra_qty_line = line['extra_qty_line']
                    if extra_qty_line > 0:
                        raise UserError(_('Please Check The Qty Entered...\nPlease follow the Balance Qty...'))
                    
                    #PRODUCT LEVEL UPDATING OF FLAG
                    cr.execute("UPDATE  prakruti_store_approve_request_item SET approve_flag = 2,status = 'close' WHERE status = 'approve' AND (requested_quantity - total_approve_qty) = 0 AND main_id = %s",((temp.id),)) 
                    cr.execute("UPDATE  prakruti_store_approve_request_item SET approve_flag = 1 WHERE status = 'approve' AND (requested_quantity - total_approve_qty) > 0 AND main_id = %s",((temp.id),))
                    
                    # CHECK ANY BALANCE QTY ARE THERE OR NOT
                    cr.execute("SELECT count(id) AS balance_line FROM prakruti_store_approve_request_item WHERE (status = 'approve' OR status = 'hold') AND (approve_flag = 1 OR approve_flag = 0) AND main_id = %s",((temp.id),))
                    for line in cr.dictfetchall():
                        balance_line = line['balance_line']
                    if balance_line:
                        cr.execute("UPDATE  prakruti_store_approve_request SET state = 'partial_approve' WHERE prakruti_store_approve_request.id = cast(%s as integer)",((temp.id),)) 
                        cr.execute("UPDATE  prakruti_store_request SET state = 'partial_approve' WHERE prakruti_store_request.store_request_no = %s",((temp.request_no),))
                    else:
                        cr.execute("UPDATE  prakruti_store_approve_request SET state = 'issue' WHERE prakruti_store_approve_request.id = cast(%s as integer)",((temp.id),)) 
                        cr.execute("UPDATE  prakruti_store_request SET state = 'issue' WHERE prakruti_store_request.store_request_no = %s",((temp.request_no),))
                    #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Store Approve Request')],context=context)[0]
                    #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
                else:
                    # CHECK ANY REJECT AND CLOSE LINE ARE THERE OR NOT
                    cr.execute("SELECT count(id) AS close_reject_line FROM prakruti_store_approve_request_item WHERE (status = 'close' OR status = 'reject') AND main_id = %s",((temp.id),))
                    for line in cr.dictfetchall():
                        close_reject_line = line['close_reject_line']
                    cr.execute("SELECT count(id) AS no_of_line FROM prakruti_store_approve_request_item WHERE main_id = %s",((temp.id),))
                    for line in cr.dictfetchall():
                        no_of_line = line['no_of_line']
                    if close_reject_line == no_of_line:
                        cr.execute("UPDATE  prakruti_store_approve_request SET state = 'issue' WHERE prakruti_store_approve_request.id = cast(%s as integer)",((temp.id),))
                    else:
                        raise UserError(_('Please Check the Status...\nThere Might be some Items which are still kept in Hold...'))
            else:
                raise UserError(_('Something Went Wrong...'))
        return {}

    '''
    This Button helps for Revision(If any changes need to be done in table 2 click this button and enter)
    '''
    @api.one
    @api.multi
    def revise_approval(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            if (temp.extraction_bom_id or temp.syrup_bom_id or temp.tablet_bom_id or temp.syrup_packing_bom_id or temp.tablet_packing_bom_id or temp.powder_bom_id or temp.powder_packing_bom_id)==0:
                ebsl_id = self.pool.get('prakruti.store_approve_request').create(cr,uid, {
                    'company_id':temp.company_id.id,
                    'purchase_type':temp.purchase_type,
                    'request_date':temp.request_date,
                    'dept_id':temp.dept_id.id,
                    'request_no':temp.request_no,
                    'requested_by':temp.requested_by.id,
                    'state':temp.state,
                    'approved_by':temp.approved_by.id,
                    'store_incharge':temp.store_incharge.id,
                    'plant_incharge':temp.plant_incharge.id,
                    'date':temp.date,
                    'production_incharge':temp.production_incharge.id,
                    'doc_no':temp.doc_no,
                    'rev_no':temp.rev_no,
                    'store_location_id':temp.store_location_id.id,
                    'revise_status':temp.revise_status,  
                    'revise_no':temp.revise_no,
                    'is_revise':temp.is_revise,
                    'revise_remarks':temp.revise_remarks,
                    'revise_remarks_update':temp.revise_remarks_update,
                    'revise_id':temp.revise_id.id,
                    'extraction_bom_id':temp.extraction_bom_id,
                    'syrup_bom_id':temp.syrup_bom_id,
                    'powder_bom_id':temp.powder_bom_id,
                    'tablet_bom_id':temp.tablet_bom_id,
                    'batch_no':temp.batch_no.id,
                    'store_location_id':temp.store_location_id.id,                
                    'syrup_packing_bom_id':temp.syrup_packing_bom_id,
                    'powder_packing_bom_id':temp.powder_packing_bom_id,                
                    'tablet_packing_bom_id':temp.tablet_packing_bom_id, 
                    'revise_flag': 1
                    })
                for item in temp.grid_id:
                    erp_id = self.pool.get('prakruti.store_approve_request_item').create(cr,uid, {
                        'product_id': item.product_id.id,
                        'uom_id': item.uom_id.id,
                        'description':item.description,
                        'batch_no':item.batch_no,
                        'requested_quantity':item.requested_quantity,
                        'approved_quantity': item.approved_quantity,
                        'remarks':item.remarks, 
                        'grn_no': item.grn_no.id,
                        'ar_no': item.ar_no.id,
                        'style_flag': item.style_flag,
                        'packing_flag': item.packing_flag,
                        'extra_readonly_flag':item.extra_readonly_flag,
                        'extra_issued_packing':item.extra_issued_packing,
                        'request_line_id':item.request_line_id,
                        'approve_flag':item.approve_flag,
                        'status':item.status,
                        'store_qty':item.store_qty,
                        'grid_common_id':item.grid_common_id,
                        'total_approve_qty':item.approved_quantity,
                        'revise_issue_line':item.revise_issue_line,
                        'main_id':ebsl_id
                        })
                cr.execute("UPDATE prakruti_store_approve_request SET revise_status = 'revise_approval',is_revise = 'True' WHERE id = %s",((temp.id),))
                cr.execute("UPDATE prakruti_store_approve_request_item SET revise_issue_line = 1 WHERE main_id = %s",((temp.id),)) 
            else:
                raise UserError(_('Record...Can\'t Be Revised...\n Record is coming From BOM...!!!'))
                
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
            #if temp.revise_from_issue==2:
                #if temp.revise_remarks:
                    #if temp.revise_id:
                        #cr.execute("UPDATE prakruti_store_approve_request_item SET revise_issue_line = 2 ,status='close' WHERE main_id = %s",((temp.id),))
                        #cr.execute("UPDATE prakruti_store_issue SET revise_status = 'revise_done' WHERE request_no = %s",((temp.request_no),))
                        #cr.execute('''SELECT revise_store_approve_request AS error_message FROM revise_store_approve_request(%s,%s)''',((temp.id),(temp.request_no),))
                        #for line in cr.dictfetchall():
                            #error_message = line['error_message']
                        #if error_message == 'Record Cannot be Revised':
                                #raise UserError(_('Record...Can\'t Be Revised...\nPlease check Issued Qty...\nPlease Contact Your Administrator...!!!'))
                    #else:
                        #raise UserError(_('Please enter Revised Person...'))
                #else:
                    #raise UserError(_('Please enter Revise Remarks...'))
            #else:
            if temp.revise_remarks:
                if temp.revise_id:
                    cr.execute("UPDATE prakruti_store_approve_request_item SET revise_issue_line = 2 WHERE main_id = %s",((temp.id),))
                    cr.execute('''SELECT revise_store_approve_request AS error_message FROM revise_store_approve_request(%s,%s)''',((temp.id),(temp.request_no),))
                    for line in cr.dictfetchall():
                        error_message = line['error_message']
                    if error_message == 'Record Cannot be Revised':
                            raise UserError(_('Record...Can\'t Be Revised...\nPlease check Issued Qty...\nPlease Contact Your Administrator...!!!'))
                else:
                    raise UserError(_('Please enter Revised Person...'))
            else:
                raise UserError(_('Please enter Revise Remarks...'))
        return {} 



class PrakrutiStoreApproveRequestItem(models.Model):
    _name = 'prakruti.store_approve_request_item'
    _table = "prakruti_store_approve_request_item"
    _description = 'Store Approve Request Item'
        
    main_id = fields.Many2one('prakruti.store_approve_request',string="Main class ID") 
    product_id = fields.Many2one('product.product', string='Product Name')
    uom_id = fields.Many2one('product.uom',string="UOM")
    description = fields.Text(string = "Description")
    batch_no = fields.Char(string = "Batch No", readonly=True)
    requested_quantity = fields.Float(string = "Req.Quantity", readonly=True,digits=(6,3))
    approved_quantity = fields.Float(string = "Approved Quantity",digits=(6,3))
    remarks = fields.Text(string="Remarks")
    store_qty = fields.Float(string="Store Qty", readonly=True,digits=(6,3))   
    grid_common_id = fields.Integer('Grid common id')
    grn_no = fields.Many2one('prakruti.grn_inspection_details',string='GRN No.')
    ar_no = fields.Many2one('prakruti.specification.ar.no',string='AR No.')    
    style_flag = fields.Integer(string= 'Style',default=0)
    packing_flag = fields.Integer(string= 'Packing',default=0)
    extra_readonly_flag = fields.Integer(string= 'Extra Flag',default=0)
    extra_issued_packing = fields.Float(string= 'Extra Packing',default=0,digits=(6,3))
    status = fields.Selection([('hold','Hold'),('approve','Approved'),('reject','Reject'),('close','Close')],string= 'Status',default='approve')
    balance_qty = fields.Float(string= 'Balance Qty',compute= '_compute_balance_qty')
    approve_flag = fields.Integer(string= 'Approve Flag',default=0,readonly=1)# 0 for initial 1 for partial and 2 for close and 3 for reject
    total_approve_qty = fields.Float(string= 'Total Approved Qty.',default=0,digits=(6,3),readonly=1)
    reserved_qty = fields.Float(string = 'Reserved Qty',readonly=1,digits=(6,3),default=0)
    
    revise_issue_line = fields.Integer(string= 'Revised Flag',default=0)
    request_line_id=fields.Integer(string='Grid id of Request')
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = False
            self.description = ''
            self.batch_no = ''
            self.requested_quantity = 0
            self.remarks = ''
            self.store_qty = 0.0
    '''
    While changing the product it will load by defaults whatever values are required for that particular product such as uom id, description etc.
    '''
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        qty_aval = 0.0
        uom_id = 0
        description = ''
        qty_aval = 0
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
        cr.execute('''  SELECT ppl.unit_price AS last_price,ppo.vendor_id AS last_purchase_vendor_name, order_date AS purchase_date FROM prakruti_purchase_order AS ppo INNER JOIN prakruti_purchase_line AS ppl ON ppo.id = ppl.purchase_line_id WHERE ppl.product_id = CAST(%s as integer) and ppo.state = 'order_close' order by ppo.id DESC LIMIT 1''', ((product_id),))
        for line in cr.dictfetchall():
            last_price = line['last_price']
            purchase_date = line['purchase_date']
            last_purchase_vendor_name = line['last_purchase_vendor_name']
        print 'UOM ID',uom_id
        print 'AVAILABLE STOCK',qty_aval
        print 'PRODUCT NAME',description
        print 'VENDOR  NAME',last_purchase_vendor_name
        print 'LAST PRICE',last_price
        return {'value' :{'uom_id':uom_id,
                          'description':description,
                          'store_qty': qty_aval or 0.0
                          }}
    '''
    Its a ORM Insert Method, Its is used because whenever we run the onchange_product the fields which are fetched from that are not save in the backend because of the readonly fields so to save in the database we use this method
    '''   
    def create(self, cr, uid, vals, context=None):
        onchangeResult = self.onchange_product(cr, uid, [], vals['product_id'])
        if onchangeResult.get('value') or onchangeResult['value'].get('store_qty'):
            vals['store_qty'] = onchangeResult['value']['store_qty']
        return super(PrakrutiStoreApproveRequestItem, self).create(cr, uid, vals, context=context)
    '''
    Its a ORM Update Method, Its will only work whenever the create is done 
    '''
    def write(self, cr, uid, ids, vals, context=None):
        op=super(PrakrutiStoreApproveRequestItem, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            store_type=record.product_id.id
        onchangeResult = self.onchange_product(cr, uid, ids, store_type)
        if onchangeResult.get('value') or onchangeResult['value'].get('store_qty'):
            vals['store_qty'] = onchangeResult['value']['store_qty']
        return super(PrakrutiStoreApproveRequestItem, self).write(cr, uid, ids, vals, context=context)
    
    '''
    Balance Qty calculation
    ''' 
    @api.depends('approved_quantity','total_approve_qty')
    def _compute_balance_qty(self):
        for order in self:
            order.update({
                'balance_qty': order.requested_quantity - order.total_approve_qty
                })
    
    '''
    Validation for approved Qty
    ''' 
    @api.one
    @api.constrains('approved_quantity')
    def _check_approved_quantity(self):
        if self.approved_quantity <= 0 :
            raise ValidationError(
                "Approved Qty. Can't be Negative or Zero !!!")
        if self.revise_issue_line==0:
            if self.approved_quantity > self.requested_quantity:
                raise ValidationError(
                    "Approved Qty. Can't be Greater than Requested Qty. !!!")