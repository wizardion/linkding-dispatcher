const host = "https://bookmarks.zarnitsa.duckdns.org";
const apiUrl = "/api/v10/dispatcher/";
const form = document.getElementById("dispatch-form");

/** @import { ApiCheckData, Metadata } from "./types" */

function getFormData(form) {
    const formData = new FormData(bookmarkForm);
    const bundleSelect = document.getElementById('id_bundle_string');
    const data = Object.fromEntries(formData.entries());

    if (formData.has('is_archived')) {
        data['is_archived'] = true;
    } else {
        data['is_archived'] = false;
    }

    if (formData.has('tag_names')) {
        const tagNames = formData.get('tag_names').split(/[, ]+/).map(t => t.trim().toLowerCase()).filter(t => t.length > 0);

        if (bundleSelect.value) {
            tagNames.push(bundleSelect.value);
        }

        data['tag_names'] = tagNames;
    }

    return data;
}

async function updateBookmark() {
    const res = await fetch('./save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: urlInput.value,
            tags: finalTags,
            is_archived: archiveCheckbox.checked
        })
    });
}

function populateTags() {
    if (bookmark && bookmark.tag_names) {
        const tagsInput = document.getElementById('id_tag_string');
        const bundleSelect = document.getElementById('id_bundle_string');

        let currentTags = bookmark.tag_names;
        let matchedBundleTag = "";

        const options = bundleSelect.options;
        for (let i = 0; i < options.length; i++) {
            const bundleTag = options[i].value;
            if (bundleTag && currentTags.includes(bundleTag)) {
                bundleSelect.selectedIndex = i;
                matchedBundleTag = bundleTag;
                break;
            }
        }

        // Hide the bundle tag from the visual textbox
        const visibleTags = currentTags.filter(t => t !== matchedBundleTag);
        tagsInput.value = visibleTags.join(', ');
    }
}

async function checkBookmark() {
    const urlParams = new URLSearchParams({ "url": window.CHECKING_URL || "" });

    if (urlParams.has('url')) {
        const encodedUrl = encodeURIComponent(urlParams.get('url'));
        const inputUrl = document.getElementById('id_url');
        const response = await fetch(`${host}${apiUrl}/check?url=${encodedUrl}`);

        /** @type {ApiCheckData} */
        const data = await response.json();

        if (data && data.metadata) {
            inputUrl.value = data.metadata.url || urlParams.get('url');
        }
    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = getFormData(bookmarkForm);

    console.log("Form data to be sent:", data);
});

checkBookmark();
