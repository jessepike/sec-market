# Empty HTML attribute handling

The missing-binding audit found a retained ReliaQuest response that crashes the article parser
on a valueless `class` attribute. Python's HTML parser returns `None` for valueless attributes.
The current code assumes strings when splitting class, relation and publication attributes.

Normalize valueless HTML attributes to empty strings at the existing article and structural-index
parser boundaries. Preserve existing valued attributes, article text, URL rules, scoping and
publication-date rules. Empty classes or relations supply no class/relation match; empty publication
metadata supplies no date. This change cannot qualify a source, complete pagination, resolve a
claim hold or admit a fact. Do not modify retained source bytes or observation times.

Tests cover class, relation, itemprop and datetime attributes on ordinary article and structural
index nodes, source-specific scoping, and unchanged normal publication metadata. Replay the exact
retained ReliaQuest response once its audit pin is available, preserving the raw hash and original
time. Run in OrbStack without network, model, state/archive writes or coverage credit.
