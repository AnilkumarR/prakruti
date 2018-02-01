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

class prakruti_tablet_production_notifications(osv.osv_memory):
    _name = "prakruti.tablet_production_notifications"
    _description = "Tablet Production Notifications"  

    def send_mail_to_higher_authority(self, cr, uid, ids, cron_mode=True, context=None):        
        ids = 22
        email_obj  = self.pool.get('email.template')
        template_id=email_obj.search(cr, uid, [('name', '=', 'Tablet Production Hours Exceeds')], context=context)[0]
        cr.execute('''  SELECT  
                                prakruti_tablet_production.write_date,
                                CURRENT_TIMESTAMP,
                                prakruti_tablet_production.batch_end_date,
                                product_product.name_template as subplant_id,
                                prakruti_batch_master.batch_no as batch_id,
                                res_partner.name as created_by,
                                CURRENT_TIMESTAMP-prakruti_tablet_production.write_date as delay_datetime,
                                cast(prakruti_tablet_production.write_date as time) as write_time,
                                cast(CURRENT_TIMESTAMP as time) as current_date,
                                cast(CURRENT_TIMESTAMP as time)-cast(prakruti_tablet_production.write_date as time) as delay_time,
                                (extract(epoch from (timestamp 'now()' - prakruti_tablet_production.write_date))/60)/60 as hours
                                 
                        FROM 
                                prakruti_sub_plant JOIN 
                                prakruti_tablet_production ON
                                prakruti_sub_plant.id = prakruti_tablet_production.subplant_id JOIN
                                prakruti_batch_master ON
                                prakruti_batch_master.id=prakruti_tablet_production.batch_id JOIN
                                product_product ON
                                prakruti_sub_plant.subplant_id = product_product.id JOIN
                                res_users ON 
                                prakruti_tablet_production.created_by = res_users.id JOIN 
                                res_partner ON res_users.partner_id = res_partner.id 
                        WHERE  
                                (CAST('2017-12-16 00:00:00' as timestamp) =
                                prakruti_tablet_production.write_date) OR 
				
                                prakruti_tablet_production.write_date > CAST('2017-12-16 00:00:00' as timestamp)
                                    ''' )       
        for plant in cr.dictfetchall():
            write_date = plant['write_date']
            created_by = plant['created_by']
            batch_id = plant['batch_id']
            subplant_id = plant['subplant_id']
            hours = plant['hours']
            batch_end_date = plant['batch_end_date']
            sub =  'Notifications From Tablet Production Hours Exceeds'          

            yesterday = date.today() - timedelta(1)
            YesDay = yesterday.strftime('%d-%m-%Y')
            yester_day = str(YesDay)
            print 'yester_dayyester_day',yester_day
            if hours> 4:
            
            
                body = '''Dear Sir/Madam <br/><br/>''' +'''Batch no '''+ batch_id +'''for product '''+ subplant_id +''' has exceeded 4 Hours of Action Time and is pending for completion, batch end date is '''+ batch_end_date+'''<br/><br/>'''+'''<i>This is a autogenerated mail please do not reply</i><br/><br/>'''+''' Thanks & Regards <br/>'''+ '''PRAKRUTI PRODUCTS PVT. LTD.'''
            
                #email_obj.write(cr, uid, template_id, {'email_to': 'induja.m@netsoftgroup.in'})
                email_obj.write(cr, uid, template_id, {'subject': sub})
                email_obj.write(cr, uid, template_id, {'body_html': body})
            
                my_date = fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context)
            
                #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
                email_obj.send_mail(cr, uid, template_id, ids, force_send=True)
   
prakruti_tablet_production_notifications()
