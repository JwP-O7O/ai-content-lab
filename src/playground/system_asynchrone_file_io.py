import asyncio
import os
import aiofiles
import time
from typing import List, Tuple, Dict, Callable, Any

class ContentQualityMonitor:
    def __init__(self, analysis_functions: Dict[str, Callable[[str], Any]] = None):
        self.analysis_functions = analysis_functions or {}

    async def _read_file_async(self, file_path: str) -> str:
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return content
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        content = await self._read_file_async(file_path)
        results = {}
        for name, func in self.analysis_functions.items():
            try:
                results[name] = func(content)
            except Exception as e:
                results[name] = f"Error during analysis: {e}"
        return results

    async def analyze_files(self, file_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        tasks = [self.analyze(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks)
        return dict(zip(file_paths, results))


def basic_word_count(text: str) -> int:
    return len(text.split())

def simple_vowel_count(text: str) -> int:
    return sum(1 for char in text.lower() if char in 'aeiou')


async def main():
    # Create some dummy files for testing
    if not os.path.exists("test_files"):
        os.makedirs("test_files")
    
    file_paths = []
    for i in range(3):
        file_path = f"test_files/test_file_{i}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"This is test file {i}.  It contains some words and some vowels. aeiou. The quick brown fox jumps over the lazy dog.")
        file_paths.append(file_path)

    analysis_functions = {
        "word_count": basic_word_count,
        "vowel_count": simple_vowel_count,
    }

    monitor = ContentQualityMonitor(analysis_functions)

    start_time = time.time()
    results = await monitor.analyze_files(file_paths)
    end_time = time.time()

    print(f"Analysis results: {results}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    # Clean up dummy files
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
    try:
        os.rmdir("test_files")
    except OSError:
        pass


if __name__ == "__main__":
    asyncio.run(main())