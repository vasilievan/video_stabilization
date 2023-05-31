function hide_unused() {
    const usrlang = (navigator.language || navigator.userLanguage).toString().substring(0,2);
    if (usrlang === "ru") {
        let not_found_en = document.getElementById("not_found_en");
        not_found_en.remove();
    } else {
        let not_found_ru = document.getElementById("not_found_ru");
        not_found_ru.remove();
    }
}

hide_unused();