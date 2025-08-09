/*
 * Custom JavaScript for the academic project template
 *
 * This file initializes the Bulma carousel and handles the
 * responsive navigation menu. The code is written in vanilla
 * JavaScript for maximum compatibility. No external dependencies
 * other than Bulma are required.
 */

document.addEventListener('DOMContentLoaded', function () {
  /**
   * Toggle the navigation menu on mobile
   *
   * Bulma’s navbar uses a burger icon to reveal the menu on narrow screens.
   * When the burger is clicked, we toggle the `is-active` class on both the
   * burger itself and the target menu (whose id is specified in the
   * `data-target` attribute). This ensures the hamburger works consistently
   * across devices without relying on any external JavaScript library.
   */
  const burger = document.querySelector('.navbar-burger');
  if (burger) {
    const targetId = burger.dataset.target;
    const menu = document.getElementById(targetId);
    burger.addEventListener('click', function () {
      burger.classList.toggle('is-active');
      if (menu) {
        menu.classList.toggle('is-active');
      }
    });
  }

  /**
   * Lightweight carousel implementation
   *
   * The original template attempted to use the Bulma Carousel extension
   * loaded from a CDN. In some environments (including this one) that
   * dependency fails to initialise, leaving the slider blank. To avoid this
   * problem, we implement a simple carousel in plain JavaScript. Each
   * `.carousel` container cycles through its children with the class
   * `.carousel-item`. Only the item marked with `.is-active` is displayed; all
   * others are hidden via CSS (see style.css). Navigation arrows allow users
   * to manually step through the slides, and an optional autoplay (using the
   * `data-autoplay` attribute) advances the slides every 3 seconds.
   */
  const carousels = document.querySelectorAll('.carousel');
  carousels.forEach(function (carousel) {
    const items = carousel.querySelectorAll('.carousel-item');
    if (items.length === 0) return;
    let currentIndex = 0;

    // Helper: show the slide at `index` and hide others
    function showItem(index) {
      items.forEach(function (item, i) {
        if (i === index) {
          item.classList.add('is-active');
        } else {
          item.classList.remove('is-active');
        }
      });
    }

    // Show the first slide initially
    showItem(currentIndex);

    // Bind navigation buttons if present
    const navLeft = carousel.querySelector('.carousel-nav-left');
    const navRight = carousel.querySelector('.carousel-nav-right');
    if (navLeft) {
      navLeft.addEventListener('click', function (event) {
        event.preventDefault();
        // Move to the previous slide (wrap around)
        currentIndex = (currentIndex - 1 + items.length) % items.length;
        showItem(currentIndex);
      });
    }
    if (navRight) {
      navRight.addEventListener('click', function (event) {
        event.preventDefault();
        // Move to the next slide (wrap around)
        currentIndex = (currentIndex + 1) % items.length;
        showItem(currentIndex);
      });
    }

    // Autoplay: if the container has a `data-autoplay` attribute set to
    // true (either as `data-autoplay="true"` or simply `data-autoplay`),
    // advance slides every 3 seconds. Pausing on hover could be added
    // similarly if needed.
    const autoplayAttr = carousel.getAttribute('data-autoplay');
    const shouldAutoplay = autoplayAttr !== null && autoplayAttr.toLowerCase() !== 'false';
    if (shouldAutoplay) {
      setInterval(function () {
        currentIndex = (currentIndex + 1) % items.length;
        showItem(currentIndex);
      }, 3000);
    }
  });
});