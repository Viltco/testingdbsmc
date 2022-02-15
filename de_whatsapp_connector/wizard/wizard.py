
from odoo import models, api, fields
import json
from odoo.exceptions import UserError, ValidationError, Warning
import base64
import requests
import re
from datetime import datetime


class WhatsappSendMessage(models.TransientModel):

    _name = 'whatsapp.message.wizard'

    contacts_to = fields.Many2many('res.partner', 'contacts_message_wizard', 'contact_id', 'partner_id',
                                   string='Selelct Recipients')
    # whatsapp_account = fields.Char(string='Whatsapp Account')
    whatsapp_account = fields.Many2one('whatsapp.settings', string='Whatsapp Account')
    message = fields.Text(string='Message')
    attatchments_whatsap = fields.Many2many(comodel_name="ir.attachment",
                                            relation="files_rel_wizard",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Add Files")
    message_sent_id = fields.Char(string='Message sent IDs Of Chat API')
    mobile_no = fields.Char('Mobile', related= 'contacts_to.mobile', readonly=True)

    record_id = fields.Integer('Record ID')

    many_sales_record_ids = fields.Many2many('sale.order', 'sales_ids_wizard', 'contact_id', 'partner_id',
                                   string='Selelct Recipients')

    model_name = fields.Char('Model Name')
    counter_wizard = 0

    def send_message(self):
        try:

            # print('xyz')

            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            # else:
            #     self.name = credetionals.id

            if not self.contacts_to:
                raise UserError('You Have Not Selected Any Recipient!')

            if not self.message and not self.attatchments_whatsap:
                raise UserError('Please Enter Message First! Or Attach Any File To Send!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for contact in self.contacts_to:

                # availableFiles = {'doc': 'document.doc',
                #                   'gif': 'gifka.gif',
                #                   'jpg': 'jpgfile.jpg',
                #                   'png': 'pngfile.png',
                #                   'pdf': 'presentation.pdf',
                #                   'mp4': 'video.mp4',
                #                   'mp3': 'mp3file.mp3'}
                # if format in availableFiles.keys():
                #     data = {
                #         'chatId': chatId,
                #         'body': f'https://domain.com/Python/{availableFiles[format]}',
                #         'filename': availableFiles[format],
                #         'caption': f'Get your file {availableFiles[format]}'
                #     } to do work

                if not contact.mobile:
                    raise UserError(f'"{contact.name}" Recipient does not contain Mobile Number!')

                if not contact.country_id.phone_code:
                    raise UserError(f'"{contact.name}" Recipient does not contain Country. Select Country frist!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')
                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    if not self.message:
                        self.message = ''
                        self.message += '\n \n--' + signature_str + '--'
                    else:
                        self.message += '\n \n--' + signature_str + '--'

                if len(contact.mobile) < 11 or len(contact.mobile) >= 13:
                    raise UserError(f'Recipient "{contact.name}" Might Have Wrong Phone Number!')

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                if len(phone) < 11:
                    raise UserError(f'"{contact}" Might Have Wrong Phone Number!')

                # responce = {'status_code': 0}
                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"

                responce_status_code = 0
                if self.message:
                    data = json.dumps({"phone": phone, "body": self.message})
                    responce = requests.post(url, data, headers=header)
                    responce_status_code = responce.status_code

                response_file_status_code = 0
                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                if self.attatchments_whatsap:
                    for file in self.attatchments_whatsap:
                        decode_data = file.datas.decode('utf-8')
                        docode_file = f"data:{file.mimetype};base64," + decode_data
                        data_file = {
                            "phone": phone,
                            'filename': file.name,
                            "body": docode_file
                        }
                        response_file = requests.request("POST", url_files, json=data_file, headers={})
                        response_file_status_code = response_file.status_code
                        # print('Ending')

                if responce_status_code == 200 or response_file_status_code == 200:
                    # self.message_sent_id = responce.json()['id'] if response_file_status_code == 200 else ''
                    if self.model_name == 'res.partner':
                        message = self.env['mail.message'].create({
                            'subject': 'Whatsapp Message',
                            'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                            'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                            'model': self.model_name,
                            'res_id': contact.id,
                            'no_auto_thread': True,
                            'add_sign': True,
                        })

                        channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                        if not channel_search:
                            self.env['mail.channel'].create({
                                # 'sl_slack_channel_id': channel_search.id,
                                'name': contact.name,
                                'alias_user_id': self.env.user.id,
                                'is_subscribed': True,
                                'is_member': True,
                                'channel_partner_ids': [[6, 0, [contact.id]]],
                                'channel_message_ids': [[4, message.id]],
                                # 'channel_message_ids': [[6, 0, [message.id]]]
                            })
                        else:
                            channel_search.write({
                                # 'sl_slack_channel_id': channel_search.id,
                                'name': contact.name,
                                'alias_user_id': self.env.user.id,
                                'is_subscribed': True,
                                'is_member': True,
                                'channel_partner_ids': [[6, 0, [contact.id]]],
                                'channel_message_ids': [[4, message.id]]
                                # 'channel_message_ids': [[6, 0, [message.id]]]
                            })
                        self.env.cr.commit()

                        partner = self.env['res.partner'].search([('id', '=', contact.id)])
                        contact.counter_wizard = partner.message_counter + 1
                        partner.write({
                            'message_counter': contact.counter_wizard,
                            'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'
                        })

                        logs = {
                            # 'sync_list_id': self.id,
                            'sync_date': datetime.now(),
                            'contact_name': contact.id,
                            'account_used': credetionals.id,
                            'message_sucess': 'Sucessful',
                            'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                            'signature_att': 'Yes' if signature_check else 'No',
                            'from_model': 'Contacts'
                        }
                        self.env['detail.logs'].create(logs)
                    elif self.model_name == 'sale.order':
                        if self.record_id:
                            message = self.env['mail.message'].create({
                                'subject': 'Whatsapp Message',
                                'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                                'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                                'model': self.model_name,
                                'res_id': self.record_id,
                                'no_auto_thread': True,
                                'add_sign': True,
                            })
                            # self.counter_wizard += 1
                            partner = self.env['sale.order'].search([('id', '=', self.record_id)])
                            partner.write({
                                'message_counter_sales': partner.message_counter_sales + 1,
                            })

                            channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                            if not channel_search:
                                self.env['mail.channel'].create({
                                    # 'sl_slack_channel_id': channel_search.id,
                                    'name': contact.name,
                                    'alias_user_id': self.env.user.id,
                                    'is_subscribed': True,
                                    'is_member': True,
                                    'channel_partner_ids': [[6, 0, [contact.id]]],
                                    'channel_message_ids': [[4, message.id]],
                                    # 'channel_message_ids': [[6, 0, [message.id]]]
                                })
                            else:
                                channel_search.write({
                                    # 'sl_slack_channel_id': channel_search.id,
                                    'name': contact.name,
                                    'alias_user_id': self.env.user.id,
                                    'is_subscribed': True,
                                    'is_member': True,
                                    'channel_partner_ids': [[6, 0, [contact.id]]],
                                    'channel_message_ids': [[4, message.id]]
                                    # 'channel_message_ids': [[6, 0, [message.id]]]
                                })
                            self.env.cr.commit()

                            logs = {
                                # 'sync_list_id': self.id,
                                'sync_date': datetime.now(),
                                'contact_name': contact.id,
                                'account_used': credetionals.id,
                                'message_sucess': 'Sucessful',
                                'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                                'signature_att': 'Yes' if signature_check else 'No',
                                'from_model': 'Sales'
                            }
                            self.env['detail.logs'].create(logs)
                        p = self.env['res.partner'].search([('id', '=', contact.id)])
                        contact.counter_wizard = p.message_counter + 1
                        p.write({
                            'message_counter': contact.counter_wizard,
                            'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'
                        })

                        if not self.record_id:
                            sale_order_id = self.env['sale.order'].search([('partner_id', '=', contact.id)]).ids
                            if sale_order_id:
                                for id_s in sale_order_id:
                                    message = self.env['mail.message'].create({
                                        'subject': 'Whatsapp Message',
                                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                                        'model': self.model_name,
                                        'res_id': id_s,
                                        'no_auto_thread': True,
                                        'add_sign': True,
                                    })
                                    # self.counter_wizard += 1
                                    partner = self.env['sale.order'].search([('id', '=', id_s)])
                                    partner.write({
                                        'message_counter_sales': partner.message_counter_sales + 1,
                                    })

                                    logs = {
                                        # 'sync_list_id': self.id,
                                        'sync_date': datetime.now(),
                                        'contact_name': contact.id,
                                        'account_used': credetionals.id,
                                        'message_sucess': 'Sucessful',
                                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                                        'signature_att': 'Yes' if signature_check else 'No',
                                        'from_model': 'Sales'
                                    }
                                    self.env['detail.logs'].create(logs)
                            p = self.env['res.partner'].search([('id', '=', contact.id)])
                            contact.counter_wizard = p.message_counter + 1
                            p.write({
                                'message_counter': contact.counter_wizard,
                                'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'
                            })

                            channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                            if not channel_search:
                                self.env['mail.channel'].create({
                                    # 'sl_slack_channel_id': channel_search.id,
                                    'name': contact.name,
                                    'alias_user_id': self.env.user.id,
                                    'is_subscribed': True,
                                    'is_member': True,
                                    'channel_partner_ids': [[6, 0, [contact.id]]],
                                    'channel_message_ids': [[4, message.id]],
                                    # 'channel_message_ids': [[6, 0, [message.id]]]
                                })
                            else:
                                channel_search.write({
                                    # 'sl_slack_channel_id': channel_search.id,
                                    'name': contact.name,
                                    'alias_user_id': self.env.user.id,
                                    'is_subscribed': True,
                                    'is_member': True,
                                    'channel_partner_ids': [[6, 0, [contact.id]]],
                                    'channel_message_ids': [[4, message.id]]
                                    # 'channel_message_ids': [[6, 0, [message.id]]]
                                })
                            self.env.cr.commit()

                    elif self.model_name == 'account.move':
                        # account_id = self.env['sale.order'].search([('partner_id', '=', contact.id)]).ids
                        account_id = self.env['account.move'].search([('partner_id', '=', contact.id)]).ids
                        if account_id:
                            for a_id in account_id:
                                message = self.env['mail.message'].create({
                                    'subject': 'Whatsapp Message',
                                    'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                                    'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                                    'model': self.model_name,
                                    'res_id': a_id,
                                    'no_auto_thread': True,
                                    'add_sign': True,
                                })

                                channel_search = self.env['mail.channel'].search(
                                    [('channel_partner_ids', '=', contact.id)])
                                if not channel_search:
                                    self.env['mail.channel'].create({
                                        # 'sl_slack_channel_id': channel_search.id,
                                        'name': contact.name,
                                        'alias_user_id': self.env.user.id,
                                        'is_subscribed': True,
                                        'is_member': True,
                                        'channel_partner_ids': [[6, 0, [contact.id]]],
                                        'channel_message_ids': [[4, message.id]],
                                        # 'channel_message_ids': [[6, 0, [message.id]]]
                                    })
                                else:
                                    channel_search.write({
                                        # 'sl_slack_channel_id': channel_search.id,
                                        'name': contact.name,
                                        'alias_user_id': self.env.user.id,
                                        'is_subscribed': True,
                                        'is_member': True,
                                        'channel_partner_ids': [[6, 0, [contact.id]]],
                                        'channel_message_ids': [[4, message.id]]
                                        # 'channel_message_ids': [[6, 0, [message.id]]]
                                    })
                                self.env.cr.commit()

                                logs = {
                                    # 'sync_list_id': self.id,
                                    'sync_date': datetime.now(),
                                    'contact_name': contact.id,
                                    'account_used': credetionals.id,
                                    'message_sucess': 'Sucessful',
                                    'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                                    'signature_att': 'Yes' if signature_check else 'No',
                                    'from_model': 'Invoicing'
                                }
                                self.env['detail.logs'].create(logs)
                        # self.counter_wizard += 1
                        partner = self.env['account.move'].search([('id', '=', self.record_id)])
                        partner.write({
                            'message_counter_invoice': partner.message_counter_invoice + 1,
                        })
                        p = self.env['res.partner'].search([('id', '=', contact.id)])
                        contact.counter_wizard = p.message_counter + 1
                        p.write({
                            'message_counter': contact.counter_wizard,
                            'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'
                        })
                    self.env.cr.commit()
                    continue

            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:
            # logs = {
            #     # 'sync_list_id': self.id,
            #     'sync_date': datetime.now(),
            #     'contact_name': contact.id,
            #     'account_used': credetionals.id,
            #     'message_sucess': 'Sucessful',
            #     'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
            #     'signature_att': 'Yes' if signature_check else 'No',
            #     'from_model': 'Contacts' if self.model_name == 'res.partner' else 'Error',
            # }
            # self.env['detail.logs'].create(logs)
            # self.env.cr.commit()

            raise ValidationError(e)

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }


class WhatsappSendMessageEmploye(models.TransientModel):

    _name = 'whatsapp.message.wizard.employee'

    contacts_to = fields.Many2many('hr.employee', 'employee_message_wizard', 'contact_id', 'partner_id',
                                   string='Selelct Recipients')
    whatsapp_account = fields.Many2one('whatsapp.settings', string='Whatsapp Account')
    message = fields.Text(string='Message')
    attatchments_whatsap = fields.Many2many(comodel_name="ir.attachment",
                                            relation="files_rel_wizard_employee",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Add Files")
    message_sent_id = fields.Char(string='Message sent IDs Of Chat API')
    mobile_no = fields.Char('Mobile', related= 'contacts_to.mobile_phone', readonly=True)

    record_id = fields.Integer('Record ID')
    model_name = fields.Char('Model Name')
    # counter_wizard = 0

    def send_message(self):
        # print('xyz')
        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        if not credetionals:
            raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
        # else:
        #     self.name = credetionals.id

        if not self.contacts_to:
            raise UserError('You Have Not Selected Any Recipient!')

        if not self.message and not self.attatchments_whatsap:
            raise UserError('Please Enter Message First! Or Attach Any File To Send!')

        instance = credetionals.whatsapp_instance_id
        token = credetionals.whatsapp_token

        header = {
            'Content-type': 'application/json',
        }

        for contact in self.contacts_to:

            # availableFiles = {'doc': 'document.doc',
            #                   'gif': 'gifka.gif',
            #                   'jpg': 'jpgfile.jpg',
            #                   'png': 'pngfile.png',
            #                   'pdf': 'presentation.pdf',
            #                   'mp4': 'video.mp4',
            #                   'mp3': 'mp3file.mp3'}
            # if format in availableFiles.keys():
            #     data = {
            #         'chatId': chatId,
            #         'body': f'https://domain.com/Python/{availableFiles[format]}',
            #         'filename': availableFiles[format],
            #         'caption': f'Get your file {availableFiles[format]}'
            #     } to do work

            if not contact.mobile_phone:
                raise UserError(f'Recipient "{contact.name}" does not contain Mobile Number!')

            if not contact.country_id.phone_code:
                raise UserError(f'Recipient "{contact.name}" does not contain Country. Select Country frist!')


            signature_check = self.env['ir.config_parameter'].sudo().get_param(
                'de_whatsapp_connector.whatsapp_signature')
            if signature_check:
                signature_str = ''
                signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                for signature in signature_list:
                    if signature:
                        signature_str += signature

                if not self.message:
                    self.message = ''
                    self.message += '\n \n' + signature_str
                else:
                    self.message += '\n \n' + signature_str

            if len(contact.mobile_phone) < 11 or len(contact.mobile_phone) >= 13:
                raise UserError(f'Recipient "{contact.name}" Might Have Wrong Phone Number!')

            phone = str(contact.country_id.phone_code) + contact.mobile_phone[-10:]

            responce_status_code = 0
            url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"
            if self.message:
                data = json.dumps({"phone": phone, "body": self.message})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

            response_file_status_code = 0
            url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
            if self.attatchments_whatsap:
                for file in self.attatchments_whatsap:
                    decode_data = file.datas.decode('utf-8')
                    docode_file = f"data:{file.mimetype};base64," + decode_data
                    data_file = {
                        "phone": phone,
                        'filename': file.name,
                        "body": docode_file
                    }
                    response_file = requests.request("POST", url_files, json=data_file, headers={})
                    response_file_status_code = response_file.status_code
                    # print('Ending')

            if responce_status_code == 200 or response_file_status_code == 200:
                # self.message_sent_id = json_responce['id']

                if self.model_name == 'hr.employee':
                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        'model': self.model_name,
                        'res_id': contact.id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })

                    # channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                    # if not channel_search:
                    #     self.env['mail.channel'].create({
                    #         # 'sl_slack_channel_id': channel_search.id,
                    #         'name': contact.name,
                    #         'alias_user_id': self.env.user.id,
                    #         'is_subscribed': True,
                    #         'is_member': True,
                    #         'channel_partner_ids': [[6, 0, contact.id]],
                    #         'channel_message_ids': [[4, message.id]],
                    #         # 'channel_message_ids': [[6, 0, [message.id]]]
                    #     })
                    # else:
                    #     channel_search.write({
                    #         # 'sl_slack_channel_id': channel_search.id,
                    #         'name': contact.name,
                    #         'alias_user_id': self.env.user.id,
                    #         'is_subscribed': True,
                    #         'is_member': True,
                    #         'channel_partner_ids': [[6, 0, [contact.id]]],
                    #         'channel_message_ids': [[4, message.id]]
                    #         # 'channel_message_ids': [[6, 0, [message.id]]]
                    #     })
                    # self.env.cr.commit()

                    partner = self.env['hr.employee'].search([('id', '=', contact.id)])
                    contact.counter_wizard = partner.message_counter_employee + 1
                    partner.write({
                        'message_counter_employee': contact.counter_wizard,
                        'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'

                    })

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'employee_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Employee'
                    }
                    self.env['detail.logs'].create(logs)
                    self.env.cr.commit()

                self.env.cr.commit()
                continue
        else:
            context = dict(self._context)
            context['message'] = 'Sucessful!'
            return self.message_wizard(context)

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }


