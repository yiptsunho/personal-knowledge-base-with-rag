from fastapi import FastAPI
from app.api import upload, chat  # , documents
from fastapi.openapi.utils import get_openapi
from app.api import status

app = FastAPI(title="Personal Second Brain API")

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(status.router, prefix="/status", tags=["status"])
# app.include_router(documents.router, prefix="/documents", tags=["documents"])

@app.get("/")
def read_root():
    return {"message": "Personal Knowledge Base API is running"}

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
    
#     openapi_schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         description=app.description,
#         routes=app.routes,
#     )
    
#     # Fix file upload schemas
#     for path in openapi_schema.get("paths", {}).values():
#         for method in path.values():
#             if "requestBody" in method and "content" in method["requestBody"]:
#                 for media_type, content in method["requestBody"]["content"].items():
#                     if media_type == "multipart/form-data":
#                         for prop_name, prop in content.get("schema", {}).get("properties", {}).items():
#                             if prop.get("type") == "string" and prop.get("contentMediaType") == "application/octet-stream":
#                                 del prop["contentMediaType"]
#                                 prop["format"] = "binary"
    
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi