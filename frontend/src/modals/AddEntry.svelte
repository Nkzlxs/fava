<script lang="ts">
  import { saveEntries } from "../api";
  import { Balance, Note, Transaction } from "../entries";
  import Entry from "../entry-forms/Entry.svelte";
  import { todayAsString } from "../format";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { addEntryContinue } from "../stores/editor";
  import { entryBalanceAmount, isEntryBalanced } from "../stores/misc";
  import { closeOverlay, urlHash } from "../stores/url";

  import ModalBase from "./ModalBase.svelte";

  /** The entry types which have support adding in the modal. */
  const entryTypes = [
    [Transaction, _("Transaction")],
    [Balance, _("Balance")],
    [Note, _("Note")],
  ] as const;

  // For the first entry to be added, use today as the default date.
  let entry: Transaction | Balance | Note = new Transaction(todayAsString());

  async function submit() {
    await saveEntries([entry]);
    const added_entry_date = entry.date;
    // Reuse the date of the entry that was just added.
    entry = new Transaction(todayAsString());
    console.log("clsoe over lay!!!");
    closeOverlay();
  }

  $: shown = $urlHash === "add-transaction";
</script>

<ModalBase {shown} focus=".payee input">
  <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
  <form on:submit|preventDefault={submit}>
    <h3>
      {_("Add")}
      {#each entryTypes as [Cls, displayName]}
        <button
          type="button"
          class:muted={!(entry instanceof Cls)}
          on:click={() => {
            // when switching between entry types, keep the date.
            entry = new Cls(entry.date);
          }}
        >
          {displayName}
        </button>
        {" "}
      {/each}
    </h3>
    <Entry bind:entry />
    {#if !$isEntryBalanced}
      <div class="flex-row">
        <span class="spacer" />
        Not balanced: {$entryBalanceAmount}
      </div>
    {/if}

    <div class="flex-row">
      <span class="spacer" />
      <label>
        <input type="checkbox" bind:checked={$addEntryContinue} />
        <span>{_("continue")}</span>
      </label>
      <button
        type="submit"
        disabled={!$isEntryBalanced}
        use:keyboardShortcut={{ key: "Control+s", mac: "Meta+s" }}
      >
        {_("Save")}
      </button>
    </div>
  </form>
</ModalBase>

<style>
  label span {
    margin-right: 1rem;
  }
</style>
