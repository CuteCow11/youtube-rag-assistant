const SERVER_URL = "http://127.0.0.1:8000";

const btnInit = document.getElementById('btn-init');
const setupArea = document.getElementById('setup-area');
const chatContainer = document.getElementById('chat-container');
const inputArea = document.getElementById('input-area');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');
const statusText = document.getElementById('status-text');
const initLoader = document.getElementById('init-loader');


btnInit.addEventListener('click', async () => {

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab.url.includes("youtube.com/watch")) {
    alert("Please open a valid YouTube video page first.");
    return;
  }

  btnInit.disabled = true;
  initLoader.style.display = "block";
  statusText.innerText = "Processing...";

  try {
    const response = await fetch(`${SERVER_URL}/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_url: tab.url })
    });
    
    const data = await response.json();
    
    if (response.ok) {
     
      setupArea.style.display = 'none';
      chatContainer.style.display = 'flex';
      inputArea.style.display = 'flex';
      statusText.innerText = "Ready to Chat";
      addMessage("bot", "Video loaded! Ask me anything about it.");
    } else {
      alert("Error: " + data.detail);
    }
  } catch (err) {
    alert("Could not connect to Python server. Is 'server.py' running?");
  } finally {
    btnInit.disabled = false;
    initLoader.style.display = "none";
  }
});

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  chatInput.value = "";
  statusText.innerText = "Thinking...";

  try {
    const response = await fetch(`${SERVER_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    });
    
    const data = await response.json();
    if (response.ok) {
      addMessage("bot", data.answer);
    } else {
      addMessage("bot", "Error: " + data.detail);
    }
  } catch (err) {
    addMessage("bot", "Server connection failed.");
  }
  
  statusText.innerText = "Ready";
}

btnSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

function addMessage(type, text) {
  const div = document.createElement('div');
  div.className = `message ${type}`;
  div.innerText = text;
  chatContainer.appendChild(div);
  chatContainer.scrollTop = chatContainer.scrollHeight; 
}