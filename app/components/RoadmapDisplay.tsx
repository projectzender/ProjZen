"use client";

import ReactMarkdown from "react-markdown";

interface Props {
  content: string;
  loading: boolean;
}

export default function RoadmapDisplay({ content, loading }: Props) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 md:p-8 backdrop-blur-sm shadow-2xl">
      {loading && !content && (
        <div className="flex flex-col items-center justify-center py-12 gap-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-4 border-purple-500/30 border-t-purple-500 animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">🧭</span>
            </div>
          </div>
          <p className="text-slate-300 text-sm animate-pulse">
            Claude is mapping your career journey...
          </p>
        </div>
      )}

      {content && (
        <div className="prose prose-invert prose-sm md:prose-base max-w-none
          prose-headings:text-white
          prose-h2:text-xl prose-h2:font-bold prose-h2:mt-8 prose-h2:mb-3
          prose-h3:text-lg prose-h3:font-semibold prose-h3:mt-5 prose-h3:mb-2
          prose-p:text-slate-300 prose-p:leading-relaxed
          prose-li:text-slate-300 prose-li:leading-relaxed
          prose-ul:my-3 prose-ul:space-y-1
          prose-strong:text-white prose-strong:font-semibold
          prose-a:text-purple-400 prose-a:no-underline hover:prose-a:underline
          [&_h2]:border-b [&_h2]:border-white/10 [&_h2]:pb-2
        ">
          <ReactMarkdown>{content}</ReactMarkdown>
          {loading && (
            <span className="inline-block w-2 h-5 bg-purple-400 animate-pulse rounded-sm ml-0.5" />
          )}
        </div>
      )}
    </div>
  );
}
