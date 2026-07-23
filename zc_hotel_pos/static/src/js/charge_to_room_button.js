/** @odoo-module **/

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { FolioSelectDialog } from "./folio_select_dialog";

export class ChargeToRoomButton extends Component {
    static template = "zc_hotel_pos.ChargeToRoomButton";
    static props = {};

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    }

    get currentFolioName() {
        const order = this.pos.get_order();
        return order?.folio_id?.name || "";
    }

    async onClick() {
        const order = this.pos.get_order();
        const folios = this.pos.models["hotel.folio"].getAll();
        if (!folios.length) {
            this.notification.add(_t("No open guest folios found."), {
                type: "warning",
            });
            return;
        }
        this.dialog.add(FolioSelectDialog, {
            folios: folios.map((f) => ({
                id: f.id,
                name: f.name,
                partner_id: f.partner_id,
                room_id: f.room_id,
                amount_due: f.amount_due,
            })),
            getPayload: (folio) => this._attachFolio(order, folio),
        });
    }

    _attachFolio(order, folio) {
        const folioRecord = this.pos.models["hotel.folio"].get(folio.id);
        order.folio_id = folioRecord;
        // Set the guest as the order customer so the receivable is per-guest.
        if (folioRecord.partner_id) {
            const partner = this.pos.models["res.partner"].get(
                folioRecord.partner_id[0]
            );
            if (partner) {
                order.set_partner(partner);
            }
        }
        // In folio mode, pre-select the room folio payment method.
        if (this.pos.config.hotel_charge_mode === "folio") {
            const pmId = this.pos.config.hotel_folio_payment_method_id?.[0];
            const method = this.pos.models["pos.payment.method"].get(pmId);
            if (method) {
                order.add_paymentline(method);
            }
        }
        this.notification.add(
            _t("Order will be charged to %s.", folio.name),
            { type: "success" }
        );
    }
}
