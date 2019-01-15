# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api,tools

from odoo.exceptions import ValidationError



#     its is a activity category Master to add activity(for ex: income )
class ActivityCategory(models.Model):
    _name="activity.category"
    _rec_name='activity_category'
    activity_category=fields.Char(string='Activity Category', help="Add Activity Category Here")
    color = fields.Char(string="Color",help="Choose your color",size=7)
    tag_ids=fields.Many2one('res.partner')

#       its is a activity type Master to add activity(for ex: income -->tax)
class ActivityType(models.Model):
    _name="activity.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='activity_type'


    activity_category_id=fields.Many2one('activity.category',string='Activity Category',help="Add Activity Category Here")
    activity_type=fields.Char(string="Activity Type",help="Add Activity Type Here") 


    # hide = fields.Boolean(string='Hide', compute="_compute_hide")
    # @api.onchange('activity_category_id')
    # def _onchange_act(self):
    #     if self.activity_category_id:
    #         return {'domain': {'eactivity_types_ids': [('activity_category_id', '=', self.activity_category_id.id)]}}
    #     else:
    #         return {'domain': {'eactivity_types_ids': []}}


    
        
    # Show Hide State selection based on Country
    # @api.depends('act')
    # def _compute_hide(self):
    #     if self.act:
    #         self.hide = False
    #     else:
    #         self.hide = True

#       its is a Sub Activity type Master to add  Sub activity(for ex: income -->tax-->file,cash etc.)

class SubActivity(models.Model):
    _name='subactivity'
    name=fields.Char('Sub Activity',required=True,help="Add Sub Activity Here")
    activity_category_id=fields.Many2one(related='eactivity_types_ids.activity_category_id',string='Activity Category',help="Add Activity Category Here")
    eactivity_types_ids=fields.Many2one('activity.type',string='Activity Type',help="Add Activity Type Here")
    user_id=fields.Many2one('res.users',string='User')
    date=fields.Date(string="Task Date")
    main_id=fields.Many2one('reminder')

    #open sub activity on the basis of activity

    @api.onchange('activity_category_id')
    def _onchange_act(self):
        if self.activity_category_id:
            return {'domain': {'eactivity_types_ids': [('activity_category_id', '=', self.activity_category_id.id)]}}
        else:
            return {'domain': {'eactivity_types_ids': []}}


class Reminder(models.Model):
    _name='reminder'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']
    _rec_name = 'user_id'


    activity_category_id=fields.Many2one(related='eactivity_types_ids.activity_category_id',string='Activity Category',help="Add Activity Category Here")
    eactivity_types_ids=fields.Many2one('activity.type',string='Activity Type',help="Add Activity Type Here")
    user_id=fields.Many2one('res.users',string="User",store=True,default=lambda self: self.env.uid,help="Add User Here")
    customer_name=fields.Many2one('res.partner',help="Add Customer Name Here")
    active = fields.Boolean(default=True)
    rem_date= fields.Date(string="Reminder",store=True,required=True,help="Add Reminder Date Here")
    last_date= fields.Date(string='Last Date',store=True,required=True,help="Add Last Date Here")
    actual_date= fields.Date(string='Actual Date',help="Add Actual Date Here")
    target_date= fields.Date(string='Target Date',store=True ,required=True,help="Add Taget Date Here")
    status= fields.Selection([('pending','Pending'),('hold','On Hold'),('done','Done')],string="status",default="hold")
    state = fields.Selection([('pending', 'Pending'), ('hold', 'On Hold'), ('done', 'Done')], string="status",
                              default="hold",track_visibility='onchange')
    # order_rem_ids=fields.Many2many('final',string="Sub Activity")
    order_rem_idss=fields.One2many('reminder_view','order_ids')
    sub_ids=fields.One2many('subactivity','main_id')
    

    @api.onchange('activity_category_id')
    def _onchange_act(self):
        if self.activity_category_id:
            return {'domain': {'eactivity_types_ids': [('activity_category_id', '=', self.activity_category_id.id)]}}
        else:
            return {'domain': {'eactivity_types_ids': []}}

# TO DEPEND THE STATE ON STATUS
    @api.onchange('status')
    def _onchange_status(self):
        if (self.status=='pending'):
            self.state = 'pending'
        elif(self.status=='hold'):
            self.state = 'hold'
        elif(self.status=='done'):
            self.state= 'done'

 #*******************************#


#TO AUTOMATIC GENERATE THE LOG NOTES
    @api.multi
    def write(self, vals):
        for seession in self:
            changes = []
            if 'customer_name' in vals and seession.customer_name != vals['customer_name']:
                value = self.env['res.partner'].browse(vals['customer_name']).name
                print("@@@@@",value,"@@@@@@@@")
                oldmodel = seession.customer_name.name or _('None')
                print("oldmodel:", oldmodel)
                changes.append(("Customer Name: from '%s' to '%s'") % (oldmodel, value))


        if len(changes) > 0:
            print(self.message_post(body=", ".join(changes)))

        return super(Reminder, self).write(vals)
#*********************************************************#

