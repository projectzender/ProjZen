import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const SYSTEM_PROMPT = `You are CareerCompass, an expert career counselor and academic advisor who specializes in helping students find their path to their dream careers. You have deep knowledge of:

- Educational pathways (middle school, high school, college, graduate school)
- AP courses, IB programs, dual enrollment options
- College admissions requirements and strategies
- Career-specific skills, certifications, and experiences
- Internships, volunteer work, and extracurricular activities that boost applications
- Top colleges and programs for every major career field
- GPA requirements, standardized tests (SAT/ACT), and portfolio requirements
- Scholarships and financial aid resources
- Alternative paths (community college, trade schools, bootcamps, etc.)

Your guidance is:
- Specific and actionable (concrete course names, real college names, actual certifications)
- Tailored to the student's exact grade level and current situation
- Realistic but encouraging
- Organized in clear sections with headers

Format your response using markdown with clear headers (##) and bullet points. Structure it as:

## 🎯 Your Career Path to [Career]

Brief encouraging intro paragraph.

## 📚 Immediate Steps (This School Year)

## 🗓️ Next 1-2 Years

## 🎓 College & Beyond

## 💪 Key Skills to Build

## 🏫 Top Programs & Colleges

## 🌟 Competitive Edge Tips

Keep the tone warm, motivating, and like a mentor who believes in them.`;

export async function POST(req: Request) {
  const body = await req.json();
  const { gradeLevel, dreamCareer, gpa, location, interests, concerns } = body;

  if (!gradeLevel || !dreamCareer) {
    return new Response(JSON.stringify({ error: "Missing required fields" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const userMessage = buildUserMessage({ gradeLevel, dreamCareer, gpa, location, interests, concerns });

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      try {
        const anthropicStream = client.messages.stream({
          model: "claude-opus-4-7",
          max_tokens: 4000,
          thinking: { type: "adaptive" },
          system: SYSTEM_PROMPT,
          messages: [{ role: "user", content: userMessage }],
        });

        for await (const event of anthropicStream) {
          if (
            event.type === "content_block_delta" &&
            event.delta.type === "text_delta"
          ) {
            controller.enqueue(encoder.encode(event.delta.text));
          }
        }

        controller.close();
      } catch (err) {
        controller.error(err);
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}

function buildUserMessage({
  gradeLevel,
  dreamCareer,
  gpa,
  location,
  interests,
  concerns,
}: {
  gradeLevel: string;
  dreamCareer: string;
  gpa?: string;
  location?: string;
  interests?: string;
  concerns?: string;
}) {
  let message = `Please create a detailed, personalized career roadmap for me.

**My Situation:**
- Current Grade/Level: ${gradeLevel}
- Dream Career: ${dreamCareer}`;

  if (gpa) message += `\n- Current GPA: ${gpa}`;
  if (location) message += `\n- Location: ${location}`;
  if (interests) message += `\n- Current Interests & Activities: ${interests}`;
  if (concerns) message += `\n- Questions or Concerns: ${concerns}`;

  message += `

Please give me a concrete, step-by-step roadmap tailored to my grade level. Include specific course names, real college programs, actual certifications, and practical advice I can act on right now.`;

  return message;
}
