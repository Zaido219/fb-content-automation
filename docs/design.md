# Project Batang90: Creative & Visual Design Specification
## 90s Cartoon Slice-of-Life in the Philippines

This document outlines the visual identity, creative guidelines, and prompt engineering rules for generating retro 90s-style cartoon and anime images set in the everyday local context of the Philippines. It serves as the single source of truth for the artistic aesthetic and conceptual formulas.

---

## 1. Visual Identity & Aesthetic Guidelines

The core objective is to generate images that evoke deep nostalgia, making them look like authentic, lost screenshots from a 1990s television broadcast of an anime or cartoon episode set in the Philippines.

### 1.1 The 90s Cel Anime Aesthetic
To capture the feel of hand-painted cels and analog broadcasting:
*   **Color Palette**: Nostalgic, warm, slightly desaturated, or low-contrast tones. Soft, pastel hues for backgrounds; solid, hand-painted colors with simple cell shading for characters.
*   **Shadows & Highlights**: Soft, simple flat-shaded shadows (1-2 tones maximum). Avoid complex modern digital ambient occlusion, ray tracing, or soft gradients on characters.
*   **Texture & Grit**: Subtle VHS scanlines, soft analog film grain, chromatic aberration at the edges, and slight color bleeding. The image should feel like a vintage CRT television screencap or a scanned 90s artbook.
*   **Background Style**: Soft-focus, hand-drawn, watercolor-washed or poster-paint-styled environments. This creates a beautiful contrast with the sharper character outlines in the foreground.

### 1.2 Aesthetic Directives (Positive Prompt Modifiers)
Always include a selection of these key phrases to enforce the style:
> `"90s retro anime screencap, hand-drawn anime background, cel-shaded animation style, vintage vintage aesthetic, warm nostalgic color grading, soft analog film grain, VHS screen grab, retro television screenshot."`

### 1.3 What to Avoid (Negative Prompt Modifiers)
To prevent modern digital engine generation patterns:
*   **Avoid**: High-contrast digital painting, 3D CGI models, ray-traced shadows, hyper-realism, photorealism, glossy textures, neon glowing gradients, vector art, smooth airbrushed coloring.
*   **Exclude**: Watermarks, artist signatures, modern gadgets (like smartphones, unless explicitly stylized for anachronistic humor), and modern high-rise architecture.

---

## 2. Character Adaptation Rules (Localizing the Icons)

Characters should not feel like they were simply copy-pasted onto a Philippine background. They must interact with and inhabit the local environment naturally.

### 2.1 Styling & Costumes
Where appropriate, adapt the character's typical wear to match the local tropical climate and culture:
*   **Casual Wear**: Colorful *tsinelas* (rubber slippers), oversized local basketball jerseys, white cotton undershirts (*sando*), or simple folded-up shorts.
*   **Academic Settings**: Wearing standard white and blue/green Philippine public high school uniforms, carrying simple backpacks or brown envelopes.
*   **Interactive Props**: Holding plastic bags of soft drinks with a straw, eating street food with a thin bamboo skewer, or carrying local snacks.

### 2.2 Character Concept Templates

| Character | Local Adaptation & Vibe | Action / Interaction |
| :--- | :--- | :--- |
| **Sailor Moon (Usagi)** | Casual, wearing oversized t-shirt and slippers | Sheltering under a colorful shared umbrella next to a rain-slicked tricycle on a wet afternoon. |
| **Goku (Dragon Ball)** | Hungry, casual *sando* look | Eating *kwek-kwek* and fishballs directly from a steaming street-side food cart with a wooden stick. |
| **Eugene / Yusuke (Ghost Fighter)** | Classic green school uniform, rebellious look | Staring out of a window during a tropical power outage (*brownout*), lit by the warm glow of a melting candle. |
| **Ash & Pikachu (Pokémon)** | Retro cap, local neighborhood kid vibe | Waiting by a *sari-sari* store, Pikachu curiously looking at hanging sachets of shampoo. |
| **Hanamichi Sakuragi (Slam Dunk)** | Red hair, local barangay jersey | Shooting a worn basketball into a makeshift hoop nailed directly to a coconut tree on a dusty alley. |

