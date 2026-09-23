import Link from "next/link";

export default function NotFound() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold">Property not found</h1>
      <p className="mt-2 text-gray-600">Check the PIN and try again.</p>
      <Link href="/" className="mt-4 inline-block underline">
        Back to search
      </Link>
    </main>
  );
}