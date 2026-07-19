import { Globals, Query } from '../types/types';

const tagsInput = <HTMLInputElement>document.getElementById('tags-id');
const listElement = <HTMLDivElement>document.getElementById('autocomplete-list');
const globals: Globals = {
  selected: 0,
  tags: new Set(),
  spliter: /[,\s]+/g,
};

function toggleTagsVisibility(visible: boolean) {
  listElement.dataset.visible = String(visible);

  if (visible) {
    listElement.classList.add('show');
  } else {
    listElement.classList.remove('show');
  }

  globals.selected = -1;
}

function selectNext(e: KeyboardEvent) {
  const span = document.getElementById('test-id');

  if (listElement.dataset.visible && ['ArrowDown', 'ArrowUp'].includes(e.code)) {
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
    }

    globals.selected = selected;

    e.preventDefault();
  }

  if (listElement.dataset.visible && e.code === 'Enter' && globals.selected >= 0) {
    const item = <HTMLUListElement>listElement.children[globals.selected];

    if (item && item.firstChild) {
      (item.firstChild as HTMLInputElement).click();
    }

    e.preventDefault();
  }
}

function selectTag(query: Query, tagName: string) {
  if (listElement.dataset.visible) {
    const caret =
      query.list.slice(0, query.index).reduce((acc, v) => acc + v.length + 2, 0) +
      tagName.length;

    query.list[query.index] = tagName;
    tagsInput.value = query.list.join(', ');
    tagsInput.setSelectionRange(caret, caret);

    toggleTagsVisibility(false);
  }
}

function isCursorInsideWord(str: string, pos: number) {
  const value = str + ' ';
  const wordRegex = /\w/;

  const charBefore = value.charAt(pos - 1);
  const charAfter = value.charAt(pos);

  // The cursor is inside a word if the character before OR after it is a word character
  return wordRegex.test(charBefore) || wordRegex.test(charAfter);
}

function getWordAtCursor(text: string, position: number) {
  const left = text.slice(0, position).split(globals.spliter);
  const right = text.slice(position).split(globals.spliter);

  // Extract and return the word
  return left[left.length - 1] + right[0];
}

function buildQuery(value: string, cursor: number): Query {
  const queryList = value.substring(0, cursor).split(globals.spliter);

  let query = queryList[queryList.length - 1] || '';
  const tags = new Set(value.split(globals.spliter).filter((v) => v));

  if (isCursorInsideWord(value, cursor)) {
    const word = getWordAtCursor(value, cursor);

    if (word) {
      query = word;
    }
  }

  return {
    value: query,
    tags: tags,
    index: queryList.length - 1,
    list: Array.from(new Set(queryList.concat([...tags]))),
  };
}

function suggestTags(e: Event) {
  const input = e.target as HTMLInputElement;

  if (input.selectionStart === input.selectionEnd) {
    const query = buildQuery(input.value.toLowerCase(), input.selectionStart || 0);

    listElement.innerHTML = '';
    globals.selected = -1;

    const matches = [...globals.tags].filter(
      (i) => i.includes(query.value) && !query.tags.has(i)
    );

    for (let i = 0; i < matches.length; i++) {
      const match = matches[i];
      const item = document.createElement('li');
      const input = document.createElement('input');

      input.type = 'button';
      input.className = 'dropdown-item';
      input.value = match;

      input.addEventListener('click', () => selectTag(query, match));

      item.appendChild(input);
      listElement.appendChild(item);
    }

    toggleTagsVisibility(matches?.length > 0);
  }
}

export function registerTagList(value: Set<string>) {
  globals.tags = value;
}

export function registerEventListeners() {
  tagsInput.addEventListener('keydown', selectNext);
  tagsInput.addEventListener('blur', (e) => toggleTagsVisibility(false));
  tagsInput.addEventListener('focus', suggestTags);
  tagsInput.addEventListener('selectionchange', suggestTags);
  listElement.addEventListener('mousedown', (e) => e.preventDefault());
}
