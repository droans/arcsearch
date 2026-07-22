"""Models related to SMS message parsint."""

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator

from .const import AddressType, MessageBox, MessageType, SMSStatus, SMSType


def _int_bool(val: str | int | None) -> bool | None:
    if val is None:
        return None
    return val not in [0, "0"]


def _str_int(val: str | None) -> int | None:
    if val is None:
        return val
    return int(val)


def _nullable_by_null(val: str) -> str | None:
    if val == "null":
        return None
    return val


def _nullable_by_zero(val: str | int) -> str | int | None:
    if val in ["0", 0]:
        return None
    return val


def _nullable_by_empty(val: str | int) -> str | int | None:
    if val == "":
        return None
    return val


SMSNullableString = Annotated[
    str | None,
    BeforeValidator(_nullable_by_null),
]
SMSNullableBlankString = Annotated[
    str | None,
    BeforeValidator(_nullable_by_null),
    BeforeValidator(_nullable_by_empty),
]

SMSNullableInt = Annotated[
    int | None,
    BeforeValidator(_str_int),
    BeforeValidator(func=_nullable_by_null),
]
SMSNullableZeroInt = Annotated[
    int | None,
    BeforeValidator(_str_int),
    BeforeValidator(func=_nullable_by_zero),
]
SMSNullableIntBool = Annotated[
    int | None,
    BeforeValidator(_int_bool),
]


class XMLAddrModel(BaseModel):
    """Model for the `addr` XML tag."""

    charset: int
    type: Annotated[AddressType, BeforeValidator(_str_int)]
    address: str


class XMLSMSModel(BaseModel):
    """Model for the `sms` XML tag."""

    tag: Literal["sms"] = "sms"
    protocol: int
    address: str
    date: int
    type: Annotated[SMSType, BeforeValidator(_str_int)]
    subject: SMSNullableString
    body: str
    toa: SMSNullableString
    sc_toa: SMSNullableString
    service_center: SMSNullableString
    read: SMSNullableIntBool
    status: Annotated[SMSStatus, BeforeValidator(_str_int)]
    locked: SMSNullableIntBool
    date_sent: SMSNullableZeroInt
    sub_id: int
    readable_date: str
    contact_name: str


class XMLRCSMMSModel(BaseModel):
    """Model for the `mms` XML tag."""

    date: int
    rr: SMSNullableInt
    sub: SMSNullableBlankString
    ct_t: SMSNullableString
    read_status: SMSNullableInt
    seen: SMSNullableIntBool
    msg_box: Annotated[MessageBox, BeforeValidator(_str_int)]
    sub_cs: SMSNullableInt
    resp_st: SMSNullableInt
    retr_st: SMSNullableInt
    d_tm: SMSNullableInt
    text_only: SMSNullableIntBool
    exp: SMSNullableInt
    locked: SMSNullableIntBool
    m_id: SMSNullableString
    st: SMSNullableInt
    retr_txt_cs: SMSNullableInt
    retr_txt: SMSNullableString
    creator: str
    date_sent: SMSNullableZeroInt
    read: SMSNullableIntBool
    m_size: SMSNullableInt
    rpt_a: SMSNullableInt
    ct_cls: SMSNullableInt
    pri: SMSNullableInt
    sub_id: int
    tr_id: SMSNullableBlankString
    resp_txt: SMSNullableString
    ct_l: SMSNullableString
    m_cls: SMSNullableString
    d_rpt: SMSNullableInt
    v: SMSNullableInt
    _id: int
    m_type: int
    readable_date: str
    contact_name: SMSNullableBlankString
    address: SMSNullableBlankString = None


class XMLRCSModel(XMLRCSMMSModel):
    """Model for RCS XML data."""

    tag: Literal["rcs"] = "rcs"


class XMLMMSModel(XMLRCSMMSModel):
    """Model for MMS XML data."""

    tag: Literal["mms"] = "mms"


class XMLPartModel(BaseModel):
    """Model for the `part` XML tag."""

    seq: int
    ct: str
    name: SMSNullableString
    chset: SMSNullableInt
    cd: SMSNullableString
    fn: SMSNullableString
    cid: SMSNullableString
    cl: SMSNullableString
    ctt_s: SMSNullableString
    text: SMSNullableString
    sub_id: int
    data: SMSNullableBlankString = None


class XMLMMSFullModel(XMLMMSModel):
    """Full XML model for MMS messages, including parts and addresses."""

    addrs: list[XMLAddrModel]
    parts: list[XMLPartModel]


class XMLRCSFullModel(XMLRCSModel):
    """Full XML model for RCS messages, including parts and addresses."""

    addrs: list[XMLAddrModel]
    parts: list[XMLPartModel]


class MMSAttachmentModel(BaseModel):
    """Model for single MMS attachment."""

    filename: str
    content_type: str


class ContactInfo(BaseModel):
    """Model for a contact."""

    name: str
    phone_number: str


class ConversationModel(BaseModel):
    """Model for a conversation."""

    recipients: list[str]  # list of phone numbers, linked to ContactInfo.phone_number
    conversation_id: int


class BaseMessageModel(BaseModel):
    """Base model for a message."""

    sender: str
    conversation_id: int  # linked to ParticipantsModel.conversation_id
    timestamp: int
    message: str | None = None
    readable_date: str | None = None
    direction: Literal["sent", "received"]
    message_id: str


class MMSModel(BaseMessageModel):
    """Model for an MMS message."""

    type: MessageType = MessageType.MMS
    images: list[MMSAttachmentModel]


class SMSModel(BaseMessageModel):
    """Model for an SMS message."""

    type: MessageType = MessageType.SMS


class RCSModel(BaseMessageModel):
    """Model for an RCS message."""

    type: MessageType = MessageType.RCS
    images: list[MMSAttachmentModel]
