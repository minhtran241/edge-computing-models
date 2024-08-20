from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="iot-edge-cloud",
    version="0.1.0",
    author="Minh Tran",
    author_email="tranmq@mail.gvsu.edu",
    url="https://github.com/minhtran241/edge-computing-models",
    description="A simple IoT edge-cloud system for benchmarking.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="iot edge cloud benchmarking",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "iot-edge-cloud=iot_edge_cloud.__main__:main",
        ],
    },
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "opencv-python>=4.2.0",
        "pytesseract>=0.3.7",
        "cython>=0.29.0",
        "click>=7.1.2",
        "colorlog>=4.6.2",
        "nltk>=3.5",
        "python-dotenv>=0.14.0",
        "python-socketio>=4.6.0",
        "tqdm>=4.48.0",
        "ultralytics>=8.0.0",
        "eventlet>=0.30.0",
        "tabulate>=0.8.7",
        "XlsxWriter>=1.3.7",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    # Uncomment if you are using Cython extensions:
    # ext_modules=cythonize("iot_edge_cloud/*.py"),
)
