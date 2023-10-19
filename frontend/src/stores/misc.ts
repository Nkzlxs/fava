import { writable } from "svelte/store";

export const globalPostingElementRef = writable<any>();
export const entryBalanceAmount = writable<number>(0);
export const isEntryBalanced = writable<boolean>(true);
export const isEditingEntry = writable<boolean>(false);