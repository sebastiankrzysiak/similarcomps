"use client";

import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from "react-leaflet";
import type { Home, Comp } from "@/lib/types";
import { moneyCents } from "@/lib/format";

type Props = {
  home: Home;
  comps: Comp[];
};

export default function CompsMap({ home, comps }: Props) {
  return (
    <MapContainer
      center={[home.lat, home.lon]}
      zoom={15}
      className="mt-8 h-96 w-full rounded-xl"
    >
      <TileLayer
        url={`https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=${process.env.NEXT_PUBLIC_STADIA_KEY}`}
        attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />

      <CircleMarker
        center={[home.lat, home.lon]}
        radius={12}
        pathOptions={{ color: "#D85A30", fillOpacity: 0.9 }}
      >
        <Popup>
          <b>Your home</b>
          <br />
          {home.address}
          <br />
          {moneyCents(home.bldg_psf)}/sq ft
        </Popup>
      </CircleMarker>

      {comps
        .filter((comp) => comp.lat && comp.lon)
        .map((comp, i) => (
          <CircleMarker
            key={comp.pin}
            center={[comp.lat, comp.lon]}
            radius={10}
            pathOptions={{ color: "#1D9E75", fillOpacity: 0.9 }}
          >
            <Tooltip permanent direction="center" className="comp-label">
              {i + 1}
            </Tooltip>
            <Popup>
              <b>{comp.address}</b>
              <br />
              {comp.bldg_sf.toLocaleString()} sq ft
              <br />
              {moneyCents(comp.bldg_psf)}/sq ft ({moneyCents(comp.diff_vs_home)} vs you)
            </Popup>
          </CircleMarker>
        ))}
    </MapContainer>
  );
}