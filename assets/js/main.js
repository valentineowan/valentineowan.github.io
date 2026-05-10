/* ===== Mobile navigation toggle ===== */

document.addEventListener("DOMContentLoaded", () => {

  const navToggle = document.querySelector(".nav-toggle");
  const siteNav = document.querySelector("#site-nav");

  if(navToggle && siteNav){

    navToggle.addEventListener("click", () => {

      const expanded =
        navToggle.getAttribute("aria-expanded") === "true";

      navToggle.setAttribute(
        "aria-expanded",
        !expanded
      );

      siteNav.classList.toggle("open");

    });

  }

});


/* ===== Auto-update footer year ===== */

document.addEventListener("DOMContentLoaded", () => {

  const yearElement =
    document.getElementById("year");

  if(yearElement){

    yearElement.textContent =
      new Date().getFullYear();

  }

});


/* ===== Rename Quotes navigation globally ===== */

document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll("a").forEach(link => {

    if(link.textContent.trim() === "Quotes"){

      link.textContent = "Reflections";

    }

  });

});