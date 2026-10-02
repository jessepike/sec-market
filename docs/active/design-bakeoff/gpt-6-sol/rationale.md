# Security Market Pulse prototype rationale

The front page opens with recent reported results and other dated company changes, so a security leader sees concrete figures and events before choosing a domain. The domain browser then shows every tracked supplier in that domain with its own reported figures, periods and sources. The page does not infer which supplier is doing well.

## Revision after the first render

The supplied 1440 and 390 pixel screenshots showed a calm page, but the first screen used too much space for the headline and led with leadership changes. I reduced the opening height, added 30-day counts for records, reported results and acquisition events, and changed the opening list to the two newest results plus the two newest other company events, with that selection rule stated below it. I also shortened acquired-company rows to the structured buyer and announcement or close date, leaving the full source one click away. The first render exposed a misleading “quarter ended” caption on a leadership item; non-result events now show the source date instead. The revised file has not been rendered again in this sandbox.

## Information architecture

At 1440 pixels, the opening pairs a short description and the 30-day record counts with four sourced examples: the two newest results and the two newest other events. The full 30-day record sits below the domain browser and includes all 25 current entries: 17 tracker events and eight latest-quarter SEC filings. The browser starts with the first domain alphabetically and offers all 12 domains; each selection shows the full supplier set for that domain, also alphabetically. On a phone, a native domain selector keeps the page short and operable without a horizontal table.

## Visual system

The page uses a cool white base, deep blue-green text, restrained teal links, and pale separators. Teal identifies actions and source access; it carries no positive or negative market meaning. Plus Jakarta Sans gives the large opening and compact controls a contemporary shape, while IBM Plex Sans keeps long disclosure text and figures readable. The dated disclosure rail is the visual focus; supplier facts use a repeatable, quieter row layout.

## Constraint check

1. The page renders the tracker’s company records, events and latest-quarter filing entries as facts. It uses no score, stance, ranking, forecast, performance color or generated interpretation. The default order is alphabetical in the domain browser and newest first in the dated record.
2. Reported revenue, growth, company metrics, funding and ownership each show their recorded period or event date. Their values link directly to the repository evidence source. Every recent-change entry has a source link and a visible period or filing date. Coverage counts are derived from the embedded tracker data and link to the method note.
3. A missing financial figure is described as absent from this tracker rather than displayed as a dash. Collection status is linked in the first screen and detailed below, including the suppliers whose news sources were not read in the last collection run.
4. The CSS declares a light color scheme and has no dark mode rule.
5. The layouts are written for 1440 and 390 pixels. The mobile layout stacks content, replaces the domain rail with a native select, and avoids wide tables. Interactive controls have at least 24 pixel height and visible keyboard focus. The lead's screenshots verified that the first version rendered at both widths without visible horizontal overflow. The revised file still needs a fresh render because the sandbox blocks Chrome launch and the available browser surface refuses local `file:` URLs.
6. There is no owner byline in the opening. “Not a news site and not investment advice” appears in the method section.
7. The JSON block embeds the actual 12 domains, 74 suppliers, 95 recorded events, relevant evidence records, SEC filing data and collection status from the repository. The complete current 30-day change list is rendered, and every domain has its full supplier set available.

## Next pass

Render this revision in Chrome at both required widths, inspect the first screen and full page, and adjust any spacing or overflow exposed by those images. Then test the domain selector, source links and keyboard path in the browser. The revision has static data and JavaScript checks, plus a visual critique of the first render; it has no post-revision browser check.
