import argparse

from . import func


def main():
    parser = argparse.ArgumentParser(prog="scfile")

    parser.add_argument("source", type=str, help="Path to game file.")

    parser.add_argument(
        "--output",
        type=str,
        help=(
            "Optional path to output (include new filename). "
            "Defaults to source path with new suffix."
        )
    )

    args = parser.parse_args()

    source = args.source
    output = args.output

    # TODO: Add proper error handling

    try:
        func.auto(source, output)

    except Exception as err:
        print("Error:", err)


if __name__ == "__main__":
    main()
