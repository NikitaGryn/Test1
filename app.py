import base64
import json
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from models import SearchRequest, SignedApiData, Transaction, TransactionsData
from storage import storage
from helpers import (
    build_signed_api_data,
    compute_transaction_hash,
    create_receipt_message,
    create_transaction_for_message,
    decode_message_from_transaction,
    emulate_transaction_signature,
    unpack_signed_api_data,
)
from test_data import init_test_data


app = FastAPI(title="FinSelvat Test API", version="1.0.0")


@app.on_event("startup")
async def on_startup() -> None:
    init_test_data()


@app.get("/api/health", response_class=PlainTextResponse)
async def health() -> str:
    return "OK"


@app.post("/api/messages/outgoing", response_model=SignedApiData)
async def get_outgoing_messages(request: SignedApiData) -> SignedApiData:
    # Список исходящих в SYSTEM_A за период (SignedApiData → SignedApiData)
    data_dict = unpack_signed_api_data(request)
    try:
        search = SearchRequest.model_validate(data_dict)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Invalid SearchRequest payload: {ex}")
    result = storage.list_outgoing_for_system_a(
        start=search.StartDate, end=search.EndDate, limit=search.Limit, offset=search.Offset
    )
    return build_signed_api_data(result, signer_name="SYSTEM_B")


@app.post("/api/messages/incoming", response_model=SignedApiData)
async def post_incoming_messages(request: SignedApiData) -> SignedApiData:
    # Принять сообщения от Системы А, сохранить, вернуть квитки 215
    data_dict = unpack_signed_api_data(request)
    try:
        incoming = TransactionsData.model_validate(data_dict)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Invalid TransactionsData payload: {ex}")
    receipts: List[Transaction] = []
    for tx in incoming.Transactions:
        recomputed_hash = compute_transaction_hash(tx)
        if tx.Hash and recomputed_hash != tx.Hash:
            raise HTTPException(status_code=400, detail="Transaction hash mismatch")
        tx.Hash = recomputed_hash
        if not tx.Sign:
            tx.Sign = emulate_transaction_signature(tx.Hash)
        storage.add_transaction(tx)
        msg = decode_message_from_transaction(tx)
        if msg.InfoMessageType == 215:
            continue
        bank_hash = None
        try:
            payload_dict = json.loads(base64.b64decode(msg.Data).decode("utf-8"))
            bank_hash = payload_dict.get("BankGuaranteeHash")
        except Exception:
            pass
        if not bank_hash:
            continue
        receipt_msg = create_receipt_message(msg, bank_guarantee_hash=bank_hash, previous_tx_hash=tx.Hash)
        receipts.append(create_transaction_for_message(receipt_msg))
    return build_signed_api_data(TransactionsData(Transactions=receipts, Count=len(receipts)), signer_name="SYSTEM_B")
