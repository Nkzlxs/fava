<script lang="ts">
  import { doDelete, get, put } from "../api";
  import { getBeancountLanguageSupport } from "../codemirror/beancount";
  import DeleteButton from "../editor/DeleteButton.svelte";
  import SaveButton from "../editor/SaveButton.svelte";
  import SliceEditor from "../editor/SliceEditor.svelte";
  import { Balance, Note, Transaction } from "../entries";
  import Entry from "../entry-forms/Entry.svelte";
  import { todayAsString } from "../format";
  import { _ } from "../i18n";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { notify_err } from "../notifications";
  import router from "../router";
  import { reloadAfterSavingEntrySlice } from "../stores/editor";
  import {
    entryBalanceAmount,
    isEditingEntry,
    isEntryBalanced,
  } from "../stores/misc";
  import { closeOverlay, urlHash } from "../stores/url";
  import ModalBase from "./ModalBase.svelte";

  // Initialize variables
  let entry: Transaction | Balance | Note;
  let content: Promise<any> | null = null;
  let sha256sum: string = "";

  let oriSlice = "";
  let currentSlice = "";
  let changed: boolean = false;
  let shown: boolean = false;
  let entry_hash: string = "";
  $: {
    changed = currentSlice !== oriSlice;

    shown = $urlHash.startsWith("context");
    entry_hash = shown ? $urlHash.slice(8) : "";

    if (entry) {
      currentSlice = entry.toString();
    }
    // Load content if it should be shown
    if (shown && content === null) {
      content = new Promise<any>((resolve, reject) => {
        get("context", { entry_hash }).then((res) => {
          const tmp = res as any;
          let entryData: Transaction = new Transaction(todayAsString());
          sha256sum = res.sha256sum;
          oriSlice = res.slice;
          entryData.date = tmp["entry"]["date"];
          entryData.meta = tmp["entry"]["meta"];
          entryData.postings = [...tmp["entry"]["postings"]]; // Clone the postings
          // TODO entryData.postings is different from the displayed one after removePosting()
          console.log(entryData.postings);

          $isEditingEntry = true;
          entry = entryData;
          resolve(res);
        });
      });
    }
  }

  let saving = false;
  let deleting = false;

  async function save() {
    saving = true;
    try {
      sha256sum = await put("source_slice", {
        entry_hash,
        source: currentSlice,
        sha256sum,
      });
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      closeThisModal();
    } catch (error) {
      notify_err(error, (err) => `Saving failed: ${err.message}`);
    } finally {
      saving = false;
    }
  }

  async function deleteSlice() {
    deleting = true;
    try {
      await doDelete("source_slice", {
        entry_hash,
        sha256sum,
      });
      entry_hash = "";
      if ($reloadAfterSavingEntrySlice) {
        router.reload();
      }
      closeThisModal();
    } catch (error) {
      notify_err(error, (err) => `Deleting failed: ${err.message}`);
    } finally {
      deleting = false;
    }
  }

  function closeThisModal() {
    content = null;
    closeOverlay();
  }
</script>

<ModalBase {shown} closeHandler={closeThisModal}>
  <div class="content">
    {#await content}
      Loading entry context...
    {:then response}
      {#if response}
        <h3>Edit Journal</h3>
        <form on:submit|preventDefault={save}>
          <Entry bind:entry />
          <!-- {#await getBeancountLanguageSupport() then beancount_language_support}
          <SliceEditor
            {entry_hash}
            slice={response.slice}
            sha256sum={response.sha256sum}
            {beancount_language_support}
          />
        {:catch}
          Loading tree-sitter language failed...
        {/await} -->
          {#if !$isEntryBalanced}
            <div class="flex-row">
              <span class="spacer" />
              Not balanced: {$entryBalanceAmount}
            </div>
          {/if}

          <div class="flex-row">
            <span class="spacer" />
            <DeleteButton {deleting} onDelete={deleteSlice} />
            <button
              type="submit"
              disabled={!$isEntryBalanced}
              use:keyboardShortcut={{ key: "Control+s", mac: "Meta+s" }}
            >
              {_("Save")}
            </button>
          </div>
        </form>
      {/if}
    {:catch error}
      Loading entry context failed: {error.message}
    {/await}
  </div>
</ModalBase>
