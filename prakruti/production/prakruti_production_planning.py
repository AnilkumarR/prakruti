'''
Company : EBSL
Author: Induja
Module: Production Planning
Class 1: PrakrutiProductionPlanning
Class 2: PrakrutiProductionPlanningLine
Table 1  & Reference id  : prakruti_production_planning ,planning_line
Table 2 & Reference id  : prakruti_production_planning_line ,planning_id
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

class PrakrutiProductionPlanning(models.Model):
    _name = 'prakruti.production_planning'
    _table = 'prakruti_production_planning'
    _description = 'Production Planning'
    _order= "id desc"
    _rec_name= 'product_id' 
    
    planning_line = fields.One2many('prakruti.production_planning_line','planning_id',string = 'Planning Line')
    slip_no= fields.Char(string='Slip No.',readonly=1)
    product_id = fields.Many2one('product.product',string= 'Product Name',readonly=1)
    standard_batch_id = fields.Many2one('prakruti.standard_product',string = 'Batch Size')
    output_yield_qty = fields.Float(string= 'Output Yield Qty',digits=(6,3))
    standard_yield_qty= fields.Float(related= 'standard_batch_id.standard_output_yield',string= "Standard Yield Qty",digits=(6,3),store=1,readonly=1)
    raw_material_id = fields.Many2one('product.product', related = 'planning_line.product_id', string='Raw Material')
    flag_display_count = fields.Integer(string='Display Product',default=0)
    flag_delete_count = fields.Integer(string='Delete Product',default=0)
    all_send_to_request = fields.Integer(string='All Send To Request',default=0,readonly=1)
    request_id = fields.Many2one('res.users',string= 'Requested By')
    ps_line_grid_id = fields.Integer('Production Slip Line Grid ID')
    status = fields.Selection([('planning','Production Planning Draft'),('done','Production Planning Done')],default='planning',string= 'Status')
    availble_stock_qty = fields.Float(string= 'Available Stock',digits=(6,3),readonly=1)
    slip_id = fields.Many2one('prakruti.production_slip',string = 'Slip ID',readonly=1)
    location_id = fields.Many2one('prakruti.stock_location',string = 'Location')
    company_id = fields.Many2one('res.company',string = 'Company',default=lambda self: self.env.user.company_id,required="True")
    remarks = fields.Text(string= 'Remarks')
    
    
    '''
    means that automatically shows this fields while creating this record.
    '''
    _defaults = {
        'request_id': lambda s, cr, uid, c:uid
        }
    
    '''
    listing the products  from Standard product
    '''
    @api.one
    @api.multi
    def action_list_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("SELECT prakruti_standard_product_line.product_id,prakruti_standard_product_line.uom_id,prakruti_standard_product_line.description,prakruti_standard_product_line.standard_value FROM prakruti_standard_product_line INNER JOIN prakruti_standard_product ON prakruti_standard_product.id=prakruti_standard_product_line.standard_line_id INNER JOIN prakruti_production_planning ON prakruti_production_planning.standard_batch_id = prakruti_standard_product.id WHERE prakruti_production_planning.id = CAST(%s as integer)",((temp.id),))
            for item in cr.dictfetchall():
                print 'CURRENT DATABASE CURSOR',cr
                print 'CURRENT USER ID',uid
                print 'CURRENT IDS',ids
                product_id=item['product_id']
                uom_id=item['uom_id']
                description =item['description']
                standard_value=item['standard_value']
                product_line = self.pool.get('prakruti.production_planning_line').create(cr,uid, {
                    'product_id':product_id,
                    'uom_id':uom_id,
                    'description':description,
                    'standard_value':standard_value,
                    'planning_id':temp.id,
                        })
            cr.execute("UPDATE  prakruti_production_planning SET flag_display_count = 1,flag_delete_count = 0 WHERE id = %s",((temp.id),))
        return {}
    
    
    '''
    deleting produts in planning
    '''        
    @api.one
    @api.multi
    def action_delete_products(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        for temp in self:
            cr.execute("DELETE FROM prakruti_production_planning_line WHERE planning_id = %s", ((temp.id),))
            cr.execute("UPDATE  prakruti_production_planning SET flag_delete_count = 1,flag_display_count = 0 WHERE id = %s",((temp.id),))
        return {}
        
    
    '''
    Checking stock
    '''
    @api.one
    @api.multi
    def check_stock(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute("SELECT planning_update_stock(%s)",((temp.id),))
            cr.execute('''  UPDATE
                                prakruti_production_planning_line
                            SET
                                group_id = a.group_id
                            FROM(
                                SELECT 
                                    product_group.id as group_id,
                                    prakruti_production_planning_line.id as sub_id,
                                    prakruti_production_planning.id as main_id
                                FROM 
                                    prakruti_production_planning JOIN
                                    prakruti_production_planning_line on
                                    prakruti_production_planning_line.planning_id = prakruti_production_planning.id JOIN
                                    product_product ON
                                    prakruti_production_planning_line.product_id = product_product.id JOIN
                                    product_template ON
                                    product_product.product_tmpl_id = product_template.id JOIN
                                    product_group ON
                                    product_template.group_ref = product_group.id
                                WHERE 
                                    prakruti_production_planning_line.planning_id = %s                                
                                ) as a
                            WHERE
                                a.sub_id = prakruti_production_planning_line.id AND
                                a.main_id = prakruti_production_planning_line.planning_id''',((temp.id),))
            cr.execute('''  UPDATE
                                prakruti_production_planning_line
                            SET
                                requisition_status = 'False'
                            FROM(
                                SELECT 
                                    prakruti_production_planning_line.id as sub_id,
                                    prakruti_production_planning.id as main_id
                                FROM 
                                    prakruti_production_planning JOIN
                                    prakruti_production_planning_line on
                                    prakruti_production_planning_line.planning_id = prakruti_production_planning.id
                                WHERE 
                                    prakruti_production_planning_line.planning_id = %s AND
                                    (prakruti_production_planning.output_yield_qty * prakruti_production_planning_line.standard_value)/prakruti_production_planning.standard_yield_qty <= prakruti_production_planning_line.virtual_qty
                                ) as a
                            WHERE
                                a.sub_id = prakruti_production_planning_line.id AND
                                a.main_id = prakruti_production_planning_line.planning_id''',((temp.id),))
            cr.execute('''  UPDATE
                                prakruti_production_planning_line
                            SET
                                requisition_status = 'True'
                            FROM(
                                SELECT 
                                    prakruti_production_planning_line.id as sub_id,
                                    prakruti_production_planning.id as main_id
                                FROM 
                                    prakruti_production_planning JOIN
                                    prakruti_production_planning_line on
                                    prakruti_production_planning_line.planning_id = prakruti_production_planning.id
                                WHERE 
                                    prakruti_production_planning_line.planning_id = %s AND
                                    (prakruti_production_planning.output_yield_qty * prakruti_production_planning_line.standard_value)/prakruti_production_planning.standard_yield_qty > prakruti_production_planning_line.virtual_qty
                                ) as a
                            WHERE
                                a.sub_id = prakruti_production_planning_line.id AND
                                a.main_id = prakruti_production_planning_line.planning_id''',((temp.id),))
        return {}
    
    '''
   Pulls the data to BMR Requistion
    '''    
    @api.one
    @api.multi 
    def raise_purchase_requisition(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            cr.execute("SELECT count(id) as requisition_flag_status FROM prakruti_production_planning_line WHERE planning_id = %s AND requisition_status = 'True' AND requisition_flag = 0",((temp.id),))
            for line in cr.dictfetchall():
                requisition_flag_status = line['requisition_flag_status']
            if requisition_flag_status >= 1:
                cr.execute('''  SELECT 
                                    DISTINCT group_id 
                                FROM 
                                    prakruti_production_planning_line
                                WHERE 
                                    planning_id = %s AND 
                                    requisition_status = 'True' AND 
                                    requisition_flag = 0''',((temp.id),))
                for p_group in cr.dictfetchall():
                    group_id = p_group['group_id']
                    print 'GROUPS ARE AS FOLLOWS ',group_id
                    ebsl_id = self.pool.get('prakruti.purchase_requisition').create(cr,uid, {
                        'purchase_manager':temp.request_id.id,
                        'plant_manager':temp.request_id.id,
                        'stores_incharge':temp.request_id.id,
                        'company_id':temp.company_id.id,
                        'to_name':temp.request_id.id,
                        'purchase_type':group_id,
                        'remarks':'Requisition Raised Against this Slip Number ' + temp.slip_no + ' For Production'
                        })
                    for item in temp.planning_line:
                        if (group_id == item.group_id.id and item.requisition_status == True and item.requisition_flag == 0):
                            print 'Requisition Status',item.requisition_status
                            print 'Requisition Falg',item.requisition_flag
                            print 'PRODUCT NAME',item.product_id.name_template
                            grid_values = self.pool.get('prakruti.purchase_requisition_line').create(cr,uid,{
                                'product_id':item.product_id.id,
                                'description':item.description,
                                'uom_id':item.uom_id.id,
                                'quantity_req':(temp.output_yield_qty * item.standard_value)/temp.standard_yield_qty - item.virtual_qty,
                                'remarks':temp.slip_no,
                                'slip_id':temp.slip_id.id,
                                'order_id':ebsl_id
                                })
                cr.execute("UPDATE prakruti_production_planning_line SET requisition_flag = 1 WHERE requisition_status = 'True' AND planning_id = %s",((temp.id),))
                cr.execute("SELECT count(id) as flag_line FROM prakruti_production_planning_line WHERE planning_id = %s AND requisition_flag = 1",((temp.id),))
                for line in cr.dictfetchall():
                    flag_line = line['flag_line']
                cr.execute("SELECT count(id) as total_line FROM prakruti_production_planning_line WHERE planning_id = %s",((temp.id),))
                for line in cr.dictfetchall():
                    total_line = line['total_line']
                if total_line == flag_line:
                    cr.execute("UPDATE prakruti_production_planning SET all_send_to_request = 1 WHERE id = %s",((temp.id),))
            else:
                raise UserError(_('No Any Product to send for Requisition'))
        return {}
    
    
    '''
    Updating data to productiion slip
    '''
    @api.one
    @api.multi 
    def update_production_slip(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'
        virtual_quantity = 0.0
        for temp in self:
            for line in temp.planning_line:
                #Push to Reservation Screen
                reserved_id = self.pool.get('prakruti.reserved_product').create(cr,uid,{
                    'slip_id':temp.slip_id.id,
                    'subplant_id':temp.product_id.id,
                    'product_id':line.product_id.id,
                    'reserved_qty':line.actual_qty
                    })
                cr.execute("SELECT prakruti_production_planning.output_yield_qty,prakruti_production_planning.standard_yield_qty,prakruti_production_planning_line.standard_value FROM public.prakruti_production_planning, public.prakruti_production_planning_line WHERE prakruti_production_planning.id = prakruti_production_planning_line.planning_id AND prakruti_production_planning_line.product_id = CAST(%s AS INTEGER) AND prakruti_production_planning.id = CAST(%s AS INTEGER)", ((line.product_id.id),(temp.id),))
                for item in cr.dictfetchall():
                    output_yield_qty = item['output_yield_qty']
                    standard_value = item['standard_value']
                    standard_yield_qty = item['standard_yield_qty']
                cr.execute('''  SELECT 
                                    product_id,
                                    name,
                                    id,
                                    (sum(virtual_qty)) as virtual_quantity 
                                FROM ( 
                                    SELECT 
                                        prakruti_stock.product_id,
                                        product_template.name,
                                        prakruti_stock.virtual_qty,
                                        prakruti_production_planning_line.id 
                                    FROM 
                                        product_template INNER JOIN 
                                        product_product  ON 
                                        product_product.product_tmpl_id = product_template.id INNER JOIN 
                                        prakruti_stock ON 
                                        prakruti_stock.product_id = product_product.id INNER JOIN 
                                        prakruti_production_planning_line ON 
                                        prakruti_production_planning_line.product_id = prakruti_stock.product_id 
                                    WHERE 
                                        prakruti_production_planning_line.planning_id = %s
                                    )AS a GROUP BY product_id,id,name''',((temp.id),))
                for item in cr.dictfetchall():
                    virtual_quantity = item['virtual_quantity']
                    print '-----PRODUCT ID------',line.product_id.id
                    print '-----PRODUCT NAME-------',line.product_id.name_template
                    print '-----ACTUAL QTY---------',((output_yield_qty * standard_value)/standard_yield_qty)
                    print '-----VIRTUAL QTY--------',line.virtual_qty
                    print '-----INVALID VIRTUAL QTY--------',virtual_quantity
                    if ((output_yield_qty * standard_value)/standard_yield_qty) > line.virtual_qty:
                        raise UserError(_('Your Actual Qty is %s for the Product [ %s ] and the Stock Availability is %s') %(((output_yield_qty * standard_value)/standard_yield_qty),line.product_id.name_template,line.virtual_qty))
            cr.execute("UPDATE prakruti_production_slip_line AS b SET planning_done = 'True' FROM(SELECT ps_line_grid_id,product_id FROM prakruti_production_planning WHERE id= %s ) AS a WHERE a.ps_line_grid_id = b.id AND a.product_id = b.product_id",((temp.id),))
            cr.execute("UPDATE prakruti_production_planning SET status = 'done' WHERE id = %s",((temp.id),))
            cr.execute('''SELECT update_planning(%s)''',((temp.id),))
        return True

class PrakrutiProductionPlanningLine(models.Model):
    _name= 'prakruti.production_planning_line'
    _table = 'prakruti_production_planning_line'
    _description = 'Production Planning Line'
    _order= "id desc"
    
    planning_id = fields.Many2one('prakruti.production_planning',string= 'Planning ID',readonly=1)
    product_id = fields.Many2one('product.product',string= 'Ingredient',readonly=1,required=1)
    description = fields.Text(string= 'Description',readonly=1)
    uom_id= fields.Many2one('product.uom', string="UOM",readonly=1)
    standard_value=fields.Float(string='Standard Qty',digits=(6,3),default=0,readonly=1)
    actual_qty=fields.Float(string='Actual Qty',digits=(6,3),compute= '_compute_actual_qty')
    virtual_qty = fields.Float(string="Available Qty",digits=(6,3),default=0,readonly=1)
    store_qty = fields.Float(string="Store Qty",digits=(6,3),readonly=1,default=0)
    requisition_qty = fields.Float(string="Requisition Qty",digits=(6,3),compute= '_calculate_requisition_qty')
    standard_yield_qty= fields.Float(related='planning_id.standard_yield_qty',string="Standard Yield Qty")
    output_yield_qty= fields.Float(related='planning_id.output_yield_qty',string="Output Yield Qty")
    remarks = fields.Text(string= 'Remarks')
    requisition_status = fields.Boolean(string= 'Requisition Check')
    requisition_flag = fields.Integer(string= 'Requisition Flag',default=0,readonly=1)
    group_id = fields.Many2one('product.group',string = 'Product Group',readonly=1)
    
    '''
    While selecting product  automatically store qty of particular product will dispaly
    ''' 
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        line3 = 0.0
        qty_aval = 0.0
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
            line3 = line['qty_aval']
        print 'AVAILABLE STOCK',line3
        return {'value' :{
                          'store_qty': line3 or 0.0
                          }}
    '''
    Actual Qty calculation
    ''' 
    @api.depends('standard_yield_qty','output_yield_qty','standard_value')
    def _compute_actual_qty(self):
        for order in self:
            actual_qty = single_value = standard_value = standard_yield_qty = output_yield_qty = 0.0
            single_value = (order.output_yield_qty * order.standard_value)/order.standard_yield_qty
            order.update({
                'actual_qty': single_value
                })
    '''
    requistion qty calculation
    ''' 
    @api.depends('store_qty','actual_qty')
    def _calculate_requisition_qty(self):
        for order in self:
            store_qty = actual_qty = 0.0
            if order.actual_qty <= order.virtual_qty:
                order.update({
                    'requisition_qty': 0
                    #,'requisition_status':False
                    })
            else:
                order.update({
                    'requisition_qty': order.actual_qty - order.virtual_qty
                    #,'requisition_status':True
                    })