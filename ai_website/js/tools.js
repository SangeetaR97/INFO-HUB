/* ----------------------------------------------------------
   1) ATS SCORE CHECKER
----------------------------------------------------------- */
function checkATSScore() {
    const jd = document.getElementById("jobDescription").value.toLowerCase();
    const resume = document.getElementById("resumeText").value.toLowerCase();
    const resultEl = document.getElementById("atsResult");

    if (!jd || !resume) {
        resultEl.innerText = "Please enter both Job Description and Resume.";
        return;
    }

    const jdWords = jd.split(/[\s,.-]+/);
    let matched = 0;

    jdWords.forEach(word => {
        if (resume.includes(word)) matched++;
    });

    const score = Math.round((matched / jdWords.length) * 100);
    resultEl.innerHTML = `Your ATS Score: <b>${score}%</b>`;
}


/* ----------------------------------------------------------
   2) TEXT SUMMARIZER
----------------------------------------------------------- */
function summarizeText() {
    const text = document.getElementById("textToSummarize").value;
    const output = document.getElementById("summaryResult");

    if (!text.trim()) {
        output.innerText = "Enter text to summarize.";
        return;
    }

    // Simple summarizer → first 3 important sentences  
    const sentences = text.split(".");
    const summary = sentences.slice(0, 3).join(".") + ".";

    output.innerText = summary;
}


/* ----------------------------------------------------------
   3) IMAGE COMPRESSOR (client-side)
----------------------------------------------------------- */
function compressImage(event) {
    const file = event.target.files[0];
    const output = document.getElementById("compressResult");

    if (!file) {
        output.innerText = "Upload an image.";
        return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = function (e) {
        const img = new Image();
        img.src = e.target.result;

        img.onload = function () {
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");

            canvas.width = img.width / 2;  
            canvas.height = img.height / 2;

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            const compressed = canvas.toDataURL("image/jpeg", 0.7);

            output.innerHTML = `
                <p>Compressed Image:</p>
                <img src="${compressed}" style="width:200px;">
                <a href="${compressed}" download="compressed.jpg">Download</a>
            `;
        };
    };
}


/* ----------------------------------------------------------
   4) QR CODE GENERATOR
----------------------------------------------------------- */
function generateQR() {
    const text = document.getElementById("qrText").value;
    const qrContainer = document.getElementById("qrResult");

    if (!text.trim()) {
        qrContainer.innerHTML = "Enter text to generate QR.";
        return;
    }

    qrContainer.innerHTML = ""; // clear old QR

    new QRCode(qrContainer, {
        text: text,
        width: 150,
        height: 150
    });
}


/* ----------------------------------------------------------
   5) ENGLISH SPEAKING ASSISTANT
      (speech to text + scoring)
----------------------------------------------------------- */

let recognition;
if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
}

function startEnglishTest() {
    const result = document.getElementById("englishResult");
    
    if (!recognition) {
        result.innerHTML = "Speech Recognition not supported in this browser.";
        return;
    }

    result.innerHTML = "🎤 Listening... Speak now.";

    recognition.start();

    recognition.onresult = function (event) {
        const spokenText = event.results[0][0].transcript;
        result.innerHTML = `<b>You said:</b> ${spokenText}`;

        const score = scoreEnglishLevel(spokenText);
        result.innerHTML += `<br><br>Your English Score: <b>${score}/100</b>`;
    };

    recognition.onerror = function () {
        result.innerHTML = "❌ Error detecting speech.";
    };
}

function scoreEnglishLevel(text) {
    let score = 0;

    // scoring by sentence length
    if (text.length > 20) score += 30;
    if (text.length > 50) score += 20;

    // vocabulary check
    const goodWords = ["actually", "however", "although", "important", "communication", "experience"];
    goodWords.forEach(w => {
        if (text.includes(w)) score += 10;
    });

    // grammar estimation
    const sentences = text.split(/[.!?]/);
    if (sentences.length > 1) score += 20;

    return Math.min(score, 100);
}

