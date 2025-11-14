document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Defensive checks: if essential elements are missing, bail with a helpful console message
  if (!activitiesList || !activitySelect) {
    console.error("Required DOM elements missing: activities-list or activity select not found.");
    return;
  }
  if (!signupForm) {
    console.error("Signup form (#signup-form) not found. Signup feature disabled.");
    // still load activities so user can see them
    fetchActivities();
    return;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear and reset activity select to avoid duplicated options on refresh
      activitySelect.innerHTML = '<option value="" disabled selected>Select an activity</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants HTML (supports both string entries and objects with email/username)
        const participants = details.participants || [];
        let participantsHtml;
        if (participants.length === 0) {
          participantsHtml = `<p class="no-participants">No participants yet. Be the first!</p>`;
        } else {
          const items = participants.map(p => {
            let email = "";
            let display = "";
            if (p && typeof p === "object") {
              email = p.email || "";
              display = p.username || p.email || JSON.stringify(p);
            } else {
              email = String(p);
              display = email;
            }
            const emailSmall = email && display !== email ? ` <small class="participant-email">(${escapeHtml(email)})</small>` : "";
            return `<li class="participant-item"><span>${escapeHtml(display)}${emailSmall}</span><button class="delete-btn" data-activity="" data-email="${escapeHtml(email)}" title="Remove ${escapeHtml(display)}">✕</button></li>`;
          }).join("");
          participantsHtml = `<ul class="participants-list">${items}</ul>`;
        }

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Participants</h5>
            ${participantsHtml}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add event listeners to delete buttons
        const deleteButtons = activityCard.querySelectorAll(".delete-btn");
        deleteButtons.forEach(btn => {
          btn.setAttribute("data-activity", name);
          btn.addEventListener("click", handleDeleteParticipant);
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Simple HTML escaper to avoid injection if server data contains special chars
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const username = document.getElementById("username").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}&username=${encodeURIComponent(username)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // refresh activity list so availability / participants update
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");
      messageDiv.style.display = "block";

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
        messageDiv.style.display = "none";
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      messageDiv.style.display = "block";
      console.error("Error signing up:", error);
    }
  });

  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const email = event.currentTarget.getAttribute("data-email");
    const activityName = event.currentTarget.getAttribute("data-activity");

    if (!email || !activityName) {
      console.error("Missing email or activity name for deletion");
      return;
    }

    if (!confirm(`Are you sure you want to remove ${escapeHtml(email)} from ${escapeHtml(activityName)}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        messageDiv.textContent = "Participant removed successfully";
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        messageDiv.style.display = "block";
        fetchActivities();
        // Hide message after 3 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
          messageDiv.style.display = "none";
        }, 3000);
      } else {
        const result = await response.json();
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        messageDiv.style.display = "block";
      }
    } catch (error) {
      messageDiv.textContent = "Error removing participant";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      messageDiv.style.display = "block";
      console.error("Error deleting participant:", error);
    }
  }

  // Initialize app
  fetchActivities();
});
