# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicketInh(models.Model):
    _inherit = 'helpdesk.ticket'

    date = fields.Date('Date')
    received_via = fields.Many2one('hr.employee')
    sale_agent = fields.Many2one('hr.employee', string="Sale Agent")
    contact = fields.Char('Contact')
    address = fields.Char('Address')
    product_id = fields.Many2one('product.product')
    warranty = fields.Selection([('in', 'In Warranty'),
                                       ('out', 'Out Warranty'),
                                       ('nr', 'NR')], 'Warranty')
    # brand = fields.Selection([('apollo', 'APPOLLO'), ('tona', 'TONA'),
    #                              ('forever', 'FOREVER GLASS'),('grohe', 'GROHE'),('remer', 'REMER'),('cerdomus', 'CERDOMUS'),('supergres', 'SUPERGRES'),('versace', 'VERSACE'),('mirage', 'MIRAGE'),
    #                           ('homeworks', 'HOMEWORKS'),('florim', 'FLORIM'),('elios', 'ELIOS'),('lafabrica', 'LAFABRICA'),('rondine', 'RONDINE'),('brennero', 'BRENNERO'),('marcopolo', 'MARCOPOLO'),
    #                           ('vescovi', 'VESCOVI'),('orans', 'ORANS'),('laminam', 'LAMINAM'),('komodor', 'KOMODOR'),('swriss', 'SWRISSKRONO'),('progress', 'PROGRESS PROFILES'),('other', 'OTHER'),
    #                           ('hunter', 'HUNTER FAN'),('westinghouse', 'WESTINGHOUSE'),('kerakoll', 'KERAKOLL')], 'Brand')

    brand = fields.Selection([('apollo', 'APPOLLO'),
                              ('tona', 'TONA'),
                              ('forever', 'FOREVER GLASS'), ('grohe', 'GROHE'), ('remer', 'REMER'),
                              ('cerdomus', 'CERDOMUS'), ('supergres', 'SUPERGRES'), ('versace', 'VERSACE'),
                              ('mirage', 'MIRAGE'),
                              ('homeworks', 'HOMEWORKS'), ('florim', 'FLORIM'), ('elios', 'ELIOS'),
                              ('lafabrica', 'LAFABRICA'), ('rondine', 'RONDINE'), ('brennero', 'BRENNERO'),
                              ('marcopolo', 'MARCOPOLO'),
                              ('vescovi', 'VESCOVI'), ('orans', 'ORANS'), ('laminam', 'LAMINAM'),
                              ('komodor', 'KOMODOR'), ('swriss', 'SWRISSKRONO'), ('progress', 'PROGRESS PROFILES'),
                              ('other', 'OTHER'),
                              ('hunter', 'HUNTER FAN'), ('westinghouse', 'WESTINGHOUSE'),
                              ('kerakoll', 'KERAKOLL'),
                              ('gardenia', 'Gardenia'),
                              ('gessi', 'Gessi'),
                              ('catalano', 'Catalano'),
                              ('glassia', 'Glassia'),
                              ('zen_design', 'Zen Design'),
                              ('genwec', 'Genwec'),
                              ('linisi', 'Linisi'),
                              ('colomdo', 'Colomdo'),
                              ('marsden', 'Marsden'),
                              ('antolini', 'Antolini'),
                              ('decor_marmi', 'Decor Marmi'),
                              ('bottega', 'Bottega'),
                              ('zucchetti', 'Zucchetti'),
                              ('godi', 'Godi'),
                              ('vibia', 'Vibia'),
                              ('barbossa', 'Barbossa'),
                              ('orignal_parquet', 'Orignal Parquet'),
                              ('geberit', 'Geberit'),
                              ('kmd_floor', 'Kmd Floor'),
                              ('ormosia', 'Ormosia'),
                              ('ebony', 'Ebony'),
                              ('merbau', 'Merbau'),
                              ('teak', 'Teak'),
                              ('micawa', 'Micawa'),
                              ], 'Brand')

    problem = fields.Char('Problem')
    serial_no = fields.Char('Serial No')
    amount = fields.Float('Service Changes')
    article_no = fields.Char('Article No', related='product_id.article_no')

    confirmation = fields.Selection([('resolved', 'Resolved'),
                                 ('unresolved', 'Unresolved')], 'Client Confirmation')
    seq_no = fields.Char('Helpdesk', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('seq_no', _('New')) == _('New'):
            vals['seq_no'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket.sequence') or _('New')
        result = super(HelpdeskTicketInh, self).create(vals)
        return result
