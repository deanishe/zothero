<div align="center">
    <img src="./src/icon.png" width="200" height="200">
</div>

ZotHero
=======

[Alfred][alfred] workflow for rapidly searching your Zotero database and copying citations.

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Features](#features)
- [Download & installation](#download--installation)
- [Usage](#usage)
    - [Pasting citations](#pasting-citations)
- [Configuration](#configuration)
    - [Zotero data](#zotero-data)
    - [Citation styles](#citation-styles)
    - [Locales](#locales)
    - [All settings](#all-settings)
    - [Configuration sheet](#configuration-sheet)
- [Licence & thanks](#licence--thanks)

<!-- /MarkdownTOC -->


<a name="features"></a>
Features
--------

- Perform full-text search across your Zotero database, including only searching specific fields
- Copy citations using any [CSL][csl] style you have installed in Zotero
- Copy citations either in citation/note style or bibliography style
- Copy citations in any [locale supported by CSL](#locales)
- Citations are copied in multiple formats, so the right data are automatically pasted into the application you're using
- Trigger search while you type using the Snippet Trigger (you must assign the snippet keyword yourself in Alfred Preferences)


<a name="download--installation"></a>
Download & installation
-----------------------

Download the `ZotHero-XYZ.alfredworkflow` file from [GitHub releases](https://github.com/deanishe/zothero/releases), and double-click the downloaded file to install.


<a name="usage"></a>
Usage
-----

These are the workflow's default keywords in Alfred:

- `zot <query>` — Search your Zotero database (common fields).
    - `↩` — Open the entry in Zotero.
    - `⌘↩` — Copy citation to the pasteboard (see [Configuration](#configuration)).
    - `⌥↩` — Copy bibliography-style citation to the pasteboard (see [Configuration](#configuration)).
    - `⇧↩` — View entry attachments (if present).
        - `↩` — Open an attachment in the default application.
    - `^↩` — View all citation styles.
        - `↩` or `⌘↩` — Copy citation in selected style.
        - `⌥↩` — Copy bibliography-style citation in selected style.
        - `^↩` — Set style as default.
    - This search can also be triggered by typing a snippet (which you must first assign yourself in Alfred Preferences)
- `zot:[<query>]` — Search a specific field.
    - `↩` — Select a field to search against.
- `zotconf [<query>]` — View and edit workflow configuration.
    - `An Update is Available` / `Workflow is Up To Date` — Whether a newer version of the workflow is available.
    - `Default Style: …` — Choose a citation style for the `⌘↩` and `⌥↩` hotkeys (on search results).
    - `Locale: …` — Choose a locale for the formatting of citations. If unset, the default for the style is used, or if none is set, US English.
    - `Reload Zotero Cache` — Clear the workflow's cache of Zotero data. Useful if the workflow gets out of sync with Zotero.
    - `Open Log File` — Open the workflows log file in the default app (usually Console.app). Useful for checking on indexing problems (the indexer output isn't visible in Alfred's debugger).
    - `View Documentation` — Open this README in your browser.
    - `Report an Issue` — Open the GitHub issue tracker in your browser.


<a name="pasting-citations"></a>
### Pasting citations ###

When you copy a citation, ZotHero puts both HTML and rich text (RTF) representations on the pasteboard. That way, when you paste a citation into an application like Word, the formatted text will be pasted, but when you paste into a text/Markdown document, the HTML will be pasted.


<a name="configuration"></a>
Configuration
-------------

The workflow reads Zotero's own config files and partly manages its own configuration with the keyword `zotconf`, but you may need to use the [workflow configuration sheet][conf-sheet] if the workflow can't read Zotero's config files.


<a name="zotero-data"></a>
### Zotero data ###

The workflow uses your Zotero database and styles, therefore it needs to know where to find them. The workflow tries to read Zotero's own configuration files, and falls back to `~/Zotero` (the default location for Zotero 5).

If the workflow can't find your data, you need to set `ZOTERO_DIR` in the [workflow configuration sheet][conf-sheet].

Similarly, if you have set a "Linked Attachment Base Directory" in Zotero, but the workflow can't find the directory, enter its path for `ATTACHMENTS_DIR` in the [configuration sheet][conf-sheet].

**Note**: You can use the UNIX shortcut `~` to represent your home directory, e.g. `~/Zotero` for Zotero 5's default directory.


<a name="citation-styles"></a>
### Citation styles ###

The workflow uses the CSL styles you have installed in Zotero, so to add a new style, simply add it in Zotero. The workflow will pick up the new style(s) on the next run.

You can copy either a citation-/note-style citation or a bibliography-style one by hitting `⌘↩` or `⌥↩` respectively on a search result or citation style.

For `⌘↩` and `⌥↩` to work on search results, you must first choose a default style. You can either do this in the configuration screen (keyword `zotconf`), or hitting `^↩` on a search result to show all citation styles, then `^↩` on a style to set that as the default.


<a name="locales"></a>
### Locales ###

[CSL][csl] and ZotHero support the following locales. The default behaviour is to use the locale specified in the style if there is one, and `en-US` (American English) if not. Setting a locale overrides the style's own locale.

Use the `zotconf` keyword to force a specific locale.

|                    Locale                    |   Code  |
|----------------------------------------------|---------|
| Afrikaans                                    | `af-ZA` |
| Bahasa Indonesia / Indonesian                | `id-ID` |
| Català / Catalan                             | `ca-AD` |
| Cymraeg / Welsh                              | `cy-GB` |
| Dansk / Danish                               | `da-DK` |
| Deutsch (Deutschland) / German (Germany)     | `de-DE` |
| Deutsch (Schweiz) / German (Switzerland)     | `de-CH` |
| Deutsch (Österreich) / German (Austria)      | `de-AT` |
| Eesti / Estonian                             | `et-EE` |
| English (UK)                                 | `en-GB` |
| English (US)                                 | `en-US` |
| Español (Chile) / Spanish (Chile)            | `es-CL` |
| Español (España) / Spanish (Spain)           | `es-ES` |
| Español (México) / Spanish (Mexico)          | `es-MX` |
| Euskara / Basque                             | `eu`    |
| Français (Canada) / French (Canada)          | `fr-CA` |
| Français (France) / French (France)          | `fr-FR` |
| Hrvatski / Croatian                          | `hr-HR` |
| Italiano / Italian                           | `it-IT` |
| Latviešu / Latvian                           | `lv-LV` |
| Lietuvių / Lithuanian                        | `lt-LT` |
| Magyar / Hungarian                           | `hu-HU` |
| Nederlands / Dutch                           | `nl-NL` |
| Norsk bokmål / Norwegian (Bokmål)            | `nb-NO` |
| Norsk nynorsk / Norwegian (Nynorsk)          | `nn-NO` |
| Polski / Polish                              | `pl-PL` |
| Português (Brasil) / Portuguese (Brazil)     | `pt-BR` |
| Português (Portugal) / Portuguese (Portugal) | `pt-PT` |
| Română / Romanian                            | `ro-RO` |
| Slovenčina / Slovak                          | `sk-SK` |
| Slovenščina / Slovenian                      | `sl-SI` |
| Suomi / Finnish                              | `fi-FI` |
| Svenska / Swedish                            | `sv-SE` |
| Tiếng Việt / Vietnamese                      | `vi-VN` |
| Türkçe / Turkish                             | `tr-TR` |
| Íslenska / Icelandic                         | `is-IS` |
| Čeština / Czech                              | `cs-CZ` |
| Ελληνικά / Greek                             | `el-GR` |
| Български / Bulgarian                        | `bg-BG` |
| Монгол / Mongolian                           | `mn-MN` |
| Русский / Russian                            | `ru-RU` |
| Српски / Srpski / Serbian                    | `sr-RS` |
| Українська / Ukrainian                       | `uk-UA` |
| עברית / Hebrew                               | `he-IL` |
| العربية / Arabic                             | `ar`    |
| فارسی / Persian                              | `fa-IR` |
| ไทย / Thai                                   | `th-TH` |
| ភាសាខ្មែរ / Khmer                            | `km-KH` |
| 中文 (中国大陆) / Chinese (PRC)              | `zh-CN` |
| 中文 (台灣) / Chinese (Taiwan)               | `zh-TW` |
| 日本語 / Japanese                            | `ja-JP` |
| 한국어 / Korean                              | `ko-KR` |


<a name="all-settings"></a>
### All settings ###

Theses are all settings available in the [workflow configuration sheet][conf-sheet].

You probably shouldn't edit the `CITE_STYLE` or `LOCALE` variables yourself, as there's no guarantee the value you set is actually available. Adjust them using the `zotconf` keyword.


|      Variable     |                                Meaning                                 |
|-------------------|------------------------------------------------------------------------|
| `ATTACHMENTS_DIR` | Path to your Zotero attachments. Read from Zotero's config by default. |
| `CITE_STYLE`      | Citation style copied by `⌘↩` and `⌥↩`                                 |
| `LOCALE`          | Locale for citations. Default: `en-US` (US English).                   |
| `ZOTERO_DIR`      | Path to your Zotero data. Read from Zotero's config by default.        |


<a name="licence--thanks"></a>
Licence & thanks
----------------

This workflow is released under the [MIT licence][licence].

It is heavily based on [Alfred-Workflow][aw] (also MIT) for the workflow stuff, and [citeproc-js][citeproc-js] ([AGPL][citeproc-licence]) for generating the citations.

It was inspired by the now-defunct [ZotQuery][zotquery] by [@fractaledmind][smargh].

The [Zorro icon][icon-source] was created by [Dan Lowenstein][lowenstein] from [the Noun Project][noun-project].



[alfred]: https://www.alfredapp.com/
[aw]: http://www.deanishe.net/alfred-workflow/
[citeproc-licence]: https://github.com/Juris-M/citeproc-js/blob/master/AGPLv3
[citeproc-js]: https://github.com/Juris-M/citeproc-js
[conf-sheet]: https://www.alfredapp.com/help/workflows/advanced/variables/#environment
[csl]: http://citationstyles.org
[icon-source]: https://thenounproject.com/term/zorro/14540/
[licence]: ./LICENCE
[lowenstein]: https://thenounproject.com/danny_mustache
[noun-project]: https://thenounproject.com
[releases]: https://github.com/deanishe/zothero/releases
[smargh]: https://github.com/fractaledmind
[zotquery]: https://github.com/fractaledmind/alfred_zotquery
