'''
Company : EBSL
Author : Karan
Module : Purchase Return
Class 1 : PrakrutiPurchaseReturnItems
Class 2 : PrakrutiPurchaseReturnItemsLine
Table 1 & Reference Id : prakruti_purchase_return,return_line
Table 2 & Reference Id : prakruti_purchase_return_line,return_line_id
Updated By : Karan 
Updated Date & Version : 2017/08/23 & 0.1
'''
import time
import openerp
from datetime import date, datetime
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize, image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError
from openerp import tools
from openerp.tools.translate import _
from datetime import timedelta
##################################################################################################

class PrakrutiPurchaseReturnItems(models.Model):
    _name = 'prakruti.purchase_return'
    _table= 'prakruti_purchase_return'
    _description = 'Purchase Return'
    _rec_name="mrn_no"
    _order = 'id desc'
    
    return_line = fields.One2many('prakruti.purchase_return_line','return_line_id',string='Purchase Return Line')
    invoice_no = fields.Many2one('prakruti.purchase_invoice',string='Select Invoice No.')
    invoice_date=fields.Date('Invoice Date')
    pr_no = fields.Char(string="Requisition No" , readonly=1)
    pr_date= fields.Date(string="Requisition Date", readonly=1)
    po_no = fields.Char(string='Order No', readonly=1)
    vendor_id = fields.Many2one('res.partner',string="Vendor/Supplier", readonly=1)
    return_date= fields.Date(string="Return Date",default=fields.Date.today, readonly=1)
    order_date = fields.Date(string='Order Date', readonly= 1)
    stores_incharge = fields.Many2one('res.users','Stores Incharge',readonly=1)
    dispatch_asst = fields.Many2one('res.users','Dispatch Assistant',readonly=1)
    doc_no=fields.Char('Doc. No')
    rev_no=fields.Char('Rev. No')
    doc_date=fields.Date('Document Date',default= fields.Date.today)
    company_address = fields.Many2one('res.company',string='Company Address',readonly=1)
    purchase_manager = fields.Many2one('res.users',string="Purchase Manager",readonly=1)
    dispatch_through = fields.Char(string='Dispatch Through')
    total= fields.Float(string='Total',digits=(6,3))
    mrn_no=fields.Char('MRN No',readonly=1)
    mrn_date=fields.Date('MRN Date',readonly=1) 
    product_id = fields.Many2one('product.product', related='return_line.product_id', string='Product')
    #added by induja on 20170928 for categorising the products
    categorization = fields.Selection([
		('goods','Goods'),
		('services','Services'),
		('goods_services','Goods and Services')],default= 'goods',string='Category',readonly=1) 
    #added by induja on 20171011 for Other details
    
    document_no = fields.Char(string ="Document No",readonly=1 )
    revision_no = fields.Char(string = "Rev. No",readonly=1)
    default_pr_date = fields.Char(string="Document Date" , default= fields.Date.today,readonly=1)
    plant_manager = fields.Many2one('res.users',string="Plant Manager",readonly=1)
    to_name = fields.Many2one('res.users',string="Name",readonly=1)
    grn_id = fields.Many2one('prakruti.grn_inspection_details',string = 'GRN No',readonly=1)
    grn_date = fields.Date('GRN Date',readonly=1)
    status = fields.Selection([('draft','Return Draft'),  
                              ('debit_note','Debit Note')
                              ],default= 'draft', string= 'Status') 
    grn_no = fields.Char(string= 'GRN No')  
    
    
    '''
    Strictly stopping to delete 
    '''
    @api.multi
    def unlink(self):
        raise UserError(_('Can\'t Delete'))
        return super(PrakrutiPurchaseReturnItems, self).unlink()
    
    
    '''
    Pushing the data to raise Debit Note
    '''
    @api.one
    @api.multi 
    def debit_note(self):
        cr = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = 'context'        
        for temp in self:
            debit_id = self.pool.get('prakruti.debit.note').create(cr,uid, {
                'po_no':temp.po_no,
                'vendor_id':temp.vendor_id.id,
                'order_date':temp.order_date,
                'purchase_manager':temp.purchase_manager.id,
                'categorization':temp.categorization,
                'stores_incharge':temp.stores_incharge.id,
                'company_address':temp.company_address.id,
                'to_name':temp.to_name.id,
                'plant_manager':temp.plant_manager.id,
                'document_no':temp.doc_no,
                'revision_no':temp.rev_no,
                'default_pr_date':temp.default_pr_date,
                })
            for line in temp.return_line:
                debit_line_id = self.pool.get('prakruti.debit.note.line').create(cr,uid, {
                    'product_id': line.product_id.id,
                    'description': line.description,
                    'remarks': line.remarks,
                    'return_qty': line.return_qty,
                    'uom_id': line.uom_id.id, 
                    'unit_price': line.unit_price,
                    'purchase_line_common_id': line.purchase_line_common_id,
                    'hsn_code': line.hsn_code,
                    'discount_rate': line.discount_rate,
                    'cgst_id': line.cgst_id.id,
                    'cgst_rate': line.cgst_rate,
                    'sgst_id': line.sgst_id.id,
                    'sgst_rate': line.sgst_rate,
                    'igst_id': line.igst_id.id,
                    'igst_rate': line.igst_rate,
                    'taxable_value': line.taxable_value,
                    'taxable_value_after_adding_other': line.taxable_value_after_adding_other,
                    'line_id': debit_id
                    })
            cr.execute("UPDATE prakruti_purchase_return SET status = 'debit_note' WHERE id = %s",((temp.id),))
        return {}
    
    
