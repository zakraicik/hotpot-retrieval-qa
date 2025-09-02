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
} from "lucide-react";

interface QAResponse {
  question: string;
  answer: string;
  confidence: string;
  reasoning_steps: string;
  queries_used: string[];
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
    "What is the capital of the country where Mount Everest is located?",
    "What movie came out first? Titanic or Interstellar?",
    "Who was the president when the Eiffel Tower was built?",
    "What language is spoken in the birthplace of Tesla?",
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
                    <p className="text-gray-100 font-mono text-sm leading-relaxed">
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

              {/* Combined Reasoning & Query Flow */}
              <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Search className="w-4 h-4 text-gray-400" />
                    <h3 className="text-sm font-mono text-gray-300 uppercase tracking-wider">
                      Multi-Hop Reasoning Pipeline
                    </h3>
                  </div>
                  <div className="text-xs font-mono text-gray-500">
                    {response.num_hops} hops • {response.queries_used.length}{" "}
                    queries • {response.processing_time.toFixed(2)}s
                  </div>
                </div>

                {/* Combined reasoning steps with queries */}
                <div className="space-y-6">
                  {response.reasoning_steps
                    .split(/\d+\.\s+/)
                    .filter((step) => step.trim())
                    .map((step, index) => {
                      const stepText = step.trim();

                      // Better parsing to separate reasoning from source references
                      const parts = stepText.split(/[-–]\s*/);
                      const mainReasoning = parts[0].trim();
                      const sourceReferences = parts.slice(1);

                      // Extract quoted evidence
                      const quotes = stepText.match(/"([^"]*)"/g) || [];

                      // Clean up reasoning text more thoroughly
                      let cleanReasoning = mainReasoning
                        .replace(
                          /from the (first|second|third) paragraph:?/gi,
                          ""
                        )
                        .replace(/from the context:?/gi, "")
                        .replace(
                          /the context (refers to|states that|mentions)/gi,
                          "The retrieved documents $1"
                        )
                        .replace(/\.\s*$/, "") // Remove trailing period and whitespace
                        .replace(/\s+\.$/, "") // Remove period with preceding whitespace
                        .replace(/\s+/g, " ") // Normalize whitespace
                        .trim();

                      // Extract any remaining context clues for better labeling
                      const contextClues = sourceReferences
                        .join(" ")
                        .toLowerCase();
                      const hasContextReference =
                        contextClues.includes("context") ||
                        contextClues.includes("paragraph") ||
                        contextClues.includes("information") ||
                        quotes.length > 0;

                      // Determine the type of operation for better labeling
                      const isSearchStep =
                        cleanReasoning.toLowerCase().includes("identify") ||
                        cleanReasoning.toLowerCase().includes("find") ||
                        cleanReasoning.toLowerCase().includes("determine");

                      // Get the corresponding query for this step
                      const correspondingQuery = response.queries_used[index];

                      return (
                        <div key={index} className="relative">
                          {/* Connection line to next step */}
                          {index <
                            response.reasoning_steps
                              .split(/\d+\.\s+/)
                              .filter((step) => step.trim()).length -
                              1 && (
                            <div className="absolute left-6 top-20 w-px h-16 bg-gradient-to-b from-gray-600 to-transparent" />
                          )}

                          <div className="flex gap-4">
                            {/* Step indicator with hop info */}
                            <div className="flex flex-col items-center">
                              <div className="flex items-center justify-center w-12 h-12 bg-gray-800 border-2 border-gray-600 rounded-full relative">
                                <span className="text-sm font-mono text-gray-300 font-bold">
                                  {(index + 1).toString().padStart(2, "0")}
                                </span>
                                <div className="absolute inset-0 bg-gray-600 rounded-full animate-ping opacity-20" />
                              </div>
                              {/* Hop indicator */}
                              <div className="mt-2 text-xs font-mono text-gray-500 bg-gray-800 px-2 py-1 rounded border border-gray-700">
                                {index === 0 ? "ROOT" : `HOP_${index}`}
                              </div>
                            </div>

                            {/* Combined step content */}
                            <div className="flex-1 space-y-3">
                              {/* Query that triggers this step */}
                              {correspondingQuery && (
                                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
                                  <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                      <Layers className="w-3 h-3 text-gray-400" />
                                      <span className="text-xs font-mono text-gray-400 uppercase">
                                        Query Input
                                      </span>
                                    </div>
                                    <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
                                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                                      <span>EXECUTED</span>
                                    </div>
                                  </div>

                                  {/* Original question for first step */}
                                  {index === 0 && (
                                    <div className="mb-3 pb-3 border-b border-gray-700">
                                      <div className="text-xs font-mono text-gray-500 mb-1 uppercase">
                                        Original Question
                                      </div>
                                      <div className="text-sm font-mono text-gray-300 italic">
                                        "{response.question}"
                                      </div>
                                    </div>
                                  )}

                                  {/* Step objective */}
                                  <div className="mb-3">
                                    <div className="text-xs font-mono text-gray-500 mb-1 uppercase">
                                      Step Objective
                                    </div>
                                    <div className="text-sm font-mono text-gray-300">
                                      {cleanReasoning ||
                                        `Process information for step ${
                                          index + 1
                                        }`}
                                    </div>
                                  </div>

                                  {/* Generated query */}
                                  <div>
                                    <div className="text-xs font-mono text-gray-500 mb-1 uppercase">
                                      Generated Query
                                    </div>
                                    <code className="text-sm font-mono text-gray-200 break-words">
                                      {correspondingQuery}
                                    </code>
                                  </div>
                                </div>
                              )}

                              {/* FAISS Vector Search Indicator */}
                              {hasContextReference && correspondingQuery && (
                                <div className="bg-green-950/30 border border-green-800/50 rounded-lg p-3">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Search className="w-3 h-3 text-green-400" />
                                    <span className="text-xs font-mono text-green-400 uppercase">
                                      FAISS Vector Search
                                    </span>
                                  </div>
                                  <div className="text-xs font-mono text-green-300 space-y-1">
                                    <span>
                                      Embedding similarity search on HotpotQA
                                      dataset
                                    </span>
                                    <br />
                                    <span>
                                      Retrieved {quotes.length} relevant text
                                      segments
                                    </span>
                                  </div>
                                </div>
                              )}

                              {/* Evidence snippets without FAISS labels */}
                              {quotes.length > 0 && (
                                <div className="bg-blue-950/30 border border-blue-800/50 rounded-lg p-3">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Terminal className="w-3 h-3 text-blue-400" />
                                    <span className="text-xs font-mono text-blue-400 uppercase">
                                      Retrieved Evidence
                                    </span>
                                  </div>
                                  {quotes.map((quote, qIndex) => (
                                    <div
                                      key={qIndex}
                                      className="bg-gray-950/60 border-l-2 border-blue-500/50 pl-3 py-2 mb-2 last:mb-0"
                                    >
                                      <code className="text-xs font-mono text-blue-300 block">
                                        {quote.replace(/"/g, "")}
                                      </code>
                                    </div>
                                  ))}
                                </div>
                              )}

                              {/* Step result - shows what was determined */}
                              <div className="bg-gray-950/50 border border-gray-800 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <CheckCircle className="w-3 h-3 text-green-500" />
                                  <span className="text-xs font-mono text-green-400 uppercase">
                                    Step Result
                                  </span>
                                </div>
                                <p className="text-sm font-mono text-gray-300 leading-relaxed">
                                  {/* Extract the key finding from evidence or use a generic result */}
                                  {quotes.length > 0 && quotes[0]
                                    ? // If we have evidence, show the key fact extracted
                                      quotes[0]
                                        .replace(/"/g, "")
                                        .split(".")[0] +
                                      (quotes[0].includes(".") ? "." : "")
                                    : cleanReasoning
                                    ? // If no evidence but we have reasoning, show that
                                      cleanReasoning
                                    : // Fallback
                                      `Information gathered for step ${
                                        index + 1
                                      }`}
                                </p>
                              </div>

                              {/* Flow indicator to next hop */}
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
                      );
                    })}
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
