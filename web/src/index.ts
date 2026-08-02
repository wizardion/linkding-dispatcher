import './styles/autocomplete.scss';
import './styles/main.scss';
import {
  ApiCheckData,
  Bookmark,
  UserForm,
  ApiInfoData,
  ApiJobDetails,
  ResultInfo,
  Payload,
  ApiMetadataData,
} from './types/types';
import { registerEventListeners, registerTagList } from './autocomplete/autocomplete';
import { nextFrame } from './core';
import { HttpClient } from './request/request';
import { ApiError } from './request/exceptions';

const apiUrl = '/api/v10/dispatcher';
const editForm = <HTMLFormElement>document.getElementById('dispatch-form');
const splitTagsRegex = /[,\s]+/g;

let bookmarkInfo: ApiInfoData | null = null;
let bookmark: Bookmark | null = null;

const userForm: UserForm = {
  url: document.getElementById('url-id') as HTMLInputElement,
  title: document.getElementById('title-id') as HTMLInputElement,
  dropdown: document.getElementById('bundle-id') as HTMLElement,
  dropdownTitle: document.getElementById('dropdown-title') as HTMLElement,
  bundles: (document
    .getElementById('bundle-id')
    ?.querySelectorAll('input[name="bundle"]') || []) as RadioNodeList,
  tags: document.getElementById('tags-id') as HTMLInputElement,
  session: document.getElementById('session-id') as HTMLInputElement,
  archived: document.getElementById('archived-id') as HTMLInputElement,
  description: document.getElementById('description-id') as HTMLTextAreaElement,
  submit: document.getElementById('submit-id') as HTMLButtonElement,
  remove: document.getElementById('remove-id') as HTMLButtonElement,
  headTitle: document.getElementById('head-title-id') as HTMLElement,
};

function selectBundle(value: string) {
  const radios = userForm.bundles;

  for (let i = 0; i < radios.length; i++) {
    const radio = radios[i];

    if (radio.value === value) {
      radio.click();
      break;
    }
  }
}

async function getPreference(client: HttpClient): Promise<ApiInfoData | null> {
  try {
    const data = await client.get<ApiInfoData>(`${apiUrl}/bookmark/info`);

    if (data) {
      const radios = userForm.bundles;
      let i = 0,
        j = 0;

      while (i < data.bundles.length || j < radios.length) {
        const bundle = data.bundles[i];
        const radio = radios[j];

        if (!bundle && radio?.parentElement) {
          radio.parentElement.remove();
          j += 1;
          continue;
        }

        if (bundle && radio && radio.value == '-1' && radio.nextSibling) {
          radio.nextSibling.textContent = bundle.name;
          radio.value = bundle.tag;
          radio.dataset.name = bundle.name;
          i += 1;
        }

        if (bundle && !radio) {
          const label = document.createElement('label');
          const input = document.createElement('input');
          const fragment = document.createDocumentFragment();

          input.type = 'radio';
          input.name = 'bundle';
          input.className = 'form-check-input me-2';
          input.value = bundle.tag;
          input.dataset.name = bundle.name;
          label.className = 'list-group-item';
          fragment.append(bundle.name);
          label.appendChild(input);
          label.appendChild(fragment);

          userForm.dropdown.appendChild(label);
          i += 1;
        }

        j += 1;
      }
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.log('ERROR:', [error.message]);
    } else {
      console.error('An unexpected error occurred');
    }
  }

  return null;
}

async function checkBookmark(
  url: string,
  client: HttpClient
): Promise<Bookmark | null> {
  if (url) {
    userForm.url.value = url;

    try {
      const encodedUrl = encodeURIComponent(url);
      const data = await client.get<ApiCheckData>(
        `${apiUrl}/bookmark/check?url=${encodedUrl}`
      );

      userForm.url.value = data.url;

      if (data.bookmark) {
        userForm.title.value = data.bookmark.title;
        userForm.description.value = data.bookmark.description;
        userForm.tags.value = data.bookmark.tags.join('');
        userForm.archived.checked = data.bookmark.archived;

        userForm.headTitle.textContent = 'Edit bookmark';
        document.title = 'Edit bookmark';

        userForm.remove.classList.remove('d-none');
        userForm.submit.classList.remove('w-100');
        userForm.submit.classList.add('w-75');
        userForm.headTitle.classList.add('text-success');

        userForm.submit.innerText = 'Save Bookmark';

        return data.bookmark;
      }

      userForm.headTitle.textContent = 'New bookmark';
      document.title = 'New bookmark';
    } catch (error) {
      if (error instanceof ApiError) {
        console.log('ERROR:', [error.message]);
      } else {
        console.error('An unexpected error occurred');
      }
    }
  }

  return null;
}

