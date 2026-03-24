/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { DashboardItem } from "./dashboard_item";

export class UnifiedDashboard extends Component {
    static template = "galaxy_practice_management_app.UnifiedDashboard";
    static components = { DashboardItem };

    setup() {
        // params passed from ir.actions.client are in this.props.action.params
        this.actions = this.props.action.params.actions || [];

        // Split actions into 2 columns for display
        this.leftColumn = this.actions.filter((_, i) => i % 2 === 0);
        this.rightColumn = this.actions.filter((_, i) => i % 2 !== 0);
    }
}

registry.category("actions").add("galaxy_practice_management_app.dashboard", UnifiedDashboard);
