# -*- coding: utf-8 -*-

from odoo import fields, models


class PkfAcEvaluationOverview(models.Model):
    _inherit = "pkf.ac.evaluation"

    # =========================
    # POTENTIAL UPCOMING ENGAGEMENT
    # =========================
    overview_type_of_engagement = fields.Selection(
        [
            ("audit_1y", "Audit for 1 Year"),
            ("audit_2y", "Audit for 2 Years"),
            ("audit_3y", "Audit for 3 Years"),
            ("q1_review", "Q1 Review"),
            ("q2_review", "Q2 Review"),
            ("q3_review", "Q3 Review"),
            ("q4_review", "Q4 Review"),
        ],
        string="1.1 Type of Engagement",
    )

    overview_reason_for_engagement = fields.Selection(
        [
            ("listed", "Required for listed companies"),
            ("debt", "Required for debt covenants"),
            ("shareholders", "Requested by shareholders"),
            ("regulations", "Required by regulations"),
            ("investors", "For potential investors"),
            ("financing", "To obtain additional financing"),
            ("tendering", "Tendering for work / For Customers"),
            ("suppliers", "For suppliers"),
            ("governance", "Good Governance"),
            ("fraud", "Fraud Prevention"),
            ("process", "Process improvement"),
        ],
        string="1.2 Reason for Engagement",
    )

    does_company_have_revenue = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Does the company have a revenue?",
    )

    does_company_have_itgc = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Does the company have an ITGC?",
    )

    # =========================
    # PREVIOUS ENGAGEMENT
    # =========================
    prev_new_or_continuing_client = fields.Selection(
        [
            ("new", "New Client"),
            ("continuing", "Continuing Client"),
        ],
        string="1.5 New or Continuing Client",
    )

    prev_type_of_engagement = fields.Selection(
        [
            ("audit_1y", "Audit for 1 Year"),
            ("audit_2y", "Audit for 2 Years"),
            ("audit_3y", "Audit for 3 Years"),
            ("q1_review", "Q1 Review"),
            ("q2_review", "Q2 Review"),
            ("q3_review", "Q3 Review"),
            ("q4_review", "Q4 Review"),
        ],
        string="1.6 Type of Engagement",
    )

    prev_reason_for_engagement = fields.Selection(
        [
            ("listed", "Required for listed companies"),
            ("debt", "Required for debt covenants"),
            ("shareholders", "Requested by shareholders"),
            ("regulations", "Required by regulations"),
            ("investors", "For potential investors"),
            ("financing", "To obtain additional financing"),
            ("tendering", "Tendering for work / For Customers"),
            ("suppliers", "For suppliers"),
            ("governance", "Good Governance"),
            ("fraud", "Fraud Prevention"),
            ("process", "Process improvement"),
        ],
        string="1.7 Reason for Engagement",
    )
    has_revenue = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Does the company have a revenue?",
    )
    # =========================
    # GENERAL (1.17 - 1.21)
    # =========================
    nature_of_assignment = fields.Char(string="1.17 Nature of assignment")
    period_covered_by_the_engagement = fields.Char(string="1.18 Period covered by the engagement")

    relevant_auditing_framework = fields.Selection(
        [
            ("csae3000", "CSAE 3000"),
            ("csae3001", "CSAE 3001"),
            ("csae3410", "CSAE 3410"),
            ("csae3416", "CSAE 3416"),
            ("csae3530", "CSAE 3530"),
            ("csae3531", "CSAE 3531"),
        ],
        string="1.19 Relevant auditing framework",
    )

    type_of_attestation_work = fields.Selection(
        [
            ("reasonable", "Reasonable assurance"),
            ("limited", "Limited assurance"),
        ],
        string="1.20 Type of attestation work",
    )

    other_assignment_requested_performed = fields.Char(
        string="1.21 Other assignment requested / performed"
    )
    # =========================
    # Engagement risk factors
    # =========================
    search_new_emerging_risks = fields.Text(
        string="1.10 Searches for any new or emerging engagement risks"
    )
    # =========================
    # SAFETY FIELD (to avoid crashes if an old field name is still referenced in XML)
    # =========================
    general_nature_of_assignment = fields.Char(string="(legacy) General Nature of Assignment")

    # =========================
    # TEXT / QA / DATA / COMPETENCIES (from overview.xml)
    # =========================
    qa_accepting_contravene_firm = fields.Text(
        string="Accepting engagement would contravene firm policies?"
    )
    data_unavailable_or_unreliable = fields.Text(string="Unavailable or unreliable data")

    staff_resources_availability_expertise = fields.Text(
        string="Staff resources availability / expertise"
    )
    external_expertise_necessity = fields.Text(string="External expertise necessity")
    need_for_eqcr_where_required = fields.Text(string="Need for EQCR where required")

    check_for_updated_engagement_letter = fields.Text(
        string="Check for updated engagement letter"
    )
