<!--
  @component
  An autocomplete input for fuzzy selection of suggestions.
-->
<script lang="ts">
  import { createEventDispatcher } from "svelte";

  import type { KeySpec } from "./keyboard-shortcuts";
  import { keyboardShortcut } from "./keyboard-shortcuts";
  import { fuzzyfilter, fuzzywrap } from "./lib/fuzzy";

  const dispatch = createEventDispatcher<{
    blur: HTMLInputElement;
    enter: HTMLInputElement;
    select: HTMLInputElement;
  }>();

  /** The currently entered value. */
  export let value: string;
  /** The suggestions for the value. */
  export let suggestions: readonly string[];
  /** A placeholder for the input field. */
  export let placeholder = "";
  /** A function to extract the string that should be used for suggestion filtering. */
  export let valueExtractor:
    | ((val: string, input: HTMLInputElement) => string)
    | null = null;
  /** A function to update the value after selecting a suggestion. */
  export let valueSelector:
    | ((val: string, input: HTMLInputElement) => string)
    | null = null;
  /** Automatically adjust the size of the input element. */
  export let setSize = false;
  /** An optional class name to assign to the input element. */
  export let className: string | undefined = undefined;
  /** A key binding to add for this input. */
  export let key: KeySpec | undefined = undefined;
  /** A function that checks the entered value for validity. */
  export let checkValidity: ((val: string) => string) | undefined = undefined;
  /** Whether to show a button to clear the input. */
  export let clearButton = false;

  let filteredSuggestions: { suggestion: string; innerHTML: string }[] = [];
  let hidden = true;
  let index = -1;
  let input: HTMLInputElement;

  $: size = setSize
    ? Math.max(value.length, placeholder.length) + 1
    : undefined;

  $: if (input && checkValidity) {
    input.setCustomValidity(checkValidity(value));
  }

  $: {
    const val = input && valueExtractor ? valueExtractor(value, input) : value;
    const filtered = fuzzyfilter(val, suggestions)
      .slice(0, 30)
      .map((suggestion) => ({
        suggestion,
        innerHTML: fuzzywrap(val, suggestion),
      }));
    filteredSuggestions =
      filtered.length === 1 && filtered[0]?.suggestion === val ? [] : filtered;
    index = Math.min(index, filteredSuggestions.length - 1);
  }

  let suggestionSelected = true;

  function select(suggestion: string) {
    value =
      input && valueSelector ? valueSelector(suggestion, input) : suggestion;
    dispatch("select", input);
    hidden = true;
    suggestionSelected = true;
  }

  function mousedown(event: MouseEvent, suggestion: string) {
    if (event.button === 0) {
      select(suggestion);
    }
  }

  function keydown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      let suggestion = filteredSuggestions[index]?.suggestion;

      // if enter press without selecting anything
      // default to the first one
      if (index == -1 && filteredSuggestions.length > 0) {
        suggestion = filteredSuggestions[0]?.suggestion;
      }
      if (!hidden && suggestion) {
        event.preventDefault();
        select(suggestion);
      } else {
        dispatch("enter", input);
      }
    } else if (event.key === " " && event.ctrlKey) {
      hidden = false;
    } else if (event.key === "Escape") {
      if (!hidden && filteredSuggestions.length > 0) {
        event.stopPropagation();
        index = -1;
      }
      event.stopPropagation();
      input.blur();
      hidden = true;
      suggestionSelected = true;
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      index = index === 0 ? filteredSuggestions.length - 1 : index - 1;
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      index = index === filteredSuggestions.length - 1 ? 0 : index + 1;
    } else if (event.key === "Tab" && !suggestionSelected) {
      event.preventDefault();
      event.stopPropagation();
      index = index === filteredSuggestions.length - 1 ? 0 : index + 1;

      // if press tab with only 1 choice, choose it
      if (index == 0 && filteredSuggestions.length == 1) {
        let suggestion = filteredSuggestions[0]?.suggestion;

        if (suggestion) {
          select(suggestion);
        }
      }
    }
  }
</script>

<span class={className}>
  <input
    type="text"
    autocomplete="off"
    bind:value
    bind:this={input}
    use:keyboardShortcut={key}
    on:blur={() => {
      hidden = true;
      suggestionSelected = true;
      dispatch("blur", input);
    }}
    on:focus={() => {
      hidden = false;
      suggestionSelected = true;
    }}
    on:input={() => {
      hidden = false;
      suggestionSelected = false;
    }}
    on:keydown={keydown}
    {placeholder}
    {size}
  />
  {#if clearButton && value}
    <button
      type="button"
      tabindex={-1}
      class="muted round"
      on:click={() => {
        value = "";
        dispatch("select", input);
      }}
    >
      ×
    </button>
  {/if}
  {#if filteredSuggestions.length}
    <ul {hidden}>
      {#each filteredSuggestions as { innerHTML, suggestion }, i}
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <li
          class:selected={i === index}
          on:mousedown={(ev) => {
            mousedown(ev, suggestion);
          }}
        >
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html innerHTML}
        </li>
      {/each}
    </ul>
  {/if}
</span>

<style>
  span {
    position: relative;
    display: inline-block;
  }

  input {
    width: 100%;
  }

  ul {
    position: absolute;
    z-index: var(--z-index-autocomplete);
    overflow-x: hidden;
    overflow-y: auto;
    background-color: var(--background);
    border: 1px solid var(--border-darker);
    box-shadow: 0 3px 3px var(--border);
  }

  :global(aside) ul {
    /* the only way to get the list to overflow the
       aside is to put it in fixed position */
    position: fixed;
  }

  li {
    min-width: 8rem;
    padding: 0 0.5em;
    white-space: nowrap;
    cursor: pointer;
  }

  li.selected,
  li:hover {
    color: var(--background);
    background-color: var(--link-color);
  }

  button {
    position: absolute;
    top: 8px;
    right: 4px;
    background: transparent;
  }

  li :global(span) {
    height: 1.2em;
    padding: 0 0.05em;
    margin: 0 -0.05em;
    background-color: var(--autocomplete-match);
    border-radius: 2px;
  }
</style>
