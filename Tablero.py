import streamlit as st
from streamlit_drawable_canvas import st_canvas
import base64
import numpy as np
from PIL import Image
import openai

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.set_page_config(page_title="Tablero Inteligente", layout="centered")
st.title("🖌️ Tablero Inteligente")

st.markdown("Dibuja algo y deja que la IA lo interprete.")

# -----------------------------
# CONTROLES
# -----------------------------
stroke_width = st.slider("Grosor del pincel", 1, 25, 5)
stroke_color = st.color_picker("Color del pincel", "#000000")
bg_color = st.color_picker("Color de fondo", "#FFFFFF")

drawing_mode = st.selectbox(
    "Modo de dibujo",
    ("freedraw", "line", "rect", "circle")
)

# -----------------------------
# CANVAS
# -----------------------------
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=400,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# -----------------------------
# API KEY
# -----------------------------
api_key = st.text_input("Ingresa tu OpenAI API Key", type="password")

if api_key:
    openai.api_key = api_key

# -----------------------------
# FUNCIÓN BASE64
# -----------------------------
def encode_image(image):
    buffered = Image.fromarray(image.astype("uint8"))
    buffered.save("temp.png")
    with open("temp.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

# -----------------------------
# BOTÓN ANALIZAR
# -----------------------------
if st.button("🔍 Analizar dibujo"):

    if canvas_result.image_data is None:
        st.warning("Primero dibuja algo.")
    elif not api_key:
        st.warning("Ingresa tu API key.")
    else:
        with st.spinner("Analizando dibujo..."):

            # Convertir imagen
            img_array = np.array(canvas_result.image_data)
            base64_image = encode_image(img_array)

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe brevemente en español lo que ves en este dibujo"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=300,
                )

                result = response.choices[0].message.content
                st.subheader("🧠 Interpretación:")
                st.write(result)

            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------
# LIMPIAR CANVAS
# -----------------------------
if st.button("🧹 Limpiar"):
    st.session_state["canvas"] = None
    st.rerun()