class PrakrutiPurchaseReturnItemsLine(models.Model):
    _name="prakruti.purchase_return_line"
    _table= 'prakruti_purchase_return_line'
    _description = 'Purchase Return Line'
    
    return_line_id = fields.Many2one('prakruti.purchase_return', ondelete='cascade')
    product_id= fields.Many2one('product.product', string="Product", readonly=1)
    description = fields.Char(string="Description", readonly=1)
    uom_id = fields.Many2one('product.uom', string="UOM", readonly=1)
    return_qty= fields.Float(string="Return Qty" ,digits=(6,3))
    quantity= fields.Float(string="Ordered Qty" ,digits=(6,3))
    total= fields.Float(string='Total' ,digits=(6,3))
    no_of_packings =  fields.Float(string="No. of Packing" ,digits=(6,3))
    pack_per_qty = fields.Float(string="Packing Per Qty." ,digits=(6,3))
    extra_packing= fields.Float(string= "(+)Extra Packing",default=0 ,digits=(6,3))
    unit_price = fields.Float(string='Unit price' ,digits=(6,3))
    remarks= fields.Char(string="Remarks")    
    purchase_line_common_id = fields.Integer(string="Purchase Line ID")
    hsn_code = fields.Char(string='HSN/SAC',readonly=1)
    discount_rate = fields.Float(string= 'Discount(%)',default=0)
    cgst_id = fields.Many2one('account.other.tax',string= 'CGST Rate',domain=[('select_type', '=', 'cgst')])
    cgst_rate = fields.Float(related='cgst_id.per_amount',string= 'CGST Rate',default=0,store=1)
    sgst_id = fields.Many2one('account.other.tax',string= 'SGST Rate',domain=[('select_type', '=', 'sgst')])
    sgst_rate = fields.Float(related='sgst_id.per_amount',string= 'SGST Rate',default=0,store=1)
    igst_id = fields.Many2one('account.other.tax',string= 'IGST Rate',domain=[('select_type', '=', 'igst')])
    igst_rate = fields.Float(related='igst_id.per_amount',string= 'IGST Rate',default=0,store=1)
    taxable_value = fields.Float(string= 'Taxable Value',digits=(6,3)) 
    taxable_value_after_adding_other = fields.Float(string='Taxable Value After Adding Other Charges',digits=(6,3))