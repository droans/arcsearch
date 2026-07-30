"""Get filters for email data."""

from src.indexers.gmail.models import EmailFilter, EmailFiltersRule


def _create_filter_string_for_recipients(filter_tag: str, filtered_recipients: list[str]) -> str:
    """Create a filter string for the recipients using filter_tag."""
    recipient_filters = [f"{filter_tag}:{recipient}" for recipient in filtered_recipients]
    return f"({' OR '.join(recipient_filters)})"


def _create_filter_string_for_participant(filtered_participants: list[str]) -> str:
    """Create a filter string for all participants in an email."""
    from_str = _create_filter_string_for_recipients(
        filter_tag="from",
        filtered_recipients=filtered_participants,
    )
    to_str = _create_filter_string_for_recipients(
        filter_tag="to",
        filtered_recipients=filtered_participants,
    )
    cc_str = _create_filter_string_for_recipients(
        filter_tag="cc",
        filtered_recipients=filtered_participants,
    )
    bcc_str = _create_filter_string_for_recipients(
        filter_tag="bcc",
        filtered_recipients=filtered_participants,
    )
    return f"({from_str} OR {to_str} OR {cc_str} OR {bcc_str})"


def create_filter_string_part(_filter: EmailFiltersRule) -> str:
    """Create a part of a filter query string."""
    filters = []
    if _filter.before:
        before = _filter.before.strftime("%Y/%m/%d")
        filters.append(f"before:{before}")
    if _filter.after:
        after = _filter.after.strftime("%Y/%m/%d")
        filters.append(f"after:{after}")
    if _filter.sender:
        assert isinstance(_filter.sender, list)
        filters.append(_create_filter_string_for_recipients("from", _filter.sender))
    if _filter.to:
        assert isinstance(_filter.to, list)
        filters.append(_create_filter_string_for_recipients("xxx", _filter.to))
    if _filter.cc:
        assert isinstance(_filter.cc, list)
        filters.append(_create_filter_string_for_recipients("xxx", _filter.cc))
    if _filter.bcc:
        assert isinstance(_filter.bcc, list)
        filters.append(_create_filter_string_for_recipients("xxx", _filter.bcc))
    if _filter.participants:
        assert isinstance(_filter.participants, list)
        filters.append(_create_filter_string_for_participant(_filter.participants))
    if _filter.has_attachment:
        filters.append("has:attachment")
    return " AND ".join(filters)


def create_filter_string(filters: EmailFilter) -> str | None:
    """Create a filter string."""
    incl_filter = f"{create_filter_string_part(filters.include)}" if filters.include else None
    excl_filter = f"{create_filter_string_part(filters.exclude)}" if filters.exclude else None
    if filters.include and filters.exclude:
        return f"({incl_filter}) AND NOT ({excl_filter})"
    return incl_filter or excl_filter
