"""Search with MariaDB's FULLTEXT indexes.

The indexes are created by the wlsearch migrations. Other databases (SQLite in
development and tests) have no FULLTEXT index, there the words are matched as
substrings instead.
"""

import re
from functools import cache, reduce
from operator import and_, or_
from typing import NamedTuple

import snowballstemmer
from django.db import connections
from django.db.models import F, Lookup, Q, Value
from django.db.models.expressions import ExpressionList

# An optional '-' followed by a "quoted phrase" or a word
_TERM = re.compile(r'(-?)(?:"([^"]*)"?|(\S+))')
# Characters that are part of a word in a FULLTEXT index
_WORD = re.compile(r"\w+")
# Shorter stems are the beginning of too many unrelated words
MIN_STEM_LENGTH = 4


class Term(NamedTuple):
    words: tuple[str, ...]
    is_phrase: bool
    # For a single word: the beginnings of the words it matches
    prefixes: tuple[str, ...] = ()
    # The term as typed, without '-' and quotes
    text: str = ""


class SearchQuery:
    """A parsed search string.

    All terms must match, except those starting with '-', which must not match.
    A term is a "quoted phrase", which matches exactly, or a word. Words match
    all words they or their English stem are the beginning of, e.g. 'mining'
    matches 'mining', 'mine' and 'mines'. Words joined by punctuation, like
    'std::vector', are a phrase.
    """

    def __init__(self, query):
        stemmer = snowballstemmer.stemmer("english")
        self.required = []
        self.excluded = []
        for minus, phrase, word in _TERM.findall(query):
            words = tuple(_WORD.findall(phrase or word))
            if not words:
                continue
            if phrase or len(words) > 1:
                term = Term(words, True, text=phrase or word)
            else:
                word = words[0].lower()
                stem = stemmer.stemWord(word)
                if len(stem) < MIN_STEM_LENGTH:
                    prefixes = (word,)
                elif word.startswith(stem):
                    prefixes = (stem,)
                else:
                    prefixes = (word, stem)
                term = Term(words, False, prefixes, word)
            (self.excluded if minus else self.required).append(term)

    @property
    def highlight_words(self):
        return {
            word.lower()
            for term in self.required
            for word in (term.words if term.is_phrase else term.prefixes)
        }

    def boolean_mode(self, ignored, required=None, excluded=None):
        """Return the query for MATCH() ... AGAINST(... IN BOOLEAN MODE).

        By default all terms are used, required and excluded give subsets.
        Words that are not in the index (see _ignored_words) are left out:
        MariaDB finds nothing if a required word is not in the index.
        """

        def terms(operator, terms):
            for term in terms:
                if term.is_phrase:
                    if not all(map(ignored, term.words)):
                        yield f'{operator}"{" ".join(term.words)}"'
                elif not ignored(term.words[0]):
                    prefixes = " ".join(f"{prefix}*" for prefix in term.prefixes)
                    if len(term.prefixes) > 1:
                        prefixes = f"({prefixes})"
                    yield f"{operator}{prefixes}"

        required = self.required if required is None else required
        excluded = self.excluded if excluded is None else excluded
        required = list(terms("+", required))
        if not required:
            return ""
        return " ".join(required + list(terms("-", excluded)))


@cache
def _ignored_words(alias):
    """Return a function telling whether a word is not in the FULLTEXT index:
    either it is shorter than innodb_ft_min_token_size or it is a stopword.
    """
    with connections[alias].cursor() as cursor:
        cursor.execute("SELECT @@innodb_ft_min_token_size, @@innodb_ft_enable_stopword")
        min_size, stopwords_enabled = cursor.fetchone()
        stopwords = set()
        if stopwords_enabled:
            cursor.execute(
                "SELECT value FROM information_schema.INNODB_FT_DEFAULT_STOPWORD"
            )
            stopwords = {value for (value,) in cursor.fetchall()}
    return lambda word: len(word) < min_size or word.lower() in stopwords


class Match(Lookup):
    """MATCH (columns) AGAINST (query IN BOOLEAN MODE).

    The columns must be exactly the columns of one FULLTEXT index. This is a
    lookup, so that filter() uses its result as is: compared to TRUE, the
    relevance MATCH() returns would rarely be equal.
    """

    def __init__(self, *columns, against):
        super().__init__(ExpressionList(*map(F, columns)), Value(against))

    def as_mysql(self, compiler, connection):
        columns_sql, columns_params = self.process_lhs(compiler, connection)
        against_sql, against_params = self.process_rhs(compiler, connection)
        return (
            f"MATCH ({columns_sql}) AGAINST ({against_sql} IN BOOLEAN MODE)",
            (*columns_params, *against_params),
        )


def substring_search(queryset, fields, query, also_matches=None):
    """Return the rows of queryset in which every required term is a substring
    of one of the fields, and no excluded term is. For a word, any of its
    prefixes is enough.

    also_matches(term) may return a Q of further rows that match the term,
    see fulltext_search().
    """

    def matches(term):
        texts = [" ".join(term.words)] if term.is_phrase else term.prefixes
        condition = reduce(
            or_,
            (Q(**{f"{field}__icontains": text}) for field in fields for text in texts),
        )
        alternative = also_matches and also_matches(term)
        return condition | alternative if alternative else condition

    if not query.required:
        return queryset.none()
    queryset = queryset.filter(reduce(and_, map(matches, query.required)))
    for term in query.excluded:
        queryset = queryset.exclude(matches(term))
    return queryset


def fulltext_search(queryset, fields, query, also_matches=None):
    """Return the rows of queryset whose fields match the query.

    The fields must be exactly the columns of one FULLTEXT index.

    also_matches(term) may return a Q of further rows that match the term, or
    None. Such a term matches a row if the fields match it or the Q does:
    for a required term the row is found, for an excluded term it is left
    out. The other terms stay in one MATCH(), which uses the index.
    """
    if connections[queryset.db].vendor != "mysql":
        return substring_search(queryset, fields, query, also_matches)
    ignored = _ignored_words(queryset.db)
    alternatives = {}
    if also_matches:
        for term in query.required + query.excluded:
            alternatives[term] = also_matches(term)

    def match(required, excluded=()):
        against = query.boolean_mode(ignored, required, excluded)
        return Q(Match(*fields, against=against)) if against else None

    def text_only(terms):
        return [term for term in terms if alternatives.get(term) is None]

    conditions = []
    against = match(text_only(query.required), text_only(query.excluded))
    if against:
        conditions.append(against)
    for term in query.required:
        if alternatives.get(term) is not None and (term_match := match([term])):
            # A word missing from the index is left out, like in the MATCH()
            conditions.append(term_match | alternatives[term])
    if not conditions:
        return queryset.none()
    queryset = queryset.filter(*conditions)
    for term in query.excluded:
        alternative = alternatives.get(term)
        if alternative is not None:
            term_match = match([term])
            queryset = queryset.exclude(term_match | alternative if term_match else alternative)
        elif not against:
            # The MATCH() above has no required words to exclude this from
            if term_match := match([term]):
                queryset = queryset.exclude(term_match)
    return queryset
