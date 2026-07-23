/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ChargeToRoomButton } from "./charge_to_room_button";

// Show the button only when this POS config has a hotel charge mode set.
PaymentScreen.addControlButton({
    component: ChargeToRoomButton,
    condition() {
        return Boolean(this.pos.config.hotel_charge_mode);
    },
});
