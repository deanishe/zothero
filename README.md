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
    - `⌥↩` — Copy citation to the pasteboard (see [Configuration](#configuration)).
    - `⇧↩` — View entry attachments (if present).
        - `↩` — Open an attachment in the default application.
    - `^↩` — View all citation styles.
        - `↩` — Copy citation in selected style.
        - `⌘↩` — Set style as default for `⌘↩`.
        - `⌥↩` — Set style as default for `⌥↩`.
- `zot:[<query>]` — Search a specific field.
    - `↩` — Select a field to search against.
- `zotconf [<query>]` — View and edit workflow configuration.
    - `An Update is Available` / `Workflow is Up To Date` — Whether a newer version of the workflow is available.
    - `⌘↩ Style: …` and `⌥↩ Style: …` — Choose citation styles set for the `⌘↩` and `⌥↩` hotkeys (on search results).
    - `Reload Zotero Cache` — Clear the workflow's cache of Zotero data. Useful if the workflow gets out of sync with Zotero.
    - `View Documentation` — Open this README in your browser.
    - `Report an Issue` — Open the GitHub issue tracker in your browser.


<a name="configuration"></a>
Configuration
-------------

The workflow partly manages its own configuration, but you may need to use the [workflow configuration sheet][conf-sheet] if you don't use Zotero 5's default data directory.


<a name="zotero-data"></a>
### Zotero data ###

The workflow uses your Zotero database and styles, therefore it needs to know where to find them. By default, the workflow looks in `~/Zotero` (the default location for Zotero 5).

If you data are stored somewhere else, you need to set `ZOTERO_DIR` in the [workflow configuration sheet][conf-sheet].

If you have set a "Linked Attachment Base Directory" in Zotero, enter its path for `ATTACHMENTS_DIR` in the [configuration sheet][conf-sheet].


<a name="citation-styles"></a>
### Citation styles ###

The workflow uses the CSL styles you have installed in Zotero, so to add a new style, simply add it in Zotero. The workflow will pick up the new style(s) on the next run.

To quickly copy citations using `⌘↩` and `⌥↩`, you must first assign citation styles to them. To do this, hit `^↩` on an entry to show all available styles, then use `⌘↩` or `⌥↩` on a style to set that as the default for that key combo.


<a name="all-settings"></a>
### All settings ###

Theses are all settings available in the [workflow configuration sheet][conf-sheet].

You probably shouldn't edit the `CITE_*` variables yourself, as they need to be set to the internal ID of the style. Set them using the method described [above](#citation-styles).


|      Variable     |             Meaning              |
|-------------------|----------------------------------|
| `ATTACHMENTS_DIR` | Path to your Zotero attachments. |
| `CITE_CMD`        | Citation style copied by `⌘↩`    |
| `CITE_OPT`        | Citation style copied by `⌘⌥`    |
| `ZOTERO_DIR`      | Path to your Zotero data.        |


<a name="licence--thanks"></a>
Licence & thanks
----------------

This workflow is released under the [MIT licence][licence].

It is heavily based on the [citeproc][citeproc] ([BSD][citeproc-licence]) and [Alfred-Workflow][aw] (also MIT) libraries.

The [Zorro icon][icon-source] was created by [Dan Lowenstein][lowenstein] from [the Noun Project][noun-project].



[aw]: http://www.deanishe.net/alfred-workflow/
[citeproc]: https://pypi.python.org/pypi/citeproc-py/
[citeproc-licence]: https://github.com/brechtm/citeproc-py/blob/master/LICENSE
[conf-sheet]: https://www.alfredapp.com/help/workflows/advanced/variables/#environment
[icon-source]: https://thenounproject.com/term/zorro/14540/
[lowenstein]: https://thenounproject.com/danny_mustache
[licence]: ./LICENCE
[noun-project]: https://thenounproject.com
