import OpenGL.GL as gl
from PIL import Image

def load_texture(image_path: str) -> tuple[int, int, int]:
    """
    Loads an image file as an OpenGL texture.
    Returns:
        (texture_id, width, height) - texture_id is 0 if failed.
    """
    try:
        img = Image.open(image_path)
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img = img.convert("RGBA")
        width, height = img.size
        data = img.tobytes("raw", "RGBA", 0, -1)
        
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        
        # Set texture parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        
        # Upload data
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data
        )
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return int(texture_id), width, height
    except Exception as e:
        print(f"Failed to load texture from {image_path}: {e}")
        return 0, 0, 0
