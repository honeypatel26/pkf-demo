from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
import base64


class EngagementLetter(models.Model):
    _name = "engagement.letter"
    _description = "Engagement Letter"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, default=lambda self: _("New"),
                       tracking=True)

    state = fields.Selection(
        [
            ("draft", "New"),
            ("review", "Ready for Review"),
            ("approved", "Approved by Partner"),
            ("sent", "Sent to Client"),
        ],
        default="draft",
        tracking=True,
    )

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)
    responsible_partner_id = fields.Many2one("res.users", string="Responsible Partner", required=True, tracking=True)
    owner_id = fields.Many2one("res.users", string="Owner", required=True, tracking=True)

    sign_template_id = fields.Many2one("sign.template", string="Signed Template", copy=False)
    sign_request_count = fields.Integer(compute="_compute_sign_request_count")

    sale_order_ids = fields.One2many("sale.order", "engagement_letter_id", string="Sale Orders", copy=False)
    sale_order_count = fields.Integer(compute="_compute_sale_order_count")

    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    block_ids = fields.One2many(
        "engagement.letter.block",
        "letter_id",
        string="Selected Templates",
        copy=False,
    )

    @api.depends("sign_template_id.sign_request_ids")
    def _compute_sign_request_count(self):
        for rec in self:
            rec.sign_request_count = len(rec.sign_template_id.sign_request_ids) if rec.sign_template_id else 0

    @api.depends("sale_order_ids")
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("engagement.letter") or _("New")
        return super().create(vals_list)

    # ----------------------------
    # PREVIEW PDF
    # ----------------------------
    def action_preview_pdf(self):
        self.ensure_one()
        return self.env.ref("engagement_letter.action_report_engagement_letter").report_action(self)

    # ----------------------------
    # SEND FLOW
    # ----------------------------
    def action_send_to_partner(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("You can send to partner only from Draft."))
            if not rec.responsible_partner_id:
                raise UserError(_("Responsible Partner is required."))
            # логика: партнер НЕ должен нажимать send_to_partner сам себе
            if self.env.user == rec.responsible_partner_id:
                raise UserError(_("Responsible Partner cannot send to himself."))

            rec.state = "review"
            rec.message_post(body=_("Sent to Responsible Partner for review."))
            
            # Send Email
            template = self.env.ref("engagement_letter.email_template_engagement_letter_review", raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)

    def action_partner_approve(self):
        for rec in self:
            if rec.state != "review":
                raise UserError(_("You can approve only in Review."))
            if self.env.user != rec.responsible_partner_id:
                raise UserError(_("Only the Responsible Partner can approve."))

            rec.state = "approved"
            rec.message_post(body=_("Approved by Responsible Partner: %s") % rec.responsible_partner_id.name)

            # Send Email to Creator
            if rec.create_uid:
                template = self.env.ref("engagement_letter.email_template_engagement_letter_approved", raise_if_not_found=False)
                if template:
                    template.send_mail(
                        rec.id, 
                        force_send=True, 
                        email_values={'recipient_ids': [(4, rec.create_uid.id)]}
                    )

    def _render_pdf_attachment(self):
        self.ensure_one()
        report_xmlid = "engagement_letter.action_report_engagement_letter"
        report_action = self.env.ref(report_xmlid)
        pdf_bytes, _ = report_action._render_qweb_pdf(report_xmlid, res_ids=[self.id])

        attach = self.env["ir.attachment"].create(
            {
                "name": f"Engagement Letter - {self.name or self.display_name}.pdf",
                "type": "binary",
                "datas": base64.b64encode(pdf_bytes),
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/pdf",
            }
        )
        return attach

    def action_send_for_sign(self):
        self.ensure_one()
        if self.state != "approved":
            raise UserError(_("You can start signature process only after partner approval."))

        # 1. Render PDF Attachment
        attachment = self._render_pdf_attachment()

        # 2. Create Sign Template
        # parsing the PDF to create sign items (documents)
        # We use the helper method provided by sign module to handle attachment -> template conversion
        tpl_id, tpl_name = self.env["sign.template"].create_sign_template_from_ir_attachment_data(
            attachment_id=attachment.id
        )
        sign_template = self.env["sign.template"].browse(tpl_id)

        # Helper creates it as inactive by default, we might want it active?
        # Let's activate it just in case
        sign_template.active = True

        # Save reference
        self.sign_template_id = sign_template.id

        # 3. Redirect to the Sign Template to add fields (Signature, Date, etc.)
        # Use the sign module's method to open the editor/preview
        return sign_template.go_to_custom_template()

    def action_view_sign_requests(self):
        self.ensure_one()
        if not self.sign_template_id:
            return
        return {
            "name": _("Sign Requests"),
            "type": "ir.actions.act_window",
            "res_model": "sign.request",
            "view_mode": "list,form",
            "domain": [("template_id", "=", self.sign_template_id.id)],
            "context": {"create": False},
        }

    # ----------------------------
    # LIST VIEW ACTIONS
    # ----------------------------
    latest_sign_request_id = fields.Many2one(
        "sign.request", 
        compute="_compute_latest_sign_request", 
        string="Latest Sign Request"
    )
    sign_request_state = fields.Selection(
        [
            ("shared", "Shared"),
            ("sent", "To Sign"),
            ("signed", "Signed"),
            ("canceled", "Cancelled"),
            ("expired", "Expired"),
        ],
        compute="_compute_sign_request_state",
        string="Sign Request State"
    )

    @api.depends("sign_template_id.sign_request_ids.state")
    def _compute_sign_request_state(self):
        for rec in self:
            rec.sign_request_state = rec.latest_sign_request_id.state

    @api.depends("sign_template_id.sign_request_ids")
    def _compute_latest_sign_request(self):
        for rec in self:
            # We take the most recent request created for this template
            # Since engagement letter creates a new template for each letter, 
            # this template's requests are specific to this letter.
            reqs = rec.sign_template_id.sign_request_ids
            rec.latest_sign_request_id = reqs.sorted("create_date", reverse=True)[:1]

    def action_download_signed_document(self):
        self.ensure_one()
        if self.latest_sign_request_id:
            return self.latest_sign_request_id.get_sign_request_documents()

    def action_resend_sign_request(self):
        self.ensure_one()
        if self.latest_sign_request_id:
            # This method sends signature accesses for 'sent' items
            return self.latest_sign_request_id.send_signature_accesses()

    def action_create_sale_order(self):
        self.ensure_one()
        if self.state != "approved":
            raise UserError(_("You can create Sale Order only after partner approval."))

        # Prepare Order Lines
        order_line_vals = []
        for block in self.block_ids:
            # Add Section
            order_line_vals.append(
                Command.create({
                    "display_type": "line_section",
                    "name": block.title,
                })
            )
            # Add Lines
            for line in block.line_ids:
                if line.display_type == "line" and line.product_id:
                    order_line_vals.append(
                        Command.create({
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.product_uom_qty,
                            "product_uom_id": line.product_uom_id.id,
                            "price_unit": line.price_unit,
                            "discount": line.discount,
                            "tax_ids": [Command.set(line.tax_id.ids)],
                            "name": line.name or line.product_id.name,
                        })
                    )
                elif line.display_type in ("note", "section"):
                    order_line_vals.append(
                        Command.create({
                            "display_type": "line_" + line.display_type,
                            "name": line.name,
                        })
                    )

        # Create Sale Order
        vals = {
            "partner_id": self.partner_id.id,
            "user_id": self.owner_id.id,
            "company_id": self.company_id.id,
            "engagement_letter_id": self.id,
            "origin": self.name,
            "order_line": order_line_vals,
        }

        so = self.env["sale.order"].create(vals)

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": so.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            "name": _("Sale Orders"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "domain": [("engagement_letter_id", "=", self.id)],
            "view_mode": "list,form",
            "context": {"default_engagement_letter_id": self.id},
        }

    def action_mark_sent_to_client(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("You can mark as sent only after partner approval."))
            if self.env.user == rec.responsible_partner_id:
                raise UserError(_("Responsible Partner should not mark sent in this flow."))

            rec.state = "sent"
            rec.message_post(body=_("Marked as sent to client (manual)."))


