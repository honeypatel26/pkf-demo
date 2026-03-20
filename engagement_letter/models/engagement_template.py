# engagement_letter/models/engagement_template.py
from odoo import api, fields, models, _, Command


class EngagementLetterTemplate(models.Model):
    _name = "engagement.letter.template"
    _description = "Engagement Letter Template"
    _order = "name asc"

    name = fields.Char(required=True)
    description = fields.Html(string="Description")
    line_ids = fields.One2many(
        "engagement.letter.template.line",
        "template_id",
        string="Template Lines",
        copy=False,
    )


class EngagementLetterTemplateLine(models.Model):
    _name = "engagement.letter.template.line"
    _description = "Engagement Letter Template Line"
    _order = "sequence, id"

    template_id = fields.Many2one("engagement.letter.template", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    display_type = fields.Selection(
        [("line", "Line"), ("section", "Section"), ("note", "Note")],
        default="line",
        required=True,
    )
    
    name = fields.Char(string="Description")
    product_id = fields.Many2one("product.product", string="Product")
    product_uom_qty = fields.Float(string="Quantity", default=1.0)
    product_uom_id = fields.Many2one("uom.uom", string="UoM")
    
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    
    price_unit = fields.Float(string="Unit Price", default=0.0)
    discount = fields.Float(string="Discount %", default=0.0)
    
    price_subtotal = fields.Monetary(string="Subtotal", compute="_compute_amount", store=True)
    price_tax = fields.Monetary(string="Tax", compute="_compute_amount", store=True)
    price_total = fields.Monetary(string="Total",compute="_compute_amount",store=True)
    
    tax_id = fields.Many2many("account.tax", string="Taxes")

    @api.depends("product_uom_qty","price_unit","discount","tax_id")
    def _compute_amount(self):
        for line in self:
            qty = line.product_uom_qty or 0.0
            price = line.price_unit or 0.0

            discount_amount = price * (line.discount or 0.0) / 100.0
            effective_price = price - discount_amount

            subtotal = qty * effective_price

            if line.tax_id:
                taxes = line.tax_id.compute_all(
                    effective_price,
                    currency=line.currency_id,
                    quantity=qty,
                    product=line.product_id,
                    partner=False
                )
                line.price_subtotal = taxes["total_excluded"]
                line.price_tax = taxes["total_included"] - taxes["total_excluded"]
                line.price_total = taxes["total_included"]
            else:
                line.price_subtotal = subtotal
                line.price_tax = 0.0
                line.price_total = subtotal

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.name = rec.name or rec.product_id.display_name
                rec.product_uom_id = rec.product_uom_id or rec.product_id.uom_id
                rec.price_unit = rec.product_id.list_price
