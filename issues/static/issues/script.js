// If you need to add JavaScript for form validation or confirmation
document.addEventListener("DOMContentLoaded", function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
      button.addEventListener('click', function(event) {
        const confirmation = confirm('Are you sure you want to delete this issue?');
        if (!confirmation) {
          event.preventDefault();  // Prevents the link from being followed
        }
      });
    });
  });
  