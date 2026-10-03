# wlsearch

Site search: MariaDB FULLTEXT indexes queried through the Django ORM
(`wlsearch/fulltext.py`); substring search on SQLite. The small encyclopedia
has no index and always uses the substring search.

## Known limitation: stemming only on the query side

MariaDB FULLTEXT has no stemming. The stored text is indexed as written, so a
query word is searched as a prefix of itself and of its English Snowball stem;
stems shorter than 4 letters are not used because they match too much. This
misses inflections that do not share a long prefix: "settings" (stem `set`)
does not find "setting", "mines" (stem `mine`) does not find "mining". The
Whoosh index used before stemmed both the documents and the query, so it found
these.

## Possible improvement: stemmed search table

Stem the documents too, inside MariaDB:

- A table `wlsearch_entry` (content type, object id, `stems` TEXT with a
  FULLTEXT index) with one row per forum post, topic, wiki article, news post
  and map. `stems` holds the Snowball stems of the searchable text (English,
  optionally also German stems, so mixed-language posts are covered).
- Keep it current with `post_save`/`post_delete` signals in the same
  transaction, plus a management command to fill and rebuild it. Writes that
  bypass signals (`QuerySet.update()`, bulk operations) need a rebuild or
  explicit handling.
- Query: stem each query word the same way and match the stems exactly
  (`MATCH(stems) AGAINST(... IN BOOLEAN MODE)`), then apply the existing
  visibility rules by joining to the original tables, so a stale entry can
  never reveal hidden or deleted content.
- Highlighting: mark words in the snippet whose stem equals a query stem.
- Stemmer: `snowballstemmer` (pure Python, already locked) or PyStemmer
  (C implementation of the same algorithms, wheels for cp314).

This needs no new service and no schema change on the existing large tables,
at the cost of a new model, signals and a rebuild command.
