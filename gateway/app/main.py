from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from app.load_balancer import get_next_backend
from app.rate_limiter import check_rate_limit

app = FastAPI(title="API Gateway")

# Configuração do CORS para liberar o acesso da interface front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

client = httpx.AsyncClient()

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    # 1. Verifica Rate Limit
    client_ip = request.client.host
    check_rate_limit(client_ip)

    # 2. Load Balancer escolhe o alvo
    backend_url = get_next_backend()
    target_url = f"{backend_url}/{path}"

    # 3. Proxy repassa a requisição
    body = await request.body()
    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=dict(request.headers)
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Backend indisponível no momento")

    # 4. Prepara a resposta e avisa quem atendeu (X-Served-By)
    headers = dict(response.headers)
    headers["X-Served-By"] = backend_url

    return Response(
        content=response.content, 
        status_code=response.status_code, 
        headers=headers
    )