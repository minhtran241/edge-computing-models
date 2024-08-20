from setuptools import setup, find_packages

setup(
    name="iot-edge-cloud",
    version="0.1.0",
    author="Minh Tran",
    author_email="tranmq@mail.gvsu.edu",
    url="https://github.com/minhtran241/edge-computing-models",
    description="A simple IoT edge-cloud system for benchmarking.",
    license="MIT",
    keywords="iot edge cloud benchmarking",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "iot-edge-cloud=iot_edge_cloud.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
