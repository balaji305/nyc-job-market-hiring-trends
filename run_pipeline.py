"""Execute the complete project from ingestion through reporting."""
from src.ingest import download
from src.clean import run as clean
from src.metrics import run as analyze

if __name__ == "__main__":
    download(); clean(); summary = analyze()
    print("\nPROJECT SUMMARY")
    print(f"Total rows analyzed: {summary['total_postings']:,}")
    print(f"Agencies: {summary['agencies']}")
    print(f"Job categories: {summary['job_categories']}")
    print(f"Date range: {summary['date_min']} to {summary['date_max']}")
    print("Key data-quality issues: see data/processed/data_quality_summary.json")
    print("Verified resume bullets:")
    for bullet in summary["resume_bullets"]: print(f"- {bullet}")
