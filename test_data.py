import base64
import uuid
from datetime import datetime

from models import GuaranteeMessage201, Message, Obligation, ObligationTax
from storage import storage
from helpers import create_transaction_for_message


def create_example_201_message() -> Message:
    # Пример 1: сообщение о выдаче гарантии (201)
    payload = GuaranteeMessage201(
        InformationType=201,
        InformationTypeString="Выдача гарантии",
        Number="BG-2024-001",
        IssuedDate=datetime.fromisoformat("2024-05-20T10:00:00+00:00"),
        Guarantor="ООО 'Финансовая гарантия'",
        Beneficiary="Государственное учреждение 'Получатель'",
        Principal="ООО 'Должник'",
        Obligations=[
            Obligation(
                Type=1,
                StartDate=datetime.fromisoformat("2024-06-01T00:00:00+00:00"),
                EndDate=datetime.fromisoformat("2024-12-01T00:00:00+00:00"),
                ActDate=datetime.fromisoformat("2024-05-15T00:00:00+00:00"),
                ActNumber="ПР-2024/05/15-001",
                Taxs=[
                    ObligationTax(Number="1", NameTax="Обязательство по контракту №К-2024-01", Amount=50000.00, PennyAmount=0.00),
                    ObligationTax(Number="2", NameTax="Гарантийное обеспечение", Amount=15000.00, PennyAmount=500.00),
                ],
            )
        ],
        StartDate=datetime.fromisoformat("2024-06-01T00:00:00+00:00"),
        EndDate=datetime.fromisoformat("2024-12-15T00:00:00+00:00"),
        CurrencyCode="USD",
        CurrencyName="Доллар США",
        Amount=65000.00,
        RevokationInfo="Безотзывная",
        ClaimRightTransfer="Не допускается",
        PaymentPeriod="5 рабочих дней с момента получения требования",
        SignerName="Иванов Иван Иванович",
        AuthorizedPosition="Генеральный директор",
        BankGuaranteeHash="5D6F8E2A1C3B9F4D7E8A2C5B1D3F6E8A9C2D4F6A8B1C3E5F7A9D2B4C6E8F0A1",
    )
    payload_b64 = base64.b64encode(payload.model_dump_json().encode("utf-8")).decode("utf-8")
    message_time = datetime.fromisoformat("2024-05-20T10:00:00+00:00")
    return Message(
        Data=payload_b64,
        SenderBranch="SYSTEM_B",
        ReceiverBranch="SYSTEM_A",
        InfoMessageType=201,
        MessageTime=message_time,
        ChainGuid=uuid.uuid4(),
        PreviousTransactionHash=None,
        Metadata=None,
    )


def init_test_data() -> None:
    if storage.transactions:
        return
    msg = create_example_201_message()
    storage.add_transaction(create_transaction_for_message(msg))