class WhatsappSendMessagepayments(models.TransientModel):

    _name = 'whatsapp.message.wizard.payments'

    contacts_to = fields.Many2many('res.partner', 'payment_message_wizard', 'contact_id', 'partner_id',
                                   string='Selelct Recipients')
    whatsapp_account = fields.Many2one('whatsapp.settings', string='Whatsapp Account')
    message = fields.Text(string='Message')
    attatchments_whatsap = fields.Many2many(comodel_name="ir.attachment",
                                            relation="files_rel_wizard_payment",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Add Files")
    message_sent_id = fields.Char(string='Message sent IDs Of Chat API')
    mobile_no = fields.Char('Mobile', related= 'contacts_to.mobile', readonly=True)

    record_id = fields.Integer('Record ID')
    model_name = fields.Char('Model Name')
    counter_wizard = 0

    def send_message(self):
        # print('xyz')
        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        if not credetionals:
            raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
        # else:
        #     self.name = credetionals.id

        if not self.contacts_to:
            raise UserError('You Have Not Selected Any Recipient!')

        if not self.message and not self.attatchments_whatsap:
            raise UserError('Please Enter Message First! Or Attach Any File To Send!')

        instance = credetionals.whatsapp_instance_id
        token = credetionals.whatsapp_token

        header = {
            'Content-type': 'application/json',
        }

        for contact in self.contacts_to:

            # availableFiles = {'doc': 'document.doc',
            #                   'gif': 'gifka.gif',
            #                   'jpg': 'jpgfile.jpg',
            #                   'png': 'pngfile.png',
            #                   'pdf': 'presentation.pdf',
            #                   'mp4': 'video.mp4',
            #                   'mp3': 'mp3file.mp3'}
            # if format in availableFiles.keys():
            #     data = {
            #         'chatId': chatId,
            #         'body': f'https://domain.com/Python/{availableFiles[format]}',
            #         'filename': availableFiles[format],
            #         'caption': f'Get your file {availableFiles[format]}'
            #     } to do work

            if not contact.mobile:
                raise UserError(f'Recipient "{contact.name}" does not contain Mobile Number!')

            if not contact.country_id.phone_code:
                raise UserError(f'Recipient "{contact.name}" does not contain Country. Select Country frist!')

            signature_check = self.env['ir.config_parameter'].sudo().get_param(
                'de_whatsapp_connector.whatsapp_signature')
            if signature_check:
                signature_str = ''
                signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                for signature in signature_list:
                    if signature:
                        signature_str += signature

                if not self.message:
                    self.message = ''
                    self.message += '\n \n--' + signature_str + '--'
                else:
                    self.message += '\n \n--' + signature_str + '--'

            if len(contact.mobile) < 11 or len(contact.mobile) >= 13:
                raise UserError(f'Recipient "{contact.name}" Might Have Wrong Phone Number!')

            phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

            responce_status_code = 0
            url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"
            if self.message:
                data = json.dumps({"phone": phone, "body": self.message})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

            response_file_status_code = 0
            url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
            if self.attatchments_whatsap:
                for file in self.attatchments_whatsap:
                    decode_data = file.datas.decode('utf-8')
                    docode_file = f"data:{file.mimetype};base64," + decode_data
                    data_file = {
                        "phone": phone,
                        'filename': file.name,
                        "body": docode_file
                    }
                    response_file = requests.request("POST", url_files, json=data_file, headers={})
                    response_file_status_code = response_file.status_code
                    # print('Ending')

            if responce_status_code == 200 or response_file_status_code == 200:
                # self.message_sent_id = json_responce['id']

                if self.model_name == 'account.payment':
                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        'model': self.model_name,
                        'res_id': self.record_id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })

                    channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                    if not channel_search:
                        self.env['mail.channel'].create({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]],
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    else:
                        channel_search.write({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]]
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    self.env.cr.commit()

                    p = self.env['account.payment'].search([('id', '=', self.record_id)])
                    p.write({
                        'msg_count_pay': p.msg_count_pay + 1,
                    })

                    partner = self.env['res.partner'].search([('id', '=', contact.id)])
                    contact.counter_wizard = partner.message_counter + 1
                    partner.write({
                        'message_counter': contact.counter_wizard,
                        'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'

                    })

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Account Payments'
                    }
                    self.env['detail.logs'].create(logs)
                    self.env.cr.commit()

                elif self.model_name == 'purchase.order':
                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        'model': self.model_name,
                        'res_id': self.record_id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })

                    channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                    if not channel_search:
                        self.env['mail.channel'].create({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]],
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    else:
                        channel_search.write({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]]
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    self.env.cr.commit()

                    p = self.env['purchase.order'].search([('id', '=', self.record_id)])
                    p.write({
                        'msg_count_pur': p.msg_count_pur + 1,
                    })

                    partner = self.env['res.partner'].search([('id', '=', contact.id)])
                    contact.counter_wizard = partner.message_counter + 1
                    partner.write({
                        'message_counter': contact.counter_wizard,
                        'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'

                    })

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Purchase'
                    }
                    self.env['detail.logs'].create(logs)
                    self.env.cr.commit()

                self.env.cr.commit()
                continue
        else:
            context = dict(self._context)
            context['message'] = 'Sucessful!'
            return self.message_wizard(context)

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }


