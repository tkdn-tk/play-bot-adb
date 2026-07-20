import sys
import yaml
import threading
import asyncio
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.logger import logger
from main import load_config, scan_mumu_instances
from core.bot import AutoPlayBot

app = FastAPI()

bot_thread = None
global_bot_instance = None
bot_is_running = False
loop = None
log_queues = set()

def start_bot_thread(config):
    global bot_thread, bot_is_running, global_bot_instance
    bot_is_running = True
    
    def run_wrapper():
        global bot_is_running, global_bot_instance
        try:
            logger.set_config(config)
            global_bot_instance = AutoPlayBot(config)
            global_bot_instance.start()
        except Exception as e:
            logger.error(f"Bot thread error: {e}")
        finally:
            bot_is_running = False
            global_bot_instance = None
            
    bot_thread = threading.Thread(target=run_wrapper, daemon=True)
    bot_thread.start()

def stop_bot_thread():
    global bot_is_running, global_bot_instance
    if global_bot_instance:
        global_bot_instance.stop()
        bot_is_running = False

class ConfigModel(BaseModel):
    config: dict

@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_running_loop()

def sync_log_callback(log_entry):
    if loop is None: return
    for q in log_queues:
        loop.call_soon_threadsafe(q.put_nowait, log_entry)

logger.add_callback(sync_log_callback)

@app.get("/api/config")
def get_config():
    return load_config("config.yaml")

@app.post("/api/config")
def save_config(model: ConfigModel):
    try:
        with open("config.yaml", "w") as f:
            yaml.safe_dump(model.config, f, sort_keys=False)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/instances")
def get_instances():
    return scan_mumu_instances()

@app.get("/api/status")
def get_status():
    import time
    is_paused = False
    current_state = "STOPPED"
    session_count = 0
    total_time = 0
    current_loop_time = 0
    current_step_time = 0
    gift_countdown = 0
    
    if global_bot_instance:
        is_paused = global_bot_instance.paused
        if global_bot_instance.running:
            current_state = global_bot_instance.current_state.name
            session_count = getattr(global_bot_instance, 'session_count', 0)
            st = getattr(global_bot_instance, 'start_time', 0)
            if st: total_time = time.time() - st
            clst = getattr(global_bot_instance, 'current_loop_start_time', 0)
            if clst: current_loop_time = time.time() - clst
            csst = getattr(global_bot_instance, 'current_state_start_time', 0)
            if csst: current_step_time = time.time() - csst
            
            # Gift countdown
            gift_interval_min = global_bot_instance.config.get("gift_interval_minutes")
            if gift_interval_min is None:
                gift_interval_min = global_bot_instance.config.get("gift_interval_hours", 1.0) * 60.0
            
            elapsed_gift = time.time() - getattr(global_bot_instance, 'last_gift_time', 0)
            gift_countdown = max(0, (gift_interval_min * 60) - elapsed_gift)
            
    return {
        "running": bot_is_running, 
        "paused": is_paused, 
        "current_state": current_state,
        "session_count": session_count,
        "total_time": total_time,
        "current_loop_time": current_loop_time,
        "current_step_time": current_step_time,
        "gift_countdown": gift_countdown
    }

@app.post("/api/start")
def start_bot():
    if not bot_is_running:
        config = load_config("config.yaml")
        start_bot_thread(config)
        return {"status": "started"}
    return {"status": "already_running"}

@app.post("/api/stop")
def stop_bot():
    if bot_is_running:
        stop_bot_thread()
        return {"status": "stopped"}
    return {"status": "not_running"}

@app.post("/api/pause")
def pause_bot():
    if bot_is_running and global_bot_instance:
        if not global_bot_instance.paused:
            global_bot_instance.toggle_pause()
        return {"status": "paused"}
    return {"status": "not_running"}

@app.post("/api/resume")
def resume_bot():
    if bot_is_running and global_bot_instance:
        if global_bot_instance.paused:
            global_bot_instance.toggle_pause()
        return {"status": "resumed"}
    return {"status": "not_running"}

@app.post("/api/terminate")
def terminate_app():
    stop_bot_thread()
    def seppuku():
        import time
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=seppuku).start()
    return {"status": "terminating"}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    q = asyncio.Queue()
    log_queues.add(q)
    try:
        while True:
            log_entry = await q.get()
            await websocket.send_json(log_entry)
    except WebSocketDisconnect:
        log_queues.remove(q)

app.mount("/", StaticFiles(directory="web", html=True), name="web")

def minimize_to_tray():
    try:
        import pystray
        from PIL import Image, ImageDraw
        
        def create_image():
            image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
            d = ImageDraw.Draw(image)
            d.ellipse((8, 8, 56, 56), fill=(210, 140, 75))
            d.ellipse((16, 24, 24, 32), fill=(76, 42, 21))
            d.ellipse((36, 16, 44, 24), fill=(76, 42, 21))
            d.ellipse((24, 40, 32, 48), fill=(76, 42, 21))
            d.ellipse((40, 36, 48, 44), fill=(76, 42, 21))
            d.ellipse((28, 20, 34, 26), fill=(76, 42, 21))
            return image
            
        def exit_action(icon, item):
            import os
            icon.stop()
            os._exit(0)
            
        def open_webui(icon, item):
            import webbrowser
            webbrowser.open_new("http://localhost:8000")
            
        menu = pystray.Menu(
            pystray.MenuItem('Show WebUI', open_webui),
            pystray.MenuItem('Exit', exit_action)
        )
        icon = pystray.Icon("CookieBot", create_image(), "CookieRun Bot", menu)
        
        icon.run_detached()
    except ImportError:
        pass # If pystray isn't installed, just stay hidden (can be closed via UI)

def run_webui():
    import webbrowser
    import time
    def open_browser():
        time.sleep(1.5)
        webbrowser.open_new("http://localhost:8000")
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("Starting WebUI on http://localhost:8000")
    minimize_to_tray()
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)

if __name__ == "__main__":
    run_webui()
