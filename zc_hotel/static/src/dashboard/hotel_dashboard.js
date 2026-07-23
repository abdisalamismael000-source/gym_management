/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class HotelDashboard extends Component {
    static template = "zc_hotel.HotelDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ data: null, loading: true });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        this.state.data = await this.orm.call(
            "hotel.dashboard",
            "get_dashboard_data",
            []
        );
        this.state.loading = false;
    }

    formatMoney(value) {
        const symbol = this.state.data ? this.state.data.currency_symbol || "" : "";
        const amount = (value || 0).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
        return `${symbol} ${amount}`;
    }

    openReservations(extraContext = {}) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Reservations",
            res_model: "hotel.reservation",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            context: extraContext,
        });
    }

    openArrivals() {
        this.openReservations({ search_default_arrivals_today: 1 });
    }

    openDepartures() {
        this.openReservations({ search_default_departures_today: 1 });
    }

    openInHouse() {
        this.openReservations({ search_default_in_house: 1 });
    }
}

registry.category("actions").add("hotel_dashboard", HotelDashboard);
