set apiFile=main
python -m uvicorn "%apiFile%:app" --reload --port 8000
