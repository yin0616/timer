document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');  
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const profileBlock = document.querySelector('.profile-block');  
    const themeBtn = document.getElementById("theme-toggle");
    const icon = themeBtn.querySelector("i");
    
    // 初始化主題
    function loadTheme() {
      const mode = localStorage.getItem("theme");
      if (mode === "light") document.body.classList.add("light-mode");
      updateIcon();
    }
    
    // 切換主題
    function toggleTheme() {
      document.body.classList.toggle("light-mode");
      const mode = document.body.classList.contains("light-mode") ? "light" : "dark";
      localStorage.setItem("theme", mode);
      updateIcon();
    }
    
    // 更新 icon
    function updateIcon() {
      icon.className = document.body.classList.contains("light-mode") ? "bx bx-sun" : "bx bx-moon";
    }
    
    // 綁定點擊
    themeBtn.addEventListener("click", toggleTheme);
    
    // 初始化
    loadTheme();

    // 建立訊息框放錯誤 / 成功訊息
    let msgbox = document.createElement("div");
    msgbox.style.margin = "10px 0";
    msgbox.style.fontSize = "14px";
    form.insertBefore(msgbox, form.querySelector("button"));  

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = usernameInput.value.trim(); 
        const password = passwordInput.value;

        msgbox.textContent = "";
        msgbox.style.color = "#fff"; 

        const res = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ username, password })
        });

        const result = await res.json();

        if (result.success) {
            msgbox.textContent = "註冊成功！請前往登入頁。";
            msgbox.style.color = '#6f6';
            form.reset();
            setTimeout(() => {
                window.location.href = "/";  // 成功跳轉登入頁
            }, 1500);
        } else {
            msgbox.textContent = "X " + (result.message || "註冊失敗"); 
            msgbox.style.color = "#f66";  
            usernameInput.style.border = "1px solid #f66";
        }
    });
});