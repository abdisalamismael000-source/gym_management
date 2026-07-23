/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";

export class FolioSelectDialog extends Component {
    static template = "zc_hotel_pos.FolioSelectDialog";
    static components = { Dialog };
    static props = {
        folios: Array,
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.state = useState({ query: "" });
    }

    get filteredFolios() {
        const q = this.state.query.trim().toLowerCase();
        if (!q) {
            return this.props.folios;
        }
        return this.props.folios.filter((f) => {
            const guest = (f.partner_id?.[1] || "").toLowerCase();
            const room = (f.room_id?.[1] || "").toLowerCase();
            const ref = (f.name || "").toLowerCase();
            return guest.includes(q) || room.includes(q) || ref.includes(q);
        });
    }

    selectFolio(folio) {
        this.props.getPayload(folio);
        this.props.close();
    }

    get dialogTitle() {
        return _t("Charge to Room");
    }
}
