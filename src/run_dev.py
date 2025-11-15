# run_dev.py
import sys
import asyncio


try:
    if "_patch_asyncio" in getattr(asyncio.run, "__qualname__", ""):
        # restore original run implementation
        import asyncio.runners
        asyncio.run = asyncio.runners.run
        print("Restored asyncio.run to original runner to avoid PyCharm debug incompatibility.")
except Exception:
    pass

import uvicorn

if __name__ == "__main__":
    # reload=True 会启用热重载（会 spawn 子进程），debug 时你也可以把它关掉
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=False, log_level="debug")
