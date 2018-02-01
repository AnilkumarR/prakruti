# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp.tools.translate import _
import time
from datetime import datetime
import sys, os, urllib2, urlparse
import sys, os, urllib2, urlparse
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import email, re
from datetime import datetime
from datetime import date, timedelta
import cgi
import lxml.html
import lxml.html.clean as clean
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
from openerp import models, fields, api,_
    
    
class PrakrutiProductionPlanningNotifications(models.TransientModel):
    _name = "prakruti.production_planning_notifications"
    _table = "prakruti_production_planning_notifications"
    _description = "Production Planning Notifications"  
    
    
    notification_slip_line = fields.One2many('prakruti.production_planning_notifications_line','slip_notification_id',string = 'Slip Notifications Line')
    notification_id = fields.Integer(string = 'Notification ID')
    
    def send_mail_to_higher_authority(self, cr, uid, ids, cron_mode=True, context=None):        
        ids = 22
        
        email_obj  = self.pool.get('email.template')
        template_id=email_obj.search(cr, uid, [('name', '=', 'Planning Notifications')], context=context)[0]
        email_obj.write(cr, uid, template_id, {'email_to': 'induja.m@netsoftgroup.in'})
        email_obj.send_mail(cr, uid, template_id, ids, force_send=True)
        cr.execute('''  INSERT INTO prakruti_production_planning_notifications
                                        (
                                        notification_id
                                        )
                        VALUES (1)
                    ''')       
        cr.execute('''  INSERT INTO prakruti_production_planning_notifications_line
                                    (
                                    product_name,
                                    scheduled_date,
                                    scheduled_qty,
                                    raw_material,
                                    store_qty,
                                    slip_notification_id
                                    )
                        SELECT
                            product_name,
                            scheduled_date,
                            scheduled_qty,
                            raw_material,
                            store_qty,
                            slip_notification_id
                        FROM(
                            SELECT
                                prakruti_production_slip_line.description AS product_name,
                                prakruti_production_slip_line.scheduled_date,
                                prakruti_production_slip_line.scheduled_qty,
                                prakruti_production_planning_line.description AS raw_material,
                                prakruti_production_planning_line.store_qty,
                                1 AS notification_id
                            FROM	
                                prakruti_production_planning JOIN
                                prakruti_production_planning_line ON
                                prakruti_production_planning_line.planning_id = prakruti_production_planning.id JOIN
                                prakruti_production_slip_line ON
                                prakruti_production_planning.product_id = prakruti_production_slip_line.product_id JOIN
                                prakruti_production_slip ON
                                prakruti_production_slip.id = prakruti_production_planning.slip_id                    
                            WHERE
                                prakruti_production_slip_line.scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 15
                            ) AS a JOIN (
                                SELECT 
                                    prakruti_production_planning_notifications.id AS slip_notification_id,
                                    prakruti_production_planning_notifications.notification_id
                                FROM  
                                    prakruti_production_planning_notifications
                                ORDER BY id desc limit 1
                                        ) AS b ON a.notification_id = b.notification_id
                    ''')
       

class PrakrutiProductionPlanningNotificationsLine(models.TransientModel):
    _name = "prakruti.production_planning_notifications_line"
    _table = "prakruti_production_planning_notifications_line"
    _description = "Production Planning Notifications Line"  
    
    slip_notification_id = fields.Many2one('prakruti.production_planning_notifications',string = 'Slip Notification ID')
    product_name = fields.Char(string = 'Finished Product')
    scheduled_date = fields.Date(string = 'Scheduled Date')
    scheduled_qty = fields.Float(string = 'Scheduled Qty')
    raw_material = fields.Char(string = 'Raw Material')
    store_qty = fields.Float(string = 'Store Qty')