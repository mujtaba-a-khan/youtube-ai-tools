from __future__ import annotations
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from ytai.config import settings
from ytai.tools.youtube import YouTubeClient
# Lazy imports for chains (build LLM only when needed)
from ytai.chains import get_analyzer, get_summary_chain

app = typer.Typer(add_completion=False)
console = Console()


def _yt() -> YouTubeClient:
    return YouTubeClient(api_key=settings.youtube_api_key)


@app.command()
def trending(
    region: str = typer.Option("US", help="ISO 3166-1 alpha-2 code, e.g., US, GB, IN"),
    max_results: int = typer.Option(10, min=1, max=50),
    summarize: bool = typer.Option(False, help="Summarize top N videos (requires LLM)"),
    top_n: int = typer.Option(3, help="How many to summarize when --summarize"),
):
    """Show trending videos in a region (and optionally summarize)."""
    yt = _yt()
    vids = yt.get_trending(region=region, max_results=max_results)

    table = Table(title=f"Trending in {region}")
    table.add_column("#", style="bold")
    table.add_column("Title")
    table.add_column("Channel")
    table.add_column("Views")
    table.add_column("URL")

    for i, v in enumerate(vids, 1):
        table.add_row(str(i), v.title, v.channel, f"{v.view_count or '-'}", v.url)
    console.print(table)

    if summarize:
        console.rule("Summaries")
        chain = get_analyzer()  # builds LLM on first use
        for v in vids[:top_n]:
            transcript, _ = yt.get_transcript(v.video_id)
            if not transcript:
                console.print(f"[yellow]No transcript for:[/] {v.title}")
                continue
            result = chain.invoke({"title": v.title, "channel": v.channel, "transcript": transcript})
            console.print(f"\n[bold]{v.title}[/]")
            console.print("[cyan]Summary:[/]")
            console.print(result["summary"]) 
            console.print("[cyan]Hashtags:[/] " + result["hashtags"]) 
            console.print("[cyan]Ideas:[/] " + result["ideas"]) 


@app.command()
def transcript(url_or_id: str, summarize: bool = typer.Option(False, help="Run LLM summary")):
    """Fetch transcript for a single video by URL or ID, optionally summarize."""
    yt = _yt()
    vid = yt.extract_video_id(url_or_id)
    meta = yt.get_video_snippet(vid)
    title = meta.get("items", [{}])[0].get("snippet", {}).get("title", vid)
    channel = meta.get("items", [{}])[0].get("snippet", {}).get("channelTitle", "")

    text, segs = yt.get_transcript(vid)
    if not text:
        console.print("[red]No transcript available.[/]")
        raise typer.Exit(code=1)

    console.rule(f"Transcript: {title}")
    console.print(text)

    if summarize:
        res = get_summary_chain().invoke({"title": title, "channel": channel, "transcript": text})
        console.rule("Summary")
        console.print(res)


@app.command()
def search(query: str, region: Optional[str] = typer.Option(None, help="Optional region code")):
    """Search YouTube for videos."""
    yt = _yt()
    results = yt.search(query, region=region)
    table = Table(title=f"Search: {query}")
    table.add_column("#")
    table.add_column("Title")
    table.add_column("Channel")
    table.add_column("URL")
    for i, v in enumerate(results, 1):
        table.add_row(str(i), v.title, v.channel, v.url)
    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()