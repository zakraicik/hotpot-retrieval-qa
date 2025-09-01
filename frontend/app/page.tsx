import { Brain, Search, ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="text-center mb-16">
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900">HotpotQA</h1>
        </div>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Multi-hop reasoning question-answering system powered by DSPy and
          HotpotQA dataset
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
          <div className="p-3 bg-green-100 rounded-lg w-fit mb-4">
            <Search className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-xl font-semibold mb-3 text-gray-900">
            Multi-hop Retrieval
          </h3>
          <p className="text-gray-600 leading-relaxed">
            Performs iterative information gathering across multiple sources
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
          <div className="p-3 bg-purple-100 rounded-lg w-fit mb-4">
            <Brain className="w-8 h-8 text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold mb-3 text-gray-900">
            Chain-of-Thought
          </h3>
          <p className="text-gray-600 leading-relaxed">
            Uses reasoning steps to synthesize complex answers
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
          <div className="p-3 bg-orange-100 rounded-lg w-fit mb-4">
            <ArrowRight className="w-8 h-8 text-orange-600" />
          </div>
          <h3 className="text-xl font-semibold mb-3 text-gray-900">
            Query Rewriting
          </h3>
          <p className="text-gray-600 leading-relaxed">
            Transforms questions into focused search queries
          </p>
        </div>
      </div>

      {/* Example Questions */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-8 border border-blue-200">
        <h2 className="text-2xl font-semibold mb-6 text-gray-900">
          Try asking questions like:
        </h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-gray-700 font-medium">
              "What nationality is the director of Lagaan?"
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-gray-700 font-medium">
              "What is the capital of the country where Mount Everest is
              located?"
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-gray-700 font-medium">
              "What movie came out first? Titanic or Interstellar?"
            </p>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="mt-12 text-center">
        <div className="inline-flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-full border border-green-200">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium">
            Frontend initialized • Ready for QA interface
          </span>
        </div>
      </div>
    </main>
  );
}
