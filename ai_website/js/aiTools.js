// aiTools.js
// Replaces previous placeholder. Adds click handlers on .tool-card to show step-by-step usage modals.
// No external library required. Works with the existing HTML structure (tool-card elements).

// --- Data: detailed step-by-step guides ---

const toolGuides = {
  tool1: {
    title: "Tool 1 — Using Chatbots (Complete Guide)",
    summary: "Guidance for using conversational chatbots: opening, prompting, follow-ups, saving, and closing.",
    steps: [
      "Open the chatbot: Click the chatbot tool or visit the chatbot's URL. If it requires login, sign in with your account (or create one).",
      "Set the context: Begin by telling the chatbot the role and context (e.g., 'You are a helpful coding tutor' or 'You are a friendly travel assistant'). This improves relevance.",
      "Start with a clear prompt: Write a concise request that contains the goal, constraints, and any examples. Example: 'Explain logistic regression in simple terms with a Python example and comments.'",
      "Use progressive prompting: Break large tasks into smaller steps. Ask for an outline, then each section. This helps get focused, constructive answers.",
      "Ask for formats: If you need code, tables, or summaries, explicitly request it: 'Give me code only inside a code block' or 'Provide a one-paragraph summary and a 5-point bullet list.'",
      "Ask clarifying questions: If the response misses details, ask follow-ups like 'Can you expand the evaluation section?' or 'Show edge cases and expected inputs.'",
      "Use example-driven prompts: Provide sample inputs or desired outputs to make responses concrete (e.g., sample dataset rows or desired file formats).",
      "Validate answers: For factual or technical outputs, cross-check with documentation or run generated code in a safe environment before trusting it.",
      "Save useful sessions: Copy helpful replies to local notes, or use the chatbot's export/save features if available. Keep versioned snippets for reuse.",
      "End the session politely: If the chatbot allows ending or clearing context, do so. Clear context if you begin a new topic so previous context doesn't interfere.",
      "Safety & privacy tips: Avoid pasting sensitive data (passwords, PII). If you must use data, sanitize it first or prefer local tools."
    ]
  },

  tool2: {
    title: "Tool 2 — Other AI Tools (Non-chatbot) — List & Use",
    summary: "Common non-chatbot AI tools and precise step-by-step instructions on how to use each.",
    categories: [
      {
        name: "Image Generation (e.g., Stable Diffusion, DALL·E, Midjourney)",
        steps: [
          "Open the image tool UI (web app or plugin). Sign in if required.",
          "Choose style & resolution: select art style, aspect ratio, and desired image size.",
          "Write a concise prompt: include subjects, colors, mood, and any negative prompts (what to avoid). Example: 'A pastel-color portrait of a smiling child in a sunflower field, cinematic lighting, photorealistic.'",
          "Generate and iterate: create multiple variations. Use seed and tweak prompts until satisfied.",
          "Refine with edits: use inpainting or edit tools to change parts of the image, or rerun prompt with adjustments.",
          "Download and license-check: download the high-res image and check the tool's usage/licensing policies before commercial use."
        ]
      },
      {
        name: "Text-to-Speech (TTS) — (e.g., Amazon Polly, Google TTS)",
        steps: [
          "Open the TTS tool and choose the voice and language.",
          "Paste or type your text; for long texts, split into sections to avoid timeouts.",
          "Adjust speech settings: speed, pitch, emphasis or SSML tags if supported.",
          "Preview speech and iterate until the pronunciation and intonation are correct.",
          "Download the audio file (MP3/WAV) and test in your target player."
        ]
      },
      {
        name: "Speech-to-Text / Transcription (STT) — (e.g., Whisper, Google STT)",
        steps: [
          "Open the transcription tool and select language and any speaker-diarization options if needed.",
          "Upload the audio file or record directly in the tool.",
          "Run transcription; correct obvious mistakes manually.",
          "Export as text, SRT, or other formats for subtitles or analysis.",
          "Validate timestamps if using captions; adjust alignment if needed."
        ]
      },
      {
        name: "Code Assistants / Code Generation (e.g., GitHub Copilot, Codeium)",
        steps: [
          "Open the IDE plugin or web UI and authenticate if needed.",
          "Provide a clear comment or function signature to indicate desired behavior.",
          "Accept or modify auto-completions; review suggested code for correctness and security.",
          "Run tests or a linter on the generated code before use.",
          "Refine by providing examples and expected outputs to the assistant."
        ]
      },
      {
        name: "Summarizers & Extractors (e.g., SMMRY, AI summarizers)",
        steps: [
          "Paste the long text or upload a document.",
          "Choose summary length (short/medium/long) or bullet points vs paragraph output.",
          "Run summary and review key points for correctness; add context if something important is missing.",
          "Use extracts for outlines or slide creation when needed."
        ]
      },
      {
        name: "Machine Translation (e.g., DeepL, Google Translate)",
        steps: [
          "Select source and target languages.",
          "Paste text and choose formal/informal tone options if available.",
          "Review and, if needed, edit culturally-specific phrases manually.",
          "Use human proofreading for final or official documents."
        ]
      },
      {
        name: "OCR (Text from Images — e.g., Tesseract, Google Vision)",
        steps: [
          "Upload an image or PDF.",
          "Choose language and any layout options (multi-column, handwritten).",
          "Run OCR, then proofread extracted text for recognition errors.",
          "Export as text, CSV, or searchable PDF."
        ]
      },
      {
        name: "Video Generation / Editing (e.g., Runway, Pika)",
        steps: [
          "Open the video tool and choose template or blank project.",
          "Upload assets (images/audio) or enter a script for text-to-video tools.",
          "Set scene timing, transitions, and voiceover (TTS) if required.",
          "Render preview, iterate on pacing and visuals.",
          "Export final video and check codec/resolution."
        ]
      },
      {
        name: "Data & Analytics Assistants (AutoML / Notebook helpers)",
        steps: [
          "Upload dataset and inspect column types and missing values.",
          "Select analysis type (classification, regression, clustering) or ask the tool for recommendations.",
          "Run model training with default hyperparams, examine metrics.",
          "Tune, cross-validate, and export model or code snippets for production."
        ]
      }
    ]
  },

  tool3: {
    title: "Tool 3 — Quick Multi-Tool Guide & Best Practices",
    summary: "A short guide for using tools effectively and responsibly.",
    steps: [
      "Identify the tool purpose: match the tool to the job (image generation for visuals, STT for transcripts, summarizer for long docs).",
      "Prepare inputs: clean text, good prompts, high-quality audio or images improve outputs.",
      "Start small: test with short examples before batch processing large datasets.",
      "Iterate fast: tweak parameters, style, or tone and compare results.",
      "Verify outputs: always verify for accuracy, bias, or hallucination (especially with generative text).",
      "Export & archive: save versions of outputs, prompts, and tool settings for reproducibility.",
      "Respect licensing & privacy: check terms of service and avoid uploading private or copyrighted material without permission."
    ]
  }
};

