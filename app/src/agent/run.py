from agent.graph import graph
from langgraph.types import Command


def extract_final_report(event: dict):
    if 'compile_final_report' in event:
        compile_final_report = event['compile_final_report']
        if 'final_report' in compile_final_report:
            return compile_final_report['final_report']
    return None


async def deep_research(topic: str) -> str:
    input = {"topic": topic}
    thread = {"configurable": {"thread_id": "1"}}

    async for _ in graph.astream(input, config=thread):
        pass

    async for event in graph.astream(
        Command(resume="True"), thread,
    ):
        maybe_final_report = extract_final_report(event)
        if maybe_final_report:
            return maybe_final_report
    return ""
