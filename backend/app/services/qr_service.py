"""
QR Code Generation Service.
Generates cryptographically scannable PNG and base64 Data-URIs for tickets and passes.
"""
import io
import base64
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask


class QRService:
    """Encapsulates high-contrast QR code rendering for transit tickets and passes."""

    @staticmethod
    def generate_qr_image_bytes(payload: str) -> bytes:
        """
        Generate PNG bytes for a given token string.
        Optimized for mobile screen brightness and optical scanner readability.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_qr_data_uri(payload: str) -> str:
        """
        Generate inline base64 data URI (data:image/png;base64,...) for direct HTML embedding.
        """
        png_bytes = QRService.generate_qr_image_bytes(payload)
        encoded = base64.b64encode(png_bytes).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
