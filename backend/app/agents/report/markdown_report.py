from datetime import datetime


def build_markdown_report(title: str, user_query: str, sections: list[tuple[str, str]]) -> str:
    lines = [
        f"# {title}",
        "",
        f"_Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"**Request:** {user_query}",
        "",
    ]
    for heading, content in sections:
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)
