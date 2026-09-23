import asyncio
import os
import statistics

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SimilarComps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PARCEL_URL = "https://datacatalog.cookcountyil.gov/resource/nj4t-kc8j.json"
CHARS_URL = "https://datacatalog.cookcountyil.gov/resource/x54s-btds.json"
VALUES_URL = "https://datacatalog.cookcountyil.gov/resource/uzyt-m557.json"
ADDRESS_URL = "https://datacatalog.cookcountyil.gov/resource/3723-97qp.json"

APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN")
HEADERS = {"X-App-Token": APP_TOKEN} if APP_TOKEN else {}


# ---------- helpers ----------

def clean_pin(pin: str) -> str:
    pin = pin.replace("-", "").strip()
    if not (pin.isdigit() and len(pin) == 14):
        raise HTTPException(400, "PIN must be 14 digits")
    return pin


async def fetch_one(client: httpx.AsyncClient, url: str, params: dict) -> dict:
    r = await client.get(url, params=params, headers=HEADERS)
    if r.status_code != 200:
        raise HTTPException(502, f"County API error: {r.text}")
    rows = r.json()
    if not rows:
        raise HTTPException(404, "PIN not found")
    return rows[0]


async def fetch_many(client: httpx.AsyncClient, url: str, params: dict) -> list:
    r = await client.get(url, params=params, headers=HEADERS)
    if r.status_code != 200:
        raise HTTPException(502, f"County API error: {r.text}")
    return r.json()


def to_float(value):
    return float(value) if value not in (None, "") else None


# ---------- county calls ----------

async def get_parcel(client, pin):
    return await fetch_one(client, PARCEL_URL, {
        "pin": pin,
        "$select": "pin,nbhd_code,class,township_code,lat,lon,year",
        "$order": "year DESC",
        "$limit": 1,
    })


async def get_characteristics(client, pin):
    return await fetch_one(client, CHARS_URL, {
        "pin": pin,
        "$select": "pin,year,char_bldg_sf,char_yrblt,pin_is_multicard",
        "$order": "year DESC",
        "$limit": 1,
    })


async def get_values(client, pin):
    return await fetch_one(client, VALUES_URL, {
        "pin": pin,
        "$select": "pin,year,class,nbhd,mailed_bldg,mailed_land,mailed_tot",
        "$order": "year DESC",
        "$limit": 1,
    })


async def get_neighbor_characteristics(client, township, class_, year):
    return await fetch_many(client, CHARS_URL, {
        "$select": "pin,char_bldg_sf,char_yrblt,pin_is_multicard,tieback_proration_rate",
        "$where": f"township_code='{township}' AND class='{class_}' AND year={year}",
        "$limit": 50000,
    })


async def get_neighbor_values(client, nbhd, class_, year):
    return await fetch_many(client, VALUES_URL, {
        "$select": "pin,mailed_bldg,mailed_land,mailed_tot",
        "$where": f"nbhd='{nbhd}' AND class='{class_}' AND year={year}",
        "$limit": 5000,
    })


async def get_addresses(client, pins):
    if not pins:
        return []
    pin_list = ",".join(f"'{p}'" for p in pins)
    return await fetch_many(client, ADDRESS_URL, {
        "$select": "pin,year,prop_address_full,prop_address_city_name,prop_address_zipcode_1",
        "$where": f"pin in({pin_list})",
        "$order": "year DESC",
        "$limit": 5000,
    })


async def get_locations(client, pins):
    if not pins:
        return []
    pin_list = ",".join(f"'{p}'" for p in pins)
    return await fetch_many(client, PARCEL_URL, {
        "$select": "pin,year,lat,lon",
        "$where": f"pin in({pin_list})",
        "$order": "year DESC",
        "$limit": 5000,
    })


# ---------- home loader ----------

async def load_home(client, pin):
    parcel, chars, values = await asyncio.gather(
        get_parcel(client, pin),
        get_characteristics(client, pin),
        get_values(client, pin),
    )

    bldg_sf = to_float(chars.get("char_bldg_sf"))
    bldg_av = to_float(values.get("mailed_bldg"))
    bldg_psf = round(bldg_av / bldg_sf, 2) if bldg_sf and bldg_av else None

    return {
        "pin": pin,
        "nbhd_code": parcel.get("nbhd_code"),
        "class": parcel.get("class"),
        "township_code": parcel.get("township_code"),
        "lat": to_float(parcel.get("lat")),
        "lon": to_float(parcel.get("lon")),
        "bldg_sf": bldg_sf,
        "year_built": to_float(chars.get("char_yrblt")),
        "is_multicard": chars.get("pin_is_multicard"),
        "values_year": values.get("year"),
        "bldg_av": bldg_av,
        "land_av": to_float(values.get("mailed_land")),
        "total_av": to_float(values.get("mailed_tot")),
        "bldg_psf": bldg_psf,
        "market_psf": round(bldg_psf * 10, 2) if bldg_psf else None,
        "bldg_market_value": bldg_av * 10 if bldg_av else None,
    }


# ---------- comp logic ----------

def build_comps(home, chars, values):
    comps = []
    pin_to_char = {}

    for char in chars:
        pin = char["pin"]
        pin_to_char[pin] = {
            "char_bldg_sf": char.get("char_bldg_sf"),
            "char_yrblt": char.get("char_yrblt"),
            "pin_is_multicard": char.get("pin_is_multicard"),
            "tieback_proration_rate": char.get("tieback_proration_rate"),
        }

    for value in values:
        pin = value["pin"]

        if pin == home["pin"]:
            continue
        if pin not in pin_to_char:
            continue

        char = pin_to_char[pin]

        if char["pin_is_multicard"] in (True, "true"):
            continue

        proration = to_float(char.get("tieback_proration_rate"))
        if proration is not None and proration < 1:
            continue

        bldg_sf = to_float(char.get("char_bldg_sf"))
        bldg_av = to_float(value.get("mailed_bldg"))

        if not bldg_sf or not bldg_av:
            continue

        year_built = to_float(char.get("char_yrblt"))
        if home["year_built"] and year_built and abs(year_built - home["year_built"]) > 20:
             continue

        bldg_psf = round(bldg_av / bldg_sf, 2)

        comps.append({
            "pin": pin,
            "bldg_sf": bldg_sf,
            "year_built": year_built,
            "bldg_av": bldg_av,
            "land_av": to_float(value.get("mailed_land")),
            "total_av": to_float(value.get("mailed_tot")),
            "bldg_psf": bldg_psf,
            "market_psf": round(bldg_psf * 10, 2),
            "bldg_market_value": bldg_av * 10,
            "diff_vs_home": round(bldg_psf - home["bldg_psf"], 2) if home["bldg_psf"] else None,
        })

    comps.sort(key=lambda c: c["bldg_psf"])

    psfs = [c["bldg_psf"] for c in comps]
    median_psf = round(statistics.median(psfs), 2) if psfs else None

    lower_comps = [c for c in comps if c["diff_vs_home"] is not None and c["diff_vs_home"] < 0]

    return {
        "comps": lower_comps,
        "count": len(lower_comps),
        "total_comps": len(comps),
        "median_psf": median_psf,
    }


def attach_addresses(items, address_rows):
    pin_to_addr = {}
    for row in address_rows:
        pin = row["pin"]
        if pin not in pin_to_addr:
            pin_to_addr[pin] = row

    for item in items:
        addr = pin_to_addr.get(item["pin"], {})
        item["address"] = addr.get("prop_address_full")
        item["city"] = addr.get("prop_address_city_name")
        item["zip"] = addr.get("prop_address_zipcode_1")


def attach_locations(items, location_rows):
    pin_to_loc = {}
    for row in location_rows:
        pin = row["pin"]
        if pin not in pin_to_loc:
            pin_to_loc[pin] = row

    for item in items:
        loc = pin_to_loc.get(item["pin"], {})
        item["lat"] = to_float(loc.get("lat"))
        item["lon"] = to_float(loc.get("lon"))


# ---------- endpoints ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/property/{pin}")
async def get_property(pin: str):
    pin = clean_pin(pin)
    async with httpx.AsyncClient(timeout=10) as client:
        home = await load_home(client, pin)
        address_rows = await get_addresses(client, [pin])
    attach_addresses([home], address_rows)
    return home


@app.get("/property/{pin}/comps")
async def get_comps(pin: str):
    pin = clean_pin(pin)
    async with httpx.AsyncClient(timeout=30) as client:
        home = await load_home(client, pin)
        township = home["township_code"]
        class_ = home["class"]
        nbhd = home["nbhd_code"]
        year = int(float(home["values_year"]))

        chars, values = await asyncio.gather(
            get_neighbor_characteristics(client, township, class_, year),
            get_neighbor_values(client, nbhd, class_, year),
        )

        result = build_comps(home, chars, values)

        comp_pins = [c["pin"] for c in result["comps"]]
        address_rows, location_rows = await asyncio.gather(
            get_addresses(client, [home["pin"]] + comp_pins),
            get_locations(client, comp_pins),
        )

    attach_addresses([home] + result["comps"], address_rows)
    attach_locations(result["comps"], location_rows)

    return {"home": home, **result}