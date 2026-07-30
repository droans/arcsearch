"""Filter functions."""

from src.indexers.gmail.models import EmailFilter, EmailModel


def apply_before_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filters based on time before."""
    include_before = None
    exclude_before = None
    if _filter.include and _filter.include.before:
        include_before = _filter.include.before.timestamp()
    if _filter.exclude and _filter.exclude.before:
        exclude_before = _filter.exclude.before.timestamp()

    result = []
    for message in messages:
        ts = message.timestamp
        if include_before and ts > include_before:
            continue
        if exclude_before and ts < exclude_before:
            continue
        result.append(message)
    return result


def apply_after_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filters based on time after."""
    include_after = None
    exclude_after = None
    if _filter.include and _filter.include.after:
        include_after = _filter.include.after.timestamp()
    if _filter.exclude and _filter.exclude.after:
        exclude_after = _filter.exclude.after.timestamp()

    result = []
    for message in messages:
        ts = message.timestamp
        if include_after and ts < include_after:
            continue
        if exclude_after and ts > exclude_after:
            continue
        result.append(message)
    return result


def apply_sender_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filter on email `sender` field."""
    include = []
    exclude = []
    if _filter.include:
        incl = _filter.include
        if incl.sender:
            include.extend(incl.sender)
    if _filter.exclude:
        excl = _filter.exclude
        if excl.sender:
            exclude.extend(excl.sender)
    result = []
    for message in messages:
        include_email = True
        email_sender = message.sender
        for email in email_sender:
            if include and email not in include:
                include_email = False
                continue
            if exclude and email in exclude:
                include_email = False
                continue
        if include_email:
            result.append(message)
    return result


def apply_participants_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filter on email participants."""
    include = []
    exclude = []
    if _filter.include:
        incl = _filter.include
        if incl.participants:
            include.extend(incl.participants)
    if _filter.exclude:
        excl = _filter.exclude
        if excl.participants:
            exclude.extend(excl.participants)
    result = []
    for message in messages:
        include_email = True
        email_participants = [
            *message.to,
            *message.sender,
            *message.cc,
            *message.bcc,
        ]
        for email in email_participants:
            if include and email not in include:
                include_email = False
                continue
            if exclude and email in exclude:
                include_email = False
                continue
        if include_email:
            result.append(message)
    return result


def apply_to_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filter on email `to` field."""
    include = []
    exclude = []
    if _filter.include:
        incl = _filter.include
        if incl.to:
            include.extend(incl.to)
    if _filter.exclude:
        excl = _filter.exclude
        if excl.to:
            exclude.extend(excl.to)
    result = []
    for message in messages:
        include_email = True
        email_to = message.to
        for email in email_to:
            if include and email not in include:
                include_email = False
                continue
            if exclude and email in exclude:
                include_email = False
                continue
        if include_email:
            result.append(message)
    return result


def apply_cc_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filter on email `cc` field."""
    include = []
    exclude = []
    if _filter.include:
        incl = _filter.include
        if incl.cc:
            include.extend(incl.cc)
    if _filter.exclude:
        excl = _filter.exclude
        if excl.cc:
            exclude.extend(excl.cc)
    result = []
    for message in messages:
        include_email = True
        email_cc = message.cc
        for email in email_cc:
            if include and email not in include:
                include_email = False
                continue
            if exclude and email in exclude:
                include_email = False
                continue
        if include_email:
            result.append(message)
    return result


def apply_bcc_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filter on email `bcc` field."""
    include = []
    exclude = []
    if _filter.include:
        incl = _filter.include
        if incl.bcc:
            include.extend(incl.bcc)
    if _filter.exclude:
        excl = _filter.exclude
        if excl.bcc:
            exclude.extend(excl.bcc)
    result = []
    for message in messages:
        include_email = True
        email_bcc = message.bcc
        for email in email_bcc:
            if include and email not in include:
                include_email = False
                continue
            if exclude and email in exclude:
                include_email = False
                continue
        if include_email:
            result.append(message)
    return result


def apply_label_id_filter(messages: list[EmailModel], _filter: EmailFilter) -> list[EmailModel]:
    """Apply filter on email label ids field."""
    include_labels = None
    exclude_labels = None
    if _filter.include and _filter.include.label_ids:
        include_labels = _filter.include.label_ids
    if _filter.exclude and _filter.exclude.label_ids:
        exclude_labels = _filter.exclude.label_ids

    result = []
    for message in messages:
        if include_labels and not any(label in include_labels for label in message.label_ids):
            continue
        if exclude_labels and any(label in exclude_labels for label in message.label_ids):
            continue
        result.append(message)
    return result


def apply_email_filters(messages: list[EmailModel], filters: list[EmailFilter]) -> list[EmailModel]:
    """Apply filters to selection of emails."""
    result: list[EmailModel] = []
    for _filter in filters:
        tmp_messages = apply_before_filter(messages, _filter)
        tmp_messages = apply_after_filter(tmp_messages, _filter)
        tmp_messages = apply_sender_filter(tmp_messages, _filter)
        tmp_messages = apply_participants_filter(tmp_messages, _filter)
        tmp_messages = apply_to_filter(tmp_messages, _filter)
        tmp_messages = apply_cc_filter(tmp_messages, _filter)
        tmp_messages = apply_bcc_filter(tmp_messages, _filter)
        tmp_messages = apply_label_id_filter(tmp_messages, _filter)
        [result.append(message) for message in tmp_messages if message not in result]
    return list(result)
