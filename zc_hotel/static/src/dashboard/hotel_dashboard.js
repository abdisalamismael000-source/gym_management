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
        this.state = useState({ data: null, loading: true, busy: false });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        this.state.loading = true;
        this.state.data = await this.orm.call("hotel.dashboard", "get_dashboard_data", []);
        this.state.loading = false;
    }

    // --- formatting -------------------------------------------------------
    money(value) {
        const d = this.state.data || {};
        const sym = d.currency_symbol || "";
        const amount = (value || 0).toLocaleString(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        });
        return d.currency_position === "after" ? `${amount} ${sym}` : `${sym} ${amount}`;
    }

    deltaClass(v) {
        if (v === null || v === undefined) return "o_hg_flat";
        return v >= 0 ? "o_hg_up" : "o_hg_down";
    }
    deltaText(v) {
        if (v === null || v === undefined) return "—";
        const arrow = v >= 0 ? "▲" : "▼";
        return `${arrow} ${Math.abs(v)}%`;
    }

    // --- revenue area chart ----------------------------------------------
    get revenueChart() {
        const d = this.state.data;
        const series = (d && d.revenue_trend) || [0, 0];
        const W = 600, H = 180, pad = 12;
        const max = Math.max(...series, 1);
        const n = series.length;
        const pts = series.map((v, i) => {
            const x = n === 1 ? W / 2 : (i / (n - 1)) * (W - pad * 2) + pad;
            const y = H - pad - (v / max) * (H - pad * 2);
            return [Number(x.toFixed(1)), Number(y.toFixed(1))];
        });
        const line = pts.map((p) => p.join(",")).join(" ");
        const area =
            `M${pts[0][0]},${H} ` +
            pts.map((p) => `L${p[0]},${p[1]}`).join(" ") +
            ` L${pts[n - 1][0]},${H} Z`;
        return { line, area, last: pts[n - 1], labels: (d && d.trend_labels) || [], pts, W, H };
    }

    // --- donut ------------------------------------------------------------
    get donutSegments() {
        const d = this.state.data;
        if (!d) return [];
        const items = d.status_breakdown || [];
        const total = items.reduce((s, it) => s + (it.value || 0), 0) || 1;
        const C = 2 * Math.PI * 40;
        let offset = 0;
        return items.map((it) => {
            const len = ((it.value || 0) / total) * C;
            const seg = { color: it.color, dash: `${len} ${C - len}`, offset: -offset };
            offset += len;
            return seg;
        });
    }

    // --- inline actions ---------------------------------------------------
    async doCheckIn(id) {
        if (this.state.busy) return;
        this.state.busy = true;
        try {
            await this.orm.call("hotel.dashboard", "check_in", [id]);
            await this.loadData();
        } finally {
            this.state.busy = false;
        }
    }
    async doCheckOut(id) {
        if (this.state.busy) return;
        this.state.busy = true;
        try {
            await this.orm.call("hotel.dashboard", "check_out", [id]);
            await this.loadData();
        } finally {
            this.state.busy = false;
        }
    }

    openReservation(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hotel.reservation",
            res_id: id,
            views: [[false, "form"]],
        });
    }
    newReservation() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "New Reservation",
            res_model: "hotel.reservation",
            views: [[false, "form"]],
            target: "current",
        });
    }
    openReservations(ctx = {}) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Reservations",
            res_model: "hotel.reservation",
            views: [[false, "list"], [false, "form"]],
            context: ctx,
        });
    }
}

registry.category("actions").add("hotel_dashboard", HotelDashboard);
