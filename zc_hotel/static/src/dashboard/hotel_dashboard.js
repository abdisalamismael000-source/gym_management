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

    // --- Sparklines -------------------------------------------------------
    /** Build normalized polyline + area path strings for a numeric series. */
    sparkline(series) {
        const W = 100;
        const H = 32;
        const pad = 3;
        const data = series && series.length ? series : [0, 0];
        const min = Math.min(...data);
        const max = Math.max(...data);
        const span = max - min || 1;
        const n = data.length;
        const pts = data.map((v, i) => {
            const x = n === 1 ? W / 2 : (i / (n - 1)) * (W - pad * 2) + pad;
            const y = H - pad - ((v - min) / span) * (H - pad * 2);
            return [Number(x.toFixed(2)), Number(y.toFixed(2))];
        });
        const line = pts.map((p) => p.join(",")).join(" ");
        const area =
            `M${pts[0][0]},${H} ` +
            pts.map((p) => `L${p[0]},${p[1]}`).join(" ") +
            ` L${pts[n - 1][0]},${H} Z`;
        const up = data[n - 1] >= data[0];
        return { line, area, up };
    }

    // --- Donut ------------------------------------------------------------
    get donutSegments() {
        const data = this.state.data;
        if (!data) {
            return [];
        }
        const items = data.status_breakdown || [];
        const total = items.reduce((s, it) => s + (it.value || 0), 0) || 1;
        const C = 2 * Math.PI * 42; // r = 42
        let offset = 0;
        return items.map((it) => {
            const len = ((it.value || 0) / total) * C;
            const seg = {
                color: it.color,
                dash: `${len} ${C - len}`,
                offset: -offset,
            };
            offset += len;
            return seg;
        });
    }

    get totalRooms() {
        const data = this.state.data;
        return data ? data.sellable_rooms : 0;
    }

    // --- Navigation -------------------------------------------------------
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
    openHousekeeping() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Housekeeping",
            res_model: "hotel.housekeeping",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"],
            ],
        });
    }
}

registry.category("actions").add("hotel_dashboard", HotelDashboard);
