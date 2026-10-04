"""Build the trip site.

Reads  src/trip.json, src/photos-local.json, src/photos-remote.json, src/template.html
Writes docs/index.html (GitHub Pages serves /docs), docs/.nojekyll
Also writes the matching budget CSV into the analysis folder.

Run:  python3 build.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANALYSIS = Path.home() / "Documents/Work/Analysis/2026/09-September/2026-09-28-india-asia-winter-trip"
TRIP = json.loads((ROOT / "src/trip.json").read_text())

ALT = {
    "lanterns": "Sky lanterns rising over Chiang Mai at night",
    "lanterns2": "Hundreds of lanterns released at once near Chiang Mai",
    "elephant": "An Asian elephant at Elephant Nature Park",
    "naiharn": "Nai Harn Beach, Phuket",
    "promthep": "Sunset at Promthep Cape, Phuket",
    "phangnga": "Ko Tapu, the James Bond island, in Phang Nga Bay",
    "chatuchak": "Stalls at Chatuchak Weekend Market",
    "river": "The Chao Phraya river at night, seen from ICONSIAM",
    "skyline": "The Bangkok skyline from Mahanakhon Tower",
    "hero-wat-arun": "Wat Arun from the Chao Phraya river near sunset",
    "doi-suthep": "The golden chedi at Wat Phra That Doi Suthep",
    "gateway": "The Gateway of India, Mumbai",
    "lakhota": "Lakhota Lake in Jamnagar at golden hour",
    "mayabay": "Maya Bay on Ko Phi Phi Leh, turquoise water under limestone cliffs",
    "chediluang": "The great ruined chedi of Wat Chedi Luang, Chiang Mai",
    "bigbuddha": "The Big Buddha on its hilltop in Phuket",
    "oldtown": "Colourful shophouses on Thalang Road, Old Phuket Town",
    "grand-palace": "Gilded spires at Wat Phra Kaew in the Grand Palace",
    "railway": "A train passing through Maeklong Railway Market",
    "floating": "Boats loaded with bananas at Damnoen Saduak floating market",
    "maekampong": "Wooden houses along the lane in Mae Kampong village",
    "talatnoi": "A street-art mural in Talat Noi, Bangkok",
    "warorot": "Stalls inside Warorot Market, Chiang Mai",
    "nightbazaar": "Stalls at the Chiang Mai Night Bazaar",
    "thaphae": "Tha Phae Gate in Chiang Mai's old city wall",
    "babyelephants": "A mother elephant and her baby at Elephant Nature Park",
    "enp": "An elephant grazing at Elephant Nature Park",
    "flowers": "A man weaving marigold garlands at Warorot Market",
    "doiview": "Chiang Mai seen from Doi Suthep",
    "watpho": "The golden reclining Buddha at Wat Pho",
    "yaowarat": "Neon signs over Yaowarat Road, Chinatown, at night",
    "pileh": "A longtail boat in the turquoise water of Pileh Lagoon",
    "hong": "Two people kayaking at Ko Hong in Phang Nga Bay",
    "panyee": "Koh Panyee, a village on stilts under a limestone cliff",
    "marinedrive": "Sunset over the sea from Marine Drive, Mumbai",
    "csmt": "Chhatrapati Shivaji Terminus, Mumbai's Victorian railway station",
    "juhu": "Juhu Beach, Mumbai",
    "dwarka": "Dwarkadhish Temple in Dwarka",
}
USED = ({c["photo"] for c in TRIP["chapters"]} | {p[0] for p in TRIP.get("photospots", [])} | {"lanterns", "lanterns2"}
        | {p[0] for h in TRIP.get("hourly", []) for p in h.get("photos", [])} | {p[0] for c in TRIP["chapters"] for p in c.get("strip", [])})


def photos():
    out = {}
    for p in json.loads((ROOT / "src/photos-remote.json").read_text()):
        out[p["key"]] = {"src": p["src"], "title": p["title"], "author": p["author"], "license": p["license"], "page": p["page"]}
    for p in json.loads((ROOT / "src/photos-local.json").read_text()):
        out[p["key"]] = {"src": f"img/{p['key']}.jpg", "title": p["title"], "author": p["author"], "license": p["license"], "page": p["page"]}
    for k, v in out.items():
        v["alt"] = ALT.get(k, "")
    return {k: v for k, v in out.items() if k in USED}


def budget():
    pax = {"both": 2, "her": 1, "him": 1}
    rows = []
    for f in TRIP["flights"]:
        rows.append(("Flights", f'{f["date"]} {f["from"]}→{f["to"]} {f["airline"]} {f["times"]}', f["price"] * pax[f["who"]]))
    hsub = 0
    for c in TRIP["chapters"]:
        s = c.get("stay")
        if s and s.get("price"):
            amt = s["price"] * c["nights"]
            hsub += amt
            rows.append(("Hotels", f'{c["city"]} {c["dates"]}: {s["name"]} ({c["nights"]} × ${s["price"]})', amt))
    rows.append(("Hotels", f'Taxes and fees ({int(TRIP["meta"]["hotelTax"]*100)}%)', round(hsub * TRIP["meta"]["hotelTax"])))
    for e in TRIP["experiences"]:
        if e["in"]:
            rows.append(("Experiences", f'{e["when"]}: {e["name"]} (2 × ${e["pp"]})', e["pp"] * 2))
    for x in TRIP["fixed"]:
        rows.append(("Food, rides, fees", x["label"], x["amt"]))
    return rows


def main():
    tpl = (ROOT / "src/template.html").read_text()
    html = tpl.replace("/*__TRIP__*/", json.dumps(TRIP, ensure_ascii=False)).replace("/*__PHOTOS__*/", json.dumps(photos(), ensure_ascii=False))
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/index.html").write_text(html)
    (ROOT / "docs/.nojekyll").write_text("")
    rows = budget()
    cats = {}
    for c, _i, a in rows:
        cats[c] = cats.get(c, 0) + a
    total = sum(cats.values())
    for c, a in cats.items():
        print(f"  {c:<20} ${a:>6,}")
    print(f"  {'TOTAL':<20} ${total:>6,}  (${total/2:,.0f} each; ${total - TRIP['meta']['cap']:+,} vs ${TRIP['meta']['cap']:,})")
    if ANALYSIS.exists():
        with (ANALYSIS / "output/budget-v12.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["category", "item", "usd_for_two"])
            w.writerows(rows)
        print("wrote analysis output/budget-v12.csv")
    print("wrote docs/index.html")


if __name__ == "__main__":
    main()
