import { Globals, MatchesResult, Positioning, Query, TagsQuery } from '../types/types';

const listElement = <HTMLDivElement>document.getElementById('autocomplete-list');
const globals: Globals = {
  selected: 0,
  allTags: new Set(),
  tags: new Set(),
  spliter: /[,\s]+/g,
  ltrimmer: /^[,\s]+/g,
};

function removeTag(name: string) {
  const input = <HTMLInputElement>document.getElementById('tags-id');

  globals.tags.delete(name);
  renderAllTags();

  input.value = '';
}

function renderTag(name: string, predicate: (e: Event) => void): HTMLDivElement {
  const tag = document.createElement('div') as HTMLDivElement;
  const span = document.createElement('span') as HTMLSpanElement;
  const button = document.createElement('button') as HTMLButtonElement;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');

  svg.setAttribute('class', 'bi bi-x');
  svg.setAttribute('viewBox', '0 0 24 24');
  use.setAttribute('href', '#x-remove');
  use.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', '#x-remove');
  svg.appendChild(use);

  button.type = 'button';
  button.classList.add('tag-delete');
  button.setAttribute('aria-label', 'Remove ' + name);
  button.appendChild(svg);

  span.innerText = name;

  tag.classList.add('tag', 'user-select-none');
  tag.appendChild(span);
  tag.appendChild(button);
  tag.dataset.tag = name;

  button.addEventListener('mousedown', (e) => e.preventDefault());
  button.addEventListener('click', predicate);

  return tag;
}

function renderAllTags() {
  const input = document.getElementById('tags-id') as HTMLInputElement;

  while (input.previousSibling) {
    const node = input.previousSibling;

    node.remove();
  }

  for (const name of globals.tags) {
    const tag = renderTag(name, () => removeTag(name));

    input.parentElement?.insertBefore(tag, input);
  }
}

function toggleTagsVisibility(visible: boolean) {
  listElement.dataset.visible = String(visible);

  if (visible) {
    listElement.classList.add('show');
  } else {
    listElement.classList.remove('show');
  }

  globals.selected = 0;
}

function selectTag(tagName: string) {
  const input = <HTMLInputElement>document.getElementById('tags-id');

  globals.tags.add(tagName);
  globals.allTags.add(tagName);

  toggleTagsVisibility(false);
  renderAllTags();

  input.value = '';
  input.focus();
}

function searchInQuery(query: string): MatchesResult {
  if (!query || globals.allTags.has(query)) {
    return {
      isNew: false,
      matches: [],
    };
  }

  const matches = !query
    ? [...globals.allTags]
    : [...globals.allTags].filter((i) => i.startsWith(query));

  matches.sort((a, b) => {
    const aStarts = a.startsWith(query);
    const bStarts = b.startsWith(query);

    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;

    return a.localeCompare(b);
  });

  const isNew = matches.length === 0;

  return {
    isNew: isNew,
    matches: !isNew ? matches.filter((v) => !globals.tags.has(v)) : [query],
  };
}

// ------------------------------------------------------------------------------------
function showSuggestion(e: Event) {
  const input = e.target as HTMLInputElement;
  const { isNew, matches } = searchInQuery(input.value.trim());

  listElement.innerHTML = '';
  listElement.scrollTop = 0;
  globals.selected = 0;

  for (let i = 0; i < matches.length; i++) {
    const match = matches[i];
    const item = document.createElement('li');
    const input = document.createElement('input');

    input.type = 'button';
    input.className = 'dropdown-item pt-2 pb-2';
    input.value = isNew ? `new: "${match}"` : match;
    input.dataset.value = match;

    input.addEventListener('click', (e) => {
      e.preventDefault();
      selectTag(match);
    });

    item.appendChild(input);
    listElement.appendChild(item);
  }

  if (matches.length > 0) {
    const item = listElement.children[globals.selected];

    (item.firstChild as HTMLInputElement).classList.add('active');
  }

  toggleTagsVisibility(matches?.length > 0);
}

function onKeyPress(e: KeyboardEvent) {
  const suggestionVisible = listElement.dataset.visible == 'true';

  if (suggestionVisible && ['ArrowDown', 'ArrowUp'].includes(e.code)) {
    const count = listElement.childElementCount - 1;
    const selected =
      e.code === 'ArrowDown'
        ? globals.selected >= count
          ? 0
          : globals.selected + 1
        : globals.selected > 0
          ? globals.selected - 1
          : count;

    const item = listElement.children[globals.selected] as HTMLElement | null;
    const nextItem = listElement.children[selected] as HTMLElement;

    if (item && item.firstChild) {
      (item.firstChild as HTMLInputElement).classList.remove('active');
    }

    if (nextItem && nextItem.firstChild) {
      (nextItem.firstChild as HTMLInputElement).classList.add('active');
      (nextItem.firstChild as HTMLInputElement).scrollIntoView({ block: 'nearest' });
    }

    globals.selected = selected;

    e.preventDefault();
  }

  if (suggestionVisible && e.code === 'Enter') {
    const item = <HTMLUListElement>listElement.children[globals.selected];

    if (item && item.firstChild) {
      (item.firstChild as HTMLInputElement).click();
    }

    e.preventDefault();
  }

  if (['Backspace', 'Delete'].includes(e.code)) {
    const input = e.target as HTMLInputElement;

    if (input.value.trim() === '') {
      input.value = '';

      if (input.previousSibling) {
        const tag = (input.previousSibling as HTMLDivElement).dataset.tag;

        if (tag && globals.tags.delete(tag)) {
          input.previousSibling.remove();
        }
      }
    }
  }
}

function removeAllTags(e: Event) {
  const input = <HTMLInputElement>document.getElementById('tags-id');

  globals.tags.clear();
  input.value = '';
  renderAllTags();

  e.preventDefault();
}

// -----------------------------------------------------------------------------------
export function setInputTags(tags: string[]) {
  const input = <HTMLInputElement>document.getElementById('tags-id');

  globals.tags = new Set(
    tags.filter((v) => globals.allTags.has(v)).map((v) => v.toLowerCase())
  );
  renderAllTags();

  input.value = '';
}

export function registerTags(allTags: string[]) {
  globals.allTags = new Set(allTags.map((i) => i.toLowerCase()));
}

export function getSelectedTags(): string[] {
  return [...globals.tags];
}

export function registerEventListeners() {
  const input = <HTMLInputElement>document.getElementById('tags-id');
  const remove = <HTMLInputElement>document.getElementById('tags-remove-all');

  input.addEventListener('keydown', onKeyPress);
  input.addEventListener('blur', (e) => toggleTagsVisibility(false));
  listElement.addEventListener('mousedown', (e) => e.preventDefault());

  input.addEventListener('focus', (e) => setTimeout(() => showSuggestion(e), 1));
  input.addEventListener('input', showSuggestion);
  input.addEventListener('mousedown', showSuggestion);
  remove.addEventListener('mousedown', (e) => e.preventDefault());
  remove.addEventListener('click', removeAllTags);
}
