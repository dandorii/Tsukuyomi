document.addEventListener("DOMContentLoaded", () => {
    const controls = document.getElementById("letter-sharing-controls");

    if (!controls) return;

    const draftId = controls.dataset.draftId;
    const status = document.getElementById("sharing-status");
    const message = document.getElementById("sharing-message");

    const publishButton = document.getElementById("publish-letter-button");
    const copyButton = document.getElementById("copy-share-link");
    const revokeButton = document.getElementById("revoke-share-link");

    function showMessage(text, isError = false) {
        message.textContent = text;
        message.dataset.state = isError ? "error" : "success";
    }

    async function sendRequest(url) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Accept": "application/json"
            },
            credentials: "same-origin"
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || "The request could not be completed.");
        }

        return data;
    }

    function renderPublishedLink(shareUrl) {
        controls.dataset.published = "true";
        status.textContent = "THIS LETTER IS PUBLISHED";

        const container = document.createElement("div");
        container.id = "share-link-container";

        const label = document.createElement("label");
        label.htmlFor = "share-link";
        label.textContent = "SHAREABLE LINK";

        const input = document.createElement("input");
        input.id = "share-link";
        input.type = "url";
        input.readOnly = true;
        input.value = shareUrl;

        const copy = document.createElement("button");
        copy.type = "button";
        copy.id = "copy-share-link";
        copy.textContent = "COPY SHARE LINK";

        const revoke = document.createElement("button");
        revoke.type = "button";
        revoke.id = "revoke-share-link";
        revoke.textContent = "REVOKE SHARE LINK";

        container.append(label, input, copy, revoke);

        const oldButton = document.getElementById("publish-letter-button");
        if (oldButton) oldButton.replaceWith(container);
        else controls.append(container);

        copy.addEventListener("click", copyShareLink);
        revoke.addEventListener("click", revokeShareLink);
    }

    async function publishLetter() {
        publishButton.disabled = true;
        showMessage("Publishing your letter...");

        try {
            const data = await sendRequest(
                `/api/drafts/${encodeURIComponent(draftId)}/publish`
            );

            renderPublishedLink(data.share_url);
            showMessage("Published. Anyone with this link can read your letter.");
        } catch (error) {
            showMessage(error.message, true);
            publishButton.disabled = false;
        }
    }

    async function copyShareLink() {
        const input = document.getElementById("share-link");

        if (!input || !input.value) {
            showMessage("No share link is available.", true);
            return;
        }

        try {
            await navigator.clipboard.writeText(input.value);
            showMessage("Share link copied.");
        } catch {
            input.focus();
            input.select();
            showMessage("Automatic copy unavailable. Copy the selected link manually.");
        }
    }

    
function openRevokeDialog() {
    const overlay = document.getElementById("revoke-confirmation-overlay");
    const dialog = overlay?.querySelector(".revoke-confirmation-dialog");
    if (!overlay || !dialog) return;

    overlay.hidden = false;
    dialog.focus();
}

function closeRevokeDialog() {
    const overlay = document.getElementById("revoke-confirmation-overlay");
    const revokeButton = document.getElementById("revoke-share-link");

    if (!overlay) return;

    overlay.hidden = true;
    revokeButton?.focus();
}

async function revokeShareLink() {
    openRevokeDialog();
}

async function confirmRevokeShareLink() {
    const confirmButton = document.getElementById("confirm-revoke-button");
    if (!confirmButton) return;

    confirmButton.disabled = true;
    showMessage("Revoking the share link...");

    try {
        await sendRequest(
            `/api/drafts/${encodeURIComponent(draftId)}/unpublish`
        );

        controls.dataset.published = "false";
        status.textContent = "THIS LETTER IS PRIVATE AGAIN";

        const container = document.getElementById("share-link-container");
        if (container) container.remove();

        const publish = document.createElement("button");
        publish.type = "button";
        publish.id = "publish-letter-button";
        publish.textContent = "PUBLISH LETTER";
        controls.insertBefore(publish, message);
        publish.addEventListener("click", publishLetter);

        closeRevokeDialog();
        showMessage("Share link revoked. Your letter is private again.");
    } catch (error) {
        showMessage(error.message, true);
    } finally {
        confirmButton.disabled = false;
    }
}


    if (publishButton) {
        publishButton.addEventListener("click", publishLetter);
    }

    if (copyButton) {
        copyButton.addEventListener("click", copyShareLink);
    }

    if (revokeButton) {
        revokeButton.addEventListener("click", revokeShareLink);
    }

    const cancelRevokeButton = document.getElementById("cancel-revoke-button");
    const confirmRevokeButton = document.getElementById("confirm-revoke-button");
    const revokeOverlay = document.getElementById("revoke-confirmation-overlay");

    if (cancelRevokeButton) {
        cancelRevokeButton.addEventListener("click", closeRevokeDialog);
    }

    if (confirmRevokeButton) {
        confirmRevokeButton.addEventListener("click", confirmRevokeShareLink);
    }

    if (revokeOverlay) {
        revokeOverlay.addEventListener("click", (event) => {
            if (event.target === revokeOverlay) {
                closeRevokeDialog();
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            revokeOverlay &&
            !revokeOverlay.hidden
        ) {
            closeRevokeDialog();
        }
    });

});
