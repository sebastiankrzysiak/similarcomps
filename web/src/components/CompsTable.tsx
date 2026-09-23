import { money, moneyCents } from "@/lib/format";
import type { Comp } from "@/lib/types";

type Props = {
  comps: Comp[];
};

export default function CompsTable({ comps }: Props) {
  return (
    <div className="mt-4 overflow-x-auto rounded-xl border bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-gray-50 text-gray-600">
          <tr>
            <th className="px-4 py-3">Address</th>
            <th className="px-4 py-3 text-right">Sq ft</th>
            <th className="px-4 py-3 text-right">Year built</th>
            <th className="px-4 py-3 text-right">Bldg value</th>
            <th className="px-4 py-3 text-right">$/sq ft</th>
            <th className="px-4 py-3 text-right">Market value</th>
            <th className="px-4 py-3 text-right">vs You</th>
          </tr>
        </thead>
        <tbody>
          {comps.map((comp) => (
            <tr key={comp.pin} className="border-t hover:bg-gray-50">
              <td className="px-4 py-3 font-medium">{comp.address}</td>
              <td className="px-4 py-3 text-right">{comp.bldg_sf.toLocaleString()}</td>
              <td className="px-4 py-3 text-right">{comp.year_built}</td>
              <td className="px-4 py-3 text-right">{money(comp.bldg_av)}</td>
              <td className="px-4 py-3 text-right">{moneyCents(comp.bldg_psf)}</td>
              <td className="px-4 py-3 text-right">{money(comp.bldg_market_value)}</td>
              <td className="px-4 py-3 text-right font-medium text-green-600">
                {moneyCents(comp.diff_vs_home)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}