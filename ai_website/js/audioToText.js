// ================= AUDIO TO TEXT =================

// Start Live Speech to Text
function startLiveSpeechToText() {

    // Check browser support
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert(
            "Speech recognition is not supported in this browser. " +
            "Please use Microsoft Edge or Google Chrome."
        );
        return;
    }

    const output = document.getElementById("audioToTextOutput");
    const languageSelect = document.getElementById("audioLangSelect");

    // Get selected language
    const selectedLanguage = languageSelect
        ? languageSelect.value
        : "en-US";

    // Create speech recognition
    const recognition = new SpeechRecognition();

    recognition.lang = selectedLanguage;

    // Continue listening while user speaks
    recognition.continuous = false;

    // Show partial results while speaking
    recognition.interimResults = true;

    recognition.maxAlternatives = 1;

    // Start message
    output.value = "🎤 Listening... Please speak now.";

    // When speech is detected
    recognition.onresult = function(event) {

        let finalTranscript = "";
        let interimTranscript = "";

        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {

            const transcript =
                event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        // Display the result
        if (finalTranscript) {
            output.value = finalTranscript;
        } else if (interimTranscript) {
            output.value = interimTranscript;
        }
    };

    // When recognition starts
    recognition.onstart = function() {
        console.log("🎤 Speech recognition started");

        output.value =
            "🎤 Listening...\n\nStart speaking...";
    };

    // When recognition stops
    recognition.onend = function() {
        console.log("🛑 Speech recognition stopped");
    };

    // Error handling
    recognition.onerror = function(event) {

        console.error(
            "Speech recognition error:",
            event.error
        );

        if (event.error === "not-allowed") {

            output.value =
                "❌ Microphone permission was denied.\n\n" +
                "Please allow microphone access in your browser.";
        }

        else if (event.error === "no-speech") {

            output.value =
                "⚠️ No speech detected.\n\n" +
                "Please click the button and speak clearly.";
        }

        else if (event.error === "network") {

            output.value =
                "❌ Network error.\n\n" +
                "Please check your internet connection.";
        }

        else {

            output.value =
                "❌ Speech recognition error: " +
                event.error;
        }
    };

    // Start recognition
    try {
        recognition.start();
    } catch (error) {

        console.error(
            "Could not start speech recognition:",
            error
        );

        output.value =
            "❌ Could not start microphone.\n\n" +
            "Please try again.";
    }
}