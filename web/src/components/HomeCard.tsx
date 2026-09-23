import { money, moneyCents } from "@/lib/format";
import type { Home } from "@/lib/types";

type Props = {
  home: Home;
};

export default function HomeCard({ home }: Props) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <p className="text-sm text-gray-500">Your home</p>
      <h1 className="text-2xl font-bold">{home.address}</h1>
      <p className="text-gray-600">{home.city}</p>

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Building sq ft" value={home.bldg_sf.toLocaleString()} />
        <Stat label="Assessed value" value={money(home.bldg_av)} />
        <Stat label="$ per sq ft" value={moneyCents(home.bldg_psf)} />
        <Stat label="Market value" value={money(home.bldg_market_value)} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-gray-50 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  );
}