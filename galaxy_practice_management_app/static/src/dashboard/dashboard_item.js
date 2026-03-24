/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { View } from "@web/views/view";
import { makeContext } from "@web/core/context";
import { user } from "@web/core/user";
import { Domain } from "@web/core/domain";

export class DashboardItem extends Component {
    static template = "galaxy_practice_management_app.DashboardItem";
    static components = { View };
    static props = {
        action: Object, // { xml_id: ..., view_mode: ... }
    };

    setup() {
        this.actionService = useService("action");
        this.viewProps = null;
        this.isValid = true;
        this.title = this.props.action.name;

        onWillStart(async () => {
            // Load the action using its XML ID (which we must resolve first potentially?)
            // Usually /web/action/load expects an integer ID (action_id).
            // But we have XML ID.
            // We can resolve XML ID to integer ID via RPC.

            // Wait, standard Action Service loadAction usually takes ID or XML ID?
            // rpc("/web/action/load", { action_id: ... }) takes integer ID usually.

            // Let's resolve the XML ID first.
            let actionId = this.props.action.action_id;

            if (!actionId && this.props.action.xml_id) {
                // We need to find the action ID
                // We can use a search on ir.model.data or just load it via action service if it supported it.
                // Simpler: Search ir.actions.act_window directly? No.
                // Resolving xml_id:
                // model: ir.model.data
                const result = await rpc("/web/dataset/call_kw/ir.model.data/check_object_reference", {
                    model: "ir.model.data",
                    method: "check_object_reference",
                    args: this.props.action.xml_id.split("."),
                    kwargs: {},
                });
                // result is [model, id]
                if (result) {
                    actionId = result[1];
                }
            }

            if (!actionId) {
                this.isValid = false;
                return;
            }

            const result = await rpc("/web/action/load", { action_id: actionId });

            if (!result) {
                this.isValid = false;
                return;
            }

            // Logic adapted from BoardAction
            const viewMode = this.props.action.view_mode || result.views[0][1];

            // We need to construct viewProps for the <View> component

            this.viewProps = {
                resModel: result.res_model,
                type: viewMode,
                display: { controlPanel: false, searchPanel: false }, // embedding usually hides control panel
                // We might want to pass context/domain
            };

            const view = result.views.find((v) => v[1] === viewMode);
            if (view) {
                this.viewProps.viewId = view[0];
            }
            const searchView = result.views.find((v) => v[1] === "search");
            this.viewProps.views = [
                [this.viewProps.viewId || false, viewMode],
                [(searchView && searchView[0]) || false, "search"],
            ];

            if (result.context) {
                // Merge action context from the server action, plus any custom context from props, plus user lang
                const customContext = this.props.action.context || {};
                this.viewProps.context = makeContext([result.context, customContext, { lang: user.context.lang }]);
            } else if (this.props.action.context) {
                this.viewProps.context = makeContext([this.props.action.context, { lang: user.context.lang }]);
            }

            if (result.domain) {
                this.viewProps.domain = new Domain(result.domain).toList({ ...user.context, uid: user.userId });
            }

            if (viewMode === "list") {
                this.viewProps.allowSelectors = false;
            }

            // We want to link record selection to opening the record
            this.viewProps.selectRecord = (resId) => this.selectRecord(result.res_model, resId);
        });
    }

    selectRecord(resModel, resId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: resModel,
            views: [[false, "form"]],
            res_id: resId,
        });
    }
}
