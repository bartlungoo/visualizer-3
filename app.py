import streamlit as st
from PIL import Image
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Stillr Visualisatietool", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #f8f8f8;
        font-family: 'Garamond', 'Lato', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.image("stillr_logo.png", width=200)

st.title("Stillr Akoestisch Paneel Visualisatietool")

st.sidebar.header("Instellingen")

# Keuze tussen muur of plafond
oppervlak = st.sidebar.radio("Wat wil je visualiseren?", ["Muur", "Plafond"])

# Paneeltypes
paneeltypes = {
    "M": (60, 60),
    "L": (60, 120),
    "XL": (60, 180),
    "Extra-Large": (95, 190),
    "Moon": (95, 95),  # Cirkel, apart behandelen
}
paneel_keuze = st.sidebar.selectbox("Kies een paneeltype", list(paneeltypes.keys()))

# Oriëntatie
draai = st.sidebar.radio("Oriëntatie", ["Verticaal", "Horizontaal"])

# Alle stoffen inlezen uit map
stoffenpad = "blazer_lite_textures"
stoffen_lijst = sorted([
    f.replace("Blazer Lite-", "").replace(".jpg", "")
    for f in os.listdir(stoffenpad) if f.endswith(".jpg")
])

stof = st.sidebar.selectbox("Kies een stof", stoffen_lijst)

# Breedte muur (manuele invoer)
ken_breedte = st.sidebar.checkbox("Ik ken de breedte van mijn muur/plafond")
muur_breedte_cm = None
if ken_breedte:
    muur_breedte_cm = st.sidebar.number_input("Voer breedte in (cm)", min_value=50, max_value=1000, value=400)

st.write("Upload een foto van je", oppervlak.lower(), "om panelen te plaatsen.")

uploaded_file = st.file_uploader("Upload een foto", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    image.save("uploaded_image.jpg")  # tijdelijk lokaal opslaan
    img_width, img_height = image.size

    schaal = 1.0
    if ken_breedte:
        schaal = 900 / muur_breedte_cm

    st.success(f"Paneel: {paneel_keuze} ({paneeltypes[paneel_keuze][0]} x {paneeltypes[paneel_keuze][1]} cm), Oriëntatie: {draai}, Stof: {stof}")

    if "paneel_count" not in st.session_state:
        st.session_state.paneel_count = 3

    if st.button("➕ Voeg een paneel toe"):
        st.session_state.paneel_count += 1

    breedte_cm, hoogte_cm = paneeltypes[paneel_keuze]
    if draai == "Horizontaal":
        breedte_cm, hoogte_cm = hoogte_cm, breedte_cm

    breedte_px = int(breedte_cm * schaal)
    hoogte_px = int(hoogte_cm * schaal)

    panelen_html = "".join([
        f'<div class="paneel" draggable="true" id="paneel{i}" ondragstart="drag(event)" style="width:{breedte_px}px;height:{hoogte_px}px;background-image:url(\"{stoffenpad}/Blazer Lite-{stof}.jpg\");"></div>'
        for i in range(1, st.session_state.paneel_count + 1)
    ])

    rotatie_buttons = "".join([
        f'<button onclick="roteerPaneel(\"paneel{i}\")">Roteer paneel {i}</button>'
        for i in range(1, st.session_state.paneel_count + 1)
    ])

    verwijder_buttons = "".join([
        f'<button onclick="verwijderPaneel(\"paneel{i}\")">Verwijder paneel {i}</button>'
        for i in range(1, st.session_state.paneel_count + 1)
    ])

    components.html(
        f"""
        <html>
        <head>
            <style>
                #container {{
                    position: relative;
                    width: 100%;
                    max-width: 900px;
                }}
                #bg-img {{
                    width: 100%;
                }}
                .paneel {{
                    background-size: cover;
                    position: absolute;
                    top: 50px;
                    left: 50px;
                    cursor: move;
                    transform: rotate(0deg);
                }}
            </style>
        </head>
        <body style="background-color: #f8f8f8; font-family: Garamond, sans-serif;">
            <div id="container">
                <img id="bg-img" src="uploaded_image.jpg" />
                {panelen_html}
            </div>
            <br/>
            {rotatie_buttons}<br/><br/>
            {verwijder_buttons}

            <script>
                var dragged;
                document.addEventListener("dragstart", function(event) {{
                    dragged = event.target;
                    event.target.style.opacity = 0.5;
                }}, false);

                document.addEventListener("dragend", function(event) {{
                    event.target.style.opacity = "";
                }}, false);

                document.addEventListener("dragover", function(event) {{
                    event.preventDefault();
                }}, false);

                document.addEventListener("drop", function(event) {{
                    event.preventDefault();
                    if (event.target.id === "container" || event.target.id === "bg-img") {{
                        dragged.style.left = (event.clientX - 50) + "px";
                        dragged.style.top = (event.clientY - 50) + "px";
                    }}
                }}, false);

                function roteerPaneel(id) {{
                    let el = document.getElementById(id);
                    let current = el.style.transform.match(/rotate\((\d+)deg\)/);
                    let angle = current ? parseInt(current[1]) : 0;
                    angle = (angle + 90) % 360;
                    el.style.transform = `rotate(${angle}deg)`;
                }}

                function verwijderPaneel(id) {{
                    let el = document.getElementById(id);
                    if (el) el.remove();
                }}
            </script>
        </body>
        </html>
        """,
        height=850,
    )
else:
    st.info("Upload eerst een foto om te beginnen.")

