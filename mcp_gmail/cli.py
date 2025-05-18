import click
from .server import mcp
from .config import settings

@click.group()
def cli():
    "MCP GMAIL CLI"
    pass

@cli.command()
def serve():
    "Start the MCP GMAIL server"
    click.echo(
        f"Serving GmailMCP on {settings.MCP_TRANSPORT}://"
        f"{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}/sse"
    )
    mcp.run(
        transport=settings.MCP_TRANSPORT,
        host=settings.MCP_SERVER_HOST,
        port=settings.MCP_SERVER_PORT
    )

if __name__ == '__main__':
    cli()