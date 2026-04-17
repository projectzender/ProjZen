# CareerCompass 🧭

AI-powered career guidance for students at every stage. Enter your grade level and dream career, and get a personalized, step-by-step roadmap — from AP classes to college recommendations.

## Features

- **Grade-aware guidance** — tailored advice whether you're in middle school, high school, college, or changing careers
- **Personalized roadmaps** — specific AP courses, real college programs, certifications, and extracurriculars
- **Real-time streaming** — watch your roadmap generate live, powered by Claude claude-opus-4-7
- **Career autocomplete** — suggestions for 25+ career fields
- **Adaptive AI thinking** — Claude reasons deeply about your specific situation

## Getting Started

1. **Clone and install**
   ```bash
   npm install
   ```

2. **Set your API key**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local and add your ANTHROPIC_API_KEY
   ```

3. **Run the dev server**
   ```bash
   npm run dev
   ```

Open [http://localhost:3000](http://localhost:3000) to use the app.

## Tech Stack

- **Next.js 16** (App Router, TypeScript)
- **Tailwind CSS v4** with Typography plugin
- **Anthropic SDK** — Claude claude-opus-4-7 with adaptive thinking + streaming
- **react-markdown** — renders the AI-generated roadmap beautifully
