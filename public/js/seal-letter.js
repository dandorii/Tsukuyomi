document.addEventListener("DOMContentLoaded", () => {
    const sealButton = document.getElementById("seal-letter-button");
    const overlay = document.getElementById("seal-confirmation-overlay");
    const dialog = document.querySelector(".seal-confirmation-dialog");
    const cancelButton = document.getElementById("cancel-seal-button");
    const confirmButton = document.getElementById("confirm-seal-button");
    const status = document.querySelector(".read-letter-status");
    const actions = document.querySelector(".read-letter-actions");

    // Sealed letters do not have a sealing dialog.
    if (
        !sealButton ||
        !overlay ||
        !dialog ||
        !cancelButton ||
        !confirmButton
    ) {
        return;
    }

    function openDialog() {
        overlay.hidden = false;
        cancelButton.focus();
    }

    function closeDialog() {
        overlay.hidden = true;
        sealButton.focus();
    }

    sealButton.addEventListener("click", openDialog);
    cancelButton.addEventListener("click", closeDialog);

    // Close the dialog with Escape.
    overlay.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeDialog();
        }
    });

    // Permanently seal the letter through the Flask backend.
    confirmButton.addEventListener("click", async () => {
        const match = window.location.pathname.match(
            /^\/my-letters\/(\d+)$/
        );

        if (!match) {
            alert("Unable to identify this letter. Please try again.");
            return;
        }

        const draftId = match[1];

        confirmButton.disabled = true;
        cancelButton.disabled = true;
        confirmButton.textContent = "SEALING...";

        try {
            const response = await fetch(
                `/api/drafts/${draftId}/seal`,
                {
                    method: "POST",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            const result = await response.json();

            if (!response.ok || result.sealed !== true) {
                throw new Error(
                    result.error || "The letter could not be sealed."
                );
            }

            // Update the page only after the server confirms success.
            if (status) {
                status.textContent = "SEALED — NOT SENT";
            }

            if (actions) {
                const editLink = actions.querySelector(".draft-open-link");
                if (editLink) {
                    editLink.remove();
                }

                sealButton.remove();
            }

            overlay.hidden = true;

            // Focus a useful location after the controls disappear.
            if (status) {
                status.setAttribute("tabindex", "-1");
                status.focus();
            }
        } catch (error) {
            alert(error.message || "Something went wrong. Please try again.");

            confirmButton.disabled = false;
            cancelButton.disabled = false;
            confirmButton.textContent = "SEAL PERMANENTLY";
        }
    });
});