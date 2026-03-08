from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class SignedApiData(BaseModel):
    Data: str  # Base64 payload
    Sign: str  # Base64 подпись (эмуляция)
    SignerCert: str  # Base64 сертификат (эмуляция)


class ObligationTax(BaseModel):
    Number: str
    NameTax: str
    Amount: float
    PennyAmount: float


class Obligation(BaseModel):
    Type: int
    StartDate: datetime
    EndDate: datetime
    ActDate: datetime
    ActNumber: str
    Taxs: List[ObligationTax]


class GuaranteeMessage201(BaseModel):
    InformationType: int
    InformationTypeString: str
    Number: str
    IssuedDate: datetime
    Guarantor: str
    Beneficiary: str
    Principal: str
    Obligations: List[Obligation]
    StartDate: datetime
    EndDate: datetime
    CurrencyCode: str
    CurrencyName: str
    Amount: float
    RevokationInfo: str
    ClaimRightTransfer: str
    PaymentPeriod: str
    SignerName: str
    AuthorizedPosition: str
    BankGuaranteeHash: str


class Message(BaseModel):
    Data: str  # Base64 JSON полезной нагрузки
    SenderBranch: str
    ReceiverBranch: str
    InfoMessageType: int
    MessageTime: datetime
    ChainGuid: uuid.UUID
    PreviousTransactionHash: Optional[str] = None
    Metadata: Optional[str] = None


class Transaction(BaseModel):
    TransactionType: int  # 9 — инфо, 18 — гарантия
    Data: str  # Base64 JSON сообщения
    Hash: str
    Sign: str
    SignerCert: str
    TransactionTime: datetime
    Metadata: Optional[str] = None
    TransactionIn: Optional[str] = None
    TransactionOut: Optional[str] = None


class SearchRequest(BaseModel):
    StartDate: datetime
    EndDate: datetime
    Limit: int = Field(ge=0)
    Offset: int = Field(ge=0)


class TransactionsData(BaseModel):
    Transactions: List[Transaction]
    Count: int
