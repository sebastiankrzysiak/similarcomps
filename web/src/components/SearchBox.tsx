"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SearchBox() {
  const [pin, setPin] = useState("");
  const router = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleanPin = pin.replace(/\D/g, "");
    router.push(`/property/${cleanPin}`);
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 flex gap-2">
      <input
        value={pin}
        onChange={(e) => setPin(e.target.value)}
        placeholder="Enter PIN, e.g. 24-18-411-008-0000"
        className="flex-1 rounded border px-3 py-2"
      />
      <button type="submit" className="rounded bg-black px-4 py-2 text-white">
        Search
      </button>
    </form>
  );
}