// --- UI: modal builder and event wiring ---

function createModal(title, subtitle, contentHtml) {
  // modal wrapper
  const overlay = document.createElement("div");
  overlay.style.position = "fixed";
  overlay.style.top = "0";
  overlay.style.left = "0";
  overlay.style.width = "100%";
  overlay.style.height = "100%";
  overlay.style.background = "rgba(0,0,0,0.5)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = 9999;

  // modal box
  const box = document.createElement("div");
  box.style.width = "90%";
  box.style.maxWidth = "900px";
  box.style.maxHeight = "85vh";
  box.style.overflow = "auto";
  box.style.background = "white";
  box.style.borderRadius = "12px";
  box.style.padding = "20px";
  box.style.boxShadow = "0 10px 30px rgba(0,0,0,0.2)";
  box.style.fontFamily = "Segoe UI, Tahoma, Geneva, Verdana, sans-serif";
  box.style.color = "#333";

  // header
  const h = document.createElement("h2");
  h.textContent = title;
  h.style.marginTop = "0";
  box.appendChild(h);

  // subtitle
  if (subtitle) {
    const s = document.createElement("p");
    s.textContent = subtitle;
    s.style.marginTop = "4px";
    s.style.marginBottom = "12px";
    box.appendChild(s);
  }

  // content
  const content = document.createElement("div");
  content.innerHTML = contentHtml;
  content.style.lineHeight = "1.6";
  box.appendChild(content);

  // close button
  const closeBtn = document.createElement("button");
  closeBtn.textContent = "Close";
  closeBtn.style.marginTop = "16px";
  closeBtn.style.padding = "8px 12px";
  closeBtn.style.border = "none";
  closeBtn.style.borderRadius = "6px";
  closeBtn.style.background = "#3498db";
  closeBtn.style.color = "white";
  closeBtn.style.cursor = "pointer";
  closeBtn.onclick = () => document.body.removeChild(overlay);
  box.appendChild(closeBtn);

  overlay.appendChild(box);
  return overlay;
}

function renderGuideForTool(toolKey) {
  const guide = toolGuides[toolKey];
  if (!guide) return;

  let html = "";

  if (guide.summary) {
    html += `<p style="font-weight:600;">${guide.summary}</p>`;
  }

  if (guide.steps) {
    html += "<ol style='margin-left:18px;'>";
    guide.steps.forEach(step => {
      html += `<li style='margin-bottom:10px;'>${step}</li>`;
    });
    html += "</ol>";
  }

  if (guide.categories) {
    guide.categories.forEach(cat => {
      html += `<h3 style="margin-bottom:6px;margin-top:12px;">${cat.name}</h3>`;
      html += "<ol style='margin-left:18px;'>";
      cat.steps.forEach(s => {
        html += `<li style='margin-bottom:8px;'>${s}</li>`;
      });
      html += "</ol>";
    });
  }

  const modal = createModal(guide.title, null, html);
  document.body.appendChild(modal);
}

// Attach click handlers to the existing .tool-card elements
function attachToolCardHandlers() {
  // Grab tool cards in order — assume three cards as in your HTML
  const cards = document.querySelectorAll(".tool-card");
  if (!cards || cards.length === 0) return;

  cards.forEach((card, idx) => {
    card.style.cursor = "pointer";
    card.addEventListener("click", (e) => {
      e.preventDefault();
      // Map index to tool keys (0→tool1,1→tool2,2→tool3)
      const map = ["tool1", "tool2", "tool3"];
      const key = map[idx] || "tool1";
      renderGuideForTool(key);
    });
  });
}

// Initialize on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", attachToolCardHandlers);
} else {
  attachToolCardHandlers();
}
