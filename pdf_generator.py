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
                .replace("\\underline{", "")
                .replace("}", "")
            )
            story.append(Paragraph(contact, normal_style))
            story.append(Spacer(1, 20))
            logger.debug(f"Extracted contact: {contact}")

        # Parse LaTeX content to extract actual sections
        sections_added = 0
        
        # Extract Education section
        education_match = re.search(r'\\section\{Education\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if education_match:
            story.append(Paragraph("Education", section_style))
            sections_added += 1
            education_content = education_match.group(1)
            # Extract education entries
            edu_entries = re.findall(r'\\resumeSubheading\s*\{([^}]+)\}\{([^}]+)\}\s*\{([^}]+)\}\{([^}]+)\}', education_content)
            for entry in edu_entries:
                story.append(Paragraph(f"• {entry[0]} - {entry[1]}", normal_style))
                story.append(Paragraph(f"  {entry[2]} | {entry[3]}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Education section with {len(edu_entries)} entries")

        # Extract Experience section
        experience_match = re.search(r'\\section\{Experience\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if experience_match:
            story.append(Paragraph("Experience", section_style))
            sections_added += 1
            experience_content = experience_match.group(1)
            # Extract experience entries with better regex
            exp_entries = re.findall(r'\\resumeSubheading\s*\{([^}]+)\}\{([^}]+)\}\s*\{([^}]+)\}\{([^}]+)\}', experience_content)
            for entry in exp_entries:
                story.append(Paragraph(f"<b>{entry[0]}</b> - {entry[1]}", normal_style))
                story.append(Paragraph(f"  {entry[2]} | {entry[3]}", normal_style))
                
                # Extract bullet points from experience description
                exp_desc_match = re.search(r'\\resumeItemListStart(.*?)\\resumeItemListEnd', experience_content, re.DOTALL)
                if exp_desc_match:
                    desc_content = exp_desc_match.group(1)
                    bullet_points = re.findall(r'\\resumeItem\{([^}]+)\}', desc_content)
                    for bullet in bullet_points:
                        # Convert bullet points properly
                        clean_bullet = bullet.replace('•', '').strip()
                        if clean_bullet:
                            story.append(Paragraph(f"  • {clean_bullet}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Experience section with {len(exp_entries)} entries")

        # Extract Projects section
        projects_match = re.search(r'\\section\{Projects\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if projects_match:
            story.append(Paragraph("Projects", section_style))
            sections_added += 1
            projects_content = projects_match.group(1)
            # Extract project entries with better regex
            project_entries = re.findall(r'\\resumeProjectHeading\s*\{([^}]+)\}', projects_content)
            for entry in project_entries:
                # Clean up project heading (remove LaTeX formatting)
                clean_entry = entry.replace('\\textbf{', '').replace('}', '').replace('$|$', ' | ')
                story.append(Paragraph(f"<b>{clean_entry}</b>", normal_style))
                
                # Extract bullet points from project description
                proj_desc_match = re.search(r'\\resumeItemListStart(.*?)\\resumeItemListEnd', projects_content, re.DOTALL)
                if proj_desc_match:
                    desc_content = proj_desc_match.group(1)
                    bullet_points = re.findall(r'\\resumeItem\{([^}]+)\}', desc_content)
                    for bullet in bullet_points:
                        # Convert bullet points properly
                        clean_bullet = bullet.replace('•', '').strip()
                        if clean_bullet:
                            story.append(Paragraph(f"  • {clean_bullet}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Projects section with {len(project_entries)} entries")

        # Extract Technical Skills section
        skills_match = re.search(r'\\section\{Technical Skills\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if skills_match:
            story.append(Paragraph("Technical Skills", section_style))
            sections_added += 1
            skills_content = skills_match.group(1)
            # Extract skills
            skills_entries = re.findall(r'\\textbf\{([^}]+)\}:\s*([^\\\\]+)', skills_content)
            for entry in skills_entries:
                story.append(Paragraph(f"• {entry[0]}: {entry[1].strip()}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Technical Skills section with {len(skills_entries)} categories")

        # Extract Research Papers section
        research_match = re.search(r'\\section\{Research Papers\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if research_match:
            story.append(Paragraph("Research Papers", section_style))
            sections_added += 1
            research_content = research_match.group(1)
            # Extract research entries
            research_entries = re.findall(r'\\resumeSubheading\s*\{([^}]+)\}\{([^}]+)\}\s*\{([^}]+)\}\{([^}]+)\}', research_content)
            for entry in research_entries:
                story.append(Paragraph(f"• {entry[0]} ({entry[1]})", normal_style))
                story.append(Paragraph(f"  {entry[2]} | {entry[3]}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Research Papers section with {len(research_entries)} entries")

        # Extract Achievements section
        achievements_match = re.search(r'\\section\{Achievements\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if achievements_match:
            story.append(Paragraph("Achievements", section_style))
            sections_added += 1
            achievements_content = achievements_match.group(1)
            # Extract achievement items
            achievement_items = re.findall(r'\\item\{([^}]+)\}', achievements_content)
            for item in achievement_items:
                story.append(Paragraph(f"• {item.strip()}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Achievements section with {len(achievement_items)} items")

        # Extract Others section
        others_match = re.search(r'\\section\{Others\}(.*?)(?=\\section\{|\Z)', latex_content, re.DOTALL)
        if others_match:
            story.append(Paragraph("Additional Information", section_style))
            sections_added += 1
            others_content = others_match.group(1)
            # Extract other items
            other_items = re.findall(r'\\item\{([^}]+)\}', others_content)
            for item in other_items:
                story.append(Paragraph(f"• {item.strip()}", normal_style))
            story.append(Spacer(1, 12))
            logger.debug(f"Added Others section with {len(other_items)} items")

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
