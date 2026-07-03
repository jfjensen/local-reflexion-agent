import os
import json
import argparse
from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Core LangGraph and Local LangChain Ollama imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# ---------------------------------------------------------------------------
# Global Runtime State Variables (Set during initialization)
# ---------------------------------------------------------------------------
MODEL_REGISTRY = {}
QUALITY_SCORE_BAR = 95
MAX_ATTEMPTS = 4

# ---------------------------------------------------------------------------
# 2. State & Structured Output Definitions
# ---------------------------------------------------------------------------

class DocEvaluationSchema(BaseModel):
    """Pydantic schema used to force a structured JSON schema constraint out of our local critic model."""
    technical_accuracy: int = Field(description="Score from 0-100 on accuracy.")
    completeness: int = Field(description="Score from 0-100 covering parameter definitions.")
    overall_percentage: int = Field(description="The net average score.")
    is_production_ready: bool = Field(description="True if net score >= passing threshold.")
    single_critical_fix: str = Field(description="The single absolute highest priority correction required.")


def append_scores(old: List[int], new: List[int]) -> List[int]:
    return old + new

class AgentWorkflowState(TypedDict):
    """Memory tracking state for the heterogeneous local graph layout."""
    source_code: str
    generated_markdown: str
    current_score: int
    score_history: Annotated[List[int], append_scores]
    required_fix: Optional[str]
    iteration_count: int
    is_approved: bool
    final_adjudicated_markdown: Optional[str]

# ---------------------------------------------------------------------------
# 3. Graph Nodes (The Workflow Steps)
# ---------------------------------------------------------------------------

def content_generator_node(state: AgentWorkflowState) -> dict:
    """The Generator node: Focuses entirely on drafting/editing documentation text layout."""
    current_iteration = state.get("iteration_count", 0)
    target_model = MODEL_REGISTRY["GENERATOR"]
    
    print("\n" + "═"*60)
    print(f" 🛠️  [NODE: GENERATOR] Starting Round {current_iteration + 1} ({target_model})")
    print("═"*60)
    
    llm = ChatOllama(model=target_model, temperature=0.7)
    
    if not state.get("generated_markdown"):
        print(" -> Action: Generating first draft straight from raw source code...")
        system_prompt = "You are an expert technical writer. Convert raw code snippets into clean, comprehensive API markdown documentation."
        user_prompt = f"Generate Markdown documentation for the following source code:\n\n{state['source_code']}"
    else:
        print(f" -> Action: Revising previous draft (Last Score: {state['current_score']}/100)")
        print(f" 🎯 Targeted Issue to Fix: \"{state['required_fix']}\"")
        system_prompt = "You are a precise editor rewriting technical documentation to fix a structural flaw."
        user_prompt = (
            f"Your previous documentation draft was scored {state['current_score']}/100.\n"
            f"You must completely rewrite the documentation to fix this specific issue: {state['required_fix']}\n\n"
            f"Original Code Context:\n{state['source_code']}\n\n"
            f"Previous Draft:\n{state['generated_markdown']}"
        )
        
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    
    print(f" -> Querying local generator '{target_model}'...")
    response = llm.invoke(messages)
    print(" ✅ Generation complete. Passing text block to Critic.")
    
    return {
        "generated_markdown": response.content,
        "iteration_count": current_iteration + 1
    }


def content_critic_node(state: AgentWorkflowState) -> dict:
    """The Critic node: Cross-checks generator output using a different model with strict JSON formatting."""
    target_model = MODEL_REGISTRY.get("CRITIC")
    
    print("\n" + "═"*60)
    print(f" 🔍 [NODE: CRITIC] Evaluating Draft (Round {state['iteration_count']}) ({target_model})")
    print("═"*60)
    
    llm = ChatOllama(model=target_model, temperature=0.0)
    structured_llm = llm.with_structured_output(DocEvaluationSchema)
    
    system_prompt = (
        f"You are an exceptionally harsh QA inspector evaluating API documentation. "
        f"Analyze the text objectively against the source code. "
        f"If there are any subtle formatting errors, descriptive contradictions, or parameter calculation inaccuracies, "
        f"tank the score aggressively. Set 'is_production_ready' to true ONLY if the overall_percentage is >= {QUALITY_SCORE_BAR}."
    )
    
    user_prompt = (
        f"Evaluate the following markdown documentation relative to its raw source code.\n\n"
        f"Raw Source Code:\n{state['source_code']}\n\n"
        f"Generated Markdown Document:\n{state['generated_markdown']}"
    )
    
    print(f" -> Querying local critic '{target_model}' with structured engine constraints...")
    evaluation: DocEvaluationSchema = structured_llm.invoke([
        SystemMessage(content=system_prompt), 
        HumanMessage(content=user_prompt)
    ])
    
    print("\n 📊 CRITIC SCORECARD SUMMARY:")
    print(f"    ├─ Technical Accuracy : {evaluation.technical_accuracy}/100")
    print(f"    ├─ Completeness       : {evaluation.completeness}/100")
    print(f"    ├─ Net Overall Score  : {evaluation.overall_percentage}/100 (Pass Bar: {QUALITY_SCORE_BAR})")
    print(f"    ├─ Ready for Prod?    : {'🟢 YES' if evaluation.is_production_ready else '🔴 NO'}")
    print(f"    └─ Stated Feedback    : \"{evaluation.single_critical_fix}\"")
    
    return {
        "current_score": evaluation.overall_percentage,
        "score_history": [evaluation.overall_percentage],
        "required_fix": evaluation.single_critical_fix,
        "is_approved": evaluation.is_production_ready
    }

