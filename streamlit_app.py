"""Streamlit interface for Playlist Intelligence."""

import csv
import io
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from google.genai import errors

from src.curator import rank_request
from src.guide_retriever import retrieve_guide
from src.llm_client import generate_explanations
from src.recommender import load_songs
from src.study_curator import rank_study_request


PROJECT_ROOT = Path(__file__).resolve().parent

BACKGROUND_SVG = """
<svg xmlns="http://www.w3.org/2000/svg"
     width="1600" height="1000" viewBox="0 0 1600 1000">
  <defs>
    <linearGradient id="background" x2="1" y2="1">
      <stop stop-color="#071321"/>
      <stop offset=".55" stop-color="#10172f"/>
      <stop offset="1" stop-color="#071521"/>
    </linearGradient>
    <radialGradient id="teal">
      <stop stop-color="#0d9488" stop-opacity=".35"/>
      <stop offset="1" stop-color="#0d9488" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="violet">
      <stop stop-color="#7c3aed" stop-opacity=".30"/>
      <stop offset="1" stop-color="#7c3aed" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="wave">
      <stop stop-color="#2dd4bf"/>
      <stop offset="1" stop-color="#8b5cf6"/>
    </linearGradient>
  </defs>

  <rect width="1600" height="1000" fill="url(#background)"/>
  <ellipse cx="100" cy="160" rx="650" ry="520" fill="url(#teal)"/>
  <ellipse cx="1500" cy="220" rx="650" ry="550" fill="url(#violet)"/>

  <g fill="none" stroke="url(#wave)" stroke-width="2" opacity=".23">
    <path d="M-100 720 C200 400 400 1050 800 770 S1300 500 1750 760"/>
    <path d="M-100 740 C200 420 400 1070 800 790 S1300 520 1750 780"/>
    <path d="M-100 760 C200 440 400 1090 800 810 S1300 540 1750 800"/>
    <path d="M-100 780 C200 460 400 1110 800 830 S1300 560 1750 820"/>
    <path d="M-100 800 C200 480 400 1130 800 850 S1300 580 1750 840"/>
    <path d="M950 0 C1150 240 1300 -80 1650 180"/>
    <path d="M950 20 C1150 260 1300 -60 1650 200"/>
    <path d="M950 40 C1150 280 1300 -40 1650 220"/>
  </g>

  <g transform="translate(1290 650) rotate(-15)"
     fill="none" stroke="url(#wave)" opacity=".22">
    <path d="M-115 100 V-15 A115 115 0 0 1 115 -15 V100"
          stroke-width="22"/>
    <rect x="-140" y="25" width="55" height="115" rx="23"
          fill="#0f2439" stroke-width="4"/>
    <rect x="85" y="25" width="55" height="115" rx="23"
          fill="#17213c" stroke-width="4"/>
  </g>

  <g fill="#5eead4" opacity=".25">
    <circle cx="85" cy="430" r="3"/>
    <circle cx="1450" cy="340" r="4"/>
    <circle cx="1520" cy="520" r="2"/>
    <circle cx="210" cy="900" r="3"/>
  </g>
</svg>
"""


def apply_styles():
    """Apply the embedded image background and interface styling."""
    background_url = "data:image/svg+xml;charset=utf-8," + quote(
        BACKGROUND_SVG, safe=""
    )

    stylesheet = """
    <style>
    .stApp {
        background-color: #081321;
        background-image: url("BACKGROUND_URL");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #f1f5f9;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    h1 {
        color: #f8fafc;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    h2, h3 {
        color: #e2e8f0;
        letter-spacing: -0.02em;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"] p {
        color: #e2e8f0;
    }

    [data-testid="stCaptionContainer"] p {
        color: #aec0d6;
    }

    [data-testid="stForm"],
    .st-key-playlist_results,
    .st-key-approval_panel {
        padding: 1.4rem;
        background: rgba(12, 25, 44, 0.93);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 20px;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.18);
    }

    [class*="st-key-track_card_"] {
        background: rgba(22, 39, 61, 0.92);
        border-radius: 15px;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] input {
        background-color: #17283e;
        color: #f1f5f9;
    }

    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(110deg, #0f766e, #0e7490);
        border: 1px solid #2dd4bf;
        border-radius: 11px;
        min-height: 2.8rem;
        padding: 0.5rem 1.4rem;
    }

    [data-testid="stFormSubmitButton"] button p {
        color: white;
        font-weight: 700;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        border-color: #99f6e4;
        background: #115e59;
    }

    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button {
        background: #172c44;
        border: 1px solid #526d8a;
        border-radius: 10px;
        min-height: 2.6rem;
    }

    [data-testid="stButton"] button p,
    [data-testid="stDownloadButton"] button p {
        color: #f1f5f9;
    }

    [data-testid="stButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover {
        border-color: #5eead4;
    }

    [data-testid="stMetric"] {
        background: rgba(20, 184, 166, 0.09);
        border: 1px solid rgba(94, 234, 212, 0.12);
        padding: 0.9rem;
        border-radius: 13px;
    }

    [data-testid="stMetricValue"] {
        color: #5eead4;
    }

    [data-testid="stMetricLabel"] p {
        color: #cbd5e1;
    }

    button:focus-visible,
    input:focus-visible {
        outline: 2px solid #5eead4;
        outline-offset: 3px;
    }

    hr {
        border-color: rgba(148, 163, 184, 0.20);
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1.5rem 1rem;
        }

        [data-testid="stForm"],
        .st-key-playlist_results,
        .st-key-approval_panel {
            padding: 1rem;
        }
    }
    </style>
    """

    st.markdown(
        stylesheet.replace("BACKGROUND_URL", background_url),
        unsafe_allow_html=True,
    )


