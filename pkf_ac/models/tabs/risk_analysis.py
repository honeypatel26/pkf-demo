# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PkfAcEvaluationRiskAnalysis(models.Model):
    _inherit = "pkf.ac.evaluation"

    # ============================================================
    # Header readonly texts
    # ============================================================

    risk_objective_text = fields.Text(
        string="Objective (readonly)",
        readonly=True,
        default=(
            "The firm requires engagement teams to perform a comprehensive and objective assessment\n"
            "of each category during the acceptance and continuance process. This ensures that risk\n"
            "factors are appropriately evaluated without being influenced by association bias or planned\n"
            "procedures. All assessments should be made on a standalone basis, reflecting the inherent\n"
            "risks, complexity, and ethical considerations associated with the engagement.\n"
            "\n"
            "The engagement team is expected to:\n"
            "• Identify and assess all relevant risk factors.\n"
            "• Provide clear, well-documented responses for each category.\n"
            "• Take appropriate actions to address identified risks.\n"
        ),
    )

    risk_framework_text = fields.Text(
        string="Risk Assessment Framework (readonly)",
        readonly=True,
        default=(
            "Engagement teams must assign a risk rating (1, 2, or 3) for each category based on the "
            "following criteria, unless there is a specific guidance for the risk:\n"
            "• Low Risk (1) – None of the risk factors exist.\n"
            "• Moderate Risk (2) – One but less than two risk factors exist.\n"
            "• High Risk (3) – Two or more risk factors exist.\n"
            "Each response must be supported with sufficient documentation and, where necessary, "
            "proposed mitigating actions.\n"
        ),
    )

    _RISK_LEVEL_SELECTION = [
        ('low', '1 - Low'),
        ('medium', '2 - Medium'),
        ('high', '3 - High'),
        ("na", "N/A"),
    ]

    # ============================================================
    # 2.1 - 2.32 (AUDIT / general risk analysis)
    # ============================================================

    # 2.1
    risk_reasoning_1 = fields.Text(string="2.1 Market Capitalization")
    risk_level_1 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_1 = fields.Text(
        string="2.1 Guidance (readonly)",
        readonly=True,
        default=(
            "Market Capitalization = Number of Shares * Share Price at December 31\n"
            "Based on professional judgement:\n"
            "- Market Capitalization over $50 million is High risk\n"
            "- $25 million to $50 million is Medium risk\n"
            "- Below $25 million is Low risk"
        ),
    )

    # 2.2
    risk_reasoning_2 = fields.Text(
        string="2.2 Entity participates in high-risk business industries or actively engages in high-risk operations."
    )
    risk_level_2 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_2 = fields.Text(
        string="2.2 Guidance (readonly)",
        readonly=True,
        default=(
            "The entity operates within a high-risk industry and risk of financial failure exists. "
            "Either or both conditions might apply.\n"
            "\n"
            "Most common high-risk businesses include (but are not limited to) (according to payment-card processors):\n"
            "- Online Gambling, Online Gaming, and Casinos\n"
            "- Sports Booking\n"
            "- Bitcoin Mining or Forex Trading\n"
            "- Cannabis Products / Head Shops\n"
            "- Pharmaceuticals\n"
            "- Online Dating and Adult services\n"
            "- E-cigarettes and tobacco\n"
            "\n"
            "https://www.mymoid.com/blog/high-risk-business/"
        ),
    )

    # 2.3
    risk_reasoning_3 = fields.Text(string="2.3 Entity operates in or does business with unstable governments/countries.")
    risk_level_3 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_3 = fields.Text(
        string="2.3 Guidance (readonly)",
        readonly=True,
        default=(
            "As regulatory requirements vary based on the industry sector you operate in, you should know "
            "the regulations that apply to your client's industry.\n"
            "\n"
            "Examples:\n"
            "- Known or potential fraud cases\n"
            "- Failure to wear personal protective equipment (PPE)\n"
            "- Insufficient administration of operations\n"
            "- Failure to obtain proper certifications / illegal operations\n"
            "- Failure to follow operation procedures\n"
            "- Failure to report to relevant authorities\n"
            "\n"
            "Non-compliance which may have a material financial impact or risk of going concern are rated as High risk."
        ),
    )

    # 2.4
    risk_reasoning_4 = fields.Text(string="2.4 The Engagement requires the use of component practitioners.")
    risk_level_4 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_4 = fields.Text(
        string="2.4 Guidance (readonly)",
        readonly=True,
        default=(
            "Litigation that, according to generally accepted accounting principles, is significant and must be disclosed.\n"
            "\n"
            "Examples to consider (high-risk triggers):\n"
            "- Legislation or regulations with a significant and possibly negative impact not adequately addressed/evaluated\n"
            "- Entity prone to lawsuits or controversies (including class actions)\n"
            "- History of regulatory violations involving management\n"
            "- Allegations of possible fraud or compliance violations made by third parties or entity staff\n"
            "- Disregard displayed toward regulatory or legislative authorities\n"
            "- Lack of documentation to explain impact of actual or pending events\n"
            "- Overly optimistic assessments of re-assessments, investigations, and other regulatory reviews"
        ),
    )

    # 2.5
    risk_reasoning_5 = fields.Text(string="2.5 Non-compliance with industry laws/regulations.")
    risk_level_5 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_5 = fields.Text(
        string="2.5 Guidance (readonly)",
        readonly=True,
        default=(
            "An ethical violation is something that is spoken, written, or actioned that violates a company's code of ethics.\n"
            "\n"
            "Examples:\n"
            "- No emphasis placed on integrity and ethical values\n"
            "- Senior managers demonstrate a poor ethical example (e.g., inflating expense accounts, petty theft)\n"
            "- Weak tone at the top\n"
            "- Regular whistleblower reports/calls\n"
            "- Concerns about management integrity, non-ethical behaviour, or poor attitude toward internal control\n"
            "- Two or more different auditors in the past 3 years"
        ),
    )

    # 2.6
    risk_reasoning_6 = fields.Text(string="2.6 Potential material litigation")
    risk_level_6 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_6 = fields.Text(
        string="2.6 Guidance (readonly)",
        readonly=True,
        default=(
            "Independence threats:\n"
            "- Self-interest (economically dependent on maintaining client fees / influenced by desire to retain)\n"
            "- Self-review (assisting in preparing financial statements / bookkeeping / later auditing own judgments)\n"
            "- Advocacy (acting as a client advocate in tax, litigation, or share promotion)\n"
            "- Familiarity (close/family/long-time relationships leading to being too sympathetic)\n"
            "- Intimidation (client threats: replace firm unless scope limits / accept management positions, etc.)"
        ),
    )

    # 2.7
    risk_reasoning_7 = fields.Text(string="2.7 Questionable management/TCWG ethics.")
    risk_level_7 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_7 = fields.Text(
        string="2.7 Guidance (readonly)",
        readonly=True,
        default=(
            "Going concern indicators:"
            "- Negative trends (recurring losses, working capital deficiencies, negative operating cash flows, adverse ratios)Negative trends (recurring losses, working capital deficiencies, negative operating cash flows, adverse ratiosNegative trends (recurring losses, working capital deficiencies, negative operating cash flows, adverse ratios\n"
            "- Other financial difficulty indicators (loan default, dividend arrears, denial of trade credit, debt restructuring)\n"
            "- Internal matters (work stoppages, dependence on one project, uneconomic commitments, need to revise operations)\n"
            "- External matters (legal proceedings/legislation, loss of franchise/license/patent, loss of principal customer, catastrophe)"
        ),
    )

    # 2.8
    risk_reasoning_8 = fields.Text(string="2.8 Threat to Independence with Entity.")
    risk_level_8 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_8 = fields.Text(
        string="2.8 Guidance (readonly)",
        readonly=True,
        default=(
            "Note: Most clients will likely have poor or no sales.\n"
            "\n"
            "Examples:\n"
            "- High degree of competition or market saturation\n"
            "- Losses and/or declining profit margins\n"
            "- Declining industry with increasing business failures\n"
            "- Significant declines in customer demand\n"
            "- High vulnerability to rapidly changing technology or product obsolescence\n"
            "- Excessive interest in maintaining/increasing stock price or earnings trend"
        ),
    )

    # 2.9
    risk_reasoning_9 = fields.Text(string="2.9 Entity has high debt levels and/or poor cash flow.")
    risk_level_9 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_9 = fields.Text(
        string="2.9 Guidance (readonly)",
        readonly=True,
        default="Examples:\n- Unusually high dependence on debt\n- High vulnerability to changes in interest rates\n- Negative cash flows",
    )

    # 2.10
    risk_reasoning_10 = fields.Text(string="2.10 Poor sales outlook or intense competition.")
    risk_level_10 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_10 = fields.Text(
        string="2.10 Guidance (readonly)",
        readonly=True,
        default=(
            "Covenants may be related to finances, property, law, or religion.\n"
            "In business, a loan covenant may disallow acquisitions or require minimum cash."
        ),
    )

    # 2.11
    risk_reasoning_11 = fields.Text(string="2.11 Entity has high debt levels.")
    risk_level_11 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_11 = fields.Text(
        string="2.11 Guidance (readonly)",
        readonly=True,
        default=(
            "Public interest factors:\n"
            "- Nature of business\n- Size of the entity\n- Importance to markets and stakeholders\n- Systemic impact\n\n"
            "Political connection factors:\n"
            "- Relations to politicians\n- Indirect connections (donations/lobbying)\n- Close identification with political actors"
        ),
    )

    # 2.12
    risk_reasoning_12 = fields.Text(string="2.12 Bank covenant or other contractual violations.")
    risk_level_12 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_12 = fields.Text(
        string="2.12 Guidance (readonly)",
        readonly=True,
        default=(
            "International operations can introduce:\n"
            "- Logistical risk\n- Regulatory risk\n- Corruption risk\n- Health & Safety risk\n- Legal risk\n"
            "- Cultural risk\n- Financial risk\n- Political risk"
        ),
    )

    # 2.13
    risk_reasoning_13 = fields.Text(string="2.13 High media or political interest in the entity and management.")
    risk_level_13 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_13 = fields.Text(
        string="2.13 Guidance (readonly)",
        readonly=True,
        default="Consider using metrics such as:\n- Political stability index\n- Fragile States Index",
    )

    # 2.14
    risk_reasoning_14 = fields.Text(string="2.14 Entity operates in multiple locations or conducts operations overseas.")
    risk_level_14 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_14 = fields.Text(
        string="2.14 Guidance (readonly)",
        readonly=True,
        default=(
            "Examples:\n"
            "- Overly complex managerial lines of authority\n"
            "- Numerous or unusual legal entities\n"
            "- Complex structure with no apparent reason\n"
            "- Unusual transactions near period end\n"
            "- Significant related-party transactions\n"
            "- Tax-haven structures without clear justification"
        ),
    )

    # 2.15
    risk_reasoning_15 = fields.Text(string="2.15 Overly complex corporate/operational structures")
    risk_level_15 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_15 = fields.Text(
        string="2.15 Guidance (readonly)",
        readonly=True,
        default=(
            "Signs a business is growing too quickly:\n"
            "- Hiring fast and firing slowly\n- High turnover\n- Systems can't handle added activity\n"
            "- Chaos/disorganization\n- Increasing customer dissatisfaction\n- Falling employee enthusiasm"
        ),
    )

    # 2.16
    risk_reasoning_16 = fields.Text(string="2.16 Fast growth of the business - revenue, locations, staff")
    risk_level_16 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_16 = fields.Text(
        string="2.16 Guidance (readonly)",
        readonly=True,
        default=(
            "Examples:\n"
            "- Misleading representations\n- Delays in obtaining evidence\n- Incomplete/misleading information\n"
            "- Restricts access\n- Unreasonable demands/constraints\n- Evasive answers\n- Requests to change staff"
        ),
    )

    # 2.17
    risk_reasoning_17 = fields.Text(string="2.17 Poor cooperation from management.")
    risk_level_17 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_17 = fields.Text(
        string="2.17 Guidance (readonly)",
        readonly=True,
        default=(
            "Examples:\n"
            "- Lack of segregation of duties\n- Deficiencies ignored\n- Inadequate supervision\n- Unqualified staff\n"
            "- Failure to monitor controls\n- High turnover\n- Lack of mandatory vacations"
        ),
    )

    # 2.18
    risk_reasoning_18 = fields.Text(string="2.18 Poor control environment, leadership and staff morale.")
    risk_level_18 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_18 = fields.Text(
        string="2.18 Guidance (readonly)",
        readonly=True,
        default="Consider competence and document steps taken to improve competence where necessary.",
    )

    # 2.19
    risk_reasoning_19 = fields.Text(string="2.19 Firm has limited experience in the entity’s industry.")
    risk_level_19 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_19 = fields.Text(
        string="2.19 Guidance (readonly)",
        readonly=True,
        default="Engagement partner shall determine resources are sufficient and available timely.",
    )

    # 2.20
    risk_reasoning_20 = fields.Text(string="2.20 Reporting timeframes are unrealistic based on time available or firm resources.")
    risk_level_20 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_20 = fields.Text(
        string="2.20 Guidance (readonly)",
        readonly=True,
        default=(
            "Complex transactions requiring analysis/judgment may include:\n"
            "- Business combinations\n- Financial instruments\n- Shareholder agreements\n- Joint venture agreements\n"
            "- Deferred tax\n- Complex leases\n- Service concessions\n- Major revenue contracts"
        ),
    )

    # 2.21
    risk_reasoning_21 = fields.Text(string="2.21 Complex accounting transactions during the period.")
    risk_level_21 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_21 = fields.Text(
        string="2.21 Guidance (readonly)",
        readonly=True,
        default=(
            "Examples:\n"
            "- Directors have limited financial expertise\n"
            "- Little attention by board/audit committee\n"
            "- Unqualified staff\n"
            "- Financial reporting process not properly trained"
        ),
    )

    # 2.22
    risk_reasoning_22 = fields.Text(string="2.22 Incompetence of senior accounting personnel.")
    risk_level_22 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_22 = fields.Text(
        string="2.22 Guidance (readonly)",
        readonly=True,
        default="Examples:\n- Disagreements in fee negotiations\n- Owes previous audit firm material amounts\n- Low cash reserves / large vendor payables",
    )

    # 2.23
    risk_reasoning_23 = fields.Text(string="2.23 Entity unable or unwilling to pay a fair fee.")
    risk_level_23 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_23 = fields.Text(
        string="2.23 Guidance (readonly)",
        readonly=True,
        default=(
            "Examples:\n"
            "- No period-end timetable\n- No cut-off requirements\n- Reconciliations not performed\n"
            "- No control over spreadsheets\n- No standardization\n- Missing documentation for major transactions"
        ),
    )

    # 2.24
    risk_reasoning_24 = fields.Text(string="2.24 Poor/inadequate/missing accounting systems and records.")
    risk_level_24 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_24 = fields.Text(
        string="2.24 Guidance (readonly)",
        readonly=True,
        default=(
            "Factors may include:\n"
            "- Hardware/network complexity\n- Applications and data entry complexity\n- IT organization\n"
            "- Systems under change\n- Data sensitivity\n- Audit trail quality\n- Auditor IT skills"
        ),
    )

    # 2.25
    risk_reasoning_25 = fields.Text(string="2.25 Complex IT environments.")
    risk_level_25 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_25 = fields.Text(
        string="2.25 Guidance (readonly)",
        readonly=True,
        default="Significant ITGC/ITAC reliance triggers High risk.\nLimited ITGC/ITAC reliance triggers Medium risk.\n",
    )

    # 2.26
    risk_reasoning_26 = fields.Text(string="2.26 The Engagement requires the use of external experts.")
    risk_level_26 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_26 = fields.Text(
        string="2.26 Guidance (readonly)",
        readonly=True,
        default=(
            "- Allowance for bad debts, obsolete inventory\n"
            "- Allocation to inventory\n"
            "- Recoverability/impairment\n"
            "- Deferred charges\n"
            "- Timing of revenue recognition\n"
            "- Projections to bankers/creditors"
        ),
    )

    # 2.27
    risk_reasoning_27 = fields.Text(string="2.27 Estimates involve a high degree of estimation uncertainty.")
    risk_level_27 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_27 = fields.Text(
        string="2.27 Guidance (readonly)",
        readonly=True,
        default="Consider dominant influence over management and related parties.",
    )

    # 2.28
    risk_reasoning_28 = fields.Text(string="2.28 Extensive related-party transactions.")
    risk_level_28 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_28 = fields.Text(
        string="2.28 Guidance (readonly)",
        readonly=True,
        default=(
            "Aggressive accounting may overstate performance:\n"
            "- Revenue before sale finalized\n- Overhead over-capitalized\n- Deferred expenses not expensed/capitalized"
        ),
    )

    # 2.29
    risk_reasoning_29 = fields.Text(string="2.29 Entity chooses aggressive/ controversial accounting policies.")
    risk_level_29 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_29 = fields.Text(
        string="2.29 Guidance (readonly)",
        readonly=True,
        default="- Material adjustments near period end\n- Correction of major errors regularly\n- Many adjusting entries not accepted previously",
    )

    # 2.30
    risk_reasoning_30 = fields.Text(string="2.30 Significant adjustments are required.")
    risk_level_30 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_30 = fields.Text(
        string="2.30 Guidance (readonly)",
        readonly=True,
        default=(
            "- Unusual size/incidence\n- Overly complex form\n- Focus on accounting over economics\n"
            "- SPE/related-party not approved\n- Counterparties lack substance/strength"
        ),
    )

    # 2.31
    risk_reasoning_31 = fields.Text(string="2.31 Unusual transactions not in the ordinary course of business.")
    risk_level_31 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_31 = fields.Text(
        string="2.31 Guidance (readonly)",
        readonly=True,
        default=(
            "- Unusual size/incidence\n- Overly complex form\n- Focus on accounting over economics\n"
            "- SPE/related-party not approved\n- Counterparties lack substance/strength"
        ),
    )

    # 2.32
    risk_reasoning_32 = fields.Text(string="2.32 Other (specify):")
    risk_level_32 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_32 = fields.Text(
        string="2.32 Guidance (readonly)",
        readonly=True,
        default=(
            "- Unusual size/incidence\n- Overly complex form\n- Focus on accounting over economics\n"
            "- SPE/related-party not approved\n- Counterparties lack substance/strength"
        ),
    )

    # ============================================================
    # 2.33 - 2.47 (REVIEW questions + guidance text)
    # Renamed to risk_reasoning_* / risk_level_* / risk_guidance_* for consistency.
    # ============================================================

    # 2.33
    risk_reasoning_33 = fields.Text(string="2.33 Quality assurance manual")
    risk_level_33 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_33 = fields.Text(
        string="2.33 Guidance (readonly)",
        readonly=True,
        default=(
            "Determine whether accepting this engagement would contravene any of the firm's quality assurance policies. "
            "Also consider related services provided, such as those addressed by CSRS 4460 (Reports on Supplementary Matters "
            "Arising from an Audit or Review Engagement) and other advisory and tax planning services."
        ),
    )

    # 2.34
    risk_reasoning_34 = fields.Text(string="2.34 Engagement risk factors (a)")
    risk_level_34 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_34 = fields.Text(
        string="2.34 Guidance (readonly)",
        readonly=True,
        default=(
            "Indicate who in the firm has knowledge about, or contacts with, the prospective client and whether they "
            "recommend that this entity be accepted as a new client."
        ),
    )

    # 2.35
    risk_reasoning_35 = fields.Text(string="2.35 Engagement risk factors (b)")
    risk_level_35 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_35 = fields.Text(
        string="2.35 Guidance (readonly)",
        readonly=True,
        default=(
            "Indicate what other procedures were performed (including results and conclusions) to identify engagement risk "
            "factors that would cause us to decline the engagement. Consider procedures such as:\n"
            "• Inquiries of management/TCWG about: the reason for the change in accountants; whether another accounting firm(s) "
            "has recently declined the engagement; if so, why; other engagement risk factors.\n"
            "• An Internet news/social media search.\n"
            "• Review of relevant communications between the previous accountants and management/TCWG.\n"
            "• Obtaining permission from the prospective client to perform a credit check and to make inquiries with bankers, "
            "other advisors, regulators, etc."
        ),
    )

    # 2.36
    risk_reasoning_36 = fields.Text(string="2.36 Management’s integrity")
    risk_level_36 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_36 = fields.Text(
        string="2.36 Guidance (readonly)",
        readonly=True,
        default=(
            "Based on previous contact (if any) with key entity personnel and the results of procedures performed in Step 2 above, "
            "determine whether any concern has been identified that might cause us to doubt or distrust the management "
            "representations/assertions that we will be requesting and relying upon if the engagement is accepted. Consider:\n"
            "• Observed disregard for telling the truth.\n"
            "• Criminal convictions and regulatory sanctions.\n"
            "• History or suspicion of unethical actions, illegal acts or management override of controls.\n"
            "• Negative publicity.\n"
            "• Close association with people/companies with reputations for questionable ethics."
        ),
    )

    # 2.37
    risk_reasoning_37 = fields.Text(string="2.37 Opening balance (ONLY FOR ACCEPTANCE CLIENTS)")
    risk_level_37 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_37 = fields.Text(
        string="2.37 Guidance (readonly)",
        readonly=True,
        default=(
            "ONLY FOR ACCEPTANCE CLIENTS:\n"
            "a) Identify whether the opening balances have been reviewed.\n"
            "b) Make inquiries and reach a conclusion on whether there is sufficient evidence available on opening balances to identify:\n"
            "   i) Misstatements that could materially affect the current period’s financial statements; and\n"
            "   ii) Inconsistent application of accounting policies (reflected in the opening balances) in the current period’s financial statements."
        ),
    )

    # 2.38
    risk_reasoning_38 = fields.Text(string="2.38 Purpose of the review engagements")
    risk_level_38 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_38 = fields.Text(
        string="2.38 Guidance (readonly)",
        readonly=True,
        default=(
            "What is the entity’s intention for having a review engagement? Ensure:\n"
            "a) There is a rational purpose for the engagement.\n"
            "b) A review engagement would be appropriate in the circumstances.\n"
            "Consider:\n"
            "• Any significant scope limitations expected.\n"
            "• Any intent to inappropriately associate the firm’s name with the financial statements.\n"
            "• Any laws or regulations that require an audit rather than a review."
        ),
    )

    # 2.39
    risk_reasoning_39 = fields.Text(string="2.39 Independence threats")
    risk_level_39 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_39 = fields.Text(
        string="2.39 Guidance (readonly)",
        readonly=True,
        default=(
            "Identify and describe any significant threats to independence and the safeguards (if any) to reduce each threat "
            "to an acceptable level. Address the threats in relation to the firm and any member of the engagement team:\n"
            "a) Self-interest\n"
            "b) Self-review\n"
            "c) Advocacy\n"
            "d) Familiarity\n"
            "e) Intimidation\n"
            "Perform a search on our TREND database (365 on the PKF Hub) to check if another PKF office is performing any services "
            "for the client or its related entities resulting in a potential independence threat. Evaluate client for inclusion in TREND "
            "and document in Caseware."
        ),
    )

    # 2.40
    risk_reasoning_40 = fields.Text(string="2.40 Independence prohibitions")
    risk_level_40 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_40 = fields.Text(
        string="2.40 Guidance (readonly)",
        readonly=True,
        default=(
            "Identify and describe any potential independence prohibitions that could occur, and provide reasons why they do or do not "
            "preclude the firm or particular staff members from performing the engagement. Address each of the prohibitions listed below:\n"
            "a) Services performed\n"
            "b) Relationships\n"
            "c) Financial interests"
        ),
    )

    # 2.41
    risk_reasoning_41 = fields.Text(string="2.41 Unavailable or unreliable data")
    risk_level_41 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_41 = fields.Text(
        string="2.41 Guidance (readonly)",
        readonly=True,
        default=(
            "Based on preliminary understanding, is there any indication that the information needed to perform the engagement "
            "will be unavailable or unreliable?"
        ),
    )

    # 2.42
    risk_reasoning_42 = fields.Text(string="2.42 Firm competencies")
    risk_level_42 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_42 = fields.Text(
        string="2.42 Guidance (readonly)",
        readonly=True,
        default=(
            "Assess whether the firm has the necessary skills/resources to perform the engagement on a timely basis. Address the following:\n"
            "a) The availability of staff/resources with the appropriate level of experience, relevant industry/subject matter knowledge, "
            "and any required regulatory and reporting experience.\n"
            "b) The need for external experts and component practitioners.\n"
            "c) The need for an EQCR (where required)."
        ),
    )

    # 2.43
    risk_reasoning_43 = fields.Text(string="2.43 Engagement preconditions (a)")
    risk_level_43 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_43 = fields.Text(
        string="2.43 Guidance (readonly)",
        readonly=True,
        default="Determine whether the financial reporting framework to be applied in the preparation of the financial statements is appropriate.",
    )

    # 2.44
    risk_reasoning_44 = fields.Text(string="2.44 Engagement preconditions (b)")
    risk_level_44 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_44 = fields.Text(
        string="2.44 Guidance (readonly)",
        readonly=True,
        default=(
            "Ensure management has acknowledged its understanding and responsibility for:\n"
            "• The preparation of financial statements in accordance with the applicable financial reporting framework.\n"
            "• Such internal controls as management determines necessary to enable the preparation of financial statements that are free "
            "from material misstatement (whether due to fraud or error).\n"
            "• Providing the practitioners with:\n"
            "  - Access to all information relevant to the preparation of the financial statements;\n"
            "  - Additional information we may request;\n"
            "  - Unrestricted access to persons within the entity from whom we determine it necessary to obtain evidence."
        ),
    )

    # 2.45
    risk_reasoning_45 = fields.Text(string="2.45 Signed engagement letter")
    risk_level_45 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_45 = fields.Text(
        string="2.45 Guidance (readonly)",
        readonly=True,
        default="Where the engagement is to be accepted, obtain a signed engagement letter before commencing any work on the engagement.",
    )

    # 2.46
    risk_reasoning_46 = fields.Text(string="2.46 EQCR recruitment")
    risk_level_46 = fields.Selection(_RISK_LEVEL_SELECTION, string="Risk Level")
    risk_guidance_46 = fields.Text(
        string="2.46 Guidance (readonly)",
        readonly=True,
        default=(
            "Is an EQCR required on this engagement (select one)? This decision should be based on the engagement risk identified above "
            "and the firm’s criteria for when an EQCR is required. Basis for decision:"
        ),
    )

    # 2.47 (Studio-like field: N/A, 1, 2, 3)
    _REVIEW_RISK_LEVEL_SELECTION = [
        ('low', '1 - Low'),
        ('medium', '2 - Medium'),
        ('high', '3 - High'),
        ("na", "N/A"),
    ]
    risk_level_47 = fields.Selection(
        _REVIEW_RISK_LEVEL_SELECTION,
        string="2.47 Conclusion (Risk Level)",
        tracking=True,
    )
    risk_guidance_47 = fields.Text(
        string="2.47 Guidance (readonly)",
        readonly=True,
        default="Based on the information and risk factors identified above, this engagement is assessed as follows (select one):",
    )

    # ============================================================
    # 2.48 - 2.71 (Due Diligence / Attestation / Compilation)
    # Renamed to risk_reasoning_* / risk_guidance_* (and risk_level_* where applicable).
    # ============================================================

    # 2.48
    risk_reasoning_48 = fields.Text(string="2.48 Quality assurance manual")
    risk_guidance_48 = fields.Text(
        string="2.48 Guidance (readonly)",
        readonly=True,
        default=(
            "Determine whether accepting this engagement would contravene any of the firm's quality assurance policies. "
            "Also consider related services provided, and other advisory and tax planning services."
        ),
    )

    # 2.49
    risk_reasoning_49 = fields.Text(string="2.49 Engagement risk factors (a)")
    risk_guidance_49 = fields.Text(
        string="2.49 Guidance (readonly)",
        readonly=True,
        default=(
            "Indicate who in the firm has knowledge about, or contacts with, the prospective client and whether they "
            "recommend that this entity be accepted as a new client."
        ),
    )

    # 2.50
    risk_reasoning_50 = fields.Text(string="2.50 Engagement risk factors (b)")
    risk_guidance_50 = fields.Text(
        string="2.50 Guidance (readonly)",
        readonly=True,
        default=(
            "Indicate what other procedures were performed (including results and conclusions) to identify engagement risk factors "
            "that would cause us to decline the engagement.\n"
            "\n"
            "Consider procedures such as:\n"
            "• Inquiries of management/TCWG of the engaging entity about:\n"
            "  - The purpose for conducting the assignment.\n"
            "  - The type of report to be issued as a result of the engagement.\n"
            "  - The users of the report.\n"
            "  - The reason for the change in accountants (if applicable).\n"
            "  - Whether another accounting firm(s) has recently declined the engagement. If so, why?\n"
            "  - Other engagement risk factors.\n"
            "• An Internet news/social media search.\n"
            "• Obtaining permission from the prospective client to perform a credit check and to make inquiries "
            "with bankers, other advisors, regulators, etc."
        ),
    )

    # 2.51
    risk_reasoning_51 = fields.Text(string="2.51 Engagement risk factors (b)")
    risk_guidance_51 = fields.Text(
        string="2.51 Guidance (readonly)",
        readonly=True,
        default=(
            "Indicate what other procedures were performed (including results and conclusions) to identify engagement risk factors "
            "that would cause us to decline the engagement. Consider procedures such as:\n"
            "• Inquiries of management/TCWG about the engaging entity (incl. purpose of conducting the assignment; type of report to be issued; users of the report; "
            "reason for the change in accountants (if applicable); whether another accounting firm(s) has recently declined the engagement; if so, why; other engagement risk factors).\n"
            "• An Internet news/social media search.\n"
            "• Obtaining permission from the prospective client to perform a credit check and to make inquiries with bankers, other advisors, regulators, etc."
        ),
    )

    # 2.52
    risk_reasoning_52 = fields.Text(string="2.52 Purpose of the engagements")
    risk_guidance_52 = fields.Text(
        string="2.52 Guidance (readonly)",
        readonly=True,
        default=(
            "What is the entity's intention for having an engagement?\n"
            "\n"
            "Ensure:\n"
            "a) There is a rational purpose for the engagement.\n"
            "b) The engagement would be appropriate in the circumstances.\n"
            "\n"
            "Consider:\n"
            "• Any significant scope limitations expected.\n"
            "• Any intent to inappropriately associate the firm’s name with the financial statements or other records.\n"
            "• Any laws or regulations that require an audit or review rather than a due diligence engagement.\n"
            "\n"
            "c) Obtain understanding of other parties (i.e. potential buyers, seller, investor) interested in the engagement.\n"
            "d) Obtain an understanding of the terms of any potential agreement related to purchase, sale or investment "
            "of entities related to the engagement.\n"
            "\n"
            "Consider the areas of interest for the proposed transaction:\n"
            "• Revenue\n"
            "• Assets\n"
            "• Customer information\n"
            "• Other areas\n"
            "• Quality of Earnings (QofE)"
        ),
    )

    # 2.53
    risk_reasoning_53 = fields.Text(string="2.53 Purpose of the engagement")
    risk_guidance_53 = fields.Text(
        string="2.53 Guidance (readonly)",
        readonly=True,
        default=(
            "What is the entity’s intention for having an engagement? Ensure:\n"
            "a) There is a rational purpose for the engagement.\n"
            "b) The engagement would be appropriate in the circumstances.\n"
            "Consider:\n"
            "• Any significant scope limitations expected.\n"
            "• Any intent to inappropriately associate the firm’s name with the financial statements/other records.\n"
            "c) Obtain understanding of other parties (e.g. potential buyers, seller, investor) interested in the engagement."
        ),
    )

    # 2.54
    risk_reasoning_54 = fields.Text(string="2.54 Independence prohibitions")
    risk_guidance_54 = fields.Text(
        string="2.54 Guidance (readonly)",
        readonly=True,
        default=(
            "Identify and describe any potential independence prohibitions that could occur, and provide reasons why they do or do not "
            "preclude the firm or particular staff members from performing the engagement. Address each of the prohibitions listed below:\n"
            "a) Services performed\n"
            "b) Relationships\n"
            "c) Financial interests"
        ),
    )

    # 2.55
    risk_reasoning_55 = fields.Text(string="2.55 Independence threats")
    risk_guidance_55 = fields.Text(
        string="2.55 Guidance (readonly)",
        readonly=True,
        default=(
            "Identify and describe any significant threats to independence and the safeguards (if any) to reduce each threat to an acceptable level. "
            "Address the threats in relation to the firm and any member of the engagement team:\n"
            "a) Self-interest\n"
            "b) Self-review\n"
            "c) Advocacy\n"
            "d) Familiarity\n"
            "e) Intimidation"
        ),
    )

    # 2.56
    risk_reasoning_56 = fields.Text(string="2.56 Management’s integrity of the engaging entity")
    risk_guidance_56 = fields.Text(
        string="2.56 Guidance (readonly)",
        readonly=True,
        default=(
            "Based on previous contact (if any) with key entity personnel and the results of procedures performed above, "
            "determine whether any concern has been identified that might cause us to doubt or distrust the management "
            "representations/assertions that we will be requesting and relying upon if the engagement is accepted. Consider:\n"
            "• Observed disregard for telling the truth\n"
            "• Criminal convictions and regulatory sanctions\n"
            "• History or suspicions of unethical actions, illegal acts or management override of controls\n"
            "• Negative publicity\n"
            "• Close association with people/companies with reputations for questionable ethics"
        ),
    )

    # 2.57
    risk_reasoning_57 = fields.Text(string="2.57 Unavailable or unreliable data")
    risk_guidance_57 = fields.Text(
        string="2.57 Guidance (readonly)",
        readonly=True,
        default=(
            "Based on preliminary understanding, is there any indication that the information needed to perform the engagement "
            "will be unavailable or unreliable?"
        ),
    )
    # 2.58
    risk_reasoning_58 = fields.Text(string="2.58 Firm competencies")
    risk_guidance_58 = fields.Text(
        string="2.58 Guidance (readonly)",
        readonly=True,
        default=(
            "Assess whether the firm has the necessary skills and resources to perform the engagement on a timely basis.\n"
            "\n"
            "Address the following:\n"
            "a) The availability of staff and resources with the appropriate level of experience, relevant industry or subject matter knowledge, "
            "and any required regulatory and reporting experience.\n"
            "b) The need for external experts, specialists, and component practitioners.\n"
            "c) The need for an EQCR (if considered necessary due to specific challenges in the engagement).\n"
            "\n"
            "Inquire from the client about the proposed deadline and evaluate whether it is sufficient to conclude the engagement "
            "while achieving the Firm’s quality standards."
        ),
    )

    # 2.59
    risk_reasoning_59 = fields.Text(string="2.59 Firm competencies")
    risk_guidance_59 = fields.Text(
        string="2.59 Guidance (readonly)",
        readonly=True,
        default=(
            "Assess whether the firm has the necessary skills/resources to perform the engagement on a timely basis. Address the following:\n"
            "a) The availability of staff/resources with the appropriate level of experience, relevant industry/subject matter knowledge, and any required regulatory and reporting experience.\n"
            "b) The need for external experts, specialist and component practitioners.\n"
            "c) The need for an EQCR (if considered necessary due to specific challenges in the engagement).\n"
            "Inquire from the client about the deadline. Evaluate if the proposed deadline is sufficient to conclude the engagement while achieving quality standards of the Firm."
        ),
    )

    # 2.60 (Compilation)
    risk_reasoning_60 = fields.Text(string="2.60 Engagement preconditions (a)")
    risk_guidance_60 = fields.Text(
        string="2.60 Guidance (readonly)",
        readonly=True,
        default=(
            "Obtain an acknowledgment from management of the basis of accounting expected to be applied in the preparation of the compiled financial information. "
            "NOTE: Paragraph 25 of CSRS 4200 states that when the compiled financial information is intended to be used by a third party, the practitioner may accept or continue the engagement "
            "if, according to management: (a) the third party: (a) is in a position to request and obtain further information from the entity; or (Ref: Para. A25-A26) "
            "(b) has agreed with management the basis of accounting to be applied in the preparation of the compiled financial information. (Ref: Para. A27) "
            "If neither (a) nor (b) above are met, the practitioner shall not accept or continue the engagement, unless the basis of accounting to be applied in the preparation of the compiled financial information is a general purpose framework. (Ref: Para. A28)"
        ),
    )

    # 2.61 (Compilation)
    risk_reasoning_61 = fields.Text(string="2.61 Engagement preconditions (b)")
    risk_guidance_61 = fields.Text(
        string="2.61 Guidance (readonly)",
        readonly=True,
        default=(
            "For engagements other than compilation engagements, determine there is another suitable basis for the rendering of such service "
            "which is acceptable to us, management and any other intended user of the report."
        ),
    )

    # 2.62 (Compilation)
    risk_reasoning_62 = fields.Text(string="2.62 Engagement preconditions (c)")
    risk_guidance_62 = fields.Text(
        string="2.62 Guidance (readonly)",
        readonly=True,
        default=(
            "Ensure that management has acknowledged its understanding and responsibility for:\n"
            "• The preparation of financial information in accordance with the applicable basis of accounting.\n"
            "• Such internal controls as management determines necessary to enable the preparation of financial information that are free from material misstatement (whether due to fraud or error).\n"
            "• Providing the practitioners with:\n"
            "  - Access to all information relevant to the preparation of the financial statements/other financial information;\n"
            "  - Additional information we may request from management;\n"
            "  - Unrestricted access to persons within the entity from whom we determine it is necessary to obtain evidence."
        ),
    )

    # 2.63 (Attestation)
    risk_reasoning_63 = fields.Text(string="2.63 Engagement preconditions (a)")
    risk_guidance_63 = fields.Text(
        string="2.63 Guidance (readonly)",
        readonly=True,
        default="Determine the underlying subject matter is appropriate.",
    )

    # 2.64 (Attestation)
    risk_reasoning_64 = fields.Text(string="2.64 Engagement preconditions (b)")
    risk_guidance_64 = fields.Text(
        string="2.64 Guidance (readonly)",
        readonly=True,
        default=(
            "Determine whether the criteria to be applied in the preparation of the aforementioned subject matter are suitable for the engagement circumstances, "
            "including that they exhibit the following characteristics:\n"
            "- Relevance\n- Completeness\n- Reliability\n- Neutrality\n- Understandability"
        ),
    )

    # 2.65 (Attestation)
    risk_reasoning_65 = fields.Text(string="2.65 Engagement preconditions (c)")
    risk_guidance_65 = fields.Text(
        string="2.65 Guidance (readonly)",
        readonly=True,
        default="Whether the criteria used in the preparation of subject matter will be available to the intended users.",
    )

    # 2.66 (Attestation)
    risk_reasoning_66 = fields.Text(string="2.66 Engagement preconditions (d)")
    risk_guidance_66 = fields.Text(
        string="2.66 Guidance (readonly)",
        readonly=True,
        default=(
            "Ensure that management has acknowledged its understanding and responsibility for:\n"
            "• The preparation of financial information in accordance with the applicable basis of accounting.\n"
            "• Such internal controls as management determines necessary to enable the preparation of financial information that are free from material misstatement (whether due to fraud or error).\n"
            "• Providing the practitioners with:\n"
            "  - Access to all information relevant to the preparation of the financial statements/other financial information;\n"
            "  - Additional information we may request from management for the purpose of the engagement; and\n"
            "  - Unrestricted access to persons within the entity from whom we determine it is necessary to obtain evidence."
        ),
    )

    # 2.67 (Due Diligence)
    risk_reasoning_67 = fields.Text(string="2.67 Engagement preconditions (a)")
    risk_guidance_67 = fields.Text(
        string="2.67 Guidance (readonly)",
        readonly=True,
        default=(
            "Determine whether the financial reporting framework to be applied in the preparation of the financial statements/other financial information "
            "is appropriate for the due diligence work to be carried out."
        ),
    )

    # 2.68 (Due Diligence)
    risk_reasoning_68 = fields.Text(string="2.68 Engagement preconditions (b)")
    risk_guidance_68 = fields.Text(
        string="2.68 Guidance (readonly)",
        readonly=True,
        default=(
            "Ensure management has acknowledged its understanding and responsibility for:\n"
            "• The preparation of financial statements/other financial information in accordance with the applicable financial reporting framework.\n"
            "• Such internal controls as management determines necessary to enable the preparation of financial statements/other financial information that are free from material misstatement (whether due to fraud or error).\n"
            "• Providing the practitioners with:\n"
            "  - Access to all information relevant to the preparation of the financial statements/other financial information;\n"
            "  - Additional information we may request from management for the purpose of the engagement; and\n"
            "  - Unrestricted access to persons within the entity from whom we determine it is necessary to obtain evidence."
        ),
    )

    # 2.69
    risk_reasoning_69 = fields.Text(string="2.69 Signed engagement letter")
    risk_guidance_69 = fields.Text(
        string="2.69 Guidance (readonly)",
        readonly=True,
        default="Where the engagement is to be accepted, obtain a signed engagement letter before commencing any work on the engagement.",
    )

    # 2.70 (Conclusion) - Select N/A/1/2/3
    _ENG_CONCLUSION_RISK_LEVEL_SELECTION = [
        ('low', '1 - Low'),
        ('medium', '2 - Medium'),
        ('high', '3 - High'),
        ("na", "N/A"),
    ]
    risk_level_70 = fields.Selection(
        _ENG_CONCLUSION_RISK_LEVEL_SELECTION,
        string="2.70 Conclusion",
        tracking=True,
    )
    risk_guidance_70 = fields.Text(
        string="2.70 Guidance (readonly)",
        readonly=True,
        default="Based on the information and risk factors identified above, this engagement is assessed as follows (select one):",
    )

    # 2.71 (Partner/Practitioner assessment) - Select Yes/No
    _ENG_PARTNER_ASSESSMENT_SELECTION = [
        ("yes", "Yes"),
        ("no", "No"),
    ]
    risk_partner_assessment_71 = fields.Selection(
        _ENG_PARTNER_ASSESSMENT_SELECTION,
        string="2.71 Partner/Practitioner assessment",
        tracking=True,
    )
    risk_guidance_71 = fields.Text(
        string="2.71 Guidance (readonly)",
        readonly=True,
        default="I have read the responses to the questions above and agree with the risk assessment and decision above.",
    )

    # ============================================================
    # Summary fields (used in view)
    # ============================================================

    low_risk_factors = fields.Integer(string="Low Risk Factors", compute="_compute_risk_summary_metrics", store=True)
    medium_risk_factors = fields.Integer(string="Medium Risk Factors", compute="_compute_risk_summary_metrics", store=True)
    high_risk_factors = fields.Integer(string="High Risk Factors", compute="_compute_risk_summary_metrics", store=True)

    total_score = fields.Integer(string="Total Score", compute="_compute_risk_summary_metrics", store=True)
    out_of_possible = fields.Integer(string="Out of a Possible", compute="_compute_risk_summary_metrics", store=True)
    rating = fields.Char(string="Rating", compute="_compute_risk_summary_metrics", store=True)

    overall_engagement_risk = fields.Char(
        string="Engagement Risk",
        compute="_compute_overall_engagement_risk",
        store=True,
    )

    # ============================================================
    # Computes
    # ============================================================

    @api.depends(*[f"risk_level_{i}" for i in range(1, 33)])
    def _compute_risk_summary_metrics(self):
        """Counts only 2.1-2.32 scores (audit/general block)."""
        for rec in self:
            low_cnt = 0
            med_cnt = 0
            high_cnt = 0
            total = 0
            answered = 0

            for i in range(1, 33):
                val = rec[f"risk_level_{i}"]  # '1','2','3','na' or False
                if val == "low":
                    low_cnt += 1
                    total += 1
                    answered += 1
                elif val == "medium":
                    med_cnt += 1
                    total += 2
                    answered += 1
                elif val == "high":
                    high_cnt += 1
                    total += 3
                    answered += 1

            out_of = answered * 3
            rating_str = f"{round(total * 100.0 / out_of)}%" if out_of else "0%"

            rec.low_risk_factors = low_cnt
            rec.medium_risk_factors = med_cnt
            rec.high_risk_factors = high_cnt
            rec.total_score = total
            rec.out_of_possible = out_of
            rec.rating = rating_str

    @api.depends(
        "risk_score",
        "engagement_type",
        "risk_level_47",
        "risk_level_70",
        "low_risk_factors",
        "medium_risk_factors",
        "high_risk_factors",
    )
    def _compute_overall_engagement_risk(self):
        """
        Engagement Risk logic (with Partner override and proper reset on type change):

        0) If risk_score is set to low/medium/high -> overwrite overall_engagement_risk
           (n_a / empty -> no override)

        Then by engagement_type:
        - review -> only risk_level_47. If not set -> blank " "
        - due_diligence/attestation/compilation -> only risk_level_70. If not set -> blank " "
        - audit -> use counters logic (2.1-2.32). If all counters 0 -> blank " "
        - anything else -> blank " "
        """
        for rec in self:
            # 0) Partner override (highest priority)
            if rec.risk_score in ("low", "medium", "high"):
                rec.overall_engagement_risk = {
                    "low": "Low Risk",
                    "medium": "Medium Risk",
                    "high": "High Risk",
                }[rec.risk_score]
                continue

            # If risk_score is 'n_a' or empty -> ignore override and compute normally

            # 1) Review: ONLY from risk_level_47, otherwise blank
            if rec.engagement_type == "review":
                if rec.risk_level_47 in ("low", "medium", "high"):
                    rec.overall_engagement_risk = {
                        "low": "Low Risk",
                        "medium": "Medium Risk",
                        "high": "High Risk",
                    }[rec.risk_level_47]
                else:
                    rec.overall_engagement_risk = " "
                continue

            # 2) Due Diligence / Attestation / Compilation: ONLY from risk_level_70, otherwise blank
            if rec.engagement_type in ("due_diligence", "attestation", "compilation"):
                if rec.risk_level_70 in ("low", "medium", "high"):
                    rec.overall_engagement_risk = {
                        "low": "Low Risk",
                        "medium": "Medium Risk",
                        "high": "High Risk",
                    }[rec.risk_level_70]
                else:
                    rec.overall_engagement_risk = " "
                continue

            # 3) Audit: ONLY counters logic
            if rec.engagement_type == "audit":
                l = rec.low_risk_factors or 0
                m = rec.medium_risk_factors or 0
                h = rec.high_risk_factors or 0

                if l == 0 and m == 0 and h == 0:
                    rec.overall_engagement_risk = " "
                elif m <= 6 and h == 0:
                    rec.overall_engagement_risk = "Low Risk"
                elif m <= 22 and h <= 1:
                    rec.overall_engagement_risk = "Medium Risk"
                elif m >= 23 or h >= 2:
                    rec.overall_engagement_risk = "High Risk"
                else:
                    rec.overall_engagement_risk = "Unknown Risk"
                continue

            # 4) Any other engagement_type -> blank (prevents showing stale risk)
            rec.overall_engagement_risk = " "