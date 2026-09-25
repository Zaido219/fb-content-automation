# fb-content-automation

I built this because I wanted a lightweight way to turn a single content idea into a Facebook-ready image prompt and post flow without doing everything by hand.

This project is a personal automation tool for the Batang90 concept: a nostalgic 90s Filipino slice-of-life vibe mixing classic anime and cartoon characters with authentic Philippine settings. At the moment, it is more of a small experimental pipeline than a polished app. It is meant to help me generate images, review them, and post them to a Facebook Page with less manual work.

## What it does

The main piece is `PromptBuilder`. It takes a user prompt and the brand config in `config/brand_rules.json`, then builds a more structured image-generation prompt with:

- brand tone and voice
- Philippine setting details
- character-specific visual references
- forbidden elements and negative constraints
- layout settings for a retro-style Facebook-friendly image

It also builds a negative prompt from a few sources: default negatives, blocked content rules, and any rejection notes added during the review loop. The idea is to keep the output consistent with the Batang90 theme and avoid things that break the mood, like modern cityscapes, contemporary fashion, or random visual clutter.

## How it roughly works

The flow is simple:

1. A user enters a content idea in the Streamlit UI.
2. `PromptBuilder.orchestrate()` loads the JSON config and assembles a positive prompt.
3. It injects relevant thematic pillars, like street food, local neighborhood life, jeepneys, and 90s childhood games, when they match the request.
4. It also checks for known characters in the query and adds design notes so the character stays recognizable.
5. The prompt and negative prompt are passed to `ImagenClientWrapper`, which calls the Google AI image generation API.
6. The generated image is saved locally and can be reviewed in the UI.
7. If the result is rejected, the user can add feedback as a negative prompt and regenerate.
8. If approved, the image can be published to Facebook through the Graph API.

This is a config-driven prompt builder at the center of it, with the rest of the app being a thin wrapper around generation, review, and posting.

## Project structure

```text
fb-content-automation/
├── config/
│   ├── brand_rules.json
│   ├── default_negatives.json
│   └── layout_specs.json
├── src/
│   ├── app.py
│   ├── builders/
│   │   └── prompt_builder.py
│   ├── exceptions/
│   │   └── exceptions.py
│   ├── interface/
│   │   └── interface.py
│   ├── models/
│   │   └── DTO.py
│   ├── services/
│   │   ├── facebook_service.py
│   │   ├── imagen_service.py
│   │   └── storage_service.py
│   └── ...
├── storage/
│   ├── approved/
│   ├── test_images/
│   └── transient/
├── ui/
│   └── app_streamlit.py
├── requirements.txt
├── pyproject.toml
├── notes.txt
└── README.md
```

The main files to look at are:

- `src/builders/prompt_builder.py` for the prompt assembly logic
- `config/brand_rules.json` for the brand/theme rules
- `config/default_negatives.json` for default blocking terms
- `config/layout_specs.json` for aspect ratio and layout specs
- `src/services/imagen_service.py` for the image generation call
- `src/services/facebook_service.py` for posting to Facebook
- `ui/app_streamlit.py` for the local review workflow

## Setup and installation

I usually work in a virtual environment.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

You also need environment values in a `.env` file at the project root:

```env
GEMINI_API_KEY=your_api_key
FB_ACCESS_TOKEN=your_facebook_page_token
FB_PAGE_ID=your_facebook_page_id
```

Then run the app:

```bash
streamlit run ui/app_streamlit.py
```

That starts the local UI where I can type a concept, generate an image, reject or approve it, and publish it to Facebook if it looks right.

## Current state and known limitations

This is still a personal work in progress. The overall idea is working, but there are a few rough edges:

- the repo is built around my own content style and use cases, not a general-purpose platform
- config files are the real source of the brand logic, so the tool is only as good as those JSON rules
- the prompt flow is fairly opinionated and not fully generalized
- there is some manual setup around credentials and API access
- the Facebook and image generation pieces are functional enough for a personal workflow, but not hardened for production use
- there are a few things that look unfinished or slightly hacky in the code, especially around assumptions about image payloads and default layout handling

So yes, this is useful for my own workflow, but I would not describe it as a polished app or a product that is ready for public use.

## What I might add later

I might clean this up more if I keep using it. The main things I’d want are a clearer review flow, a better way to save and recall prompt history, more structured config editing, and a few improvements around validation and error handling.

For now, though, this is just a practical little project for generating nostalgic Filipino content in a repeatable way, and that is the main thing it does.
