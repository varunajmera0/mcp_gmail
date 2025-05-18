# setup.py
from setuptools import setup, find_packages

setup(
    name='mcp_gmail',
    version='0.1.0',
    description='Gmail MCP Server for LLM RAG workflows',
    author='Varun Ajmera',
    author_email='',
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=[
        'fastmcp',
        'google-api-python-client',
        'google-auth-oauthlib',
        'pydantic',
        'click',
        'PyPDF2',
        'python-dotenv',
        'pydantic-settings'
    ],
    entry_points={
        'console_scripts': [
            'mcp_gmail = mcp_gmail.cli:cli',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
)
