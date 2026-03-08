import base64
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel

from models import Message, SignedApiData, Transaction


def compute_transaction_hash(tx: Transaction) -> str:
    # Хэш по спецификации: без Hash/Sign/SignerCert, JSON, SHA-256, HEX верхний регистр
    tx_dict = tx.model_dump(mode="json")
    tx_dict["Hash"] = None
    tx_dict["Sign"] = ""
    tx_dict["SignerCert"] = ""
    json_bytes = json.dumps(tx_dict, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(json_bytes).hexdigest().upper()


def emulate_transaction_signature(hash_hex: str) -> str:
    # Эмуляция ЭЦП: Hash (UTF-8) в Base64
    return base64.b64encode(hash_hex.encode("utf-8")).decode("utf-8")


def build_signed_api_data(payload: BaseModel, signer_name: str = "SYSTEM_B") -> SignedApiData:
    # Sign = SHA256(Data) в Base64, SignerCert = Base64(имя отправителя)
    payload_json = payload.model_dump_json()
    payload_bytes = payload_json.encode("utf-8")
    data_b64 = base64.b64encode(payload_bytes).decode("utf-8")
    sha = hashlib.sha256(data_b64.encode("utf-8")).digest()
    sign_b64 = base64.b64encode(sha).decode("utf-8")
    signer_cert_b64 = base64.b64encode(signer_name.encode("utf-8")).decode("utf-8")
    return SignedApiData(Data=data_b64, Sign=sign_b64, SignerCert=signer_cert_b64)


def unpack_signed_api_data(signed: SignedApiData) -> dict:
    try:
        raw_bytes = base64.b64decode(signed.Data)
        return json.loads(raw_bytes.decode("utf-8"))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Cannot decode SignedApiData.Data: {ex}")


def decode_message_from_transaction(tx: Transaction) -> Message:
    raw_bytes = base64.b64decode(tx.Data)
    data = json.loads(raw_bytes.decode("utf-8"))
    return Message.model_validate(data)


def encode_message_to_transaction_data(msg: Message) -> str:
    return base64.b64encode(msg.model_dump_json().encode("utf-8")).decode("utf-8")


def create_receipt_message(
    original_msg: Message, bank_guarantee_hash: str, previous_tx_hash: Optional[str]
) -> Message:
    # Квиток 215 с хэшем гарантии для цепочки
    now = datetime.now(timezone.utc)
    payload_b64 = base64.b64encode(
        json.dumps({"BankGuaranteeHash": bank_guarantee_hash}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("utf-8")
    return Message(
        Data=payload_b64,
        SenderBranch="SYSTEM_B",
        ReceiverBranch="SYSTEM_A",
        InfoMessageType=215,
        MessageTime=now,
        ChainGuid=original_msg.ChainGuid,
        PreviousTransactionHash=previous_tx_hash,
        Metadata=None,
    )


def create_transaction_for_message(msg: Message) -> Transaction:
    now = datetime.now(timezone.utc)
    data_b64 = encode_message_to_transaction_data(msg)
    temp = Transaction(
        TransactionType=9,
        Data=data_b64,
        Hash="",
        Sign="",
        SignerCert="",
        TransactionTime=now,
        Metadata=None,
        TransactionIn=None,
        TransactionOut=None,
    )
    tx_hash = compute_transaction_hash(temp)
    return Transaction(
        TransactionType=9,
        Data=data_b64,
        Hash=tx_hash,
        Sign=emulate_transaction_signature(tx_hash),
        SignerCert=base64.b64encode(b"SYSTEM_B").decode("utf-8"),
        TransactionTime=now,
        Metadata=None,
        TransactionIn=None,
        TransactionOut=None,
    )
