# Local Reflexion Agent

A fully local self-correcting agent loop for generating API documentation from source code. It uses [LangGraph](https://github.com/langchain-ai/langgraph) to orchestrate a Generator → Critic → Adjudicator cycle, with each role served by a different local model via [Ollama](https://ollama.com/).

## How it works

1. **Generator** drafts (or revises) Markdown documentation for a given source file.
2. **Critic** scores the draft against the source code using a structured JSON rubric (technical accuracy, completeness, overall score) and returns the single highest-priority fix.
3. **Router** sends the draft back to the Generator if the score is below the quality bar and attempts remain, otherwise hands off to the Adjudicator.
4. **Adjudicator** performs a final pass to resolve contradictions and polish the text before it's written to disk.

Using separate models for generation and critique avoids a single model rubber-stamping its own output.

## Requirements

- Python >= 3.12
- [Ollama](https://ollama.com/) running locally with the models referenced in `config.json` pulled (defaults: `qwen3.5:9b`, `deepseek-coder:6.7b`, `llama3:8b`)

## Installation

```bash
pip install -e .
```

## Usage

```bash
reflexion --input input/source_function_a.py --output output/result.md --config config.json
```

| Flag | Default | Description |
| --- | --- | --- |
| `-i`, `--input` | `input/source_function.py` | Path to the source Python file to document |
| `-o`, `--output` | `output/optimized_documentation.md` | Path to write the final Markdown documentation |
| `-c`, `--config` | `config.json` | Path to the pipeline configuration file |

## Configuration

`config.json` controls the model roles and loop behavior:

```json
{
  "model_registry": {
    "GENERATOR": "qwen3.5:9b",
    "CRITIC": "deepseek-coder:6.7b",
    "ADJUDICATOR": "llama3:8b"
  },
  "quality_score_bar": 95,
  "max_attempts": 4
}
```

- `model_registry` — Ollama model names for each pipeline role.
- `quality_score_bar` — minimum critic score (0-100) required to exit the revision loop.
- `max_attempts` — hard cap on Generator/Critic iterations before forcing adjudication.

## Project layout

```
src/reflexion/main.py   # LangGraph pipeline: nodes, routing, CLI entry point
input/                  # Sample source files used as documentation targets
output/                 # Generated Markdown documentation
config.json             # Model registry and quality-loop settings
```

## License

MIT — see [LICENSE](LICENSE) for details.