#count the number of ids
    @api.multi
    def name_get(self):
        return [(alert.id, '%s %s' % ((""), '%d' % alert.id)) for alert in self]


    # @api.onchange('eactivity_types_ids')
    # def _onchange_state(self):
    #     subactivities = self.env['final'].search([('eactivity_types_ids', '=', self.eactivity_types_ids.id)])
    #     temp = [[4, sub.id] for sub in subactivities]
    #     self.order_rem_ids= temp

    # automatic fill up the subactivity field when activity type is selected for many2many

    #****************************************#
    @api.onchange('eactivity_types_ids')
    def _onchange_sub(self):
        activities=[]
        subactivities=self.env['subactivity'].search([('eactivity_types_ids', '=', self.eactivity_types_ids.id)])
        
        for activity in subactivities:
            activities.append((0,0,{
                'name':activity.name
                }))
            print(activities)
        self.order_rem_idss=activities
    # automatic fill up the subactivity field when activity type is selected for one2many

    # validation accroding to the date user selected
    @api.multi
    @api.constrains('last_date','rem_date','actual date','target_date')
    def reminder_date(self):
        for this in self:
            end =fields.Date.from_string(this.last_date)
            rem = fields.Date.from_string(this.rem_date)
            target= fields.Date.from_string(this.target_date)
            if end < rem:
                raise ValidationError("Reminder Date is not valid")
            elif end < target:
                raise ValidationError("Target Date is not valid")
        # this api create automatic action on the employee date

    @api.model
    def todays_reminder(self):
        # get tommorrow's date by adding days=1
        Activity = self.env['mail.activity']
        IrModel = self.env['ir.model']
        today_date = datetime.today()
        next_date = datetime.today()
        next_date += relativedelta(days=1)
        day_after_tommorrow = next_date + relativedelta(days=1)
        # Here we are searching all records where date is of tommorrow and less that day after tommorrow and we will create activity for all such records
        # here I want to remind instrutor before 1 day, so I will create activity of todo here

        today_records = self.search([('last_date', '=', today_date.strftime("%Y-%m-%d 00:00:00"))])
        next_records = self.search([('last_date', '>=', next_date.strftime("%Y-%m-%d 00:00:00")),('last_date', '<=', day_after_tommorrow.strftime("%Y-%m-%d 00:00:00"))])
        # print("********", tommorrow_records, "**********")
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)

        print("::::::::::", activity_type, "::::::::::")

        for record in today_records:
            # We will prepare data for activity, I am creating activity type of todo, you can check I fetched mail_activity_data_todo record using env.ref and use that as acitvity_type_id
            # note that: few activities are already created using xml data files in mail module
            print("record:", record)
            activity_data = {
                'res_id': record.id,
                'res_model_id': IrModel.search([('model', '=', 'reminder')]).id,
                'activity_type_id': activity_type.id,
                'summary': 'Reminder of mine',
                'user_id': record.user_id.id or self.env.uid,
                # You have to set user for whom you want to show activity in system tray
                'date_deadline': today_date.strftime("%Y-%m-%d"),
            }
            print("\n\nactivity_data ::: ", activity_data)
            Activity.create(activity_data)

        for record in next_records:
            # We will prepare data for activity, I am creating activity type of todo, you can check I fetched mail_activity_data_todo record using env.ref and use that as acitvity_type_id
            # note that: few activities are already created using xml data files in mail module
            print("record:", record)
            activity_datas = {
                'res_id': record.id,
                'res_model_id': IrModel.search([('model', '=', 'reminder')]).id,
                'activity_type_id': activity_type.id,
                'summary': 'Reminder of mine',
                'user_id': record.user_id.id or self.env.uid,
                # You have to set user for whom you want to show activity in system tray
                'date_deadline': next_date.strftime("%Y-%m-%d"),
            }
            print("\n\nactivity_data ::: ", activity_datas)
            Activity.create(activity_datas)



# this model show views of every subactivity combine with reminder
class reminderview(models.Model):
    _name='reminder_view'

    name=fields.Char(string='Sub activity',required=True)

    customer_name = fields.Many2one('res.partner', string="Customer Name", related='order_ids.customer_name',readonly=True)

    activity_category_id = fields.Many2one('activity.category', string='Activity Category',
                                  related='order_ids.activity_category_id', readonly=True, store=True)

    eactivity_types_ids = fields.Many2one('activity.type', string='Activity Type',
                                  related='order_ids.eactivity_types_ids', readonly=True, store=True)
    date = fields.Date(string='Sub Activity Target Date', related='product_ids.date', store=True)
    sub_activity_date = fields.Date(string='Sub Activity Actual Date', related='product_ids.date', store=True)
    order_ids = fields.Many2one('reminder',ondelete='cascade', required=True,string='Reminder ID')
    product_ids=fields.Many2one('subactivity','Sub Activity')
    #                            readonly=True, store=True)
    user_id = fields.Many2one('res.users', string='Sub Activity User',related='product_ids.user_id', store=True)
    status= fields.Selection([('pending','Pending'),('hold','On Hold'),('done','Done')])
    
    
class MainPartner(models.Model):
    _inherit = 'res.partner'

    activity_count = fields.Integer(compute='_compute_activity_count')

    # activity_id=fields.One2many('main','partner_id')

#this api is used to count the activity respective with customer
    @api.multi
    def _compute_activity_count(self):
        for partner in self:
            operator = 'child_of'
            partner.activity_count = self.env['reminder'].search_count([('customer_name', operator, partner.id)])

# Add Mutiple service in partner
class AddServices(models.Model):
    _inherit = 'res.partner'

    activity_tags = fields.Many2many('activity.category', 'tag_ids', string="Services")
   

