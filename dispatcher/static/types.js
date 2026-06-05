const test = {
    "url": "https://zulip2.com/",
    "bundles": [
        {
            "id": 1,
            "name": "Home",
            "search": "",
            "any_tags": "",
            "all_tags": "home/my-home",
            "excluded_tags": "",
            "order": 0,
            "date_created": "2026-05-28T02:18:51.421276Z",
            "date_modified": "2026-05-28T22:06:53.916035Z"
        }
    ],
    "bookmark": null,
    "metadata": {
        "url": "https://zulip2.com/",
        "title": null,
        "description": null,
        "preview_image": null
    }
};

/**
 * @typedef {Object} Metadata
 * @property {string} url - The URL of the bookmark
 * @property {string} title - The title of the bookmark
 * @property {string} description - The description of the bookmark
 * @property {string} preview_image - The URL of the preview image
 */


/**
 * @typedef {Object} ApiCheckData
 * @property {string} url - The URL of the bookmark
 * @property {Array} bundles - List of bundles that match the bookmark
 * @property {Object|null} bookmark - The existing bookmark data if it exists, otherwise null
 * @property {Metadata} metadata - The metadata associated with the bookmark
 */

export { };