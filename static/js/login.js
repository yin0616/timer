const form = document.getElementById('login-form');
const themeBtn = document.getElementById("theme-toggle");
const icon = themeBtn.querySelector("i");

// 主題功能
function loadTheme() {
  const mode = localStorage.getItem("theme");
  if (mode === "light") document.body.classList.add("light-mode");//切換成白色主題
  updateIcon();
}

function toggleTheme() {
  document.body.classList.toggle("light-mode");
  const mode = document.body.classList.contains("light-mode") ? "light" : "dark"//判斷主題
  localStorage.setItem("theme", mode);
  updateIcon();
}

function updateIcon() {
  icon.className = document.body.classList.contains("light-mode") ? "bx bx-sun" : "bx bx-moon";
}

themeBtn.addEventListener("click", toggleTheme);
loadTheme();

// 登入邏輯
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const username = form.username.value.trim();
  const password = form.password.value;

  const res = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const result = await res.json();

  if (result.success) {
    window.location.href = "/";
  } else {
    alert(result.message || "Login failed");
    form.password.style.border = '2px solid #f66';
  }
});