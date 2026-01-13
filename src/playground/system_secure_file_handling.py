import json
import os
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def safe_read_file(filepath, chunk_size=8192):
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

        import aiofiles  # Import aiofiles inside the function where it's used.

        async with aiofiles.open(filepath, mode="r", encoding="utf-8") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        raise
    except ImportError as e:  # Handle the ImportError
        logging.error(
            f"aiofiles not installed: {e}.  Install with: pip install aiofiles"
        )
        raise  # Re-raise to signal the issue
    except IOError as e:
        logging.error(f"IO error during read: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during read: {e}")
        raise


async def process_file_content(filepath):
    """
    Processes the content of a file, chunk by chunk.  Example uses json loading.
    """
    try:
        data = []
        async for chunk in safe_read_file(filepath):
            try:
                # Attempt to parse each chunk as JSON.  Handle potential errors.
                for line in chunk.splitlines():
                    if line.strip():  # ignore empty lines
                        try:
                            json_data = json.loads(line)
                            data.append(json_data)
                        except json.JSONDecodeError as e:
                            logging.warning(
                                f"Invalid JSON in chunk: {e}. Skipping line: {line[:50]}..."
                            )
            except Exception as e:
                logging.error(f"Error processing chunk: {e}")
                raise
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
            f.write(
                '{"lesson": "example"}\n{"lesson": "another"}\n'
            )  # Simulate multiple JSON objects per line

    try:
        lessons = await process_file_content(filepath)
        if lessons:
            print(json.dumps(lessons, indent=2))
        else:
            print("Failed to process lessons_learned.json")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
