"""
from setuptools import setup, find_packages
setup(
    name="apibank",
    version="0.1.0",
    author="MNA ESG TEAM",
    description="Une API FastAPI pour gérer les transactions bancaires",
    packages=find_packages(include=["apibank", "apibank.*"]),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "pandas",
        "kaggle",
    ],
    entry_points={
        "console_scripts": [
            "apibank-run=apibank.main:run_api",  
        ],
    },
)
"""
