// import { Globals, Positioning, TagsQuery } from '../types/types';

// const globalsTags: Globals = {
//   selected: 0,
//   tags: new Set(),
//   input: new Set(),
//   spliter: /([,\s]+)/g,
//   ltrimmer: /^[,\s]+/g,
// };

/*

function buildQuery(text: string, cursor: number): any {
  const input = text.toLowerCase();
  const left = input.substring(0, cursor);
  const right = input.substring(cursor);

  const tokensLeft = left.split(globals.spliter);
  const tokensRight = right.split(globals.spliter);

  console.log('tokens', tokensLeft, tokensRight);

  const pred = (t: string, i: number) => {
    if (i % 2 === 0) {
      // word
      return true;
    } else {
    }

    return false;
  };

  const l = tokensLeft.filter(pred);
  const r = tokensRight.filter(pred);

  console.log('tokens-2', l, r);
}

*/

// export function registerInputTags(tags: string[]) {
//   globalsTags.input = new Set(tags.map((tag) => tag.toLowerCase()));
// }

// // "pics, tech, content|"
// // "   ,   pics, tech, content, zebra, "
// export function buildQuery2(text: string, cursor: number): any {
//   const input = text.toLowerCase();
//   const tokens = input.split(globalsTags.spliter);
//   // const tokens = input.match(globalsTags.spliter);

//   const words = [];

//   console.log('cursor', [cursor]);

//   let currentOffset = 0;
//   let intex = -1;
//   for (let index = 0; index < tokens.length; index++) {
//     const element = tokens[index];
//     const end = currentOffset + element.length;

//     currentOffset = end;

//     if (index % 2 === 0) {
//       if (element === '') continue; // Skips empty tokens from leading/trai
//       console.log(currentOffset, 'word', [element]);
//       if (intex < 0 && currentOffset >= cursor) {
//         intex = words.length;
//       }
//       words.push(element);
//     } else {
//       console.log(currentOffset, 'separator', [element]);
//       if (intex < 0 && currentOffset >= cursor) {
//         intex = words.length;
//         words.push('');
//       }
//     }
//   }

//   console.log(intex, words);

//   // for (const match of input.matchAll(globalsTags.spliter)) {
//   //   const fullMatch = match[0]; // The separator (e.g., ", ")
//   //   const group1 = match[1]; // The captured group
//   //   const index = match.index; // Exactly where it is in the string

//   //   console.log(`Found separator: "${group1}" at index ${index}`);
//   // }
// }

// export function buildTagsQuery(text: string, cursor: number): TagsQuery {
//   const input = text.toLowerCase();
//   const words = input.split(globalsTags.spliter);
//   const position = Math.max(0, Math.min(cursor, input.length));
//   let wordIndex = 0;
//   const tokens = [...input.matchAll(/[^,\s]+/g)].map((match) => {
//     while (words[wordIndex] === '') {
//       wordIndex++;
//     }

//     return {
//       value: match[0],
//       start: match.index,
//       end: match.index + match[0].length,
//       wordIndex: wordIndex++,
//     };
//   });
//   const activeToken = tokens.find(
//     ({ start, end }) => position >= start && position <= end
//   );
//   const unknownTokens = tokens.filter(({ value }) => !globalsTags.input.has(value));

//   if (unknownTokens.length > 1) {
//     throw new Error('More than one new tag was entered.');
//   }

//   const newToken =
//     activeToken && !globalsTags.input.has(activeToken.value) ? activeToken : undefined;
//   let index = newToken?.wordIndex ?? activeToken?.wordIndex ?? words.length - 1;
//   const cursorIndex = activeToken ? position - activeToken.start : 0;
//   const cursorPosition = activeToken
//     ? position === activeToken.start
//       ? Positioning.Start
//       : position === activeToken.end
//         ? Positioning.End
//         : Positioning.Middle
//     : Positioning.Start;

//   if (!newToken) {
//     index += 1;
//   }

//   words[index] = '';

//   return {
//     value: newToken?.value ?? '',
//     tags: new Set(words.filter((word) => word && globalsTags.input.has(word))),
//     words,
//     index,
//     metrics: {
//       position: cursorPosition,
//       index: cursorIndex,
//     },
//   };
// }
