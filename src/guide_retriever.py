"""Retrieve activity guidance from the project's custom document."""

from pathlib import Path


GUIDE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "curation_guides.md"
)


def retrieve_guide(activity: str) -> dict:
    """Return an activity's guide text and source reference."""
    requested_section = activity.strip().casefold()

    if not requested_section:
        raise ValueError("Enter an activity to retrieve its guide.")

    try:
        document = GUIDE_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(
            "Could not read data/curation_guides.md."
        ) from error

    for section in document.split("\n## ")[1:]:
        heading, _, body = section.partition("\n")

        if heading.strip().casefold() == requested_section:
            content = body.strip()
            if not content:
                raise ValueError(
                    f"The guide for '{activity}' is empty."
                )

            return {
                "activity": heading.strip(),
                "content": content,
                "source": (
                    f"data/curation_guides.md"
                    f"#{heading.strip().lower().replace(' ', '-')}"
                ),
            }

    raise ValueError(f"No guide found for activity '{activity}'.")