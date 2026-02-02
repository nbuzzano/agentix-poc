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
    click.echo("🚀 Starting Agentix Translation Pipeline (Agent-Based Skills)")
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
            click.secho("✅ Pipeline Completed Successfully!", fg="green", bold=True)
            
            # Show results from each skill
            read_results = result.get("read_results", {})
            translate_results = result.get("translate_results", {})
            validate_results = result.get("validate_results", {})
            report = result.get("report", {})
            
            click.echo(f"\n📖 Read Queries Skill:")
            if isinstance(read_results, dict):
                click.echo(f"   Status: {read_results.get('status', 'unknown')}")
                if 'folders' in read_results:
                    click.echo(f"   Folders processed: {len(read_results.get('folders', []))}")
                    click.echo(f"   Total queries: {read_results.get('total_queries', 0)}")
            
            click.echo(f"\n🔄 Translate Skill:")
            if isinstance(translate_results, dict):
                click.echo(f"   Status: {translate_results.get('status', 'unknown')}")
            
            click.echo(f"\n✔️  Validate Skill:")
            if isinstance(validate_results, dict):
                click.echo(f"   Status: {validate_results.get('status', 'unknown')}")
            
            click.echo(f"\n📊 Generate Report Skill:")
            if isinstance(report, dict):
                click.echo(f"   Status: {report.get('status', 'unknown')}")
                if 'summary' in report:
                    summary = report['summary']
                    click.echo(f"   Total Items: {summary.get('total_queries', 0)}")
                    click.echo(f"   Successful: {summary.get('successful', 0)}")
                    click.echo(f"   Failed: {summary.get('failed', 0)}")
            
            click.echo(f"\nLogs: {result['logs_path']}")
        else:
            click.secho(f"❌ Error: {result['error']}", fg="red")
            if 'skill' in result:
                click.echo(f"Failed skill: {result['skill']}")
            click.echo(f"Logs: {result['logs_path']}")

        click.echo("=" * 50)

    except Exception as e:
        click.secho(f"❌ Fatal Error: {str(e)}", fg="red")
        raise click.Abort()


@cli.group()
def skills():
    """Manage individual skills"""
    pass


@skills.command()
def list():
    """List available skills"""
    click.echo("Available Skills:")
    skills_list = [
        ("read-queries", "Read and catalog SQL queries from input folders"),
        ("translate-teradata-to-redshift", "Translate Teradata queries to Redshift syntax"),
        ("validate-queries", "Validate translated queries for Redshift compatibility"),
        ("generate-report", "Generate comprehensive reports and logs"),
    ]

    for skill_name, description in skills_list:
        click.echo(f"  • {skill_name:<30} - {description}")


@skills.command()
@click.argument("skill_name")
@click.option("--input", type=click.Path(exists=True), default="./data/input")
@click.option("--output", type=click.Path(), default="./data/output")
@click.option("--logs", type=click.Path(), default="./logs")
@click.option("--data-file", type=click.Path(exists=True), help="Input data JSON file")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), default="INFO")
def run(
    skill_name: str,
    input: str,
    output: str,
    logs: str,
    data_file: Optional[str],
    log_level: str,
):
    """Run a specific skill"""
    click.echo(f"🎯 Executing skill: {skill_name}")

    # Configure
    Config.DATA_INPUT_PATH = input
    Config.DATA_OUTPUT_PATH = output
    Config.LOGS_PATH = logs
    Config.LOG_LEVEL = log_level
    Config.ensure_paths()

    try:
        orchestrator = TranslationOrchestrator(Config)

        # Load input data if provided
        input_data = None
        if data_file:
            with open(data_file, "r") as f:
                input_data = json.load(f)
            click.echo(f"   Loaded data from: {data_file}")
        else:
            # Build default input based on skill
            if skill_name == "read-queries":
                input_data = {
                    "input_path": input,
                    "file_extensions": [".sql", ".txt"],
                }
            else:
                input_data = {}

        # Execute skill
        result = orchestrator.execute_skill(
            skill_name,
            input_data=input_data,
            context=f"Executing {skill_name} skill as requested"
        )

        if result["status"] == "success":
            click.secho(f"✅ Skill '{skill_name}' executed successfully!", fg="green")
            
            skill_data = result.get("data", {})
            click.echo(f"\nResult:")
            # Show summary based on skill type
            if skill_name == "read-queries":
                if isinstance(skill_data, dict) and "total_queries" in skill_data:
                    click.echo(f"  Total queries: {skill_data.get('total_queries', 0)}")
                    click.echo(f"  Folders processed: {len(skill_data.get('folders', []))}")
            elif skill_name == "translate-teradata-to-redshift":
                click.echo(f"  Status: {skill_data.get('status', 'unknown')}")
            elif skill_name == "validate-queries":
                click.echo(f"  Status: {skill_data.get('status', 'unknown')}")
            elif skill_name == "generate-report":
                if isinstance(skill_data, dict) and "summary" in skill_data:
                    summary = skill_data["summary"]
                    click.echo(f"  Total queries: {summary.get('total_queries', 0)}")
                    click.echo(f"  Successful: {summary.get('successful', 0)}")
                    click.echo(f"  Failed: {summary.get('failed', 0)}")

            # Save output data
            output_file = Path(logs) / f"{skill_name.replace('-', '_')}_output.json"
            with open(output_file, "w") as f:
                json.dump(skill_data, f, indent=2)
            click.echo(f"\n  Output saved to: {output_file}")

        else:
            click.secho(f"❌ Error: {result['error']}", fg="red")

    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg="red")
        raise click.Abort()


@cli.command()
def init():
    """Initialize project structure"""
    click.echo("📁 Initializing Agentix project structure...")
    click.echo("   (Agent-Based Skills Architecture)")

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
    click.echo("\nAvailable commands:")
    click.echo("  • agentix translate          - Run full pipeline")
    click.echo("  • agentix skills list        - List available skills")
    click.echo("  • agentix skills run <name>  - Execute a specific skill")


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
