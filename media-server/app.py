from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles

app = Starlette(debug=False)
# เสิร์ฟไฟล์ media ภายใต้ /s65114540635/media
app.mount("/s65114540635/media", StaticFiles(directory="/data", check_dir=True), name="media")
