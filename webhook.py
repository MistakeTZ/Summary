from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import JSONResponse

app = FastAPI()
send_request = None

@app.post("/request")
async def handle_json(request: Request):
    try:
        data = await request.form()
        await send_request(data)
    except Exception as e:
        return JSONResponse(content={"status": "failed", "error": str(e)}, status_code=400)
    return JSONResponse(content={"status": "success", "message": "Заявка успешно отправлена"})

async def run_api(log_func):
    global send_request
    send_request = log_func

    config = uvicorn.Config("webhook:app", host="0.0.0.0", port=8098, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()