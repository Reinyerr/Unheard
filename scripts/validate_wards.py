"""T-006: acquire/validate official ward geometry; no backend or UI changes.

Default validates local real snapshots. --refresh obtains the fixed official
sources. Failures remove stale public geometry and write a map-disabled status.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import shapely
from shapely.errors import GEOSException
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.validation import explain_validity

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data/raw/ward_geometry"
PUBLIC = REPO / "frontend/public/data"
ITEM_ID = "f1cad02b3a40422dac2ea99b59cc36a5"
SERVICE = "https://services6.arcgis.com/hM5ymMLbxIyWTjn2/arcgis/rest/services/Ward_Boundaries/FeatureServer"
TERMS = "https://smartcity.mississauga.ca/wp-content/uploads/2021/04/CityofMississauga_TermsofUse.pdf"
URLS = {
    "item.json": f"https://www.arcgis.com/sharing/rest/content/items/{ITEM_ID}?f=pjson",
    "service.json": SERVICE + "?f=pjson",
    "layer.json": SERVICE + "/2?f=pjson",
    "wards.geojson": SERVICE + "/2/query?where=1%3D1&outFields=*&outSR=4326&f=geojson",
    "vintage.json": "https://ext.maps.mississauga.ca/Geocortex/Essentials/REST/sites/eMaps/map/mapservices/57/layers/2?f=json",
}
OUTPUT = PUBLIC / "mississauga_wards.geojson"
STATUS = PUBLIC / "ward_geometry_status.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def encode(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode()


def download(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "UNHEARD-local-geometry/1.0"}), timeout=30) as response:
        raw = response.read(8 * 1024 * 1024 + 1)
    require(len(raw) <= 8 * 1024 * 1024, "Official response exceeds 8 MiB limit")
    return raw


def refresh() -> None:
    snapshot = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "files": {}}
    for name, url in URLS.items():
        raw = download(url)
        value = json.loads(raw)
        require("error" not in value, f"{name}: official endpoint returned an error")
        write(RAW / name, raw)
        snapshot["files"][name] = {"url": url, "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        raw = download(TERMS)
        require(raw.startswith(b"%PDF"), "Linked terms response is not a PDF")
        write(RAW / "license.pdf", raw)
        snapshot["terms_retrieval"] = "downloaded; legal review remains pending"
    except (OSError, ValueError, HTTPError) as exc:
        snapshot["terms_retrieval"] = f"unavailable ({type(exc).__name__}; HTTP {getattr(exc, 'code', 'unknown')}); terms not verified"
    write(RAW / "retrieval.json", encode(snapshot))


def timestamp(milliseconds) -> str | None:
    return datetime.fromtimestamp(milliseconds / 1000, timezone.utc).isoformat() if milliseconds is not None else None


def ward_id(value) -> int:
    require(type(value) in {str, int} and bool(re.fullmatch(r"(?:[1-9]|1[01])", str(value))),
            f"Invalid WARD value: {value!r}")
    return int(value)


def validate_geometry(geometry: dict, identity: int):
    require(geometry.get("type") in {"Polygon", "MultiPolygon"}, f"Ward {identity}: expected Polygon/MultiPolygon")
    coordinates = geometry.get("coordinates")
    require(isinstance(coordinates, list) and bool(coordinates), f"Ward {identity}: missing coordinates")
    polygons = [coordinates] if geometry["type"] == "Polygon" else coordinates
    for polygon in polygons:
        require(isinstance(polygon, list) and bool(polygon), f"Ward {identity}: empty polygon")
        for ring in polygon:
            require(isinstance(ring, list) and len(ring) >= 4 and ring[0] == ring[-1], f"Ward {identity}: unclosed/short ring")
            for point in ring:
                require(isinstance(point, list) and len(point) == 2
                        and all(type(n) in {int, float} and math.isfinite(n) for n in point),
                        f"Ward {identity}: invalid 2D coordinate")
                require(-180 <= point[0] <= 180 and -90 <= point[1] <= 90,
                        f"Ward {identity}: coordinate not WGS84 longitude/latitude")
    polygon = shape(geometry)
    require(not polygon.is_empty and polygon.is_valid and polygon.area > 0,
            f"Ward {identity}: {explain_validity(polygon)}")
    return polygon


def validate() -> dict:
    raw_inputs = {name: (RAW / name).read_bytes() for name in URLS}
    data = {name: json.loads(raw) for name, raw in raw_inputs.items()}
    item, service, layer, geo, vintage = (data[name] for name in URLS)
    require(item.get("id") == ITEM_ID and item.get("owner") == "MississaugaData"
            and item.get("url", "").lower() == SERVICE.lower(), "Official item/publisher/service identity changed")
    require(service.get("serviceItemId") == ITEM_ID, "Service does not reference official item")
    require(any(row.get("id") == 2 and row.get("name") == "Ward Boundaries" for row in service.get("layers", [])),
            "Official ward layer 2 not found")
    require(layer.get("id") == 2 and layer.get("geometryType") == "esriGeometryPolygon"
            and any(field["name"] == "WARD" for field in layer.get("fields", [])), "Layer geometry/ward field changed")
    require(vintage.get("name") == "Municipal Wards (2006-)" and vintage.get("featureLabel") == "Ward {WARD}",
            "Municipal ward-scheme vintage evidence changed; review before use")
    require(geo.get("type") == "FeatureCollection" and not geo.get("exceededTransferLimit"), "Incomplete/non-GeoJSON source")
    require(geo.get("crs") in (None, {"type": "name", "properties": {"name": "EPSG:4326"}}),
            "Unexpected CRS; require the verified ArcGIS outSR=4326 export")
    require(isinstance(geo.get("features"), list) and len(geo["features"]) == 11, "Expected exactly 11 official ward features")
    census_path = PUBLIC / "wards.v1.json"
    census_raw = census_path.read_bytes()
    census = json.loads(census_raw)
    require(census.get("schema_version") == "1.0" and not census.get("is_fixture")
            and census.get("generated_at_utc")
            and census.get("source_file") == "01_people_census/derived/ward_language_profile_2021_corrected.csv",
            "Corrected, generated T-004 census artifact required; fixtures prohibited")
    census_ids = [row["ward_id"] for row in census["wards"]]
    require(all(type(n) is int for n in census_ids) and sorted(census_ids) == list(range(1, 12)), "Census wards must be unique integers 1–11")
    features, polygons, seen = [], [], set()
    for feature in geo["features"]:
        require(feature.get("type") == "Feature", "Invalid GeoJSON feature")
        identity = ward_id(feature["properties"]["WARD"])
        require(identity not in seen, f"Duplicate ward {identity}")
        seen.add(identity)
        polygons.append(validate_geometry(feature["geometry"], identity))
        features.append({"type": "Feature", "id": identity,
                         "properties": {"ward_id": identity, "source_ward": feature["properties"]["WARD"]},
                         "geometry": feature["geometry"]})
    require(seen == set(census_ids), "Polygon IDs do not exactly match corrected census wards")
    overlap_tolerance = 1e-12  # Square degrees, numerical reporting threshold only.
    overlaps = []
    for i, left in enumerate(polygons):
        for j, right in enumerate(polygons[i + 1:], i + 1):
            area = left.intersection(right).area
            if area > overlap_tolerance:
                overlaps.append({"ward_ids": [features[i]["id"], features[j]["id"]],
                                 "intersection_square_degrees": area,
                                 "fraction_of_smaller_polygon": area / min(left.area, right.area)})
    bounds = list(unary_union(polygons).bounds)
    extent = layer["extent"]
    require(extent["spatialReference"].get("latestWkid", extent["spatialReference"].get("wkid")) == 3857,
            "Unexpected source-layer CRS; no inferred reprojection")
    radius = 6378137
    expected_bounds = [math.degrees(extent["xmin"] / radius), math.degrees(math.atan(math.sinh(extent["ymin"] / radius))),
                       math.degrees(extent["xmax"] / radius), math.degrees(math.atan(math.sinh(extent["ymax"] / radius)))]
    require(all(abs(left - right) < 1e-6 for left, right in zip(bounds, expected_bounds)), "Exported geographic bounds disagree with source layer extent")
    retrieval = json.loads((RAW / "retrieval.json").read_bytes())
    for name, raw in raw_inputs.items():
        require(retrieval["files"][name]["url"] == URLS[name]
                and retrieval["files"][name]["sha256"] == hashlib.sha256(raw).hexdigest(),
                f"{name}: snapshot differs from acquisition evidence; refresh from official source")
    source = {
        "publisher": "City of Mississauga / MississaugaData",
        "attribution": "Contains information provided by the City of Mississauga; Ward Boundaries",
        "catalogue_url": "https://data.mississauga.ca/datasets/mississauga::ward-boundaries/about",
        "item_id": ITEM_ID, "layer_url": SERVICE + "/2", "query_url": URLS["wards.geojson"],
        "terms_url": TERMS, "terms_retrieval": retrieval["terms_retrieval"],
        "redistribution_status": "Unverified linked terms; local prototype use only pending T-019 review",
        "retrieved_at_utc": retrieval["retrieved_at_utc"], "item_modified_at_utc": timestamp(item.get("modified")),
        "layer_data_edited_at_utc": timestamp(layer.get("editingInfo", {}).get("dataLastEditDate")),
        "scheme_vintage": "City municipal map labels Municipal Wards (2006-); current official layer snapshot, not a verified immutable 2021 snapshot",
        "vintage_evidence_url": URLS["vintage.json"],
        "input_crs": "EPSG:3857", "output_crs": "OGC:CRS84 / WGS84 longitude,latitude (ArcGIS outSR=4326)",
        "modifications": "Server WGS84 export; verified legacy EPSG:4326 crs member removed for RFC 7946; coordinates/rings preserved without simplification/repair; properties reduced to canonical ward_id and original source_ward; features sorted",
        "source_files_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in raw_inputs.items()},
        "census_artifact_sha256": hashlib.sha256(census_raw).hexdigest(),
        "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shapely_version": shapely.__version__, "geos_version": shapely.geos_version_string,
        "feature_count": len(features), "census_ward_count": len(census_ids),
        "source_overlap_diagnostics": overlaps,
        "limitations": "Individual polygon validity/ID matching does not certify disjoint city coverage, a historical boundary-change audit or geographic speech performance; source overlap diagnostics retained and linked licence unresolved",
    }
    timestamp_utc = datetime.now(timezone.utc).isoformat()
    output = {"type": "FeatureCollection", "schema_version": "1.0", "generated_at_utc": timestamp_utc,
              "source": source, "bbox": bounds, "features": sorted(features, key=lambda feature: feature["id"])}
    raw = encode(output)
    status = {"schema_version": "1.0", "generated_at_utc": timestamp_utc, "status": "validated", "map_ready": True,
              "geometry_file": "mississauga_wards.geojson", "geometry_sha256": hashlib.sha256(raw).hexdigest(),
              "ward_ids": sorted(seen), "source": source,
              "warnings": [source["scheme_vintage"], source["redistribution_status"]]
                          + ([f"Official source has {len(overlaps)} interior-overlap pairs; coordinates retained without repair. See source diagnostics."] if overlaps else [])}
    write(OUTPUT, raw)
    write(STATUS, encode(status))
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Fetch the fixed official source snapshots before validation")
    args = parser.parse_args()
    try:
        if args.refresh:
            refresh()
        status = validate()
        print(f"Validated {len(status['ward_ids'])} real polygons against 11 census wards; map-ready for local use.")
        print("Historical 2021 snapshot and linked redistribution terms remain unverified; see source warnings.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, GEOSException) as exc:
        OUTPUT.unlink(missing_ok=True)
        write(STATUS, encode({"schema_version": "1.0", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                             "status": "failed", "map_ready": False, "geometry_file": None,
                             "message": f"Ward geometry unavailable: {exc}. Use the verified ward chart/table."}))
        print(f"Geometry export blocked: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
