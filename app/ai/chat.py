from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json

from app.dependencies.chat import get_chat_service
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)):
    return service.chat(request)

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    async def generate():
        try:
            async for chunk in service.stream(request):
                print("CHUNK:", repr(chunk))
                yield f"data: {json.dumps({'token': chunk})}\n\n"

            print("STREAM DONE")
            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            print("STREAM ERROR:", repr(e))
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )