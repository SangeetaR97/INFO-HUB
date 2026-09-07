import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();
const PORT = 3000;

// Get API keys from environment
const HF_API_KEY = process.env.HF_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// Log startup info
console.log('HF KEY LOADED:', HF_API_KEY ? 'YES' : 'NO');
console.log('GEMINI KEY LOADED:', GEMINI_API_KEY ? 'YES' : 'NO');
if (HF_API_KEY) {
  console.log('HF Key length:', HF_API_KEY.length);
}
if (GEMINI_API_KEY) {
  console.log('Gemini Key length:', GEMINI_API_KEY.length);
}

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    hfApiKeyLoaded: !!HF_API_KEY,
    geminiApiKeyLoaded: !!GEMINI_API_KEY,
    timestamp: new Date().toISOString()
  });
});

// Prompt suggestion endpoint
app.post('/api/suggest-prompt', async (req, res) => {
  try {
    const { topic, userMessage } = req.body;
    console.log('\n💡 Generating prompt suggestions');
    console.log('Topic:', topic);
    console.log('User message:', userMessage);

    // Determine what to generate prompts about
    let promptTopic = topic;
    
    if (!promptTopic && userMessage) {
      // Extract topic from user's message
      promptTopic = userMessage;
    }
    
    if (!promptTopic) {
      return res.status(400).json({ error: 'Topic or userMessage is required' });
    }

    // Use HuggingFace if no Gemini key or Gemini fails
    if (!GEMINI_API_KEY) {
      console.log('⚠️  No Gemini API key - using HuggingFace');
      return await generatePromptsWithHF(promptTopic, res, userMessage);
    }

    // Try Gemini first
    try {
      console.log('🔮 Trying Gemini API...');
      
      // Different prompts based on whether we have a user message or just a topic
      const systemPrompt = userMessage 
        ? `The user asked: "${userMessage}". Generate 3 better, more specific learning questions that would help them learn about this topic more effectively. Make the questions clear, focused, and educational. Return ONLY a JSON array of 3 strings.`
        : `Generate 3 excellent learning questions about "${promptTopic}". Each question should be clear, specific, and help someone learn about this topic. Return ONLY a JSON array of 3 strings.`;
      
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{
              parts: [{ text: systemPrompt }]
            }],
            generationConfig: {
              temperature: 0.7,
              maxOutputTokens: 300
            }
          })
        }
      );

      const data = await response.json();

      if (response.ok && data.candidates?.[0]?.content?.parts?.[0]?.text) {
        const generatedText = data.candidates[0].content.parts[0].text;
        const cleanText = generatedText.replace(/```json\n?|\n?```/g, '').trim();
        
        try {
          const prompts = JSON.parse(cleanText);
          console.log('✅ Gemini prompts:', prompts);
          return res.json({ prompts: Array.isArray(prompts) ? prompts.slice(0, 3) : prompts });
        } catch (parseError) {
          console.log('⚠️  Could not parse Gemini response as JSON');
        }
      }
    } catch (geminiError) {
      console.log('⚠️  Gemini failed, falling back to HuggingFace:', geminiError.message);
    }

    // Fallback to HuggingFace
    return await generatePromptsWithHF(promptTopic, res, userMessage);

  } catch (error) {
    console.error('❌ Server Error:', error);
    res.status(500).json({ 
      error: error.message || 'An unexpected error occurred' 
    });
  }
});

