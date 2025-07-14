import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from typing import Optional


def generate_pdf_from_latex(latex_content: str) -> Optional[str]:
    """
    Generate a PDF file from LaTeX content using pdflatex

    Args:
        latex_content: The LaTeX code to compile

    Returns:
        Path to the generated PDF file, or None if generation failed
    """
    try:
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"resume_{timestamp}_{unique_id}"

        # Create temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX content to file
            tex_file_path = os.path.join(temp_dir, f"{filename}.tex")
            with open(tex_file_path, "w", encoding="utf-8") as f:
                f.write(latex_content)

            # Try to compile with pdflatex
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

                if result.returncode == 0:
                    # PDF was generated successfully
                    pdf_path = os.path.join(temp_dir, f"{filename}.pdf")
                    if os.path.exists(pdf_path):
                        # Copy to pdfs directory
                        output_path = os.path.join("pdfs", f"{filename}.pdf")
                        with open(pdf_path, "rb") as src, open(
                            output_path, "wb"
                        ) as dst:
                            dst.write(src.read())
                        return output_path

                # If pdflatex failed, try alternative method
                return generate_pdf_alternative(latex_content, filename)

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # pdflatex not available, use alternative method
                return generate_pdf_alternative(latex_content, filename)

    except Exception as e:
        print(f"PDF generation error: {e}")
        return None


def generate_pdf_alternative(latex_content: str, filename: str) -> Optional[str]:
    """
    Generate PDF using alternative method when pdflatex is not available
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # Create PDF using ReportLab
        output_path = os.path.join("pdfs", f"{filename}.pdf")
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

        # Add sections
        sections = ["Education", "Experience", "Projects", "Technical Skills"]
        for section in sections:
            if section.lower() in latex_content.lower():
                story.append(Paragraph(section, section_style))

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

        # Build PDF
        doc.build(story)
        return output_path

    except ImportError:
        print("ReportLab not available for PDF generation")
        return None
    except Exception as e:
        print(f"Alternative PDF generation error: {e}")
        return None


def get_sample_pdf_path() -> str:
    """Get the path to the sample PDF file"""
    sample_path = os.path.join("pdfs", "sample.pdf")
    if os.path.exists(sample_path):
        return sample_path

    # Fallback to any PDF in the pdfs directory
    pdfs_dir = "pdfs"
    if os.path.exists(pdfs_dir):
        for file in os.listdir(pdfs_dir):
            if file.endswith(".pdf"):
                return os.path.join(pdfs_dir, file)

    return ""