def content_adjudicator_node(state: AgentWorkflowState) -> dict:
    """The Adjudicator node: Runs outside the loop to resolve structural contradictions and finalize text."""
    target_model = MODEL_REGISTRY["ADJUDICATOR"]
    
    print("\n" + "═"*60)
    print(f" ⚖️  [NODE: ADJUDICATOR] Reviewing Final Synthesis Output ({target_model})")
    print("═"*60)
    
    llm = ChatOllama(model=target_model, temperature=0.2)
    
    system_prompt = (
        "You are a senior technical documentation editor giving the final word on an API document "
        "that has been through multiple revision rounds. Your job is to read the raw source code, "
        "look at the latest draft, eliminate any conflicting statements, clean up semantic prose, and output the polished final markdown document. "
        "Do not include any preamble, comments, conversational pleasantries, or explanations—return ONLY the markdown documentation."
    )
    
    user_prompt = (
        f"Review and finalize this documentation template.\n\n"
        f"Raw Source Reference Code:\n{state['source_code']}\n\n"
        f"Latest Revision Draft:\n{state['generated_markdown']}\n\n"
        f"Last Remaining Critic Concern:\n\"{state['required_fix']}\""
    )
    
    print(f" -> Querying local judge '{target_model}' for final text harmonization...")
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    print(" ✅ Adjudication final review step complete.")
    
    return {"final_adjudicated_markdown": response.content}

# ---------------------------------------------------------------------------
# 4. Routing Logic and Graph Compilation
# ---------------------------------------------------------------------------

def execution_router(state: AgentWorkflowState) -> Literal["content_generator", "content_adjudicator"]:
    """Monitors workflow states and determines whether to repeat, loop, or step out to adjudication."""
    print("\n" + "🔀 [ROUTER] Assessing State Variables:")
    print(f"    ├─ Current Total Attempts : {state['iteration_count']}/{MAX_ATTEMPTS}")
    print(f"    └─ Quality History Log    : {state['score_history']}")
    
    if state["is_approved"]:
        print(f"\n 🎉 [LOOP EXIT] Document cleared quality standards. Passing to Adjudicator for final polish.")
        return "content_adjudicator"
        
    if state["iteration_count"] >= MAX_ATTEMPTS:
        print(f"\n ⚠️  [LOOP EXIT] Hard iteration cap of {MAX_ATTEMPTS} runs reached. Transferring control to Adjudicator.")
        return "content_adjudicator"
        
    print(f" 🔁 [DECISION] Score ({state['current_score']}) below target ({QUALITY_SCORE_BAR}). Routing back to Generator.")
    return "content_generator"


builder = StateGraph(AgentWorkflowState)

builder.add_node("content_generator", content_generator_node)
builder.add_node("content_critic", content_critic_node)
builder.add_node("content_adjudicator", content_adjudicator_node)

builder.set_entry_point("content_generator")
builder.add_edge("content_generator", "content_critic")

builder.add_conditional_edges(
    "content_critic",
    execution_router,
    {
        "content_generator": "content_generator",
        "content_adjudicator": "content_adjudicator"
    }
)

builder.add_edge("content_adjudicator", END)
agent_pipeline = builder.compile()

