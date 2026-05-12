class CodeAnalysisTool:
    name = "code_analysis"

    def create_implementation_plan(self, objective: str, research_summary: str) -> dict:
        return {
            "objective": objective,
            "recommended_stack": ["FastAPI", "LangGraph", "PostgreSQL", "ChromaDB", "Next.js"],
            "steps": [
                "Define contracts and typed schemas before adding runtime behavior.",
                "Keep tools small and observable so agent decisions are auditable.",
                "Gate external API calls behind provider interfaces for Gemini/OpenAI portability.",
                "Add integration tests around workflow transitions and retrieval quality.",
            ],
            "research_context": research_summary,
        }

