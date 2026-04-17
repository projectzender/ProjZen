"use client";

import { useState, useRef } from "react";
import RoadmapDisplay from "./components/RoadmapDisplay";

const GRADE_LEVELS = [
  { value: "Middle School (6th-8th grade)", label: "Middle School (6th–8th grade)" },
  { value: "High School Freshman (9th grade)", label: "High School Freshman (9th grade)" },
  { value: "High School Sophomore (10th grade)", label: "High School Sophomore (10th grade)" },
  { value: "High School Junior (11th grade)", label: "High School Junior (11th grade)" },
  { value: "High School Senior (12th grade)", label: "High School Senior (12th grade)" },
  { value: "College Freshman", label: "College Freshman" },
  { value: "College Sophomore", label: "College Sophomore" },
  { value: "College Junior", label: "College Junior" },
  { value: "College Senior", label: "College Senior" },
  { value: "Recent Graduate", label: "Recent Graduate" },
  { value: "Career Changer / Adult Learner", label: "Career Changer / Adult Learner" },
];

const CAREER_SUGGESTIONS = [
  "Software Engineer", "Doctor / Physician", "Lawyer / Attorney",
  "Data Scientist", "Nurse", "Mechanical Engineer", "Architect",
  "Psychologist", "Marine Biologist", "Aerospace Engineer",
  "Game Developer", "Financial Analyst", "Pharmacist", "Teacher / Professor",
  "Graphic Designer", "Veterinarian", "Journalist", "Chef / Culinary Arts",
  "Civil Engineer", "Neuroscientist", "Pilot", "Dentist", "Social Worker",
  "Environmental Scientist", "Entrepreneur / Startup Founder",
];

export default function Home() {
  const [gradeLevel, setGradeLevel] = useState("");
  const [dreamCareer, setDreamCareer] = useState("");
  const [gpa, setGpa] = useState("");
  const [location, setLocation] = useState("");
  const [interests, setInterests] = useState("");
  const [concerns, setConcerns] = useState("");
  const [roadmap, setRoadmap] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const roadmapRef = useRef<HTMLDivElement>(null);

  const filteredSuggestions = CAREER_SUGGESTIONS.filter((c) =>
    c.toLowerCase().includes(dreamCareer.toLowerCase()) && dreamCareer.length > 0
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!gradeLevel || !dreamCareer) return;

    setLoading(true);
    setRoadmap("");
    setError("");

    setTimeout(() => {
      roadmapRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);

    try {
      const res = await fetch("/api/guidance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gradeLevel, dreamCareer, gpa, location, interests, concerns }),
      });

      if (!res.ok) throw new Error("Failed to generate roadmap");

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        setRoadmap((prev) => prev + decoder.decode(value));
      }
    } catch {
      setError("Something went wrong. Please check your API key and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-slate-900">
      {/* Hero */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-800/30 via-transparent to-transparent" />
        <div className="relative max-w-4xl mx-auto px-4 pt-16 pb-12 text-center">
          <div className="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-400/30 rounded-full px-4 py-1.5 mb-6">
            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
            <span className="text-purple-300 text-sm font-medium">AI-Powered Career Guidance</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 leading-tight">
            Your Path to Your
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
              Dream Career
            </span>
          </h1>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto">
            Tell us where you are and where you want to go. We&apos;ll map out every step —
            from the classes to take this semester to the colleges that will get you there.
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-2xl mx-auto px-4 pb-16">
        <form
          onSubmit={handleSubmit}
          className="bg-white/5 border border-white/10 rounded-2xl p-6 md:p-8 backdrop-blur-sm shadow-2xl"
        >
          {/* Grade Level */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-200 mb-2">
              Your Current Grade Level <span className="text-purple-400">*</span>
            </label>
            <select
              value={gradeLevel}
              onChange={(e) => setGradeLevel(e.target.value)}
              required
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
            >
              <option value="" className="bg-slate-900">Select your grade level...</option>
              {GRADE_LEVELS.map((g) => (
                <option key={g.value} value={g.value} className="bg-slate-900">
                  {g.label}
                </option>
              ))}
            </select>
          </div>

          {/* Dream Career */}
          <div className="mb-6 relative">
            <label className="block text-sm font-semibold text-slate-200 mb-2">
              Dream Career or Field <span className="text-purple-400">*</span>
            </label>
            <input
              type="text"
              value={dreamCareer}
              onChange={(e) => { setDreamCareer(e.target.value); setShowSuggestions(true); }}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
              onFocus={() => setShowSuggestions(true)}
              placeholder="e.g. Neuroscientist, Game Developer, Architect..."
              required
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
            />
            {showSuggestions && filteredSuggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-slate-800 border border-white/20 rounded-xl shadow-xl overflow-hidden">
                {filteredSuggestions.slice(0, 6).map((s) => (
                  <button
                    key={s}
                    type="button"
                    onMouseDown={() => { setDreamCareer(s); setShowSuggestions(false); }}
                    className="w-full text-left px-4 py-2.5 text-slate-200 hover:bg-purple-600/40 text-sm transition"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* GPA and Location row */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-2">
                Current GPA <span className="text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={gpa}
                onChange={(e) => setGpa(e.target.value)}
                placeholder="e.g. 3.5"
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-200 mb-2">
                State / Location <span className="text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. California, Texas..."
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              />
            </div>
          </div>

          {/* Interests */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-200 mb-2">
              Current Interests &amp; Activities <span className="text-slate-500 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              placeholder="e.g. Math club, robotics, painting, sports..."
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
            />
          </div>

          {/* Concerns */}
          <div className="mb-8">
            <label className="block text-sm font-semibold text-slate-200 mb-2">
              Any Questions or Concerns? <span className="text-slate-500 font-normal">(optional)</span>
            </label>
            <textarea
              value={concerns}
              onChange={(e) => setConcerns(e.target.value)}
              placeholder="e.g. Worried about cost, not sure if I'm smart enough, want to know about scholarships..."
              rows={3}
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition resize-none"
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-xl text-red-300 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !gradeLevel || !dreamCareer}
            className="w-full py-4 px-6 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all duration-200 shadow-lg shadow-purple-900/50 text-lg"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Building Your Roadmap...
              </span>
            ) : (
              "✨ Generate My Career Roadmap"
            )}
          </button>
        </form>

        {/* Roadmap Output */}
        {(roadmap || loading) && (
          <div ref={roadmapRef} className="mt-8">
            <RoadmapDisplay content={roadmap} loading={loading} />
          </div>
        )}
      </div>

      <footer className="border-t border-white/10 py-6 text-center text-slate-500 text-sm">
        Powered by Claude claude-opus-4-7 · CareerCompass by ProjZen
      </footer>
    </main>
  );
}
