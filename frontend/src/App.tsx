import React, { useState } from "react";
import { Upload, FileText, Shield, BarChart3, Menu, X } from "lucide-react";
import axios from "axios";

interface AnalysisResult {
  overall_score: number;
  internet_matches: Array<{
    source: string;
    similarity_score: number;
    matched_text: string;
  }>;
  explainability: {
    temporal_scoring: string;
    semantic_analysis: string;
    multimodal_extraction: string;
  };
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>("");
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleFileUpload = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("research_paper", file);

    try {
      const response = await axios.post("/detect-plagiarism", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const Navbar = () => (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Shield className="h-8 w-8 mr-2" />
            <span className="font-bold text-xl">Plagiarism Detector</span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#home" className="hover:text-blue-200 transition-colors">
              Home
            </a>
            <a
              href="#analyze"
              className="hover:text-blue-200 transition-colors"
            >
              Analyze
            </a>
            <a
              href="#results"
              className="hover:text-blue-200 transition-colors"
            >
              Results
            </a>
            <a href="#stats" className="hover:text-blue-200 transition-colors">
              Statistics
            </a>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-white hover:text-blue-200"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-blue-700">
              <a
                href="#home"
                className="block px-3 py-2 hover:bg-blue-800 rounded"
              >
                Home
              </a>
              <a
                href="#analyze"
                className="block px-3 py-2 hover:bg-blue-800 rounded"
              >
                Analyze
              </a>
              <a
                href="#results"
                className="block px-3 py-2 hover:bg-blue-800 rounded"
              >
                Results
              </a>
              <a
                href="#stats"
                className="block px-3 py-2 hover:bg-blue-800 rounded"
              >
                Statistics
              </a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div id="home" className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Advanced Internet Plagiarism Detection
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload your research paper and get comprehensive plagiarism analysis
            with AI-powered semantic understanding and explainable results.
          </p>
        </div>

        {/* Upload Section */}
        <div id="analyze" className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="text-center">
            <Upload className="mx-auto h-12 w-12 text-blue-600 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Upload Your Paper
            </h2>

            <div className="max-w-md mx-auto">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />

              {file && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-blue-600 mr-2" />
                    <span className="text-sm text-blue-700">{file.name}</span>
                  </div>
                </div>
              )}

              <button
                onClick={handleFileUpload}
                disabled={!file || isAnalyzing}
                className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isAnalyzing ? "Analyzing..." : "Analyze Paper"}
              </button>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div id="results" className="space-y-6">
            {/* Overall Score */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-center">
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                  Analysis Results
                </h3>
                <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-blue-100 mb-4">
                  <span className="text-3xl font-bold text-blue-600">
                    {Math.round(result.overall_score * 100)}%
                  </span>
                </div>
                <p className="text-gray-600">
                  {result.overall_score < 0.3
                    ? "Low plagiarism risk"
                    : result.overall_score < 0.7
                      ? "Moderate plagiarism risk"
                      : "High plagiarism risk"}
                </p>
              </div>
            </div>

            {/* Internet Matches */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="h-6 w-6 mr-2" />
                Internet Matches
              </h4>
              <div className="space-y-4">
                {result.internet_matches.map((match, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <a
                        href={match.source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {match.source}
                      </a>
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          match.similarity_score > 0.8
                            ? "bg-red-100 text-red-800"
                            : match.similarity_score > 0.5
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-green-100 text-green-800"
                        }`}
                      >
                        {Math.round(match.similarity_score * 100)}% similar
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm">
                      {match.matched_text}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Explainability */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h4 className="text-xl font-semibold text-gray-900 mb-4">
                Analysis Details
              </h4>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">
                    Temporal Scoring
                  </h5>
                  <p className="text-sm text-gray-600">
                    {result.explainability.temporal_scoring}
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">
                    Semantic Analysis
                  </h5>
                  <p className="text-sm text-gray-600">
                    {result.explainability.semantic_analysis}
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">
                    Multimodal Extraction
                  </h5>
                  <p className="text-sm text-gray-600">
                    {result.explainability.multimodal_extraction}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Section */}
        <div id="stats" className="bg-white rounded-lg shadow-md p-6 mt-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">
            System Statistics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">1,245</div>
              <div className="text-sm text-gray-600">Total Analyses</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">67.3%</div>
              <div className="text-sm text-gray-600">Avg Novelty Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">12.4%</div>
              <div className="text-sm text-gray-600">High Risk Detection</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">99.9%</div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2024 Plagiarism Detector. Advanced AI-powered analysis.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
