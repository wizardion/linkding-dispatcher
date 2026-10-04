export interface Bookmark {
  id: number | null;
  url: string;
  title: string;
  bundle: string;
  tags: string[];
  archived: boolean;
  description: string;
}

export interface Payload extends Bookmark {
  remember?: boolean;
}

export interface Metadata {
  url: string;
  title: string;
  description: string;
}

export interface Bundle {
  name: string;
  tag: string;
}

export interface UserPreference {
  bundle: string;
  tags: string[];
  archived: boolean;
  remember: boolean;
}

export interface ApiCheckData {
  url: string;
  bookmark: Bookmark | null;
}

export interface ApiMetadataData {
  url: string;
  bookmark: Bookmark | null;
  metadata: Metadata | null;
}

export interface ApiInfoData {
  tags: string[];
  bundles: Bundle[];
  preference: UserPreference;
}

/* 

{
   {
    "id": "08d1d2a26dc243fba8668c591724ae3b",
    "jobTry": 1,
    "name": "process_bookmark:migrate",
    "start": "2026-08-01T16:10:03.815000+00:00",
    "finish": "2026-08-01T16:10:06.865000+00:00",
    "enqueued": "2026-08-01T16:10:03.782000+00:00",
    "success": false
}
}
*/
export interface ApiJobInfo {
  id: string;
  jobTry: number;
  name: string;
  start: string;
  finish: string;
  enqueued: string;
  success: boolean;
}

export interface ApiJobDetails {
  jobId: string;
  status: 'queued' | 'in_progress' | 'complete';
  info?: ApiJobInfo;
}

export interface ApiResetDetails {
  success: boolean;
}

export interface UserForm {
  url: HTMLInputElement;
  title: HTMLInputElement;
  dropdown: HTMLElement;
  dropdownTitle: HTMLElement;
  bundles: RadioNodeList;
  tags: HTMLInputElement;
  session: HTMLInputElement;
  archived: HTMLInputElement;
  description: HTMLTextAreaElement;
  submit: HTMLButtonElement;
  remove: HTMLButtonElement;
  reset: HTMLLinkElement;
  headTitle: HTMLElement;
  devOptions?: {
    headTitle: HTMLElement;
  };
}

export interface ResultInfo {
  element: HTMLElement;
  title?: HTMLElement;
  message?: HTMLElement;
}

export interface Query {
  index: number;
  lookup: string;
  list: string[];
  tagged: Set<string>;
}

export enum Positioning {
  Start = 1,
  Middle = 2,
  End = 3,
}

export interface TagsQueryMetrics {
  position: Positioning;
  index: number;
}

export interface TagsQuery {
  value: string;
  tags: Set<string>;
  words: string[];
  index: number;
  metrics: TagsQueryMetrics;
}

export interface Globals {
  selected: number;
  allTags: Set<string>;
  tags: Set<string>;
  spliter: RegExp;
  ltrimmer: RegExp;
}

export interface MatchesResult {
  matches: string[];
  isNew: boolean;
}

// Declare the global window variable you were using
declare global {
  interface Window {
    allTags: Set<string>;
  }
}