# ---------------------------------------------------------------------------
# 5. Runtime Execution Loop Engine
# ---------------------------------------------------------------------------
def run():
    global MODEL_REGISTRY, QUALITY_SCORE_BAR, MAX_ATTEMPTS

    # Define base structural path environments
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Setup native CLI argument parsers
    parser = argparse.ArgumentParser(description="Cyclic Self-Correcting LLM Documentation Pipeline")
    parser.add_argument(
        "-i", "--input", 
        default=os.path.join(base_dir, "input", "source_function.py"),
        help="Path to the source python file to generate documentation for."
    )
    parser.add_argument(
        "-o", "--output", 
        default=os.path.join(base_dir, "output", "optimized_documentation.md"),
        help="Path where the output markdown file will be saved."
    )
    parser.add_argument(
        "-c", "--config",
        default=os.path.join(base_dir, "config.json"),
        help="Path to the configuration JSON setting parameters."
    )
    args = parser.parse_args()

    # ─── CONFIGURATION LOADER STEP ───
    print(f"⚙️  [CONFIG] Loading pipeline parameters from: '{args.config}'")
    if os.path.exists(args.config):
        try:
            with open(args.config, "r", encoding="utf-8") as config_file:
                config_data = json.load(config_file)
                MODEL_REGISTRY = config_data.get("model_registry", {})
                QUALITY_SCORE_BAR = config_data.get("quality_score_bar", 95)
                MAX_ATTEMPTS = config_data.get("max_attempts", 4)
                print(" -> Success: Configuration metrics synchronized successfully.")
        except Exception as e:
            print(f" -> Error reading config file ({str(e)}). Deploying runtime fallbacks...")
    else:
        print(" -> Warning: Configuration file not detected. Instantiating default fallbacks...")
        MODEL_REGISTRY = {"GENERATOR": "qwen3.5:9b", "CRITIC": "deepseek-coder:6.7b", "ADJUDICATOR": "llama3:8b"}
        QUALITY_SCORE_BAR = 95
        MAX_ATTEMPTS = 4

    # ─── FILE READER STEP ───
    print(f"📁 [FILE READER] Sourcing text strings from: '{args.input}'")
    if os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as file_stream:
            raw_input_code = file_stream.read()
    else:
        print(" -> Warning: Specified input file missing. Creating dynamic example fallback placeholder...")
        raw_input_code = "def sample_function():\n    return 'Hello World'"
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        with open(args.input, "w", encoding="utf-8") as fallback_stream:
            fallback_stream.write(raw_input_code)

    initial_state: AgentWorkflowState = {
        "source_code": raw_input_code,
        "generated_markdown": "",
        "current_score": 0,
        "score_history": [],
        "required_fix": None,
        "iteration_count": 0,
        "is_approved": False,
        "final_adjudicated_markdown": ""
    }
    
    print("="*60)
    print("🚀 Initiating HETEROGENEOUS Local Agent Loop Framework via Ollama")
    print(f"    ├─ 🛠️  Generator   : {MODEL_REGISTRY.get('GENERATOR')}")
    print(f"    ├─ 🔍 Critic      : {MODEL_REGISTRY.get('CRITIC')}")
    print(f"    └─ ⚖️  Adjudicator : {MODEL_REGISTRY.get('ADJUDICATOR')}")
    print("="*60)
    
    final_output = agent_pipeline.invoke(initial_state)
    
    print("\n" + "═"*60)
    print(" 🔥 FINAL PIPELINE RUN SUMMARY")
    print("═"*60)
    print(f" 📈 Score Curve Trace History   : {final_output['score_history']}")
    print(f" 🔢 Total Loop Turns Evaluated : {final_output['iteration_count']}")
    
    # --- POST-PROCESSING: Clean conversational preamble and postscript text ---
    raw_final_text = final_output.get("final_adjudicated_markdown", "")
    clean_final_markdown = raw_final_text
    
    # 1. Clean Preamble (Conversational text at the top)
    if "#" in raw_final_text:
        parts = raw_final_text.split("#", 1)
        if len(parts[0].strip()) > 0 and len(parts[0].strip()) < 200:
            print("🪓 [CLEANER] Removing conversational introductory preamble from final markdown artifact...")
            clean_final_markdown = "#" + parts[1]
            
    # 2. Clean Postscript (Conversational text at the bottom)
    # Check if the model left an conversational 'Note:' or sign-off paragraph at the very end
    lines = clean_final_markdown.rstrip().split("\n")
    if lines:
        last_line = lines[-1].strip()
        # Common local LLM signature postscript patterns
        if last_line.startswith(("Note:", "Note that", "I hope", "This concludes")):
            print("🪓 [CLEANER] Chopping off conversational chatty postscript from final markdown artifact...")
            # Rebuild the file omitting the final conversational lines
            clean_final_markdown = "\n".join(lines[:-1]).rstrip() + "\n"
            
    print("\n" + "💾 [FILE EXPORTER] Verifying Output Paths...")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(clean_final_markdown)
        print(f" 📝 [SUCCESS] Polished documentation saved successfully to: '{args.output}'")
    except Exception as e:
        print(f" ❌ [ERROR] Failed writing to disk: {str(e)}")

if __name__ == "__main__":
    run()