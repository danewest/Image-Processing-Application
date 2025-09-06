import os
import time
import psutil
import tracemalloc
import csv
import glob
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
from image_processor import ImageProcessor

ITERATIONS = 10
IMAGE_DIR = Path("../Images")
OUTPUT_DIR = Path("Results/")
IMAGE_EXTENSIONS = ("*.jpg", "*.png")

RESULTS_FILE = "Results/profiling_results.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Takes all images from the Images folder and puts them into an array
def get_all_images():
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(glob.glob(os.path.join(IMAGE_DIR, ext)))
    return images

# Profiler
def profile_function(name, func, *args, **kwargs):
    times, memories, cpu_usages, disk_ios = [], [], [], []
    process = psutil.Process()

    for _ in range(ITERATIONS):
        tracemalloc.start()
        start_time = time.perf_counter()
        func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        cpu_usage = process.cpu_percent(interval=None)
        disk_io_counters = process.io_counters()

        times.append(elapsed)
        memories.append(peak / 10**6)
        cpu_usages.append(cpu_usage)
        disk_ios.append(disk_io_counters.write_bytes + disk_io_counters.read_bytes)

    return {
        "test": name,
        "avg_time": sum(times) / ITERATIONS,
        "avg_memory_mb": sum(memories) / ITERATIONS,
        "avg_cpu_percent": sum(cpu_usages) / ITERATIONS,
        "avg_disk_io_bytes": sum(disk_ios) / ITERATIONS
    }

def run_test_suite():
    results = []
    images = get_all_images()

    if not images:
        print("No images found in", IMAGE_DIR)
        return

    # 1. Unit/method profiling
    img_file = images[0]  # single representative image
    image = ImageProcessor("input", str(img_file))

    results.append(profile_function("grayscale", image.grayscale))
    results.append(profile_function("rotate90", image.rotate_90))
    results.append(profile_function("rotate180", image.rotate_180))
    results.append(profile_function("flipx", image.flip_on_x))
    results.append(profile_function("flipy", image.flip_on_y))
    results.append(profile_function("flipxy", image.flip_on_xy))
    results.append(profile_function("blur", image.blur, 20))
    results.append(profile_function("sharpen", image.sharpen))
    results.append(profile_function("grayscale", image.grayscale))
    results.append(profile_function("sepia", image.sepia))
    results.append(profile_function("crop", image.crop, (10, 10, 100, 100)))
    results.append(profile_function("resize-pixel", image.resize_pixel, 500, 500))

    # 2. Load test (batch grayscale)
    def batch_process():
        for f in images:
            img = ImageProcessor("input", str(f))
            img.grayscale()
    results.append(profile_function("batch_grayscale_load", batch_process))

    # 3. Stress test (multi-transforms on one image)
    def stress_process():
        img = ImageProcessor("input", str(images[0]))
        img.grayscale()
        img.rotate_180()
        img.flip_on_xy()
        img.sepia()
    results.append(profile_function("stress_transformations", stress_process))

    # 4. Disk I/O test
    def save_and_reload():
        img = ImageProcessor("input", str(images[0]))
        out_path = OUTPUT_DIR / "temp.jpg"
        img.save(str(out_path))
        reloaded = Image.open(out_path)
        return reloaded
    results.append(profile_function("disk_io_save_reload", save_and_reload))

    # 5. Optimization test (resize vs full-size)
    def optimized_resize():
        img = ImageProcessor("input", str(images[0]))
        img.resize_ratio(0.8, 0.8)
    results.append(profile_function("optimized_resize", optimized_resize))

    # Write results to CSV
    with open(RESULTS_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"Profiling complete. Results saved to {RESULTS_FILE}")
    return results

def visualize_results(results):
    load_test = next((r for r in results if r["test"] == "batch_grayscale_load"), None)
    stress_test = next((r for r in results if r["test"] == "stress_transformations"), None)

    if not load_test or not stress_test:
        print("Couldn't find load or stress test results in results.")
        return

    labels = ["Load Test", "Stress Test"]

    times = [load_test["avg_time"], stress_test["avg_time"]]
    memories = [load_test["avg_memory_mb"], stress_test["avg_memory_mb"]]
    cpu_usages = [load_test["avg_cpu_percent"], stress_test["avg_cpu_percent"]]
    disk_ios = [load_test["avg_disk_io_bytes"], stress_test["avg_disk_io_bytes"]]

    # Plot execution times
    plt.figure(figsize=(10, 6))
    plt.bar(labels, times)
    plt.title("Average Execution Time (seconds)")
    plt.ylabel("Time (s)")
    plt.show()

    # Plot memory usage
    plt.figure(figsize=(10, 6))
    plt.bar(labels, memories)
    plt.title("Average Memory Usage (MB)")
    plt.ylabel("Memory (MB)")
    plt.show()

    # Plot CPU usage
    plt.figure(figsize=(10, 6))
    plt.bar(labels, cpu_usages)
    plt.title("Average CPU Usage (%)")
    plt.ylabel("CPU %")
    plt.show()

    # Plot Disk I/O
    plt.figure(figsize=(10, 6))
    plt.bar(labels, disk_ios)
    plt.title("Average Disk I/O (bytes)")
    plt.ylabel("Bytes")
    plt.show()

if __name__ == "__main__":
    results = run_test_suite()
    visualize_results(results)