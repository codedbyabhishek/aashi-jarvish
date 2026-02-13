import uvicorn


if __name__ == "__main__":
    uvicorn.run("ashi_os.api.app:app", host="127.0.0.1", port=8787, reload=True)
