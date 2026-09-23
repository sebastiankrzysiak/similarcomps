import { notFound } from "next/navigation";
import { moneyCents } from "@/lib/format";
import type { CompsResponse } from "@/lib/types";
import HomeCard from "@/components/HomeCard";
import CompsTable from "@/components/CompsTable";
import CompsMap from "@/components/CompsMapClient";

type Props = {
  params: Promise<{ pin: string }>;
};

export default async function PropertyPage({ params }: Props) {
  const { pin } = await params;
  const API_URL = process.env.API_URL ?? "http://localhost:8000";

  const res = await fetch(`${API_URL}/property/${pin}/comps`, {
    cache: "no-store",
  });

  if (!res.ok) {
    notFound();
  }

  const data: CompsResponse = await res.json();

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="mx-auto max-w-5xl p-8 text-gray-900">
        <HomeCard home={data.home} />
        <CompsMap home={data.home} comps={data.comps} />

        <p className="mt-8 text-lg">
          <span className="font-semibold text-green-600">{data.count}</span> of{" "}
          {data.total_comps} similar homes are assessed lower than yours. Median:{" "}
          <span className="font-semibold">{moneyCents(data.median_psf)}</span>/sq ft
        </p>

        <CompsTable comps={data.comps} />
      </main>
    </div>
  );
}