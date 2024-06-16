from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

import settings
from script import poll_apple_music, print_most_recent_scrobble, scrobble_to_lastfm
from service import get_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/username")
def username():
    return {"username": settings.USERNAME}


@app.get("/user")
def username():
    user = get_user()
    return {"user": user}


@app.get("/current-song")
def get_current_song():
    result = poll_apple_music()
    app.state.current_song = result
    return {"current_song": app.state.current_song}


@app.get("/recent-scrobble")
def get_recent_scrobble():
    print_most_recent_scrobble()
    return {"message": "Check the console for the most recent scrobble"}


@app.post("/scrobble")
def scrobble_song():
    result = scrobble_to_lastfm(app.state.current_song)
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host="0.0.0.0", port=8000, reload=True)
