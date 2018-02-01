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



_logger = logging.getLogger(__name__)
#hdlr = logging.FileHandler('/var/log/odoo/winstrata.log')


class production_report_email(osv.osv_memory):
    _name = "report.production_report_email"
    
    _description = "Production Report Email desc" 
    
    def send_mail(self, cr, uid, ids, cron_mode=True, context=None):        
        ids = 22
        email_obj  = self.pool.get('email.template')
        
        template_id=email_obj.search(cr, uid, [('name', '=', 'All Plant Production Report - Send by Email')], context=context)[0]
        body_content=email_obj.search(cr, uid, [('name', '=', 'All Plant Production Report - Send by Email')], context=context)[0]
        print template_id,'PPPPPPPPPPPPPPPPPP'
        
        #Here 13 is the template id 
        rptHTML = email_obj.generate_html(cr, uid, body_content, ids, context=None)  
        print 'rptHTMLrptHTMLrptHTMLrptHTMLrptHTML',rptHTML
        
        #This piece of code is added to reemove the peragraph tag from html putput i.e from rptHTML
        #If this is not removed in email body the cells will come too big irrespective of our template design
        #These are the fields and html content used to control that  cells height remove1,remove2
        remove1 = '<p style="overflow: hidden; text-indent: 0px; ">'
        remove2 = '</p>' 
       
        rptHTML = rptHTML.replace(remove1, "")	
	rptHTML = rptHTML.replace(remove2, "")
	
	my_date = fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context)

        
	yesterday = date.today() - timedelta(1)
	date1 = 'Prakruti Production Report as on - ' + yesterday.strftime('%d-%m-%Y')
	email_obj.write(cr, uid, template_id, {'body_html': rptHTML})
	email_obj.write(cr, uid, template_id, {'subject': date1})	
        email_obj.send_mail(cr, uid, template_id, ids, force_send=True)
        #email_obj.send_mail_html(cr, uid, template_id, ids, force_send=True)   

    def send_mail_to_plants(self, cr, uid, ids, cron_mode=True, context=None):        
        ids = 22
        #template_id = self.pool.get('email.template').search(cr,uid,[('name','=','Verify Mail to Plants')],context=context)[0]
        #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
        
        email_obj  = self.pool.get('email.template')
        template_id=email_obj.search(cr, uid, [('name', '=', 'Verify Mail to Plants')], context=context)[0]
        cr.execute('''SELECT b.id,b.name,b.email FROM
            (
            SELECT
              prakruti_sub_plant.id,
              PRODUCT_PRODUCT.name_template as name,
              'anilkumar.r@netsoftgroup.in' as email,
              prakruti_production.production_date
            FROM
              public.prakruti_production RIGHT JOIN
              public.prakruti_sub_plant ON prakruti_production.subplant_id = prakruti_sub_plant.id RIGHT JOIN
              PRODUCT_PRODUCT ON PRODUCT_PRODUCT.ID = prakruti_sub_plant.subplant_id
            WHERE
              prakruti_production.production_date = CAST(now()- INTERVAL '1 days' AS date) 
            )AS a RIGHT JOIN
            (
            SELECT
              prakruti_sub_plant.id,
              PRODUCT_PRODUCT.name_template as name,
              'anilkumar.r@netsoftgroup.in' as email
            FROM  
              public.prakruti_sub_plant RIGHT JOIN
              PRODUCT_PRODUCT ON PRODUCT_PRODUCT.ID = prakruti_sub_plant.subplant_id
            WHERE
              plant_type = 'extraction' 
            )AS b ON a.name = b.name
            WHERE
            production_date is null''' )       
        for plant in cr.dictfetchall():
            plantId = plant['id']
            plantName = plant['name']
            plantEmail = plant['email']
            sub =  'Alert message from Prakruti Production Reporting application'          

            yesterday = date.today() - timedelta(1)
            YesDay = yesterday.strftime('%d-%m-%Y')
            yester_day = str(YesDay)
            
               
            body = '''Dear '''+ plantName+''' Incharge, <br/><br/>''' +'''
                    Prakruti production reporting application did not get the data for the date of  ''' + yester_day +'''.  Report application generates automatic report at
                    9:30 AM every day. Please complete the data entry before 9:30 AM
                    so that reporting application takes correct data for reporting.
                    Missing data for today's report have been notified to Production Incharge / Management.
                    Make sure this doesnt happen in the future. <br/><br/> Regards <br/> Prakruti Production Reports application admin''' 
          
            email_obj.write(cr, uid, template_id, {'email_to': plantEmail})
            email_obj.write(cr, uid, template_id, {'subject': sub})
            email_obj.write(cr, uid, template_id, {'body_html': body})
	
  	    my_date = fields.datetime.context_timestamp(cr, uid, datetime.now(), context=context)
          
            #email_obj = self.pool.get('email.template').send_mail(cr, uid, template_id,ids[0],force_send=True)
            email_obj.send_mail(cr, uid, template_id, ids, force_send=True)
    
production_report_email()
