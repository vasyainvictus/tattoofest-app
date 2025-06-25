// web/script.js
document.addEventListener("DOMContentLoaded", function() {
    const contentDiv = document.getElementById('content');
    const tg = window.Telegram.WebApp;
    tg.expand();

    // ... (код displayContentByRole) ...

    try {
        if (!tg.initData) throw new Error("Нет initData");
        
        const params = new URLSearchParams(tg.initData);
        const user = JSON.parse(params.get('user'));
        const telegramId = user.id;

        // ЗАГЛУШКА: Сюда вставим URL бэкенда от Vercel
        // Обрати внимание на /api/ в пути
        const backendUrl = `https://your-app-name.vercel.app/api/users/by_telegram_id/${telegramId}`;

        fetch(backendUrl)
            // ... (остальной код fetch) ...
    } catch (e) {
        // ... (обработка ошибок) ...
    }
});