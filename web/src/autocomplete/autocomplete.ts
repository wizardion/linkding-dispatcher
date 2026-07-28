import { Globals, Query } from '../types/types';

const tagsInput = <HTMLInputElement>document.getElementById('tags-id');
const listElement = <HTMLDivElement>document.getElementById('autocomplete-list');
const globals: Globals = {
  selected: 0,
  tags: new Set(),
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

function onKeyPress(e: KeyboardEvent) {
  const span = document.getElementById('test-id');
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
    const left = input.selectionStart || 0;
    const right = input.selectionEnd || 0;

    if (left != right || isCursorInsideWord(input.value, left)) {
      return;
    }

    const query = buildQuery(input.value, left);
    let index = query.index;
    let steps = 1;

    if (query.index < query.list.length - 1 && !query.list[index]) {
      index = query.index - 1;
      steps = 2;
    }

    if (globals.tags.has(query.list[index])) {
      query.list.splice(index, steps);

      const caret = query.list
        .slice(0, index)
        .reduce((acc, v) => acc + v.length + 2, 0);

      tagsInput.value = query.list.join(', ');
      tagsInput.setSelectionRange(caret, caret);

      e.preventDefault();
    }
  }
}

function selectTag(query: Query, tagName: string) {
  if (listElement.dataset.visible == 'true') {
    const words = query.list
      .slice(0, query.index)
      .concat(tagName, query.list.slice(query.index + 1))
      .filter((v) => !!v);

    const tags = [...new Set(words)];
    const caret =
      tags.slice(0, query.index).reduce((acc, v) => acc + v.length + 2, 0) +
      tagName.length;

    tagsInput.value = tags.join(', ');
    tagsInput.setSelectionRange(caret, caret);
    globals.tags.add(tagName);

    toggleTagsVisibility(false);
  }
}

function isCursorInsideWord(str: string, pos: number) {
  const value = str + ' ';
  const wordRegex = /\w/;

  const charBefore = value.charAt(pos - 1);
  const charAfter = value.charAt(pos);

  // The cursor is inside a word if the character before OR after it is a word character
  return wordRegex.test(charBefore) && wordRegex.test(charAfter);
}

function buildQuery(text: string, cursor: number): Query {
  const input = text.toLowerCase();
  const tags = new Set(input.split(globals.spliter));

  const left = input
    .substring(0, cursor)
    .replace(globals.ltrimmer, '')
    .split(globals.spliter);
  const right = input
    .substring(cursor)
    .replace(globals.ltrimmer, '')
    .split(globals.spliter)
    .filter((v) => !!v);

  const index = left.length - 1;
  let value = left[index] || '';

  if (left[left.length - 1] && right[0] && tags.has(left[left.length - 1] + right[0])) {
    value = left[left.length - 1] + right[0];
    right[0] = value;
  }

  if (right[0] && right[0].startsWith(input[cursor])) {
    value = right[0];
  }

  return {
    value: value,
    index: index,
    tags: tags,
    list: left.concat(right),
  };
}

function searchQuery(value: string, inputTags: Set<string>): string[] {
  if (value && globals.tags.has(value)) {
    return [];
  }

  const matches = !value
    ? [...globals.tags]
    : [...globals.tags].filter((i) => i.startsWith(value));

  matches.sort((a, b) => {
    const aStarts = a.startsWith(value);
    const bStarts = b.startsWith(value);

    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;

    return a.localeCompare(b);
  });

  return matches.length ? matches.filter((v) => !inputTags.has(v)) : [value];
}

function suggestTags(e: Event) {
  const input = e.target as HTMLInputElement;

  if (input.selectionStart === input.selectionEnd) {
    const query = buildQuery(input.value, input.selectionStart || 0);
    const matches = searchQuery(query.value, query.tags);

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

      input.addEventListener('click', () => selectTag(query, match));

      item.appendChild(input);
      listElement.appendChild(item);
    }

    if (matches.length > 0) {
      const item = listElement.children[globals.selected];

      (item.firstChild as HTMLInputElement).classList.add('active');
    }

    toggleTagsVisibility(matches?.length > 0);
  } else {
    toggleTagsVisibility(false);
  }
}

export function registerTagList(tags: string[]) {
  const existingTags = tagsInput.value
    .split(globals.spliter)
    .filter((v) => v)
    .map((v) => v.toLowerCase());

  globals.tags = new Set(existingTags.concat(tags.map((i) => i.toLowerCase())));
}

export function registerEventListeners() {
  tagsInput.addEventListener('keydown', onKeyPress);
  tagsInput.addEventListener('blur', (e) => toggleTagsVisibility(false));
  tagsInput.addEventListener('selectionchange', suggestTags);
  listElement.addEventListener('mousedown', (e) => e.preventDefault());
}
