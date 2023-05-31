function hide_unused() {
    const usrlang = (navigator.language || navigator.userLanguage).toString().substring(0,2);
    if (usrlang === "ru") {
      let english_loading = document.getElementById("loading_en");
      english_loading.remove();
      let english_download_link = document.getElementById("download_link_en");
      english_download_link.remove();
  } else {
      let russian_loading = document.getElementById("loading_ru");
      russian_loading.remove();
      let russian_download_link = document.getElementById("download_link_ru");
      russian_download_link.remove();
  }
}

hide_unused();