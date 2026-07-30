import json

TASK_ANALYSIS_SYSTEM_PROMPT = """You are an expert QA automation engineer AI.
Your job is to analyze a given software development task, identify potential testing risks, and recommend a list of deterministic automation steps.
You MUST output your response in strict JSON matching the schema provided.
"""

def build_task_analysis_prompt(task_title: str, task_desc: str, acceptance_criteria: str) -> str:
    return f"""Analyze the following task:
Title: {task_title}
Description: {task_desc or ''}
Acceptance Criteria: {acceptance_criteria or ''}

Identify missing requirements and recommend a strict, deterministic test plan.
"""