class EngagementLetterBlock(models.Model):
    _name = "engagement.letter.block"
    _description = "Engagement Letter Block (Template Snapshot)"
    _order = "sequence, id"

    letter_id = fields.Many2one("engagement.letter", ondelete="cascade")
    sequence = fields.Integer(default=10)

    template_id = fields.Many2one(
        "engagement.letter.template",
        string="Template",
        required=True,
    )

    title = fields.Char(string="Title")
    description = fields.Html(string="Text")

    line_ids = fields.One2many(
        "engagement.letter.block.line",
        "block_id",
        string="Lines",
        copy=True,
    )

    @api.onchange("template_id")
    def _onchange_template_id_snapshot(self):
        for rec in self:
            if rec.template_id:
                rec._snapshot_from_template_in_memory(rec.template_id)

    def _snapshot_from_template_in_memory(self, tpl):
        self.ensure_one()
        self.title = tpl.name
        self.description = tpl.description

        cmds = [Command.clear()]
        for tl in tpl.line_ids.sorted(key=lambda x: (x.sequence, x.id)):
            cmds.append(
                Command.create(
                    {
                        "sequence": tl.sequence,
                        "display_type": tl.display_type,
                        "name": tl.name,
                        "product_id": tl.product_id.id,
                        "product_uom_qty": tl.product_uom_qty,
                        "product_uom_id": tl.product_uom_id.id if tl.product_uom_id else False,
                        "price_unit": tl.price_unit,
                        "discount": tl.discount,
                        "tax_id": [(6, 0, tl.tax_id.ids)],
                    }
                )
            )
        self.line_ids = cmds

    def action_update_original_template(self):
        self.ensure_one()
        if not self.template_id:
            raise UserError(_("No template linked to this block."))

        tpl = self.template_id

        # Prepare new lines list using Commands
        new_lines_cmds = [Command.clear()]
        for bl in self.line_ids.sorted(key=lambda x: (x.sequence, x.id)):
            new_lines_cmds.append(
                Command.create({
                    "sequence": bl.sequence,
                    "display_type": bl.display_type,
                    "name": bl.name,
                    "product_id": bl.product_id.id,
                    "product_uom_qty": bl.product_uom_qty,
                    "product_uom_id": bl.product_uom_id.id if bl.product_uom_id else False,
                    "price_unit": bl.price_unit,
                    "discount": bl.discount,
                    "tax_id": [Command.set(bl.tax_id.ids)],
                })
            )

        # Update Template
        tpl.write({
            "name": self.title,
            "description": self.description,
            "line_ids": new_lines_cmds,
        })

        # Iterate over letters in memory might be tricky, so we just raise a notification
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Original template '%s' has been updated.") % tpl.name,
                "sticky": False,
                "type": "success",
            }
        }


