import time
from fastapi import Request

async def add_process_time_header(request: Request, call_next):
    # Before request processing
    start_time = time.time()
    response = await call_next(request)

    # After the request processing
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response