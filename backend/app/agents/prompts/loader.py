"""Safe loader for versioned prompt text stored inside the repository."""

from pathlib import Path


PROMPT_ROOT = Path(__file__).resolve().parent


def load_recruitment_prompt(name: str) -> str:
    if name not in {"strategy", "hr_report", "resume_import"}:
        raise ValueError("不支持的招聘 Prompt。")
    return (PROMPT_ROOT / "recruitment" / f"{name}.md").read_text(encoding="utf-8")
