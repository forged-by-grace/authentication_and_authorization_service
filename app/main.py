from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from v1.auth_route import auth
from core.utils.settings import settings

from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from core.middleware.process_time_header_middleware import add_process_time_header


async def on_startup():
    print('Starting auth service api')
    

async def on_shut_down():
    print('Shutting down auth service api')


# init app lifecyle
@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shut_down()


# Init fastapi
app = FastAPI(
    lifespan=lifespan,
    title=settings.api_name,
    version=settings.api_version,
    description=settings.api_description,
    terms_of_service=settings.api_terms_of_service,
    contact={
        'name': settings.api_company_name,
        'url': settings.api_company_url,
        'email': settings.api_company_email
    }
)


# Set cors
origins = ['*']

# add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_credentials=True,
    allow_headers=[],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)

# Add route
app.include_router(auth)

# start the server
if __name__ == '__main__':
    uvicorn.run(
        settings.api_entry_point,
        port=settings.api_port,
        reload=settings.api_reload,
        host=settings.api_host,
        lifespan=settings.api_lifespan
    )
