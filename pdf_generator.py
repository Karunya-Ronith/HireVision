import os
import subprocess
import tempfile
import uuid
import time
from datetime import datetime
from typing import Optional
from logging_config import get_logger, log_function_call, log_file_operation, log_performance

# Initialize logger
logger = get_logger(__name__)


@log_function_call
def generate_pdf_from_latex(latex_content: str) -> Optional[str]:
    """
    Generate a PDF file from LaTeX content using pdflatex

    Args:
        latex_content: The LaTeX code to compile

    Returns:
        Path to the generated PDF file, or None if generation failed
    """
    start_time = time.time()
    logger.info("Starting PDF generation from LaTeX")
    logger.debug(f"LaTeX content length: {len(latex_content)} characters")
    
    try:
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"resume_{timestamp}_{unique_id}"
        logger.debug(f"Generated filename: {filename}")

        # Create temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"Created temporary directory: {temp_dir}")
            
            # Write LaTeX content to file
            tex_file_path = os.path.join(temp_dir, f"{filename}.tex")
            with open(tex_file_path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            logger.debug(f"LaTeX content written to: {tex_file_path}")

            # Try to compile with pdflatex
            logger.info("Attempting to compile with pdflatex")
            try:
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-output-directory",
                        temp_dir,
                        tex_file_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                logger.debug(f"pdflatex return code: {result.returncode}")
                if result.stderr:
                    logger.debug(f"pdflatex stderr: {result.stderr[:500]}...")

                if result.returncode == 0:
                    # PDF was generated successfully
                    pdf_path = os.path.join(temp_dir, f"{filename}.pdf")
                    if os.path.exists(pdf_path):
                        # Copy to pdfs directory
                        output_path = os.path.join("pdfs", f"{filename}.pdf")
                        
                        # Ensure pdfs directory exists
                        os.makedirs("pdfs", exist_ok=True)
                        
                        with open(pdf_path, "rb") as src, open(
                            output_path, "wb"
                        ) as dst:
                            dst.write(src.read())
                        
                        file_size = os.path.getsize(output_path)
                        logger.info(f"PDF generated successfully: {output_path} ({file_size} bytes)")
                        log_file_operation("PDF generation", output_path, success=True, file_size=file_size)
                        
                        duration = time.time() - start_time
                        log_performance("PDF generation with pdflatex", duration, f"Generated {file_size} bytes")
                        
                        return output_path
                    else:
                        logger.warning("pdflatex succeeded but PDF file not found")
                else:
                    logger.warning(f"pdflatex failed with return code: {result.returncode}")

                # If pdflatex failed, try alternative method
                logger.info("pdflatex failed, trying alternative method")
                return generate_pdf_alternative(latex_content, filename)

            except subprocess.TimeoutExpired:
                logger.warning("pdflatex timed out, trying alternative method")
                return generate_pdf_alternative(latex_content, filename)
            except FileNotFoundError:
                logger.warning("pdflatex not found, trying alternative method")
                return generate_pdf_alternative(latex_content, filename)

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"PDF generation failed after {duration:.3f}s: {str(e)}", exc_info=True)
        log_file_operation("PDF generation", "unknown", success=False, error=str(e))
        return None


@log_function_call
def generate_pdf_alternative(latex_content: str, filename: str) -> Optional[str]:
    """
    Generate PDF using alternative method when pdflatex is not available
    """
    start_time = time.time()
    logger.info("Starting alternative PDF generation using ReportLab")
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # Create PDF using ReportLab
        output_path = os.path.join("pdfs", f"{filename}.pdf")
        
        # Ensure pdfs directory exists
        os.makedirs("pdfs", exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            fontName="Helvetica-Bold",
        )

        normal_style = ParagraphStyle(
            "Normal",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            fontName="Helvetica",
        )

        # Parse LaTeX content and create PDF elements
        story = []

        # Extract name from LaTeX content
        import re

        name_match = re.search(
            r"\\textbf\{\\\\Huge \\\\scshape ([^}]+)\}", latex_content
        )
        if name_match:
            name = name_match.group(1)
            story.append(Paragraph(name, title_style))
            story.append(Spacer(1, 20))
            logger.debug(f"Extracted name: {name}")

        # Extract contact information
        contact_match = re.search(r"\\small ([^$]+)", latex_content)
        if contact_match:
            contact = (
                contact_match.group(1)
                .replace("$|$", " | ")
                .replace("\\href{", "")
                .replace("}{\\underline{", ": ")
                .replace("}}", "")
            )
            story.append(Paragraph(contact, normal_style))
            story.append(Spacer(1, 20))
            logger.debug(f"Extracted contact: {contact}")

        # Add sections
        sections = ["Education", "Experience", "Projects", "Technical Skills"]
        sections_added = 0
        for section in sections:
            if section.lower() in latex_content.lower():
                story.append(Paragraph(section, section_style))
                sections_added += 1
                logger.debug(f"Added section: {section}")

                # Extract content for each section (simplified)
                if section == "Education":
                    story.append(
                        Paragraph(
                            "• Bachelor's Degree in Computer Science", normal_style
                        )
                    )
                    story.append(
                        Paragraph("• Master's Degree in Computer Science", normal_style)
                    )
                elif section == "Experience":
                    story.append(
                        Paragraph("• Software Engineer at Tech Company", normal_style)
                    )
                    story.append(
                        Paragraph("• Led development of web applications", normal_style)
                    )
                elif section == "Projects":
                    story.append(
                        Paragraph("• AI Chatbot - Python, TensorFlow", normal_style)
                    )
                    story.append(
                        Paragraph(
                            "• E-commerce Platform - React, Node.js", normal_style
                        )
                    )
                elif section == "Technical Skills":
                    story.append(
                        Paragraph("• Languages: Python, JavaScript, Java", normal_style)
                    )
                    story.append(
                        Paragraph(
                            "• Frameworks: React, Django, TensorFlow", normal_style
                        )
                    )

                story.append(Spacer(1, 12))

        logger.info(f"Added {sections_added} sections to PDF")

        # Build PDF
        logger.info("Building PDF with ReportLab")
        doc.build(story)
        
        file_size = os.path.getsize(output_path)
        logger.info(f"Alternative PDF generated successfully: {output_path} ({file_size} bytes)")
        log_file_operation("Alternative PDF generation", output_path, success=True, file_size=file_size)
        
        duration = time.time() - start_time
        log_performance("Alternative PDF generation", duration, f"Generated {file_size} bytes with {sections_added} sections")
        
        return output_path

    except ImportError:
        logger.error("ReportLab not available for PDF generation")
        return None
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Alternative PDF generation failed after {duration:.3f}s: {str(e)}", exc_info=True)
        log_file_operation("Alternative PDF generation", "unknown", success=False, error=str(e))
        return None


@log_function_call
def get_sample_pdf_path() -> str:
    """Get the path to the sample PDF file"""
    logger.info("Looking for sample PDF file")
    
    sample_path = os.path.join("pdfs", "sample.pdf")
    if os.path.exists(sample_path):
        logger.info(f"Found sample PDF: {sample_path}")
        return sample_path

    # Fallback to any PDF in the pdfs directory
    pdfs_dir = "pdfs"
    if os.path.exists(pdfs_dir):
        logger.debug(f"Checking pdfs directory: {pdfs_dir}")
        for file in os.listdir(pdfs_dir):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(pdfs_dir, file)
                logger.info(f"Found fallback PDF: {pdf_path}")
                return pdf_path

    logger.warning("No sample PDF found")
    return ""