// Helper function to generate prompts with HuggingFace
async function generatePromptsWithHF(promptTopic, res, userMessage = null) {
  try {
    if (!HF_API_KEY) {
      return res.json({
        prompts: [
          `Explain ${promptTopic} in simple terms`,
          `What are the key concepts of ${promptTopic}?`,
          `How does ${promptTopic} work in practice?`
        ]
      });
    }

    const systemPrompt = userMessage
      ? `You are a helpful learning assistant. The user said: "${userMessage}". Generate exactly 3 better, more specific questions that would help them learn effectively. Be creative and educational. Return your response as a simple JSON array with exactly 3 strings. Example: ["First question here?", "Second question here?", "Third question here?"]`
      : `You are a helpful learning assistant. Generate exactly 3 excellent, specific questions about "${promptTopic}" that would help someone learn this topic deeply. Be creative and educational. Return your response as a simple JSON array with exactly 3 strings. Example: ["First question here?", "Second question here?", "Third question here?"]`;

    console.log('📤 Sending to HuggingFace...');
    const response = await fetch('https://router.huggingface.co/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${HF_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'meta-llama/Llama-3.2-3B-Instruct',
        messages: [{
          role: 'user',
          content: systemPrompt
        }],
        max_tokens: 300,
        temperature: 0.9  // Higher temperature for more creative prompts
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ HuggingFace error:', errorText);
      throw new Error('HuggingFace API failed');
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || '';
    
    console.log('📥 Raw AI response:', content);
    
    // Try multiple parsing strategies
    let prompts = null;
    
    // Strategy 1: Try direct JSON parse
    try {
      const cleanText = content.replace(/```json\n?|\n?```/g, '').trim();
      prompts = JSON.parse(cleanText);
      console.log('✅ Parsed as JSON directly');
    } catch (e) {
      console.log('⚠️  Direct JSON parse failed, trying extraction...');
    }
    
    // Strategy 2: Extract array pattern
    if (!prompts) {
      const arrayMatch = content.match(/\[[\s\S]*\]/);
      if (arrayMatch) {
        try {
          prompts = JSON.parse(arrayMatch[0]);
          console.log('✅ Extracted JSON array from text');
        } catch (e) {
          console.log('⚠️  Array extraction failed');
        }
      }
    }
    
    // Strategy 3: Extract questions manually
    if (!prompts || !Array.isArray(prompts) || prompts.length === 0) {
      console.log('⚠️  Extracting questions manually from text...');
      const lines = content.split('\n');
      prompts = [];
      
      for (const line of lines) {
        const trimmed = line.trim();
        // Look for lines that are questions or numbered items
        if (trimmed.match(/^\d+[\.\)]\s*/) || trimmed.includes('?') || trimmed.length > 30) {
          const cleaned = trimmed
            .replace(/^\d+[\.\)]\s*/, '')  // Remove numbering
            .replace(/^[-*]\s*/, '')        // Remove bullets
            .replace(/^["']|["']$/g, '')    // Remove quotes
            .trim();
          
          if (cleaned.length > 10 && !cleaned.startsWith('[') && !cleaned.startsWith('{')) {
            prompts.push(cleaned);
          }
        }
      }
      
      if (prompts.length > 0) {
        console.log('✅ Manually extracted questions');
      }
    }
    
    // Final validation
    if (!Array.isArray(prompts) || prompts.length === 0) {
      console.log('❌ Could not extract valid prompts, using fallback');
      prompts = [
        `What are the fundamental concepts of ${promptTopic}?`,
        `How does ${promptTopic} work in practical applications?`,
        `What are the latest developments in ${promptTopic}?`
      ];
    }

    // Ensure we have exactly 3 prompts
    prompts = prompts.slice(0, 3);
    
    // If we have less than 3, add generic ones
    while (prompts.length < 3) {
      prompts.push(`What else should I know about ${promptTopic}?`);
    }

    console.log('✅ Final prompts:', prompts);
    return res.json({ prompts });

  } catch (error) {
    console.error('❌ HF complete error:', error);
    // Last resort fallback
    return res.json({
      prompts: [
        `What are the key principles of ${promptTopic}?`,
        `How can I apply ${promptTopic} in real-world scenarios?`,
        `What are common misconceptions about ${promptTopic}?`
      ]
    });
  }
}

// Chat endpoint using new Hugging Face API
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    console.log('\n📩 Received message:', message);
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // If no API key, return mock response
    if (!HF_API_KEY) {
      console.log('⚠️  No API key - returning mock response');
      return res.json({ 
        response: `Mock AI Response: You said "${message}". Please add your Hugging Face API key to get real AI responses.` 
      });
    }

    // Use OpenAI-compatible endpoint with Hugging Face Inference Providers
    console.log('🤖 Calling Hugging Face Inference API...');
    const response = await fetch('https://router.huggingface.co/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${HF_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'meta-llama/Llama-3.2-3B-Instruct',
        messages: [
          {
            role: 'user',
            content: message
          }
        ],
        max_tokens: 500,
        temperature: 0.7
      })
    });

    console.log('📡 Response status:', response.status);
    
    // Get raw response text first
    const text = await response.text();
    console.log('📄 Raw response (first 200 chars):', text.substring(0, 200));

    // Check if response is ok
    if (!response.ok) {
      console.error('❌ API Error:', text);
      
      // Check for specific errors
      if (text.includes('loading')) {
        return res.status(503).json({ 
          error: 'AI model is loading. Please wait 20-30 seconds and try again.' 
        });
      }
      
      return res.status(500).json({ 
        error: `AI service error (${response.status}): ${text}` 
      });
    }

    // Parse JSON response
    let data;
    try {
      data = JSON.parse(text);
    } catch (parseError) {
      console.error('❌ JSON parse error:', parseError);
      return res.status(500).json({ 
        error: 'Invalid response from AI service: ' + text 
      });
    }

    // Extract AI response (OpenAI-compatible format)
    let aiResponse = '';
    if (data.choices && data.choices[0]?.message?.content) {
      aiResponse = data.choices[0].message.content;
    } else if (data.error) {
      return res.status(500).json({ error: data.error });
    } else {
      aiResponse = JSON.stringify(data);
    }

    console.log('✅ AI Response:', aiResponse.substring(0, 100));
    res.json({ response: aiResponse });

  } catch (error) {
    console.error('❌ Server Error:', error);
    res.status(500).json({ 
      error: error.message || 'An unexpected error occurred' 
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ AI backend running at http://localhost:${PORT}`);
  console.log(`📝 HF API Key: ${HF_API_KEY ? '✓ Loaded' : '✗ Missing'}`);
  console.log(`📝 Gemini API Key: ${GEMINI_API_KEY ? '✓ Loaded' : '✗ Missing'}`);
  
  if (!HF_API_KEY) {
    console.log('\n⚠️  WARNING: No HF_API_KEY found!');
    console.log('   Get one from: https://huggingface.co/settings/tokens');
  } else {
    console.log('📡 Using Hugging Face for chat');
    console.log('🤖 Chat Model: meta-llama/Llama-3.2-3B-Instruct');
  }
  
  if (!GEMINI_API_KEY) {
    console.log('\n⚠️  WARNING: No GEMINI_API_KEY found!');
    console.log('   Get one from: https://aistudio.google.com/apikey');
  } else {
    console.log('🔮 Using Gemini for prompt suggestions');
  }
  
  console.log('');
});