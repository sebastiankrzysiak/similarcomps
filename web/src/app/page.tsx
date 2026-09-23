import SearchBox from "@/components/SearchBox";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-xl text-center">
        <h1 className="text-4xl font-bold text-gray-900">SimilarComps</h1>
        <p className="mt-2 text-gray-600">
          Find homes like yours. See if you're overtaxed.
        </p>
        <SearchBox />
      </div>
    </main>
  );
}