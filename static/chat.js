const chat = document.getElementById("chat");
const msg = document.getElementById("msg");
const send = document.getElementById("send");
const boqUrl = document.getElementById("boqUrl");
const priceUrl = document.getElementById("priceUrl");

function add(side, text){
  const el = document.createElement("div");
  el.className = `msg ${side}`;
  el.innerHTML = text;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

send.onclick = async () => {
  const content = msg.value.trim();
  if(!content) return;
  add("user", content);
  msg.value = "";
  const res = await fetch("/api/chat/send/", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      message: content,
      boq_url: boqUrl.value.trim(),
      price_url: priceUrl.value.trim()
    })
  });
  const data = await res.json();
  add("bot", data.response || "No response");
};
