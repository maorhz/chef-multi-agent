import asyncio
import os
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from chef_grocery_app.agent import root_agent

# Load .env file containing credentials config
dotenv_path = os.path.join(os.path.dirname(__file__), 'chef_grocery_app', '.env')
load_dotenv(dotenv_path)

def print_friendly_event(event) -> None:
    """Print an ADK Event object to the console, preserving logical text order."""
    if not event.content or not event.content.parts:
        return
        
    text_buffer = []
    for part in event.content.parts:
        if part.text:
            text_buffer.append(part.text)
            
    if text_buffer:
        combined_text = ''.join(text_buffer)
        print(f"{event.author} > {combined_text}")



async def main():
    # Set up the runner
    runner = InMemoryRunner(agent=root_agent, app_name="chef_grocery_app")
    
    # Check if a query was passed as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Running single query: {query}\n")
        # Run with quiet=True to suppress the default auto-printing
        events = await runner.run_debug(query, quiet=True)
        for event in events:
            print_friendly_event(event)
        return

    print("=== Chef & Grocery Agent (CLI Mode) ===")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue
                
            # Run with quiet=True to suppress the default auto-printing
            events = await runner.run_debug(user_input, quiet=True)
            
            print("\nAgent:")
            for event in events:
                print_friendly_event(event)
            print("-" * 40)
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    asyncio.run(main())