def finish_playlist(settings, recommendations, *, approved=False):
    """Generate optional explanations and save the completed playlist."""
    mode = "Catalog explanations"
    warning = ""
    results = recommendations

    if settings["use_ai"] and recommendations:
        generation_request = settings["request"]

        if approved:
            generation_request += (
                "\nThe listener explicitly approved other genres while "
                "keeping the studying energy and mood rules. Identify "
                "tracks outside the requested genre as approved alternatives."
            )

        try:
            with st.spinner("Writing explanations for your playlist..."):
                results = generate_explanations(
                    generation_request,
                    recommendations,
                    retrieve_guide(settings["activity"]),
                    specialized=settings["specialized"],
                )

            mode = (
                "Gemini · Specialized"
                if settings["specialized"]
                else "Gemini · Baseline"
            )
        except (ValueError, errors.APIError):
            warning = (
                "AI explanations are unavailable. "
                "Your playlist uses catalog-based explanations."
            )
            mode = "Catalog fallback"

    st.session_state["playlist_result"] = {
        "settings": settings,
        "recommendations": results,
        "approved": approved,
        "mode": mode,
        "warning": warning,
    }
    st.session_state["pending_playlist"] = None


def playlist_csv(result):
    """Export displayed recommendations and their evidence as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "rank",
            "id",
            "title",
            "artist",
            "genre",
            "mood",
            "energy",
            "score",
            "explanation_mode",
            "explanation",
        ]
    )

    for rank, (song, score, explanation) in enumerate(
        result["recommendations"], start=1
    ):
        writer.writerow(
            [
                rank,
                song["id"],
                song["title"],
                song["artist"],
                song["genre"],
                song["mood"],
                song["energy"],
                f"{score:.2f}",
                result["mode"],
                explanation,
            ]
        )

    return output.getvalue().encode("utf-8-sig")


def main():
    """Display preferences, approval controls, and playlist results."""
    st.set_page_config(
        page_title="Playlist Intelligence",
        page_icon="🎧",
        layout="wide",
    )
    apply_styles()

    st.title("🎧 Playlist Intelligence")
    st.write("Find your next playlist. Understand every recommendation.")
    st.caption("Built around your activity, with evidence for every pick.")

    try:
        songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Could not load the song catalog: {error}")
        st.stop()

    if not songs:
        st.error("The song catalog is empty.")
        st.stop()

    genres = sorted({song["genre"] for song in songs})
    default_genre = genres.index("jazz") if "jazz" in genres else 0

    st.session_state.setdefault("pending_playlist", None)
    st.session_state.setdefault("playlist_result", None)

    with st.sidebar:
        st.subheader("Your music companion")
        st.write(
            "Choose an activity, request a playlist, and explore "
            "why each track fits."
        )
        st.metric("Catalog tracks", len(songs))
        st.metric("Available genres", len(genres))
        st.caption(
            "AI explanations use the Gemini configuration "
            "from the terminal that launched this app."
        )

        if st.button("Clear results", key="clear_results"):
            st.session_state["pending_playlist"] = None
            st.session_state["playlist_result"] = None
            st.rerun()

    with st.form("playlist_preferences"):
        st.subheader("Build your playlist")

        activity_column, count_column, genre_column = st.columns(3)

        with activity_column:
            activity = st.selectbox(
                "Activity",
                ["Workout", "Studying"],
                key="activity_choice",
            )

        with count_column:
            count = st.number_input(
                "Number of songs",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
                key="song_count",
            )

        with genre_column:
            genre = st.selectbox(
                "Genre for studying",
                genres,
                index=default_genre,
                key="genre_choice",
            )

        st.caption(
            "Workout searches all genres. "
            "Studying starts with your selected genre."
        )

        use_ai = st.checkbox(
            "Generate AI explanations",
            value=False,
            key="use_ai",
        )
        specialized = st.checkbox(
            "Use concise curator style with AI",
            value=True,
            key="specialized_style",
        )
        st.caption(
            "Concise curator style applies when AI explanations are enabled."
        )

        submitted = st.form_submit_button("Recommend songs")

    if submitted:
        st.session_state["pending_playlist"] = None
        st.session_state["playlist_result"] = None

        activity_name = activity.casefold()
        request = (
            f"{count} upbeat songs for a workout"
            if activity_name == "workout"
            else f"{count} calm {genre} songs for studying"
        )

        settings = {
            "request": request,
            "activity": activity_name,
            "count": int(count),
            "genre": genre,
            "use_ai": use_ai,
            "specialized": specialized,
        }

        try:
            recommendations = rank_request(request, songs)
        except ValueError as error:
            st.error(str(error))
        else:
            if activity_name == "studying" and len(recommendations) < count:
                st.session_state["pending_playlist"] = {
                    "settings": settings,
                    "recommendations": recommendations,
                    "songs": songs,
                }
            else:
                finish_playlist(settings, recommendations)

    pending = st.session_state["pending_playlist"]

    if pending is not None:
        settings = pending["settings"]
        st.divider()

        with st.container(key="approval_panel"):
            st.subheader("A quick choice")
            st.write(settings["request"])
            st.warning(
                f"Found {len(pending['recommendations'])} matching track(s) "
                f"out of {settings['count']} requested."
            )
            st.write(
                "Include other genres while keeping the studying "
                "mood and energy rules?"
            )

            approve_column, decline_column = st.columns(2)

            with approve_column:
                approve = st.button(
                    "Include other genres",
                    key="approve_genres",
                )

            with decline_column:
                decline = st.button(
                    "Keep my genre",
                    key="decline_genres",
                )

            if approve:
                try:
                    recommendations = rank_study_request(
                        settings["request"],
                        pending["songs"],
                        allow_other_genres=True,
                    )
                except ValueError as error:
                    st.error(str(error))
                else:
                    finish_playlist(
                        settings,
                        recommendations,
                        approved=True,
                    )
                    st.rerun()

            if decline:
                finish_playlist(settings, pending["recommendations"])
                st.rerun()

    result = st.session_state["playlist_result"]

    if result is not None:
        settings = result["settings"]
        recommendations = result["recommendations"]
        st.divider()

        with st.container(key="playlist_results"):
            st.subheader("Your playlist")
            st.write(settings["request"])
            st.caption(f"Explanation mode · {result['mode']}")

            if result["warning"]:
                st.warning(result["warning"])

            if result["approved"]:
                st.info(
                    "You approved other genres. "
                    "Studying mood and energy restrictions remain active."
                )

            if len(recommendations) < settings["count"]:
                st.info(
                    f"Showing {len(recommendations)} of "
                    f"{settings['count']} requested tracks."
                )

            if recommendations:
                track_column, artist_column, energy_column = st.columns(3)

                with track_column:
                    st.metric("Selected tracks", len(recommendations))

                with artist_column:
                    artist_count = len(
                        {
                            song["artist"].strip().casefold()
                            for song, _, _ in recommendations
                        }
                    )
                    st.metric("Distinct artists", artist_count)

                with energy_column:
                    average_energy = sum(
                        song["energy"]
                        for song, _, _ in recommendations
                    ) / len(recommendations)
                    st.metric("Average energy", f"{average_energy:.2f}")

                st.caption("Energy is measured on the catalog's 0–1 scale.")

                st.download_button(
                    "Download playlist CSV",
                    data=playlist_csv(result),
                    file_name="playlist_intelligence.csv",
                    mime="text/csv",
                    key="download_playlist",
                )
            else:
                st.warning("No tracks match the active preferences.")

            for rank, (song, score, explanation) in enumerate(
                recommendations, start=1
            ):
                with st.container(
                    border=True,
                    key=f"track_card_{rank}",
                ):
                    title_column, score_column = st.columns([4, 1])

                    with title_column:
                        st.subheader(f"{rank}. {song['title']}")
                        st.write(f"By {song['artist']}")
                        st.caption(
                            f"Genre · {song['genre']}  |  "
                            f"Mood · {song['mood']}  |  "
                            f"Energy · {song['energy']:.2f}"
                        )

                    with score_column:
                        st.metric("Relevance", f"{score:.2f}")

                    if (
                        result["approved"]
                        and song["genre"].strip().casefold()
                        != settings["genre"].strip().casefold()
                    ):
                        st.caption("Approved alternative genre")

                    st.write(explanation)

                    with st.expander("View catalog evidence"):
                        st.json(
                            {
                                "catalog_id": song["id"],
                                "genre": song["genre"],
                                "mood": song["mood"],
                                "energy": song["energy"],
                                "instrumentalness": song.get(
                                    "instrumentalness", 0.0
                                ),
                                "guide_source": (
                                    "data/curation_guides.md#"
                                    + settings["activity"]
                                ),
                            }
                        )

            with st.expander("How this playlist was created"):
                st.write(
                    "Python retrieves the activity guide, filters the "
                    "catalog, and ranks matching tracks. Gemini can "
                    "explain the selections using that evidence."
                )
                st.write(
                    "Studying searches retain the requested genre "
                    "unless you approve alternatives. Higher "
                    "instrumentalness breaks equal relevance scores "
                    "when requested by the guide."
                )
                st.write(
                    "Relevance scores describe catalog matches. "
                    "They are not probabilities of enjoyment."
                )

    st.divider()
    st.caption("Built by Haida Makouangou · CodePath AI110")


if __name__ == "__main__":
    main()