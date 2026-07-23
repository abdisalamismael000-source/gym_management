# Hotel Management

A complete, client-grade **Hotel Property Management System (PMS)** for
**Odoo 19**, built from four cleanly separated modules. It covers the full
guest journey — from an online booking or a walk-in, through check-in,
in-house charges and housekeeping, to check-out, invoicing and the owner's
nightly reports.

> **Note on the repository name.** This project is the *Hotel Management*
> product. The Git repository is still named `gym_management`; renaming the
> repository itself is a GitHub admin action (see
> [Renaming the repository](#renaming-the-repository) below).

---

## Modules

| Module | What it adds |
|--------|--------------|
| **`zc_hotel`** | Core PMS: rooms, room types, availability (no double-booking), reservations with a calendar planner, guest folios, rate plans, housekeeping, guest CRM, a front-desk KPI dashboard, the report pack and guest emails. Integrates Contacts, Accounting, Inventory and HR. |
| **`zc_hotel_pos`** | Charges restaurant / bar / spa / minibar **POS outlets** to the guest's room folio, split by outlet. |
| **`zc_hotel_website`** | Public **online booking engine** — room search, live availability, booking form, and a "My Bookings" portal page. |
| **`zc_hotel_maintenance`** | Links rooms to **maintenance equipment** and raises repair tickets from a room or housekeeping task. |
| **`zc_hotel_event`** | **Banquet & events** — function rooms and event bookings (weddings, conferences) with no double-booking and organiser invoicing. |

## Highlight features

- **Reliable availability** — a database-level overlap check makes
  double-booking a room impossible; a "Check Availability" finder and the
  website search both reuse the same engine.
- **Front-desk dashboard** — live **Occupancy %, ADR and RevPAR**, today's
  arrivals / departures, in-house guests and month-to-date revenue.
- **Reservations planner** — calendar, Kanban, pivot and graph views, not just
  a list.
- **Housekeeping board** — cleaning tasks auto-created on check-out and
  assigned to HR staff; completing a task frees the room.
- **Rate plans** — seasonal, per-room-type pricing and board types (RO / BB /
  HB / FB) that feed folio charges automatically.
- **Guest CRM & loyalty** — ID / nationality / preferences, VIP flag, loyalty
  points with automatic **tiers** (Bronze → Platinum), stay history and
  corporate accounts.
- **Front-desk dashboard, redesigned** — a modern card UI with live sparklines
  and a room-status donut (occupancy, ADR, RevPAR, arrivals/departures).
- **Multi-property** — group rooms and reservations under separate properties.
- **Guest services** — spa, transfers, tours and late check-outs booked and
  posted straight to the folio.
- **Distribution channels** — record OTA channels and per-booking references
  (Booking.com, Expedia…). Note: live two-way OTA sync needs each provider's
  paid API and is provided as a scaffold / integration point, not a working
  connector.
- **Billing** — deposits, configurable city / tourism tax, one-click invoicing
  to Odoo Accounting.
- **Owner report pack** — Manager Flash / daily report, Arrivals, Departures,
  In-house, Room / Housekeeping status, Guest Ledger, Revenue by Room Type,
  Occupancy, No-show and Police / Guest Registration; plus a printable Guest
  Folio and Registration Card.
- **Guest emails** — booking confirmation, pre-arrival reminder and post-stay
  thank-you / review request templates.

## Installation

1. Copy the four module folders into your Odoo `addons` path.
2. Update the apps list and install **Hotel Management** (`zc_hotel`). This is
   the only required module.
3. Install the optional add-ons as needed:
   - **Hotel POS Folio Integration** (`zc_hotel_pos`) — needs *Point of Sale*.
   - **Hotel Online Booking** (`zc_hotel_website`) — needs *Website*.
   - **Hotel Maintenance** (`zc_hotel_maintenance`) — needs *Maintenance*.
4. Install with demo data to explore a pre-populated hotel (room types, rooms,
   amenities, rate plans, guests and sample reservations).

## Quick start

1. **Front Desk** → review the dashboard KPIs.
2. **Operations → Check Availability** → pick dates → create a reservation.
3. Open the reservation → **Confirm** → **Check In** (a folio opens and the
   room-night is charged) → **Check Out** (a housekeeping task is created).
4. **Reporting → Reports** → print the Manager Flash or any night-audit report.

## Configuration

- **Configuration → Room Types** — set capacity, default rate, amenities, photo
  and the room-night service product.
- **Configuration → Rate Plans** — add seasonal pricing.
- **Configuration → Settings** — set the city / tourism tax per night.

## Renaming the repository

Renaming the GitHub repository from `gym_management` to e.g. `hotel_management`
is done in GitHub, not in code:

1. Open the repository on GitHub → **Settings**.
2. Under **General → Repository name**, enter `hotel_management` and **Rename**.
3. Update any local clones: `git remote set-url origin <new-url>`.

GitHub automatically redirects the old URL, so existing links keep working.

## License

LGPL-3.
