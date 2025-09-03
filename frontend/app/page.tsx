"use client";

import { useState } from "react";
import {
  Brain,
  Search,
  ArrowRight,
  Loader2,
  Clock,
  Layers,
  CheckCircle,
  Terminal,
  Code2,
  Zap,
  FileText,
  Target,
} from "lucide-react";

interface QAResponse {
  question: string;
  answer: string;
  confidence: string;
  reasoning_summary: string;
  queries_used: string[];
  query_objectives: string[];
  evidence_summaries: string[];
  hop_conclusions: string[];
  num_hops: number;
  processing_time: number;
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QAResponse | null>(null);
  const [error, setError] = useState("");

  const exampleQuestions = [
    "What nationality is the director of Lagaan?",
    "In which American football game was Malcolm Smith named Most Valuable player?",
    "What movie came out first? Titanic or Interstellar?",
    "Who was the president of the United States when the Eiffel Tower was built?",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setError("");
    setResponse(null);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          max_hops: 3,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: QAResponse = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Grid overlay for techy feel */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_60%,transparent_100%)]" />

      <main className="relative container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative p-3 bg-gray-900 border border-gray-800 rounded-xl">
              <div className="absolute inset-0 bg-gradient-to-r from-gray-600/20 to-gray-400/20 rounded-xl" />
              <Brain className="relative w-8 h-8 text-gray-300" />
            </div>
            <h1 className="text-5xl font-mono font-bold text-gray-100 tracking-tight">
              HotpotQA
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto font-mono">
            Multi-hop reasoning system • DSPy + HotpotQA dataset
          </p>
          <div className="mt-6 flex items-center justify-center gap-2 text-xs font-mono text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>SYSTEM ONLINE</span>
            <span className="text-gray-600">•</span>
            <span>v1.0.0</span>
          </div>
        </div>

        {/* Main Interface */}
        <div className="max-w-4xl mx-auto">
          {/* Question Input */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-xl p-6 mb-8 shadow-2xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Terminal className="w-4 h-4 text-gray-400" />
                  <label
                    htmlFor="question"
                    className="text-sm font-mono text-gray-300 uppercase tracking-wider"
                  >
                    Query Input
                  </label>
                </div>
                <div className="relative">
                  <textarea
                    id="question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter multi-hop reasoning query..."
                    className="w-full p-4 bg-gray-950/80 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 font-mono text-sm focus:border-gray-500 focus:ring-1 focus:ring-gray-500 focus:outline-none transition-all duration-200 resize-none"
                    rows={3}
                    disabled={isLoading}
                  />
                  <div className="absolute right-3 top-3 flex items-center gap-2">
                    <Search className="w-4 h-4 text-gray-500" />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={!question.trim() || isLoading}
                className="w-full bg-gray-800 hover:bg-gray-700 disabled:bg-gray-900 disabled:cursor-not-allowed text-gray-100 font-mono text-sm uppercase tracking-wider py-4 px-6 rounded-lg border border-gray-700 hover:border-gray-600 transition-all duration-200 disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center gap-3">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                    <div className="flex gap-1">
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse" />
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-100" />
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-200" />
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-3">
                    <Zap className="w-4 h-4" />
                    <span>Execute Query</span>
                  </div>
                )}
              </button>
            </form>
          </div>

          {/* Example Questions */}
          {!response && !isLoading && (
            <div className="bg-gray-900/30 backdrop-blur border border-gray-800 rounded-xl p-6 mb-8">
              <div className="flex items-center gap-2 mb-4">
                <Code2 className="w-4 h-4 text-gray-400" />
                <h3 className="text-sm font-mono text-gray-300 uppercase tracking-wider">
                  Sample Queries
                </h3>
              </div>
              <div className="space-y-2">
                {exampleQuestions.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(example)}
                    className="w-full text-left p-3 bg-gray-950/50 hover:bg-gray-800/50 border border-gray-800 hover:border-gray-700 rounded-lg transition-all duration-200 group"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xs font-mono text-gray-500 mt-1 min-w-[20px]">
                        {(index + 1).toString().padStart(2, "0")}
                      </span>
                      <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-gray-400 mt-0.5 group-hover:translate-x-1 transition-all duration-200" />
                      <span className="text-sm font-mono text-gray-400 group-hover:text-gray-200">
                        {example}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-950/50 border border-red-800 rounded-xl p-4 mb-8">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-red-400 font-mono text-sm">
                  ERROR: {error}
                </span>
              </div>
            </div>
          )}

          {/* Response Display */}
          {response && (
            <div className="space-y-6">
              {/* Answer Card */}
              <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6 shadow-2xl">
                <div className="flex items-start gap-4 mb-6">
                  <div className="p-2 bg-green-950/50 border border-green-800 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-sm font-mono text-gray-300 uppercase tracking-wider">
                        Output
                      </h3>
                    </div>
                    <p className="text-xl text-gray-100 font-mono leading-relaxed">
                      {response.answer}
                    </p>
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 border-t border-gray-800">
                  <div className="flex items-center gap-3">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-xs font-mono text-gray-500 uppercase">
                        Latency
                      </p>
                      <p className="text-lg font-mono text-gray-200">
                        {response.processing_time.toFixed(2)}s
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Layers className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-xs font-mono text-gray-500 uppercase">
                        Hops
                      </p>
                      <p className="text-lg font-mono text-gray-200">
                        {response.num_hops}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Brain className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-xs font-mono text-gray-500 uppercase">
                        Confidence
                      </p>
                      <p className="text-lg font-mono text-gray-200">
                        {response.confidence}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Reasoning Summary */}
              <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="w-4 h-4 text-gray-400" />
                  <h3 className="text-sm font-mono text-gray-300 uppercase tracking-wider">
                    Reasoning Summary
                  </h3>
                </div>
                <div className="bg-gray-950/50 border border-gray-700 rounded-lg p-4">
                  <p className="text-sm font-mono text-gray-300 leading-relaxed whitespace-pre-line">
                    {response.reasoning_summary ||
                      "No reasoning summary available"}
                  </p>
                </div>
              </div>

              {/* Multi-Hop Process Visualization */}
              <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Search className="w-4 h-4 text-gray-400" />
                    <h3 className="text-sm font-mono text-gray-300 uppercase tracking-wider">
                      Multi-Hop Process
                    </h3>
                  </div>
                  <div className="text-xs font-mono text-gray-500">
                    {response.num_hops} hops • {response.queries_used.length}{" "}
                    queries
                  </div>
                </div>

                <div className="space-y-8">
                  {response.queries_used.map((query, index) => (
                    <div key={index} className="relative">
                      {/* Connection line to next hop */}
                      {index < response.queries_used.length - 1 && (
                        <div className="absolute left-6 top-20 w-px h-16 bg-gradient-to-b from-gray-600 to-transparent" />
                      )}

                      <div className="flex gap-4">
                        {/* Hop indicator */}
                        <div className="flex flex-col items-center">
                          <div className="flex items-center justify-center w-12 h-12 bg-gray-800 border-2 border-gray-600 rounded-full relative">
                            <span className="text-sm font-mono text-gray-300 font-bold">
                              {(index + 1).toString().padStart(2, "0")}
                            </span>
                            <div className="absolute inset-0 bg-gray-600 rounded-full animate-ping opacity-20" />
                          </div>
                          <div className="mt-2 text-xs font-mono text-gray-500 bg-gray-800 px-2 py-1 rounded border border-gray-700">
                            HOP_{index + 1}
                          </div>
                        </div>

                        {/* Hop content */}
                        <div className="flex-1 space-y-4">
                          {/* Query objective */}
                          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <Target className="w-4 h-4 text-blue-400" />
                              <span className="text-xs font-mono text-blue-400 uppercase">
                                Objective
                              </span>
                            </div>
                            <p className="text-sm font-mono text-gray-300">
                              {(response.query_objectives &&
                                response.query_objectives[index]) ||
                                "Processing information"}
                            </p>
                          </div>

                          {/* Generated query */}
                          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <Search className="w-4 h-4 text-green-400" />
                              <span className="text-xs font-mono text-green-400 uppercase">
                                Vector Search Query
                              </span>
                            </div>
                            <code className="text-sm font-mono text-gray-200 bg-gray-950/80 px-3 py-2 rounded border border-gray-700 block">
                              {query}
                            </code>
                          </div>

                          {/* Evidence summary */}
                          {response.evidence_summaries &&
                            response.evidence_summaries[index] && (
                              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-3">
                                  <FileText className="w-4 h-4 text-yellow-400" />
                                  <span className="text-xs font-mono text-yellow-400 uppercase">
                                    Evidence Summary
                                  </span>
                                </div>
                                <p className="text-sm font-mono text-gray-300 leading-relaxed">
                                  {response.evidence_summaries[index]}
                                </p>
                              </div>
                            )}

                          {/* Hop conclusion */}
                          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <CheckCircle className="w-4 h-4 text-purple-400" />
                              <span className="text-xs font-mono text-purple-400 uppercase">
                                Hop Conclusion
                              </span>
                            </div>
                            <p className="text-sm font-mono text-gray-300">
                              {(response.hop_conclusions &&
                                response.hop_conclusions[index]) ||
                                "No conclusion recorded for this hop"}
                            </p>
                          </div>

                          {/* Flow to next hop */}
                          {index < response.queries_used.length - 1 && (
                            <div className="flex items-center justify-center py-2">
                              <div className="flex items-center gap-2 text-xs font-mono text-gray-600 bg-gray-800/50 px-3 py-1 rounded-full border border-gray-700">
                                <span>TRIGGERS NEXT HOP</span>
                                <ArrowRight className="w-3 h-3" />
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pipeline summary */}
                <div className="mt-8 pt-6 border-t border-gray-800">
                  <div className="bg-gray-950/60 border border-gray-700 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Layers className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-mono text-gray-400 uppercase">
                        Pipeline Summary
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono text-gray-500">
                      <div>
                        <span className="text-gray-400">Total Queries:</span>{" "}
                        {response.queries_used.length}
                      </div>
                      <div>
                        <span className="text-gray-400">Reasoning Hops:</span>{" "}
                        {response.num_hops}
                      </div>
                      <div>
                        <span className="text-gray-400">Processing Time:</span>{" "}
                        {response.processing_time.toFixed(2)}s
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Reset Button */}
              <div className="text-center pt-6">
                <button
                  onClick={() => {
                    setResponse(null);
                    setQuestion("");
                    setError("");
                  }}
                  className="bg-gray-800 hover:bg-gray-700 text-gray-200 font-mono text-sm uppercase tracking-wider py-3 px-6 rounded-lg border border-gray-700 hover:border-gray-600 transition-all duration-200"
                >
                  Reset Terminal
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Feature Cards - Only show when no response */}
        {!response && !isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-6xl mx-auto">
            <div className="bg-gray-900/30 border border-gray-800 p-6 rounded-xl hover:bg-gray-900/50 hover:border-gray-700 transition-all duration-300 group">
              <div className="p-3 bg-gray-950/80 border border-gray-700 rounded-lg w-fit mb-4 group-hover:border-gray-600 transition-colors">
                <Search className="w-6 h-6 text-gray-400" />
              </div>
              <h3 className="text-lg font-mono text-gray-200 mb-3 tracking-tight">
                Multi-hop Retrieval
              </h3>
              <p className="text-gray-500 text-sm font-mono leading-relaxed">
                Iterative information gathering across multiple knowledge
                sources with dynamic query refinement.
              </p>
            </div>

            <div className="bg-gray-900/30 border border-gray-800 p-6 rounded-xl hover:bg-gray-900/50 hover:border-gray-700 transition-all duration-300 group">
              <div className="p-3 bg-gray-950/80 border border-gray-700 rounded-lg w-fit mb-4 group-hover:border-gray-600 transition-colors">
                <Brain className="w-6 h-6 text-gray-400" />
              </div>
              <h3 className="text-lg font-mono text-gray-200 mb-3 tracking-tight">
                Chain-of-Thought
              </h3>
              <p className="text-gray-500 text-sm font-mono leading-relaxed">
                Step-by-step reasoning synthesis with transparent logical
                progression and evidence tracking.
              </p>
            </div>

            <div className="bg-gray-900/30 border border-gray-800 p-6 rounded-xl hover:bg-gray-900/50 hover:border-gray-700 transition-all duration-300 group">
              <div className="p-3 bg-gray-950/80 border border-gray-700 rounded-lg w-fit mb-4 group-hover:border-gray-600 transition-colors">
                <ArrowRight className="w-6 h-6 text-gray-400" />
              </div>
              <h3 className="text-lg font-mono text-gray-200 mb-3 tracking-tight">
                Query Rewriting
              </h3>
              <p className="text-gray-500 text-sm font-mono leading-relaxed">
                Intelligent question decomposition into optimized search queries
                with context preservation.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
