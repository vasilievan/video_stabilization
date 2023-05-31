function hide_unused() {
    const usrlang = (navigator.language || navigator.userLanguage).toString().substring(0,2);
    if (usrlang === "ru") {
        let english_form = document.getElementById("the_form_en");
        english_form.remove();
    } else {
        let russian_form = document.getElementById("the_form_ru");
        russian_form.remove();
    }
}

hide_unused();