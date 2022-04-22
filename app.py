from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import cv2

app = FastAPI()

path = Path("C:/Users/hp/Downloads/kosamba_bottle_counting/")
app.mount("/static", StaticFiles(directory=path), name="static")
templates = Jinja2Templates(directory="templates")

def stream_from_file(file_path):
    video_file = cv2.VideoCapture(file_path)
    while True:
        success, frame = video_file.read()
        if not success:
            break
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/list_dirs")
async def list_dirs(query: str, request: Request):
    paths = path / query
    total_dirs = os.listdir(paths)
    ls = []
    dir_names = []
    for i in total_dirs:
        path_to_file = paths / i
        if os.path.isfile(path_to_file):
            query = f"video/?query={path_to_file}"
        if os.path.isdir(path_to_file):
            query = f"list_dirs/?query={path_to_file}"
        #ls.append(query)
        name = i.split("/")[0]
        dictonary = {"name": name, "query": query}
        #dir_names.append(name)
        ls.append(dictonary)
    print(ls)
    return  templates.TemplateResponse("list_dirs.html", 
                                       {"request": request, 
                                        "dirs": ls, 
                                       })


@app.get("/video_stream")
async def video_html(video_path: str, response: Response):
    full_path = path / video_path
    str_path = str(full_path)
    return StreamingResponse(stream_from_file(str_path), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/video")
async def stream(request: Request, query: str):
    video_path = path / query
    path_str = str(video_path)
    return StreamingResponse(open(path_str, 'rb'), media_type='video/mp4')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
