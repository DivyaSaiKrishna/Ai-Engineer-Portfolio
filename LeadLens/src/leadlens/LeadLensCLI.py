import argparse

from leadlens.LeadLensConfig import leadlensconfig

class StructuredOutputError(Exception):
    pass

def main() -> None:
    parser = argparse.ArgumentParser(prog="leadlens")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="Ask a question")
    ask.add_argument("question")
    ask.add_argument("--model", default="claude-haiku-5-5")
    ask.add_argument("--max-tokens", type=int, default=1024)
    ask.add_argument("--stream", action="store_true")
    ask.add_argument("--json", action="store_true")
    ask.add_argument("--prof", action="store_true")

    args = parser.parse_args()

    if args.command == "ask":
        try:
            client = leadlensconfig(model=args.model, max_tokens=args.max_tokens)
        except ValueError as e:
            parser.error(str(e))
        if args.prof:
            try:
                print(client.ask_prof(args.question).model_dump_json(indent=2))
            except StructuredOutputError as e:
                print(f"Error: {e}")
                raise SystemExit(1)
        elif args.json:
            try:
                print(client.ask_json(args.question).model_dump_json(indent=2))
            except StructuredOutputError as e:
                print(f"Error: {e}")
                raise SystemExit(1)
        elif args.stream:
            for chunk in client.ask_stream(args.question):
                print(chunk, end="", flush=True)
            print()
        else:
            print(client.ask(args.question))
        print(f"\n[stop_reason={client.last_stop_reason} usage={client.last_usage}]")
    
if __name__ == "__main__":
    main()