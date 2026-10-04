import { Globals, Positioning, Query, TagsQuery } from '../types/types';

const listElement = <HTMLDivElement>document.getElementById('autocomplete-list');
const globals: Globals = {
  selected: 0,
  allTags: new Set(),
  spliter: /[,\s]+/g,
  ltrimmer: /^[,\s]+/g,
};

function toggleTagsVisibility(visible: boolean) {
  listElement.dataset.visible = String(visible);

  if (visible) {
    listElement.classList.add('show');
  } else {
    listElement.classList.remove('show');
  }

  globals.selected = 0;
}

function selectTag(input: HTMLInputElement, query: Query, tagName: string) {
  if (listElement.dataset.visible == 'true') {
    const words = query.list
      .slice(0, query.index)
      .concat(tagName, query.list.slice(query.index + 1))
      .filter((v) => !!v);

    const tags = [...new Set(words)];
    const caret =
      tags.slice(0, query.index).reduce((acc, v) => acc + v.length + 2, 0) +
      tagName.length;

    input.value = tags.join(', ');
    input.setSelectionRange(caret, caret);

    toggleTagsVisibility(false);

    globals.allTags.add(tagName);
  }
}

function buildQuery(text: string, cursor: number): Query {
  const input = text.toLowerCase();
  const left = input.substring(0, cursor);
  const right = input.substring(cursor);

  const wordsLeft = left.split(globals.spliter);
  const wordsRight = right.split(globals.spliter).filter(Boolean);

  const value = wordsLeft.length ? wordsLeft.pop() : null;
  const index = wordsLeft.length;

  return {
    index: index,
    lookup: value || '',
    list: wordsLeft.concat('', wordsRight),
    tagged: new Set(wordsLeft.concat(wordsRight).filter((v) => globals.allTags.has(v))),
  };
}

function searchInQuery(query: Query): string[] {
  if (query.lookup && globals.allTags.has(query.lookup)) {
    return [];
  }

  const matches = !query.lookup
    ? [...globals.allTags]
    : [...globals.allTags].filter((i) => i.startsWith(query.lookup));

  matches.sort((a, b) => {
    const aStarts = a.startsWith(query.lookup);
    const bStarts = b.startsWith(query.lookup);

    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;

    return a.localeCompare(b);
  });

  return matches.length ? matches.filter((v) => !query.tagged.has(v)) : [query.lookup];
}

// ------------------------------------------------------------------------------------
function showSuggestion(e: Event) {
  const input = e.target as HTMLInputElement;
  const query = buildQuery(input.value, input.selectionStart || 0);
  const matches = searchInQuery(query);

  listElement.innerHTML = '';
  listElement.scrollTop = 0;
  globals.selected = 0;

  for (let i = 0; i < matches.length; i++) {
    const match = matches[i];
    const item = document.createElement('li');
    const input = document.createElement('input');

    input.type = 'button';
    input.className = 'dropdown-item pt-2 pb-2';
    input.value = match;

    input.addEventListener('click', (e) => {
      e.preventDefault();
      selectTag(input, query, match);
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
}

function removeAllTags(e: Event) {
  console.log('revove all');
}

// -----------------------------------------------------------------------------------
export function registerTagList(tags: string[]) {
  const input = <HTMLInputElement>document.getElementById('tags-id');
  const existingTags = input.value
    .split(globals.spliter)
    .filter((v) => v)
    .map((v) => v.toLowerCase());

  globals.allTags = new Set(existingTags.concat(tags.map((i) => i.toLowerCase())));
}

export function registerEventListeners() {
  const input = <HTMLInputElement>document.getElementById('tags-id');
  const remove = <HTMLInputElement>document.getElementById('tags-remove-all');

  // tagsInput.addEventListener('keydown', onKeyPress);
  // tagsInput.addEventListener('blur', (e) => toggleTagsVisibility(false));
  // tagsInput.addEventListener('blur', (e) => validate);
  // listElement.addEventListener('mousedown', (e) => e.preventDefault());

  input.addEventListener('input', showSuggestion);
  remove.addEventListener('click', removeAllTags);
}
