// ===============================
// CHAT ELEMENTS
// ===============================
const input = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");
const sendBtn = document.getElementById("sendBtn");

// ===============================
// ADD MESSAGE TO CHAT
// ===============================
function addMessage(text, type) {
  const msg = document.createElement("div");
  msg.className = `message ${type}`;
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ===============================
// SEND MESSAGE
// ===============================
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ user_message: text })
    });

    const data = await res.json();
    addMessage(data.response, "bot");

  } catch (err) {
    addMessage("Server error. Please try again.", "bot");
    console.error(err);
  }
}

// ===============================
// EVENTS
// ===============================
sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// ===============================
// PROFILE DROPDOWN
// ===============================
function toggleProfileMenu() {
  document
    .getElementById("profile-menu")
    .classList.toggle("hidden");
}

// ===============================
// LOGOUT (ONLY ONE ✅)
// ===============================
async function logout() {
  try {
    await fetch("/logout", {
      method: "POST",
      credentials: "include"
    });
    window.location.href = "/";
  } catch (err) {
    console.error("Logout failed", err);
  }
}

// ===============================
// CLOSE DROPDOWN ON OUTSIDE CLICK (BONUS UX ✨)
// ===============================
document.addEventListener("click", function (e) {
  const profile = document.querySelector(".profile-container");
  const menu = document.getElementById("profile-menu");

  if (!profile.contains(e.target)) {
    menu.classList.add("hidden");
  }
});