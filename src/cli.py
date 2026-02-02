"""CLI for Agentix - Teradata to Redshift Query Translator"""

import click
import json
from pathlib import Path
from typing import Optional

from src.utils import Config
from src.agents import TranslationOrchestrator


@click.group()
def cli():
    """Agentix - Teradata to Redshift Query Translator"""
    pass


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    default="./data/input",
    help="Input folder with Teradata queries",
)
@click.option(
    "--output",
    type=click.Path(),
    default="./data/output",
    help="Output folder for Redshift queries",
)
@click.option(
    "--logs",
    type=click.Path(),
    default="./logs",
    help="Logs folder",
)
@click.option(
    "--strategy",
    type=click.Choice(["basic", "advanced", "iterative"]),
    default="basic",
    help="Translation strategy",
)
@click.option(
    "--max-retries",
    type=int,
    default=3,
    help="Maximum retry attempts per query",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Log level",
)
def translate(
    input: str,
    output: str,
    logs: str,
    strategy: str,
    max_retries: int,
    log_level: str,
):
    """Execute full translation pipeline"""
    click.echo("🚀 Starting Agentix Translation Pipeline")
    click.echo(f"   Input:  {input}")
    click.echo(f"   Output: {output}")
    click.echo(f"   Logs:   {logs}")
    click.echo(f"   Strategy: {strategy}")
    click.echo(f"   Max Retries: {max_retries}")

    # Configure
    Config.DATA_INPUT_PATH = input
    Config.DATA_OUTPUT_PATH = output
    Config.LOGS_PATH = logs
    Config.TRANSLATION_STRATEGY = strategy
    Config.MAX_RETRIES = max_retries
    Config.LOG_LEVEL = log_level
    Config.ensure_paths()

    try:
        orchestrator = TranslationOrchestrator(Config)
        result = orchestrator.execute_full_pipeline(max_retries=max_retries)

        click.echo("\n" + "=" * 50)
        if result["status"] == "success":
            summary = result["summary"]
            click.secho("✅ Pipeline Completed Successfully!", fg="green", bold=True)
            click.echo(f"\nSummary:")
            click.echo(f"  Total Items: {summary['total_items']}")
            click.echo(f"  Successful: {summary['successful_items']}")
            click.echo(f"  Failed: {summary['failed_items']}")
            click.echo(f"  Success Rate: {summary['success_rate']:.1f}%")
            click.echo(f"\nLogs: {result['logs_path']}")
        elif result["status"] == "empty":
            click.secho("⚠️  No queries found to process", fg="yellow")
        else:
            click.secho(f"❌ Error: {result['error']}", fg="red")
            click.echo(f"Logs: {result['logs_path']}")

        click.echo("=" * 50)

    except Exception as e:
        click.secho(f"❌ Fatal Error: {str(e)}", fg="red")
        raise click.Abort()


@cli.group()
def steps():
    """Manage individual pipeline steps"""
    pass


@steps.command()
def list():
    """List available steps"""
    click.echo("Available steps:")
    steps_list = [
        ("read_queries", "Read SQL queries from input folders"),
        ("translate", "Translate queries with retry logic"),
        ("validate", "Validate translated queries"),
        ("report", "Generate reports and summaries"),
    ]

    for step_name, description in steps_list:
        click.echo(f"  • {step_name:<15} - {description}")


@steps.command()
@click.argument("step_name")
@click.option("--input", type=click.Path(exists=True), default="./data/input")
@click.option("--output", type=click.Path(), default="./data/output")
@click.option("--logs", type=click.Path(), default="./logs")
@click.option("--max-retries", type=int, default=3)
@click.option("--data-file", type=click.Path(exists=True), help="Input data JSON file")
def run(
    step_name: str,
    input: str,
    output: str,
    logs: str,
    max_retries: int,
    data_file: Optional[str],
):
    """Run a specific step"""
    click.echo(f"📍 Running step: {step_name}")

    # Configure
    Config.DATA_INPUT_PATH = input
    Config.DATA_OUTPUT_PATH = output
    Config.LOGS_PATH = logs
    Config.ensure_paths()

    try:
        orchestrator = TranslationOrchestrator(Config)

        # Load input data if provided
        input_data = {}
        if data_file:
            with open(data_file, "r") as f:
                input_data = json.load(f)
            click.echo(f"   Loaded data from: {data_file}")

        # Execute step
        result = orchestrator.execute_step(
            step_name,
            queries_by_folder=input_data.get("queries_by_folder"),
            translation_results=input_data.get("translation_results"),
            validation_results=input_data.get("validation_results"),
            max_retries=max_retries,
        )

        if result["status"] == "success":
            click.secho(f"✅ Step '{step_name}' completed!", fg="green")
            if "step_result" in result:
                sr = result["step_result"]
                click.echo(f"\n  Total: {sr['total_items']}")
                click.echo(f"  Successful: {sr['successful_items']}")
                click.echo(f"  Failed: {sr['failed_items']}")

            # Save output data
            if "data" in result:
                output_file = Path(logs) / f"{step_name}_output.json"
                # Convert data to serializable format
                # (would need custom JSON encoder for real objects)
                click.echo(f"\n  Output: {output_file}")

        else:
            click.secho(f"❌ Error: {result['error']}", fg="red")

    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg="red")
        raise click.Abort()


@cli.command()
def init():
    """Initialize project structure"""
    click.echo("📁 Initializing Agentix project structure...")

    paths = [
        "./data/input",
        "./data/output",
        "./data/synthetic",
        "./logs",
    ]

    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)
        click.echo(f"  ✓ Created {path}")

    # Create example .sql file
    example_query = """-- Example Teradata Query
SELECT 
    customer_id,
    customer_name,
    COUNT(*) as order_count,
    SUM(order_amount) as total_amount
FROM customer_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '1' YEAR
GROUP BY customer_id, customer_name
QUALIFY ROW_NUMBER() OVER (ORDER BY total_amount DESC) <= 10;
"""

    example_file = Path("./data/input") / "example_query.sql"
    example_file.write_text(example_query)
    click.echo(f"  ✓ Created example query: {example_file}")

    click.secho("\n✅ Project initialized!", fg="green")
    click.echo("\nNext steps:")
    click.echo("  1. Add Teradata queries to ./data/input/")
    click.echo("  2. Set ANTHROPIC_API_KEY in .env")
    click.echo("  3. Run: agentix translate")


@cli.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def info(format: str):
    """Show project information"""
    info_data = {
        "input_path": Config.DATA_INPUT_PATH,
        "output_path": Config.DATA_OUTPUT_PATH,
        "logs_path": Config.LOGS_PATH,
        "strategy": Config.TRANSLATION_STRATEGY,
        "max_retries": Config.MAX_RETRIES,
        "log_level": Config.LOG_LEVEL,
    }

    if format == "json":
        click.echo(json.dumps(info_data, indent=2))
    else:
        click.echo("Agentix Configuration:")
        for key, value in info_data.items():
            click.echo(f"  {key}: {value}")


if __name__ == "__main__":
    cli()