class EngagementLetterBlockLine(models.Model):
    _name = "engagement.letter.block.line"
    _description = "Engagement Letter Block Line (Snapshot Line)"
    _order = "sequence, id"

    block_id = fields.Many2one("engagement.letter.block", required=True, ondelete="cascade")
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
    price_unit = fields.Float(string="Unit Price", default=0.0)
    discount = fields.Float(string="Discount %", default=0.0)
    tax_id = fields.Many2many("account.tax", string="Taxes")

    currency_id = fields.Many2one(related="block_id.letter_id.currency_id", store=True, readonly=True)

    price_subtotal = fields.Monetary(string="Subtotal", currency_field="currency_id", compute="_compute_amounts",
                                     store=True)
    price_total = fields.Monetary(string="Total", currency_field="currency_id", compute="_compute_amounts", store=True)

    @api.depends("display_type", "product_uom_qty", "price_unit", "discount", "tax_id")
    def _compute_amounts(self):
        for line in self:
            if line.display_type != "line":
                line.price_subtotal = 0.0
                line.price_total = 0.0
                continue

            # Apply discount on total_excluded if needed, but Odoo's compute_all handles base price.
            # Odoo sale order lines: price = unit * (1 - (discount or 0.0) / 100.0)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            taxes = line.tax_id.compute_all(
                price,
                line.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.block_id.letter_id.partner_id
            )

            line.price_subtotal = taxes["total_excluded"]
            line.price_total = taxes["total_included"]

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.name = rec.name or rec.product_id.display_name
                rec.product_uom_id = rec.product_uom_id or rec.product_id.uom_id
