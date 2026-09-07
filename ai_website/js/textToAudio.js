// textToAudio.js - Auto-detect language like audio-to-text
function textToAudio() {
    const textInput = document.getElementById("textToAudioInput").value;
    const pdfInput = document.getElementById("pdfToAudioInput").files[0];
    const languageSelect = document.getElementById("languageSelect").value;

    if (!textInput && !pdfInput) {
        alert("Please enter text OR upload a PDF file.");
        return;
    }

    if (pdfInput) {
        readPDF(pdfInput, function (pdfText) {
            speakText(pdfText, languageSelect);
        });
    } else {
        speakText(textInput, languageSelect);
    }
}

// Detect language from text
function detectLanguage(text) {
    // Check for Kannada characters (Unicode range: 0C80-0CFF)
    if (/[\u0C80-\u0CFF]/.test(text)) {
        return 'kn-IN';
    }
    // Check for Hindi/Devanagari characters (Unicode range: 0900-097F)
    if (/[\u0900-\u097F]/.test(text)) {
        return 'hi-IN';
    }
    // Default to English
    return 'en-IN';
}

// Convert Text → Speech with auto-detection
function speakText(text, selectedLanguage) {
    // Stop any currently playing audio
    stopAudio();

    // Auto-detect language from text if not manually selected
    const detectedLang = detectLanguage(text);
    const language = selectedLanguage || detectedLang;

    console.log("Selected Language:", selectedLanguage);
    console.log("Detected Language:", detectedLang);
    console.log("Using Language:", language);

    // Try browser's native speech synthesis first
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;

    // Get available voices
    const voices = speechSynthesis.getVoices();
    
    // Find the best matching voice
    let selectedVoice = null;

    if (language === "kn-IN") {
        // Try to find Kannada voice
        selectedVoice = voices.find(v => 
            v.lang === "kn-IN" || 
            v.lang === "kn" || 
            v.lang.startsWith("kn")
        );
        
        if (!selectedVoice) {
            console.warn("No Kannada voice found. Install Kannada language pack in Windows Settings.");
            // Fallback to Hindi for similar pronunciation
            selectedVoice = voices.find(v => v.lang === "hi-IN" || v.lang === "hi");
        }
    } else if (language === "hi-IN") {
        // Find Hindi voice
        selectedVoice = voices.find(v => 
            v.lang === "hi-IN" || 
            v.lang === "hi" || 
            v.lang.startsWith("hi")
        );
    } else {
        // Find English (India) voice
        selectedVoice = voices.find(v => 
            v.lang === "en-IN" || 
            v.lang === "en-US" || 
            v.lang === "en-GB" ||
            v.lang.startsWith("en")
        );
    }

    if (selectedVoice) {
        utterance.voice = selectedVoice;
        console.log("Using voice:", selectedVoice.name, selectedVoice.lang);
    } else {
        console.warn("No suitable voice found for", language);
    }

    // Set speech parameters
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Error handling
    utterance.onerror = function(event) {
        console.error("Speech synthesis error:", event);
        if (language === "kn-IN") {
            alert("⚠️ Kannada voice not available!\n\n" +
                  "To enable Kannada TTS:\n" +
                  "1. Open Windows Settings\n" +
                  "2. Go to Time & Language → Language & Region\n" +
                  "3. Add Kannada language\n" +
                  "4. Check 'Text-to-speech' option\n" +
                  "5. Use Microsoft Edge browser\n\n" +
                  "For now, using Hindi pronunciation as fallback.");
            
            // Try speaking with Hindi
            const fallbackUtterance = new SpeechSynthesisUtterance(text);
            fallbackUtterance.lang = "hi-IN";
            const hindiVoice = voices.find(v => v.lang === "hi-IN" || v.lang === "hi");
            if (hindiVoice) {
                fallbackUtterance.voice = hindiVoice;
            }
            speechSynthesis.speak(fallbackUtterance);
        }
    };

    utterance.onstart = function() {
        console.log("Speech started");
    };

    utterance.onend = function() {
        console.log("Speech finished");
    };

    // Speak the text
    speechSynthesis.speak(utterance);
}

// Read PDF and extract text
function readPDF(file, callback) {
    const reader = new FileReader();

    reader.onload = function () {
        const typedArray = new Uint8Array(this.result);

        pdfjsLib.getDocument(typedArray).promise.then(function (pdf) {
            let allText = "";
            let pagePromises = [];
            
            for (let i = 1; i <= pdf.numPages; i++) {
                pagePromises.push(
                    pdf.getPage(i).then(function (page) {
                        return page.getTextContent().then(function (textContent) {
                            let pageText = textContent.items.map((item) => item.str).join(" ");
                            allText += pageText + "\n";
                        });
                    })
                );
            }

            Promise.all(pagePromises).then(() => callback(allText));
        });
    };

    reader.readAsArrayBuffer(file);
}

function stopAudio() {
    // Stop browser speech synthesis
    if ("speechSynthesis" in window) {
        speechSynthesis.cancel();
    }
    
    // Stop any audio elements
    if (window.currentAudio) {
        window.currentAudio.pause();
        window.currentAudio.currentTime = 0;
        window.currentAudio = null;
    }
    
    console.log("All audio stopped");
}

// Load and display available voices
function loadVoices() {
    const voices = speechSynthesis.getVoices();
    
    console.log("=== Available Text-to-Speech Voices ===");
    console.log("Total voices:", voices.length);
    
    // Group voices by language
    const kannadaVoices = voices.filter(v => v.lang.includes('kn'));
    const hindiVoices = voices.filter(v => v.lang.includes('hi'));
    const englishVoices = voices.filter(v => v.lang.includes('en'));
    
    if (kannadaVoices.length > 0) {
        console.log("\n✅ KANNADA VOICES:");
        kannadaVoices.forEach(v => console.log(`  - ${v.name} (${v.lang})`));
    } else {
        console.log("\n❌ NO KANNADA VOICES - Install from Windows Settings!");
    }
    
    if (hindiVoices.length > 0) {
        console.log("\n✅ HINDI VOICES:");
        hindiVoices.forEach(v => console.log(`  - ${v.name} (${v.lang})`));
    }
    
    if (englishVoices.length > 0) {
        console.log("\n✅ ENGLISH VOICES:");
        englishVoices.forEach(v => console.log(`  - ${v.name} (${v.lang})`));
    }
    
    console.log("\n===================================");
}

// Load voices when available
if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = loadVoices;
}

// Load voices on page load
setTimeout(loadVoices, 100);