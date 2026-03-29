from transcript import extract_video_id

test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "dQw4w9WgXcQ"
]

def run_tests():
    for url in test_urls:
        try:
            vid = extract_video_id(url)
            print(f"URL: {url} => Video ID: {vid}")
            assert vid == "dQw4w9WgXcQ"
        except Exception as e:
            print(f"FAILED for {url}: {e}")

if __name__ == "__main__":
    run_tests()
