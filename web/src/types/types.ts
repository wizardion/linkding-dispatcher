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
  allTags: string[];
  activeTags: string[];
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
  value: string;
  index: number;
  tags: Set<string>;
  list: string[];
}

export interface Globals {
  selected: number;
  tags: Set<string>;
  spliter: RegExp;
  ltrimmer: RegExp;
}

// Declare the global window variable you were using
declare global {
  interface Window {
    allTags: Set<string>;
  }
}
