const form = document.querySelector("#ask-form");
const question = document.querySelector("#question");
const button = form.querySelector("button");
const feedback = document.querySelector("#feedback");
const answerLabel = document.querySelector("#answer-label");
const message = document.querySelector("#message");

function showMessage(status, text) {
    feedback.hidden = false;
    feedback.dataset.state = status;
    answerLabel.hidden = status !== "answer";
    message.textContent = text;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (button.disabled) return;

    const text = question.value.trim();
    if (!text) {
        showMessage("error", form.dataset.empty);
        question.focus();
        return;
    }

    button.disabled = true;
    form.setAttribute("aria-busy", "true");
    showMessage("loading", form.dataset.loading);

    try {
        const response = await fetch(form.dataset.endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({question: text}),
        });
        const result = await response.json();
        if (!result.status || typeof result.message !== "string") {
            throw new Error("Unexpected response");
        }
        showMessage(response.ok ? result.status : "error", result.message);
    } catch {
        showMessage("error", form.dataset.error);
    } finally {
        form.removeAttribute("aria-busy");
        button.disabled = false;
    }
});
