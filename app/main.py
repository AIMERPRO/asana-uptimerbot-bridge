import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .config import settings
from .uptime_robot import UptimeRobot
from .utils import extract_domain_from_payload, build_monitor_context

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Asana → UptimeRobot bridge")

if not settings.uptimerobot_token:
    raise Exception('No UptimerRobot API KEY set!')

ur = UptimeRobot(token=settings.uptimerobot_token)


@app.on_event("shutdown")
async def shutdown():
    if ur:
        await ur.close()


@app.post("/asana-webhook/{token}")
async def asana_webhook(request: Request, token: str):
    if not settings.asana_path_token or token != settings.asana_path_token:
        raise HTTPException(status_code=401, detail="Invalid path token")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    raw_domain = extract_domain_from_payload(payload)
    if not raw_domain:
        return JSONResponse(status_code=422, content={"ok": False, "error": "domain_not_found"})

    context = build_monitor_context(raw_domain, scheme=settings.default_scheme)

    existing = await ur.find_monitor_by_url(context["domain"])
    if existing:
        return {"ok": True, "message": "Monitor already exists", "monitor": existing.get("url")}

    created = await ur.create_http_monitor(url=context["monitor_url"], friendly_name=context["friendly_name"])
    if created.get("id"):
        return {"ok": True, "created": created}

    return JSONResponse(status_code=502, content={"ok": False, "error": created})