class WhatsappSendMessagestock(models.TransientModel):

    _name = 'whatsapp.message.wizard.stock'

    contacts_to = fields.Many2many('res.partner', 'stock_message_wizard', 'contact_id', 'partner_id',
                                   string='Selelct Recipients')
    whatsapp_account = fields.Many2one('whatsapp.settings', string='Whatsapp Account')
    message = fields.Text(string='Message')
    attatchments_whatsap = fields.Many2many(comodel_name="ir.attachment",
                                            relation="files_rel_wizard_stock",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Add Files")
    message_sent_id = fields.Char(string='Message sent IDs Of Chat API')
    mobile_no = fields.Char('Mobile', related= 'contacts_to.mobile', readonly=True)

    record_id = fields.Integer('Record ID')
    model_name = fields.Char('Model Name')
    counter_wizard = 0

    def send_message(self):
        # print('xyz')
        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        if not credetionals:
            raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
        # else:
        #     self.name = credetionals.id

        if not self.contacts_to:
            raise UserError('You Have Not Selected Any Recipient!')

        if not self.message and not self.attatchments_whatsap:
            raise UserError('Please Enter Message First! Or Attach Any File To Send!')

        instance = credetionals.whatsapp_instance_id
        token = credetionals.whatsapp_token

        header = {
            'Content-type': 'application/json',
        }

        for contact in self.contacts_to:

            # availableFiles = {'doc': 'document.doc',
            #                   'gif': 'gifka.gif',
            #                   'jpg': 'jpgfile.jpg',
            #                   'png': 'pngfile.png',
            #                   'pdf': 'presentation.pdf',
            #                   'mp4': 'video.mp4',
            #                   'mp3': 'mp3file.mp3'}
            # if format in availableFiles.keys():
            #     data = {
            #         'chatId': chatId,
            #         'body': f'https://domain.com/Python/{availableFiles[format]}',
            #         'filename': availableFiles[format],
            #         'caption': f'Get your file {availableFiles[format]}'
            #     } to do work

            if not contact.mobile:
                raise UserError(f'Recipient "{contact.name}" does not contain Mobile Number!')

            if not contact.country_id.phone_code:
                raise UserError(f'Recipient "{contact.name}" does not contain Country. Select Country frist!')

            signature_check = self.env['ir.config_parameter'].sudo().get_param(
                'de_whatsapp_connector.whatsapp_signature')
            if signature_check:
                signature_str = ''
                signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                for signature in signature_list:
                    if signature:
                        signature_str += signature

                if not self.message:
                    self.message = ''
                    self.message += '\n \n--' + signature_str + '--'
                else:
                    self.message += '\n \n--' + signature_str + '--'

            if len(contact.mobile) < 11 or len(contact.mobile) >= 13:
                raise UserError(f'Recipient "{contact.name}" Might Have Wrong Phone Number!')

            phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

            responce_status_code = 0
            url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"
            if self.message:
                data = json.dumps({"phone": phone, "body": self.message})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

            response_file_status_code = 0
            url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
            if self.attatchments_whatsap:
                for file in self.attatchments_whatsap:
                    decode_data = file.datas.decode('utf-8')
                    docode_file = f"data:{file.mimetype};base64," + decode_data
                    data_file = {
                        "phone": phone,
                        'filename': file.name,
                        "body": docode_file
                    }
                    response_file = requests.request("POST", url_files, json=data_file, headers={})
                    response_file_status_code = response_file.status_code
                    # print('Ending')

            if responce_status_code == 200 or response_file_status_code == 200:
                # self.message_sent_id = json_responce['id']

                if self.model_name == 'stock.picking':
                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        'model': self.model_name,
                        'res_id': self.record_id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })

                    channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                    if not channel_search:
                        self.env['mail.channel'].create({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]],
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    else:
                        channel_search.write({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]]
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    self.env.cr.commit()

                    p = self.env['stock.picking'].search([('id', '=', self.record_id)])
                    p.write({
                        'msg_count_pay': p.msg_count_pay + 1,
                    })

                    partner = self.env['res.partner'].search([('id', '=', contact.id)])
                    contact.counter_wizard = partner.message_counter + 1
                    partner.write({
                        'message_counter': contact.counter_wizard,
                        'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'

                    })

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Stock Picking'
                    }
                    self.env['detail.logs'].create(logs)
                    self.env.cr.commit()

                elif self.model_name == 'purchase.order':
                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        'model': self.model_name,
                        'res_id': self.record_id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })

                    channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                    if not channel_search:
                        self.env['mail.channel'].create({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]],
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    else:
                        channel_search.write({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]]
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    self.env.cr.commit()

                    p = self.env['purchase.order'].search([('id', '=', self.record_id)])
                    p.write({
                        'msg_count_pur': p.msg_count_pur + 1,
                    })

                    partner = self.env['res.partner'].search([('id', '=', contact.id)])
                    contact.counter_wizard = partner.message_counter + 1
                    partner.write({
                        'message_counter': contact.counter_wizard,
                        'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'

                    })

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Stock Picking'
                    }
                    self.env['detail.logs'].create(logs)
                    self.env.cr.commit()

                self.env.cr.commit()
                continue
        else:
            context = dict(self._context)
            context['message'] = 'Sucessful!'
            return self.message_wizard(context)

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }