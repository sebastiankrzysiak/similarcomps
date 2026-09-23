import SearchBox from "@/components/SearchBox";

export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">SimilarComps</h1>
      <p className="mt-2 text-gray-600">
        Find homes like yours. See if you're overtaxed.
      </p>
      <SearchBox />
    </main>
  );
}