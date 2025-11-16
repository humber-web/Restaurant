"""
QR Code Service for e-Fatura CV

Generates QR Codes for invoices containing IUD (Identificador Único do Documento)
According to e-Fatura CV specifications
"""
import qrcode
import io
import base64
from typing import Optional


class QRCodeService:
    """
    Service to generate QR Codes for e-Fatura CV invoices.
    
    QR Code Content:
    - IUD (Identificador Único do Documento) - 45 characters
    - Format: base64 encoded PNG image
    """
    
    @staticmethod
    def generate_qr_code(iud: str, include_prefix: bool = True) -> str:
        """
        Generate QR Code for invoice IUD.
        
        Args:
            iud: Invoice Unique Identifier (45 characters)
            include_prefix: Include "IUD:" prefix in QR content
            
        Returns:
            str: Base64 encoded PNG image (data URL format)
        """
        if not iud:
            raise ValueError("IUD is required to generate QR Code")
        
        # QR Code content
        if include_prefix:
            qr_content = f"IUD:{iud}"
        else:
            qr_content = iud
        
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,  # Size (1-40, auto-adjusts if needed)
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction
            box_size=10,  # Size of each box in pixels
            border=4,  # Border size in boxes
        )
        
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encode as base64 data URL
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_url = f"data:image/png;base64,{img_base64}"
        
        return data_url
    
    @staticmethod
    def generate_qr_code_for_payment(payment) -> Optional[str]:
        """
        Generate QR Code for a Payment/Invoice.
        
        Args:
            payment: Payment object with IUD
            
        Returns:
            str: Base64 encoded PNG image (data URL), or None if no IUD
        """
        if not payment.iud:
            return None
        
        return QRCodeService.generate_qr_code(payment.iud, include_prefix=True)
    
    @staticmethod
    def generate_qr_code_bytes(iud: str) -> bytes:
        """
        Generate QR Code as raw PNG bytes (for file download).
        
        Args:
            iud: Invoice Unique Identifier
            
        Returns:
            bytes: PNG image data
        """
        if not iud:
            raise ValueError("IUD is required to generate QR Code")
        
        qr_content = f"IUD:{iud}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return buffer.getvalue()
