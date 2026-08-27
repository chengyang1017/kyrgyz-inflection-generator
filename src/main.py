import argparse
import sys

from generator import generate_all
from i18n import SUPPORTED_LOCALES


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Kyrgyz inflection datasets with localized labels."
    )
    parser.add_argument(
        "--locale",
        choices=(*SUPPORTED_LOCALES, "all"),
        default="en",
        help="Output language for labels and meanings. Use 'all' for every supported locale.",
    )
    return parser.parse_args()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = parse_args()
    generate_all(locale=args.locale)


if __name__ == "__main__":
    main()
