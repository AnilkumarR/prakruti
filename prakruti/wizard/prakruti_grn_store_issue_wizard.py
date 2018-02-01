# -*- coding: utf-8 -*-
from openerp.tools import image_resize_image_big
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

class prakruti_grn_store_issue_wizard(models.TransientModel):
    _name = 'prakruti.grn_store_issue_wizard'
    _table = 'prakruti_grn_store_issue_wizard'
    _description = 'GRN Issue Product Wise Allocation'
    
    product_id= fields.Many2one('product.product', string="Product",readonly=1)
    store_qty= fields.Float(string= 'Store Qty',readonly=1)
    approved_quantity= fields.Float(string= 'Approved Qty',readonly=1,default=0,digits=(6,3))
    issue_line_id = fields.Integer(string= 'Issue Line ID')
    issue_id = fields.Integer(string= 'Issue ID')
    main_id=  fields.One2many('prakruti.grn_store_issue_wizard_line','grn_wizard_id',string= 'GRN Allocation Line ID')       
    
    @api.one
    @api.multi
    def action_approve(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        total_line = 0        
        packing_enter_line = 0
        total_issued_qty = 0
        for temp in self:
            cr.execute(''' select count(id) as total_line from prakruti_grn_store_issue_wizard_line where grn_wizard_id = %s''',((temp.id),))
            for line in cr.dictfetchall():
                total_line = line['total_line']
            cr.execute(''' select count(id) as packing_enter_line from prakruti_grn_store_issue_wizard_line where grn_wizard_id = %s and packing_style > 0 and packing_per_qty > 0''',((temp.id),))
            for line in cr.dictfetchall():
                packing_enter_line = line['packing_enter_line']
            if packing_enter_line == total_line:
                for item in temp.main_id:
                    if ((item.packing_style * item.packing_per_qty) + item.extra_issued_packing) > item.available_qty:
                        raise UserError(_('Your Issued Qty is %s for the GRN Number [ %s ]\n but the Available Stock is %s') %(((item.packing_style * item.packing_per_qty) + item.extra_issued_packing),item.grn_id.grn_no,item.available_qty))
                cr.execute('''  SELECT 
                                sum((coalesce(prakruti_grn_store_issue_wizard_line.packing_style,0) * coalesce(prakruti_grn_store_issue_wizard_line.packing_per_qty,0)) + coalesce(prakruti_grn_store_issue_wizard_line.extra_issued_packing,0)) AS total_issued_qty
                            FROM
                                prakruti_grn_store_issue_wizard_line
                            WHERE
                                prakruti_grn_store_issue_wizard_line.grn_wizard_id = %s
                        ''',((temp.id),))
                for line in cr.dictfetchall():
                    total_issued_qty = line['total_issued_qty']
                if total_issued_qty > temp.approved_quantity:
                    raise UserError(_('Please Check the Total Issued Qty\nIt is exceeding the Approved Qty...'))
                else:
                    cr.execute('''  UPDATE 
                                        prakruti_store_issue_item 
                                    SET
                                        grn_list = b.grn_list,
                                        packing_details = b.packing_details
                                    FROM(
                                        SELECT
                                            array_to_string(array_agg(prakruti_grn_store_issue_wizard_line.grn_no),',') AS grn_list,
                                            prakruti_grn_store_issue_wizard.product_id,
                                            prakruti_grn_store_issue_wizard.issue_line_id,	
                                            array_to_string(array_agg(prakruti_grn_store_issue_wizard_line.packing_style),',') || ' X ' ||
                                            array_to_string(array_agg(prakruti_grn_store_issue_wizard_line.packing_per_qty),',') || ' + ' ||
                                            array_to_string(array_agg(prakruti_grn_store_issue_wizard_line.extra_issued_packing),',') AS packing_details
                                        FROM
                                            prakruti_grn_store_issue_wizard_line JOIN
                                            prakruti_grn_store_issue_wizard ON
                                            prakruti_grn_store_issue_wizard_line.grn_wizard_id = prakruti_grn_store_issue_wizard.id
                                        WHERE
                                            prakruti_grn_store_issue_wizard_line.grn_wizard_id = %s
                                        GROUP BY
                                            prakruti_grn_store_issue_wizard.product_id,
                                            prakruti_grn_store_issue_wizard.issue_line_id
                                        ) AS b
                                    WHERE
                                        b.product_id = prakruti_store_issue_item.product_id AND
                                        b.issue_line_id = prakruti_store_issue_item.id 
                                ''',((temp.id),))
                    
                    cr.execute('''  INSERT INTO prakruti_issue_grn_list_line(product_id,grn_id,received_qty,issued_qty,packing_style,packing_per_qty,extra_issued_packing,issue_id)
                                    SELECT 
                                        prakruti_grn_store_issue_wizard.product_id,
                                        prakruti_grn_store_issue_wizard_line.grn_id,
                                        prakruti_grn_store_issue_wizard_line.received_qty,
                                        sum((coalesce(prakruti_grn_store_issue_wizard_line.packing_style,0) * coalesce(prakruti_grn_store_issue_wizard_line.packing_per_qty,0)) + coalesce(prakruti_grn_store_issue_wizard_line.extra_issued_packing,0)) AS issued_qty,
                                        prakruti_grn_store_issue_wizard_line.packing_style,
                                        prakruti_grn_store_issue_wizard_line.packing_per_qty,
                                        prakruti_grn_store_issue_wizard_line.extra_issued_packing,
                                        prakruti_store_issue_item.main_id
                                    FROM
                                        prakruti_grn_store_issue_wizard JOIN
                                        prakruti_grn_store_issue_wizard_line ON
                                        prakruti_grn_store_issue_wizard.id = prakruti_grn_store_issue_wizard_line.grn_wizard_id JOIN
                                        prakruti_store_issue_item ON
                                        prakruti_store_issue_item.id = prakruti_grn_store_issue_wizard.issue_line_id
                                    WHERE 
                                        prakruti_grn_store_issue_wizard.id = %s                                    
                                    GROUP BY
                                        prakruti_grn_store_issue_wizard.product_id,
                                        prakruti_grn_store_issue_wizard_line.grn_id,
                                        prakruti_grn_store_issue_wizard_line.received_qty,
                                        prakruti_grn_store_issue_wizard_line.packing_style,
                                        prakruti_grn_store_issue_wizard_line.packing_per_qty,
                                        prakruti_grn_store_issue_wizard_line.extra_issued_packing,
                                        prakruti_store_issue_item.main_id''',((temp.id),))
                
            else:
                raise UserError(_('Oops Somewhere You Missed Out Packing Details...'))
        return {}


class prakruti_grn_store_issue_wizard_line(models.TransientModel):
    _name = 'prakruti.grn_store_issue_wizard_line'
    _table = 'prakruti_grn_store_issue_wizard_line'
    _description = 'GRN Issue Product Wise Allocation Line'
    
    grn_wizard_id= fields.Many2one('prakruti.grn_store_issue_wizard', string="GRN Wizard ID")
    grn_id= fields.Many2one('prakruti.grn_inspection_details',string= 'GRN No',required=1)
    grn_no = fields.Char(string= 'GRN No')
    received_qty=fields.Float('Received Qty')
    available_qty=fields.Float('Available Qty')   
    packing_style = fields.Float(string= 'Packing Style',digits=(6,3),default=0)
    packing_per_qty = fields.Float(string= 'Packing Per Qty',digits=(6,3),default=0)
    extra_issued_packing =fields.Float(string='(+)Extra Packing',default=0,digits=(6,3)) 
    issued_qty= fields.Float('Issued Qty',compute= '_compute_issued_qty',digits=(6,3))
    
    product_id = fields.Many2one('product.product', related = 'grn_wizard_id.product_id',string = 'Product',store = 1)

    def on_change_grn_id(self, cr, uid, ids, grn_id,product_id, context=None):
        cr.execute('''  select
                                prakruti_grn_inspection_details_line.available_qty,
                                prakruti_grn_inspection_details.grn_no,
                                prakruti_grn_inspection_details_line.quantity as received_qty
                        from
                                prakruti_grn_inspection_details join
                                prakruti_grn_inspection_details_line on
                                prakruti_grn_inspection_details.id = prakruti_grn_inspection_details_line.inspection_line_id
                        where
                                prakruti_grn_inspection_details.id =  cast(%s as integer) and 
                                prakruti_grn_inspection_details_line.product_id = %s''', ((grn_id),(product_id),))
        for line in cr.dictfetchall():
            grn_no = line['grn_no']
            received_qty = line['received_qty']
            available_qty = line['available_qty']
            result = {
                'grn_no': grn_no,
                'received_qty': received_qty,
                'available_qty': available_qty
                }
            return {'value': result}
  
    
    '''
    Issued Qty calculation
    '''
    @api.depends('packing_style', 'packing_per_qty','extra_issued_packing')
    def _compute_issued_qty(self):
        for order in self:
            issued_qty = 0.0            
            order.update({                
                'issued_qty': (order.packing_style * order.packing_per_qty) + order.extra_issued_packing
            })