import json
import os
import asyncio
import logging
from typing import AsyncGenerator, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def safe_read_file(filepath: str, chunk_size: int = 8192) -> AsyncGenerator[str, None]:
    """
    Reads a file safely, chunk by chunk, to prevent excessive memory usage.

    Args:
        filepath (str): The path to the file.
        chunk_size (int): The size of each chunk to read (in bytes).

    Yields:
        str: Chunks of data read from the file.
    """
    try:
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        # Use 'async with' for file handling to ensure proper resource management
        try:
            import aiofiles
        except ImportError:
            raise ImportError("aiofiles must be installed: pip install aiofiles")

        async with aiofiles.open(filepath, mode='r', encoding='utf-8') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        raise
    except IOError as e:
        logging.error(f"IO error during read: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during read: {e}")
        raise

async def process_file_content(filepath: str) -> Optional[List[Any]]:
    """
    Processes the content of a file, chunk by chunk.  Example uses json loading.
    """
    try:
        data: List[Any] = []
        async for chunk in safe_read_file(filepath):
            # Optimisation:  Parse entire chunk instead of line by line
            for line in chunk.splitlines():
                if line.strip():
                    try:
                        json_data = json.loads(line)
                        data.append(json_data)
                    except json.JSONDecodeError as e:
                        logging.warning(f"Invalid JSON in chunk. Skipping line: {line[:50]}... Error: {e}")
        return data
    except (FileNotFoundError, IOError) as e:
        logging.error(f"Error reading or processing file: {e}")
        return None  # Or re-raise, depending on the need
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None

async def main():
    filepath = "lessons_learned.json"
    # Create a dummy file for testing if it doesn't exist
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write('{"lesson": "example"}\n{"lesson": "another"}\n') # Simulate multiple JSON objects per line

    try:
        lessons = await process_file_content(filepath)
        if lessons:
            print(json.dumps(lessons, indent=2))
        else:
            print("Failed to process lessons_learned.json")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        import aiofiles  #  Import aiofiles here to avoid import issues.
    except ImportError:
        print("aiofiles is not installed. Please install it with: pip install aiofiles")
        exit(1) # Exit gracefully if aiofiles is not available

    asyncio.run(main())