---

## 3. Philippine Cultural Settings & Environmental Details

The background must feel lived-in and undeniably Filipino. The settings should focus on the mundane, relatable "slice-of-life" moments of the 1990s.

### 3.1 Iconic Environments
*   **The Sari-Sari Store**: A small wooden or concrete neighborhood convenience store.
    *   *Details*: Hanging wire racks containing small sachets of shampoo, powdered coffee, and local snacks. Large plastic jars of biscuits on the counter. A metal screen gate or wooden counter.
*   **The Barangay Alleyway (Kalyeng Barangay)**:
    *   *Details*: Overhanging tangled electric wires, concrete walls painted with local slogans or barangay notices, potted plants in recycled tin cans or plastic gallons, and stray sleeping dogs (*aso't pusa*).
*   **Public Transportation Vibe**:
    *   *Details*: A shiny metal jeepney decorated with hand-painted religious slogans, stickers, and tassels, or a highly decorated tricycle with a sidecar.
*   **The Backyard / Front Yard**:
    *   *Details*: Clotheslines with laundry hanging under the tropical sun, plastic stools (monobloc chairs), and children playing local street games (like *tumbang preso*, *piko*, or *pogs*).

### 3.2 Atmospheric Lighting & Weather Archetypes
*   **The Rainy Afternoon**: Soft, gray, humid lighting, puddles on cracked concrete streets, warm orange headlights from incoming tricycles reflecting on wet surfaces.
*   **The Golden Sunset (Hapong Maligaya)**: Warm, long orange and magenta shadows, light filtering through large mango or coconut tree leaves, dusty air glowing in the sunlight.
*   **The Tropical High Noon**: Sharp, intense sunlight, bright, high-contrast flat highlights, characters seeking shade under corrugated iron roofs (yero).
*   **The Cozy Brownout**: Dark, shadowy rooms illuminated exclusively by a single warm orange candle or a portable kerosene/gas lamp.

---

## 4. Prompt Construction Formula

To generate consistent and high-quality results, prompts should be structured using a modular template:

```
[Subject/Character + Outfit] + [Action/Interaction] + [Philippine Location/Setting] + [Key Props/Local Elements] + [Lighting & Weather] + [Art Style Directives]
```

### 4.1 Step-by-Step Prompt Breakdown (Example)

Let's dissect a prompt designed for Usagi (Sailor Moon):

1.  **Subject**: `Sailor Moon (Usagi Tsukino) with her classic twin-tail hairstyle, wearing a simple white sando and oversized colorful shorts`
2.  **Action**: `sitting on a low plastic stool and smiling`
3.  **Location**: `outside a nostalgic Philippine sari-sari store`
4.  **Props/Details**: `surrounded by hanging colorful sachets of coffee and snacks, concrete walls, a sleeping cat nearby`
5.  **Lighting**: `warm late afternoon sunlight filtering through tree leaves`
6.  **Style**: `90s retro anime screencap, hand-drawn anime background, cel-shaded, vintage aesthetic, soft VHS film grain, warm nostalgic color grading`

**Resulting Prompt:**
> *"Sailor Moon (Usagi Tsukino) with her classic twin-tail hairstyle, wearing a simple white sando and oversized colorful shorts, sitting on a low plastic stool and smiling outside a nostalgic Philippine sari-sari store. She is surrounded by hanging colorful sachets of coffee and snacks, concrete walls, and a sleeping cat nearby. Warm late afternoon sunlight filtering through tree leaves. 90s retro anime screencap, hand-drawn anime background, cel shading, vintage aesthetic, soft VHS film grain, warm nostalgic color grading."*
