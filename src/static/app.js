document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const submitButton = signupForm.querySelector("button[type='submit']");
  const maxWaitlistSize = 5;
  let activitiesCache = {};

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#x27;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function makeParticipantItem(activityName, email, suffix) {
    const safeEmail = escapeHtml(email);
    const safeActivity = escapeHtml(activityName);
    return `<li>
      <button class="remove-participant" data-email="${safeEmail}" data-activity="${safeActivity}" title="Remove participant" aria-label="Remove participant">&#x2715;</button>
      ${safeEmail}${suffix}
    </li>`;
  }

  function buildParticipantsList(activityName, details) {
    const participants = details.participants || [];
    const auditioned = details.auditioned || [];
    const requiresAudition = details.requires_audition === true;

    if (participants.length === 0 && auditioned.length === 0) {
      return "<li class=\"participants-empty\">No participants yet</li>";
    }

    if (!requiresAudition) {
      return participants.map((p) => makeParticipantItem(activityName, p, "")).join("");
    }

    const orderedAuditioned = auditioned.map((p) => makeParticipantItem(activityName, p, "")).join("");
    const pendingAudition = participants.map((p) => makeParticipantItem(activityName, p, "*")).join("");

    return `${orderedAuditioned}${pendingAudition}`;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();
      activitiesCache = activities;

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = "<option value=\"\">-- Select an activity --</option>";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const requiresAudition = details.requires_audition === true;
        const displayName = requiresAudition ? `${name} (By Audition only)` : name;
        const spotsLeft = details.max_participants - details.participants.length;
        const instructor = details.instructor || "TBD";
        const waitlist = details.waitlist || [];
        const waitlistSpotsLeft = maxWaitlistSize - waitlist.length;
        const isParticipantsFull = details.participants.length >= details.max_participants;
        const waitlistStatus = isParticipantsFull
          ? `<p><strong>Waitlist:</strong> ${waitlist.length}/${maxWaitlistSize} filled (${waitlistSpotsLeft} spots left)</p>`
          : "";
        const auditionFootnote = requiresAudition
          ? '<p class="participants-footnote">* Students with asterisks must audition.</p>'
          : "";

        activityCard.innerHTML = `
          <h4>${displayName}</h4>
          <p><strong>Instructor:</strong> ${instructor}</p>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${waitlistStatus}
          <details class="participants-panel">
            <summary>Participants (${details.participants.length})</summary>
            <ul class="participants-list">
              ${buildParticipantsList(name, details)}
            </ul>
            ${auditionFootnote}
          </details>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      updateSignupButtonState();
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  function updateSignupButtonState() {
    const selectedActivityName = activitySelect.value;
    const selectedActivity = activitiesCache[selectedActivityName];

    if (!selectedActivity) {
      submitButton.textContent = "Sign Up";
      submitButton.disabled = false;
      return;
    }

    const isParticipantsFull = selectedActivity.participants.length >= selectedActivity.max_participants;
    const waitlist = selectedActivity.waitlist || [];
    const isWaitlistFull = waitlist.length >= maxWaitlistSize;

    if (!isParticipantsFull) {
      submitButton.textContent = "Sign Up";
      submitButton.disabled = false;
      return;
    }

    if (!isWaitlistFull) {
      submitButton.textContent = "Waitlist";
      submitButton.disabled = false;
      return;
    }

    submitButton.textContent = "Full";
    submitButton.disabled = true;
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  activitySelect.addEventListener("change", () => {
    updateSignupButtonState();
  });

  activitiesList.addEventListener("click", async (event) => {
    const btn = event.target.closest(".remove-participant");
    if (!btn) return;

    const email = btn.dataset.email;
    const activity = btn.dataset.activity;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        { method: "DELETE" }
      );
      if (response.ok) {
        fetchActivities();
      }
    } catch (error) {
      console.error("Error removing participant:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
