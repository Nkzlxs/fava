<script lang="ts" context="module">
  const TAGS_RE = /(?:^|\s)#([A-Za-z0-9\-_/.]+)/g;
  const LINKS_RE = /(?:^|\s)\^([A-Za-z0-9\-_/.]+)/g;
</script>

<script lang="ts">
  import { get } from "../api";
  import AutocompleteInput from "../AutocompleteInput.svelte";
  import { emptyPosting } from "../entries";
  import type { Posting, Transaction } from "../entries";
  import { _ } from "../i18n";
  import { notify_err } from "../notifications";
  import { payees } from "../stores";
  import {
    isEditingEntry,
    entryBalanceAmount,
    isEntryBalanced,
  } from "../stores/misc";
  import { format, parse } from "date-fns";

  import AddMetadataButton from "./AddMetadataButton.svelte";
  import EntryMetadata from "./EntryMetadata.svelte";
  import PostingSvelte from "./Posting.svelte";
  import { onMount } from "svelte";

  export let entry: Transaction;
  let suggestions: string[] | undefined;

  function removePosting(posting: Posting) {
    console.log(posting);
    // TODO the before entry.postings already wrong
    console.log(entry.postings);

    entry.postings = [...entry.postings.filter((p) => p !== posting)];
    console.log(entry.postings);
  }

  function addPosting() {
    entry.postings = entry.postings.concat(emptyPosting());
  }

  $: payee = entry.payee;
  $: if (payee) {
    suggestions = undefined;
    if ($payees.includes(payee)) {
      get("payee_accounts", { payee })
        .then((s) => {
          suggestions = s;
        })
        .catch((error) => {
          notify_err(
            error,
            (err) =>
              `Fetching account suggestions for payee ${payee} failed: ${err.message}`,
          );
        });
    }
  }

  /// Extract tags and links that can be provided in the narration <input>.
  function onNarrationChange({
    currentTarget,
  }: {
    currentTarget: HTMLInputElement;
  }) {
    const { value } = currentTarget;
    entry.tags = [...value.matchAll(TAGS_RE)].map((a) => a[1] ?? "");
    entry.links = [...value.matchAll(LINKS_RE)].map((a) => a[1] ?? "");
    entry.narration = value
      .replaceAll(TAGS_RE, "")
      .replaceAll(LINKS_RE, "")
      .trim();
  }

  /// Output tags and links in the narration <input>
  function combineNarrationTagsLinks(e: Transaction): string {
    let val = e.narration;
    if (e.tags.length) {
      val += ` ${e.tags.map((t) => `#${t}`).join(" ")}`;
    }
    if (e.links.length) {
      val += ` ${e.links.map((t) => `^${t}`).join(" ")}`;
    }
    return val;
  }
  $: narration = combineNarrationTagsLinks(entry);

  // Autofill complete transactions.
  async function autocompleteSelectPayee() {
    if (entry.narration || !entry.postings.every((p) => !p.account)) {
      return;
    }
    const data = await get("payee_transaction", { payee: entry.payee });
    data.date = entry.date;
    entry = data;
  }

  function movePosting({ from, to }: { from: number; to: number }) {
    const moved = entry.postings[from];
    if (moved) {
      entry.postings.splice(from, 1);
      entry.postings.splice(to, 0, moved);
      entry.postings = entry.postings;
    }
  }

  // check for balanced entry every render
  $: {
    $entryBalanceAmount = 0;
    entry.postings.forEach((aPost) => {
      if (aPost.amount == "") {
        $entryBalanceAmount += 0;
      } else {
        $entryBalanceAmount += Math.round(parseFloat(aPost.amount) * 100) / 100;
      }
    });
    $entryBalanceAmount = Math.round($entryBalanceAmount * 100) / 100;
    if ($entryBalanceAmount !== 0) {
      $isEntryBalanced = false;
    } else {
      $isEntryBalanced = true;
    }
  }

  let currentDateString = returnDateString(entry.date);

  function updateDate() {
    currentDateString = returnDateString(currentDateString);
    entry.date = currentDateString;
  }

  function returnDateString(dateString: string) {
    // Format strings for the expected date formats
    const formatStrings = [
      "dd MMM yyyy",
      "d MMM yyyy",
      "yyyy MMM d",
      "yyyy MMM dd",
      "yyyy MM d",
      "yyyy MM dd",
      "yyyy/MM/dd",
      "yyyy-MM-dd",
      "yyyy/MMM/dd",
      "yyyyMMdd",
    ];

    let parsedDate: number | Date | null = null;
    let formattedDate = "Invalid date"; // Default to "Invalid date"

    formatStrings.forEach((dateFormat) => {
      if (parsedDate === null) {
        // Check if the date has been successfully parsed
        const parsed = parse(dateString, dateFormat, new Date());

        if (!isNaN(parsed.getTime())) {
          // Check if the parsing was successful
          parsedDate = parsed;
          formattedDate = format(parsedDate, "yyyy-MM-dd");
        }
      }
    });

    return formattedDate;
  }

  let firstInput: HTMLInputElement;
  onMount(() => {
    firstInput.focus();
  });
</script>

<div>
  <div class="flex-row">
    <input
      type="text"
      bind:value={currentDateString}
      on:blur={updateDate}
      bind:this={firstInput}
      required
    />
    <input type="text" name="flag" bind:value={entry.flag} required />
    <!-- svelte-ignore a11y-label-has-associated-control -->
    <label>
      <span>{_("Payee")}:</span>
      <AutocompleteInput
        className="payee"
        placeholder={_("Payee")}
        bind:value={entry.payee}
        suggestions={$payees}
        on:select={autocompleteSelectPayee}
      />
    </label>
    <label>
      <span>{_("Narration")}:</span>
      <input
        type="text"
        name="narration"
        placeholder={_("Narration")}
        value={narration}
        on:change={onNarrationChange}
      />
      <AddMetadataButton bind:meta={entry.meta} />
    </label>
    <button
      type="button"
      class="muted round"
      on:click={addPosting}
      title={_("Add posting")}
      tabindex={-1}
    >
      p
    </button>
  </div>
  <EntryMetadata bind:meta={entry.meta} />
  <div class="flex-row">
    <span class="label"> <span>{_("Postings")}:</span> </span>
  </div>
  {#each entry.postings as posting, index}
    <PostingSvelte
      bind:posting
      {index}
      {suggestions}
      date={entry.date}
      add={addPosting}
      move={movePosting}
      remove={() => {
        removePosting(posting);
      }}
    />
  {/each}
</div>

<style>
  input[name="flag"] {
    width: 1.5em;
    padding-right: 2px;
    padding-left: 2px;
    text-align: center;
  }

  div :global(.payee) {
    flex-basis: 100px;
    flex-grow: 1;
  }

  input[name="narration"] {
    flex-basis: 200px;
    flex-grow: 1;
  }

  label > span:first-child,
  .label > span:first-child {
    display: none;
  }

  @media (width <= 767px) {
    label > span:first-child,
    .label > span:first-child {
      display: initial;
      width: 100%;
    }
  }
</style>
