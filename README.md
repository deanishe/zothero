<div align="center">
    <img src="./src/icon.png" width="200" height="200">
</div>

ZotHero
=======

Alfred 3 workflow for searching your Zotero database and copying citations.

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Usage](#usage)
- [Configuration](#configuration)
    - [Zotero data](#zotero-data)
    - [Citation styles](#citation-styles)
    - [All settings](#all-settings)
- [Licence & thanks](#licence--thanks)

<!-- /MarkdownTOC -->

<a name="usage"></a>
Usage
-----

- `zot <query>` — Search your Zotero database (all fields).
    - `↩` — Open the entry in Zotero.
    - `⌘↩` — Copy citation to the pasteboard (see [Configuration](#configuration)).
    - `⌥↩` — Copy bibliography-style citation to the pasteboard (see [Configuration](#configuration)).
    - `⇧↩` — View entry attachments (if present).
        - `↩` — Open an attachment in the default application.
    - `^↩` — View all citation styles.
        - `↩` or `⌘↩` — Copy citation in selected style.
        - `⌥↩` — Copy bibliography-style citation in selected style.
        - `^↩` — Set style as default.
- `zot:[<query>]` — Search a specific field.
    - `↩` — Select a field to search against.
- `zotconf [<query>]` — View and edit workflow configuration.
    - `An Update is Available` / `Workflow is Up To Date` — Whether a newer version of the workflow is available.
    - `Default Style: …` — Choose citation style for the `⌘↩` and `⌥↩` hotkeys (on search results).
    - `Reload Zotero Cache` — Clear the workflow's cache of Zotero data. Useful if the workflow gets out of sync with Zotero.
    - `Open Log File` — Open the workflows log file in the default app (usually Console.app). Useful for checking on indexing problems (the indexer output isn't visible in Alfred's debugger).
    - `View Documentation` — Open this README in your browser.
    - `Report an Issue` — Open the GitHub issue tracker in your browser.


<a name="configuration"></a>
Configuration
-------------

The workflow partly manages its own configuration with the keyword `zotconf`, but you may need to use the [workflow configuration sheet][conf-sheet] if you don't use Zotero 5's default data directory.


<a name="zotero-data"></a>
### Zotero data ###

The workflow uses your Zotero database and styles, therefore it needs to know where to find them. By default, the workflow looks in `~/Zotero` (the default location for Zotero 5).

If you data are stored somewhere else, you need to set `ZOTERO_DIR` in the [workflow configuration sheet][conf-sheet].

If you have set a "Linked Attachment Base Directory" in Zotero, enter its path for `ATTACHMENTS_DIR` in the [configuration sheet][conf-sheet].


<a name="citation-styles"></a>
### Citation styles ###

The workflow uses the CSL styles you have installed in Zotero, so to add a new style, simply add it in Zotero. The workflow will pick up the new style(s) on the next run.

You can copy either a citation-/note-style citation or a bibliography-style one by hitting `⌘↩` or `⌥↩` respectively on a search result or citation style.

For `⌘↩` and `⌥↩` to work on search results, you must first choose a default style. You can either do this in the configuration screen (keyword `zotconf`), or hitting `^↩` on a search result to show all citation styles, then `^↩` on a style to set that as the default.


<a name="all-settings"></a>
### All settings ###

Theses are all settings available in the [workflow configuration sheet][conf-sheet].

You probably shouldn't edit the `CITE_STYLE` or `LOCALE` variables yourself, as there's no guarantee the value you set is actually available. Adjust them using the `zotconf` keyword.


|      Variable     |                  Meaning                   |
|-------------------|--------------------------------------------|
| `ATTACHMENTS_DIR` | Path to your Zotero attachments.           |
| `CITE_STYLE`      | Citation style copied by `⌘↩` and `⌥↩`     |
| `LOCALE`          | Locale for citations. Default: US English. |
| `ZOTERO_DIR`      | Path to your Zotero data.                  |


<a name="licence--thanks"></a>
Licence & thanks
----------------

This workflow is released under the [MIT licence][licence].

It is heavily based on the [Alfred-Workflow][aw] (also MIT) and [citeproc-ruby][citeproc-ruby] ([AGPL][citeproc-licence]) libraries.

The [Zorro icon][icon-source] was created by [Dan Lowenstein][lowenstein] from [the Noun Project][noun-project].



[aw]: http://www.deanishe.net/alfred-workflow/
[citeproc-ruby]: https://github.com/inukshuk/citeproc-ruby
[citeproc-licence]: https://github.com/inukshuk/citeproc-ruby/blob/master/AGPL
[conf-sheet]: https://www.alfredapp.com/help/workflows/advanced/variables/#environment
[icon-source]: https://thenounproject.com/term/zorro/14540/
[lowenstein]: https://thenounproject.com/danny_mustache
[licence]: ./LICENCE
[noun-project]: https://thenounproject.com
