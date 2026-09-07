import dotenv from 'dotenv';
dotenv.config();

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

async function testModel(modelName) {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: 'Hello' }] }]
        })
      }
    );
    
    const data = await response.json();
    
    if (response.ok && data.candidates) {
      console.log(`✅ ${modelName} - WORKS!`);
      return modelName;
    } else {
      console.log(`❌ ${modelName} - ${data.error?.message || 'Failed'}`);
    }
  } catch (error) {
    console.log(`❌ ${modelName} - ${error.message}`);
  }
  return null;
}

async function findWorkingModel() {
  const models = [
    'gemini-pro',
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-2.0-flash-exp'
  ];
  
  console.log('Testing models...\n');
  
  for (const model of models) {
    const working = await testModel(model);
    if (working) {
      console.log(`\n✅ USE THIS MODEL: ${working}`);
      break;
    }
    await new Promise(r => setTimeout(r, 500));
  }
}

findWorkingModel();
