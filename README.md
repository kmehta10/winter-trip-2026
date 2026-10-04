# winter-trip-2026

A trip site for Dec 27, 2026 – Jan 14, 2027: Chiang Mai (elephants, Doi Suthep, the lantern countdown on New Year's Eve) → Bangkok → Phuket (Phi Phi, James Bond Island) → Mumbai → Jamnagar → home.

Live: https://kmehta10.github.io/winter-trip-2026/

- `src/trip.json` holds all the trip data (flights, stays, hour-by-hour days, photos, bookings, budget) and is the single source.
- `src/template.html` is the page: a D3 flight map with animated arcs, city cards, hour-by-hour Thailand days with photo collages, photo spots, New Year's, food, bookings and the budget.
- `src/photos-*.json` hold the photo sources and credits. Remote photos load from Wikimedia Commons; local ones live in `docs/img/`.
- `python3 build.py` writes `docs/index.html` (GitHub Pages serves `/docs` from `main`) and the budget CSV in the analysis folder.

Planning and price snapshots: `~/Documents/Work/Analysis/2026/09-September/2026-09-28-india-asia-winter-trip/`.
The page has no names, sets `noindex`, and leaves out visa and passport details.
