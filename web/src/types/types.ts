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

export interface ApiErrorData {
  error: string;
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

export interface ApiSaveData {
  status: string;
  jobId: string;
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
  // valid: boolean;
}

export interface Globals {
  selected: number;
  tags: Set<string>;
  spliter: RegExp;
}

// Declare the global window variable you were using
declare global {
  interface Window {
    allTags: Set<string>;
  }
}
