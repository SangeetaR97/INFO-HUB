import dotenv from 'dotenv';
dotenv.config();

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

async function listAllModels() {
  try {
    console.log('📋 Fetching all available models...\n');
    
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_API_KEY}`
    );
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error('❌ Error fetching models:', data);
      return;
    }
    
    if (!data.models || data.models.length === 0) {
      console.log('⚠️  No models found. Your API key might not be activated properly.');
      console.log('\nPlease check:');
      console.log('1. Go to https://aistudio.google.com/');
      console.log('2. Make sure the API is enabled');
      console.log('3. Try creating a new API key\n');
      return;
    }
    
    console.log('✅ Available models:\n');
    
    data.models.forEach(model => {
      const name = model.name.replace('models/', '');
      const methods = model.supportedGenerationMethods || [];
      
      if (methods.includes('generateContent')) {
        console.log(`✅ ${name}`);
      }
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

listAllModels();
