import streamlit.components.v1 as components
import os

# Determina o caminho para a pasta 'build'
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "build")

# Declara o componente
_responsive_component = components.declare_component(
    "responsive_component",
    path=build_dir
)

def responsive_component():
    """Retorna a largura da janela do navegador."""
    return _responsive_component()