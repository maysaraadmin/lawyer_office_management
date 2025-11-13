from setuptools import setup, find_packages

setup(
    name="lawyer_office_frontend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flet',
        'httpx',
        'python-jose',
    ],
    python_requires='>=3.8',
)
