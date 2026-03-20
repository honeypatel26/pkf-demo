# -*- coding: utf-8 -*-
from odoo import fields, models

class TrendResearch(models.Model):
    _name = "trend.research"
    _description = "Trend Research"



    name = fields.Char()
    description = fields.Text()
    result_file = fields.Binary("Upload The Result")
    file_name = fields.Char("File Name ")
    evaluation_id = fields.Many2one("pkf.ac.evaluation", string ="Evaluation")
