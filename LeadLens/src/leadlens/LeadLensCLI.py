import argparse

from leadlens.LeadLensConfig import leadlensconfig

def main() -> None:
    parser = argparse.ArgumentParser(prog="leadlens")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="Ask a question")
    ask.add_argument("question")
    ask.add_argument("--model", default="claude-haiku-5-5")
    ask.add_argument("--max-tokens", type=int, default=1024)
    ask.add_argument("--stream", action="store_true")

    args = parser.parse_args()

    if args.command == "ask":
        client = leadlensconfig(model=args.model, max_tokens=args.max_tokens)
        if args.stream:
            for chunk in client.ask_stream(args.question):
                print(chunk, end="", flush=True)
            print()
        else:
            print(client.ask(args.question))
        print(f"\n[stop_reason={client.last_stop_reason} usage={client.last_usage}]")
    
if __name__ == "__main__":
    main()