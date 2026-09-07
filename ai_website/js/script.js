// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Basic form validation (example)
const contactForm = document.querySelector('.contact-form form');
if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
        let name = this.querySelector('input[type="text"]').value;
        let email = this.querySelector('input[type="email"]').value;
        let message = this.querySelector('textarea').value;

        if (!name || !email || !message) {
            alert('Please fill in all fields.');
            e.preventDefault(); // Prevent form submission
        }
    });
}

// Simple scroll animation (example)
function reveal() {
    var reveals = document.querySelectorAll(".feature-card");

    for (var i = 0; i < reveals.length; i++) {
      var windowHeight = window.innerHeight;
      var elementTop = reveals[i].getBoundingClientRect().top;
      var elementVisible = 150;

      if (elementTop < windowHeight - elementVisible) {
        reveals[i].classList.add("active");
      } else {
        reveals[i].classList.remove("active");
      }
    }
  }

  window.addEventListener("scroll", reveal);
