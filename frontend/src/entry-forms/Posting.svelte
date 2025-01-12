<script lang="ts">
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import type { Posting } from "../entries";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { currencies } from "../stores";
  import { isEditingEntry } from "../stores/misc";

  import AccountInput from "./AccountInput.svelte";

  export let posting: Posting;
  export let index: number;
  export let suggestions: string[] | undefined;
  export let date: string | undefined;
  export let move: (arg: { from: number; to: number }) => void;
  export let remove: () => void;
  export let add: () => void;

  let debitValue: string = "";
  let creditValue: string = "";
  let entryError: boolean = false;

  if ($isEditingEntry) {
    console.log(posting.amount);
    let val = parseFloat(posting.amount);
    if (val > 0) {
      debitValue = posting.amount;
    } else {
      creditValue = posting.amount.replace("-", "");
    }
    entryError = false;
  }

  $: {
    try {
      let a = parseFloat(debitValue);
      let b = parseFloat(creditValue);
      if (a > 0 && Number.isNaN(b)) {
        posting.amount = debitValue;
        entryError = false;
      } else if (b > 0 && Number.isNaN(a)) {
        posting.amount = `-${creditValue}`;
        entryError = false;
      } else {
        posting.amount = "";
        entryError = true;
      }
    } catch {
      posting.amount = "";
      entryError = true;
    }
  }

  $: checkValidity = (val: string) =>
    entryError ? _("Debit Credit error") : "";

  let debit_amount_number = "";
  let debitAmountSuggestions: string[] = [];
  let credit_amount_number = "";
  let creditAmountSuggestions: string[] = [];
  $: {
    debit_amount_number = debitValue.replace(/[^\-?0-9.]/g, "");
    debitAmountSuggestions = $currencies.map(
      (c) => `${debit_amount_number} ${c}`,
    );
    credit_amount_number = creditValue.replace(/[^\-?0-9.]/g, "");
    creditAmountSuggestions = $currencies.map(
      (c) => `${credit_amount_number} ${c}`,
    );
  }

  let drag = false;
  let draggable = true;

  function mousemove(event: MouseEvent) {
    draggable = !(event.target instanceof HTMLInputElement);
  }
  function dragstart(event: DragEvent) {
    event.dataTransfer?.setData("fava/posting", `${index}`);
  }
  function dragenter(event: DragEvent) {
    if (event.dataTransfer?.types.includes("fava/posting")) {
      event.preventDefault();
      drag = true;
    }
  }
  function dragleave() {
    drag = false;
  }
  function drop(event: DragEvent) {
    const from = event.dataTransfer?.getData("fava/posting");
    if (from) {
      move({ from: +from, to: index });
      drag = false;
    }
  }
</script>

<div
  class="flex-row"
  class:drag
  {draggable}
  on:mousemove={mousemove}
  on:dragstart={dragstart}
  on:dragenter={dragenter}
  on:dragover={dragenter}
  on:dragleave={dragleave}
  on:drop|preventDefault={drop}
  role="group"
>
  <button
    type="button"
    class="muted round remove-row"
    on:click={remove}
    tabindex={-1}
  >
    ×
  </button>
  <AccountInput
    className="grow"
    bind:value={posting.account}
    {suggestions}
    {date}
  />
  <AutocompleteInput
    className="amount"
    placeholder={_("Debit Amount")}
    suggestions={debitAmountSuggestions}
    bind:value={debitValue}
    {checkValidity}
  />
  <AutocompleteInput
    className="amount"
    placeholder={_("Credit Amount")}
    suggestions={creditAmountSuggestions}
    bind:value={creditValue}
    {checkValidity}
  />
  <button
    type="button"
    class="muted round add-row"
    on:click={add}
    on:keydown={add}
    title={_("Add posting")}
  >
    +
  </button>
</div>

<style>
  .drag {
    box-shadow: 0 0 5px var(--text-color);
  }

  div {
    padding-left: 50px;
    cursor: grab;
  }

  div > * {
    cursor: initial;
  }

  div .add-row {
    display: none;
  }

  div:last-child .add-row {
    display: initial;
  }

  div :global(.amount) {
    width: 220px;
  }

  div:last-child :global(.amount) {
    width: 192px;
  }

  @media (width <= 767px) {
    div {
      padding-left: 0;
    }
  }
</style>
