# -*- coding: utf-8 -*-
#   Copyright (c) 2013 Camptocamp SA (http://www.camptocamp.com)
#   @author Vincent Renaville
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning


class SaleConditionText(models.Model):
    """Sale order Textual information"""

    _name = "sale.condition_text"
    _description = "sale conditions"

    name = fields.Char('Condition summary', required=True)
    type = fields.Selection([('header', 'Top condition'),
                             ('footer', 'Bottom condition')],
                            'type', required=True)
    text = fields.Html('Condition', translate=True, required=True)


class SaleOrder(models.Model):
    """Adds condition to SO"""

    _inherit = "sale.order"
    _description = 'Sale Order'

    text_condition1 = fields.Many2one('sale.condition_text', 'Header',
                                      domain=[('type', '=', 'header')])
    text_condition2 = fields.Many2one('sale.condition_text', 'Footer',
                                      domain=[('type', '=', 'footer')])
    note1 = fields.Html('Header')
    note2 = fields.Html('Footer')

    @api.onchange('text_condition1', 'partner_id')
    def set_header(self):
        if self.text_condition1 and not self.partner_id:
            raise Warning(_('No Customer Defined !'
                            '\n Before choosing condition text'
                            ' select a customer.'))
        ctx = dict(self._context)
        lang = self.partner_id.lang or 'en_US'
        self.text_condition1.with_context(ctx).write({'lang': lang})
        if self.text_condition1:
            self.note1 = self.text_condition1.text

    @api.onchange('text_condition2', 'partner_id')
    def set_footer(self):
        if self.text_condition2 and not self.partner_id:
            raise Warning(_('No Customer Defined !'
                            '\n Before choosing condition text'
                            ' select a customer.'))
        ctx = dict(self._context)
        lang = self.partner_id.lang or 'en_US'
        self.text_condition2.with_context(ctx).write({'lang': lang})
        if self.text_condition2:
            self.note2 = self.text_condition2.text

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        xml = 'sale_order_report_with_note.report_saleorder_qweb'
        return self.env['report'].get_action(self, xml)


class SaleOrderLine(models.Model):
    """ADD HTML note to sale order lines"""

    _inherit = "sale.order.line"

    formatted_note = fields.Html('Formatted Note')
