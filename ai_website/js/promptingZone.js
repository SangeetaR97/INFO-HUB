document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ promptingZone.js loaded");

    const btn = document.getElementById("generateBtn");
    if (!btn) {
        console.error("❌ Button with id 'generateBtn' not found");
        return;
    }

    btn.onclick = promptingZone;
});

function promptingZone() {
    console.log("🔥 Generate button clicked");

    const input = document.getElementById("promptingZoneInput");
    const output = document.getElementById("promptingZoneOutput");

    if (!input || !output) {
        console.error("❌ Input or output element missing");
        return;
    }

    const prompt = input.value;
    console.log("📝 Prompt:", prompt);

    if (!prompt.trim()) {
        output.innerHTML = "⚠️ Please enter a prompt";
        return;
    }

    output.innerHTML = "⏳ Generating better prompt...";

    fetch("http://localhost:3000/api/suggest-prompts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
    })
    .then(res => res.json())
    .then(data => {
        console.log("✅ Server response:", data);
        output.innerHTML = `<pre>${data.suggestions}</pre>`;
    })
    .catch(err => {
        console.error("❌ Fetch failed:", err);
        output.innerHTML = "Generating prompt";
    });
}
