"""
Level 4 Content Acquisition: PDF Extraction & OCR Fallback
Downloads recruitment circular PDFs safely to ephemeral temp storage, extracts page-by-page text,
detects scanned image-only PDFs, routes to Tesseract OCR when needed, and cleans up immediately.
"""
import os
import tempfile
import logging
from typing import Optional, Tuple
import httpx
from pypdf import PdfReader

from app.content.normalizer import NormalizedContent
from app.content.source_verifier import classify_source_domain
from config.settings import settings

logger = logging.getLogger(__name__)


class PdfExtractor:
    def __init__(self, max_size_mb: int = settings.MAX_PDF_SIZE_MB):
        self.max_size_bytes = max_size_mb * 1024 * 1024

    async def extract_from_url(self, pdf_url: str) -> Optional[NormalizedContent]:
        """
        Downloads PDF, extracts text, applies OCR fallback if scanned, and cleans up.
        """
        if not pdf_url:
            return None

        temp_path = None
        try:
            # Download safely with size limit
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_path = temp_file.name

            async with httpx.AsyncClient(
                timeout=35,
                follow_redirects=True,
                verify=False
            ) as client:
                async with client.stream("GET", pdf_url) as response:
                    if response.status_code != 200:
                        logger.warning(f"Failed to download PDF {pdf_url} (HTTP {response.status_code})")
                        temp_file.close()
                        return None

                    downloaded = 0
                    async for chunk in response.aiter_bytes():
                        downloaded += len(chunk)
                        if downloaded > self.max_size_bytes:
                            logger.warning(f"PDF exceeded size limit ({self.max_size_bytes} bytes): {pdf_url}")
                            temp_file.close()
                            return None
                        temp_file.write(chunk)

            temp_file.close()

            # Extract text from local temp PDF
            text, method = self._extract_text_and_ocr(temp_path)

            if not text or len(text.strip()) < 50:
                logger.warning(f"Extracted PDF text is insufficient for {pdf_url}")
                return None

            source_type, verif_status, conf = classify_source_domain(pdf_url)

            return NormalizedContent(
                source_url=pdf_url,
                canonical_url=pdf_url,
                source_type=source_type,
                title=f"Notification PDF: {os.path.basename(pdf_url)}",
                organization=None,
                content_text=text[:40000],  # Keep within reasonable LLM context limits
                pdf_url=pdf_url,
                retrieval_method=method,
                source_confidence=conf,
                verification_status=verif_status
            )

        except Exception as e:
            logger.error(f"PDF extraction failed for {pdf_url}: {e}", exc_info=True)
            return None
        finally:
            # Enforce Render ephemeral hygiene: always remove temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _extract_text_and_ocr(self, file_path: str) -> Tuple[str, str]:
        """
        Attempts native PDF text extraction. If text density is low, uses OCR.
        """
        extracted_pages = []
        full_text = ""
        try:
            reader = PdfReader(file_path)
            num_pages = min(len(reader.pages), 20)  # Read up to first 20 pages

            for idx in range(num_pages):
                page = reader.pages[idx]
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(f"--- [Page {idx + 1}] ---\n" + page_text.strip())

            full_text = "\n\n".join(extracted_pages)

            # If native text extraction yielded substantial content, return it
            if len(full_text.strip()) >= 200:
                return full_text, "pdf_text"

            logger.info("Native PDF text is sparse; attempting OCR fallback...")

        except Exception as e:
            logger.warning(f"Native PDF extraction encountered error: {e}")

        # Fallback to OCR for scanned PDFs
        ocr_text = self._perform_ocr_fallback(file_path)
        if ocr_text and len(ocr_text.strip()) >= 100:
            return ocr_text, "pdf_ocr"

        return full_text if full_text else "", "pdf_text"

    def _perform_ocr_fallback(self, file_path: str) -> str:
        """
        Extracts images from PDF and runs pytesseract.
        """
        try:
            import fitz  # PyMuPDF or pdf2image if available
            # Or use pdfplumber
            import pdfplumber
            import pytesseract

            ocr_results = []
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages[:5]):  # OCR first 5 pages
                    im = page.to_image(resolution=200)
                    text = pytesseract.image_to_string(im.original)
                    if text.strip():
                        ocr_results.append(f"--- [OCR Page {idx + 1}] ---\n" + text.strip())

            return "\n\n".join(ocr_results)
        except Exception as e:
            logger.warning(f"OCR fallback could not be executed: {e}")
            return ""