async function checkBookmarkMetadata(url: string, client: HttpClient): Promise<void> {
  if (url) {
    try {
      const encodedUrl = encodeURIComponent(url);
      const data = await client.get<ApiMetadataData>(
        `${apiUrl}/bookmark/metadata?url=${encodedUrl}`
      );

      if (!bookmark && data.metadata) {
        userForm.title.value = data.metadata.title;
        userForm.description.value = data.metadata.description;
      }
    } catch (error) {
      if (error instanceof ApiError) {
        console.log('ERROR:', [error.message]);
      } else {
        console.error('An unexpected error occurred');
      }
    }
  }
}

async function loadData() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token') || '';
  const client = new HttpClient(token);
  const url = urlParams.get('url') || '';
  const result = await Promise.all([checkBookmark(url, client), getPreference(client)]);

  bookmark = result[0];
  bookmarkInfo = result[1];

  if (!bookmark) {
    checkBookmarkMetadata(url, client);
  }

  if (bookmark && bookmarkInfo) {
    bookmarkInfo.preference = {
      ...bookmarkInfo.preference,

      tags: bookmark.tags,
      archived: bookmark.archived,
      bundle: bookmark.bundle,
    };
  }

  if (bookmarkInfo) {
    selectBundle(bookmarkInfo.preference.bundle);
    toggleTagsSet(bookmarkInfo.preference.archived);
    registerTagList(bookmarkInfo.tags || []);

    if (bookmarkInfo.preference?.remember) {
      userForm.session.checked = bookmarkInfo.preference.remember;
      userForm.archived.checked = bookmarkInfo.preference.archived;
      userForm.tags.value = bookmarkInfo.preference.tags.join(', ');
    }
  }

  userForm.title.disabled = false;
  userForm.tags.disabled = false;
  userForm.submit.disabled = false;
  userForm.remove.disabled = false;

  nextFrame().then(() => registerEventListeners());
}

function toggleTagsSet(archived: boolean) {
  const title = bookmark ? 'Edit bookmark' : 'New bookmark';

  if (archived) {
    userForm.headTitle.classList.add('text-danger');
    userForm.headTitle.textContent = `${title} (Archived)`;
  } else {
    userForm.headTitle.classList.remove('text-danger');
    userForm.headTitle.textContent = title;
  }
}

userForm.dropdown.addEventListener('change', (e: Event) => {
  const input = e.target as HTMLInputElement;
  const name = input.dataset.name ? ` (${input.dataset.name})` : '';
  const title = 'Bundles:';

  userForm.dropdownTitle.innerText = `${title}${name}`;
});

userForm.archived.addEventListener('change', (event) =>
  toggleTagsSet((<HTMLInputElement>event.target).checked)
);

editForm.addEventListener('submit', async (e) => {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token') || '';

  e.preventDefault();
  e.stopPropagation();

  if (editForm.checkValidity() && token) {
    const client = new HttpClient(token);
    const data = new FormData(editForm);
    const payload: Payload = {
      id: bookmark?.id || null,
      url: userForm.url.value,
      title: userForm.title.value,
      bundle: data.get('bundle')?.toString() || '',
      tags: [...new Set(userForm.tags.value.split(splitTagsRegex).filter((t) => t))],
      archived: userForm.archived.checked,
      description: userForm.description.value,
      remember: userForm.session.checked,
    };
    const info: ResultInfo = {
      element: document.getElementById('result-info') as HTMLElement,
    };

    userForm.submit.disabled = true;
    userForm.remove.disabled = true;

    try {
      await client.post<ApiJobDetails>(`${apiUrl}/bookmark/save`, payload);

      editForm.classList.add('d-none');
      info.element.classList.remove('d-none');
    } catch (error) {
      if (error instanceof ApiError) {
        console.log('ERROR:', [error.message]);
      } else {
        console.error('An unexpected error occurred');
      }
    }

    userForm.submit.disabled = false;
    userForm.remove.disabled = false;
  } else {
    editForm.classList.add('was-validated');
  }
});

userForm.remove.addEventListener('click', async (e) => {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token') || '';

  e.preventDefault();

  if (bookmark && token) {
    const client = new HttpClient(token);
    const info: ResultInfo = {
      element: document.getElementById('result-info') as HTMLElement,
    };

    userForm.submit.disabled = true;
    userForm.remove.disabled = true;

    try {
      const data = await client.delete<ApiJobDetails>(
        `${apiUrl}/bookmark/${bookmark.id}`
      );

      editForm.classList.add('d-none');
      info.element.classList.remove('d-none');
    } catch (error) {
      if (error instanceof ApiError) {
        console.log('ERROR:', [error.message]);
      } else {
        console.error('An unexpected error occurred');
      }
    }

    userForm.submit.disabled = false;
    userForm.remove.disabled = false;
  }
});

loadData();
