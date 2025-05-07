import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance
import uuid

st.set_page_config(page_title="Stillr Interactieve Panelen", layout="wide")

st.title("Stillr - Interactieve Akoestische Panelen")

PANEL_TYPES = {
    "M (47x95 cm)": (47, 95),
    "L (95x95 cm)": (95, 95),
    "XL (95x190 cm)": (95, 190),
    "Moon (Ø95 cm)": (95, 95)
}

TEXTURES = {
    "TOUCH Grijs": "stof_grijs.jpg",
    "Blazer Lite Courtesy": "stof_courtesy.jpg",
    "Blazer Lite Retreat": "stof_retreat.jpg"
}

st.markdown("### 1. Upload een foto van je ruimte")
uploaded_image = st.file_uploader("Upload muur- of plafondfoto", type=["jpg", "jpeg", "png"])

if uploaded_image:
    bg_image = Image.open(uploaded_image).convert("RGB")
    st.image(bg_image, caption="Originele afbeelding", use_column_width=True)

    if "panel_list" not in st.session_state:
        st.session_state.panel_list = []

    cols = st.columns([2, 2, 1, 1])
    with cols[0]:
        p_type = st.selectbox("Paneeltype", list(PANEL_TYPES.keys()))
    with cols[1]:
        p_texture = st.selectbox("Stofkleur", list(TEXTURES.keys()))
    with cols[2]:
        if st.button("➕ Voeg paneel toe"):
            new_panel = {
                "id": str(uuid.uuid4()),
                "type": p_type,
                "texture": p_texture,
                "x": 50,
                "y": 50,
                "rotated": False
            }
            st.session_state.panel_list.append(new_panel)
    with cols[3]:
        if st.button("🗑️ Reset alles"):
            st.session_state.panel_list = []

    st.markdown("### 3. Posities aanpassen & visualiseren")
    for panel in st.session_state.panel_list:
        with st.expander(f"Paneel: {panel['type']} - {panel['texture']}"):
            panel["x"] = st.slider(f"X-positie {panel['id']}", 0, 100, panel["x"])
            panel["y"] = st.slider(f"Y-positie {panel['id']}", 0, 100, panel["y"])
            panel["rotated"] = st.checkbox(f"Roteren 90° {panel['id']}", value=panel["rotated"])
            if st.button(f"Verwijder paneel {panel['id']}"):
                st.session_state.panel_list = [p for p in st.session_state.panel_list if p["id"] != panel["id"]]
                st.experimental_rerun()

    preview = bg_image.copy()
    img_w, img_h = preview.size

    for panel in st.session_state.panel_list:
        w_cm, h_cm = PANEL_TYPES[panel["type"]]
        px_per_cm = img_w / 400
        w_px = int(w_cm * px_per_cm)
        h_px = int(h_cm * px_per_cm)

        tex = Image.open(TEXTURES[panel["texture"]]).resize((w_px, h_px))

        if panel["rotated"]:
            tex = tex.rotate(90, expand=True)
            w_px, h_px = tex.size

        pos_x = int((panel["x"] / 100) * (img_w - w_px))
        pos_y = int((panel["y"] / 100) * (img_h - h_px))

        shadow = Image.new("RGBA", tex.size, (0, 0, 0, 80))
        preview_rgba = preview.convert("RGBA")
        preview_rgba.paste(shadow, (pos_x+10, pos_y+10), shadow)
        preview_rgba.paste(tex, (pos_x, pos_y))
        preview = preview_rgba.convert("RGB")

    st.image(preview, caption="Visualisatie", use_column_width=True)
    preview.save("stillr_visual_result.jpg")
    with open("stillr_visual_result.jpg", "rb") as file:
        st.download_button("📅 Download visualisatie", file, file_name="stillr_visualisatie.jpg", mime="image/jpeg")
