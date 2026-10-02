const input = document.getElementById("userInput");

const messages = document.getElementById("messages");

const loading = document.getElementById("loading");

const sendButton = document.getElementById("sendButton");


// ======================================
// Press Enter
// ======================================

input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

});


// ======================================
// Send Message
// ======================================

async function sendMessage() {

    const question = input.value.trim();


    // Don't send empty question

    if (question === "") {

        return;

    }


    // Show user message

    addUserMessage(question);


    // Clear input

    input.value = "";


    // Show loading

    loading.classList.remove("hidden");

    sendButton.disabled = true;


    try {

        console.log("Sending question:", question);


        const response = await fetch(
            "http://127.0.0.1:8000/chat",
            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })

            }
        );


        console.log(
            "Response status:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                "Server error: " +
                response.status
            );

        }


        const data = await response.json();


        console.log(
            "AI response:",
            data
        );


        // Display AI response

        addAIMessage(data.answer);


    } catch (error) {

        console.error(
            "Error:",
            error
        );


        addAIMessage(
            "Sorry, something went wrong. Please try again."
        );

    }


    // Hide loading

    loading.classList.add("hidden");

    sendButton.disabled = false;

    input.focus();

}


// ======================================
// Add User Message
// ======================================

function addUserMessage(text) {

    const message =
        document.createElement("div");


    message.className =
        "message user-message";


    message.innerHTML = `

        <div class="message-avatar">
            You
        </div>

        <div class="message-content">

            <p>
                ${escapeHTML(text)}
            </p>

        </div>

    `;


    messages.appendChild(message);


    scrollToBottom();

}


// ======================================
// Add AI Message
// ======================================

function addAIMessage(text) {

    const message =
        document.createElement("div");


    message.className =
        "message ai-message";


    message.innerHTML = `

        <div class="message-avatar">
            AI
        </div>

        <div class="message-content">

            <p>
                ${escapeHTML(text)}
            </p>

        </div>

    `;


    messages.appendChild(message);


    scrollToBottom();

}


// ======================================
// Suggested Questions
// ======================================

function askSuggestion(button) {

    const question =
        button.innerText;


    input.value =
        question;


    sendMessage();

}


// ======================================
// Scroll Chat
// ======================================

function scrollToBottom() {

    messages.scrollTop =
        messages.scrollHeight;

}


// ======================================
// Security
// ======================================

function escapeHTML(text) {

    const div =
        document.createElement("div");


    div.textContent =
        text;


    return div.innerHTML;

}