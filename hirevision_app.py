import gradio as gr
from resume_analyzer import process_resume_analysis
from learning_path_analyzer import process_learning_path_analysis
from resume_builder import process_resume_builder
from pdf_generator import get_sample_pdf_path
import traceback

# Custom CSS for professional header only
custom_css = """
/* Professional header styling */
.header-container {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}

.header-container h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-container p {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

/* Responsive design for header */
@media (max-width: 768px) {
    .header-container h1 {
        font-size: 2rem;
    }
}
"""


def safe_process_resume_analysis(pdf_file, job_description, progress=gr.Progress()):
    """Wrapper function with error handling for resume analysis"""
    try:
        progress(0.2, desc="Uploading and processing PDF...")
        result = process_resume_analysis(pdf_file, job_description)
        progress(0.8, desc="Analyzing with AI...")
        progress(1.0, desc="Analysis complete!")
        return result
    except Exception as e:
        progress(1.0, desc="Error occurred")
        error_msg = f"## Application Error\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support if the issue persists."
        print(f"Resume analysis error: {traceback.format_exc()}")
        return error_msg


def safe_process_learning_path_analysis(
    current_skills, dream_role, progress=gr.Progress()
):
    """Wrapper function with error handling for learning path analysis"""
    try:
        progress(0.2, desc="Processing your skills and goals...")
        result = process_learning_path_analysis(current_skills, dream_role)
        progress(0.8, desc="Generating personalized learning path...")
        progress(1.0, desc="Learning path ready!")
        return result
    except Exception as e:
        progress(1.0, desc="Error occurred")
        error_msg = f"## Application Error\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support if the issue persists."
        print(f"Learning path analysis error: {traceback.format_exc()}")
        return error_msg


def safe_process_resume_builder(
    name,
    email,
    phone,
    linkedin,
    github,
    education,
    experience,
    projects,
    skills,
    research_papers,
    achievements,
    others,
    progress=gr.Progress(),
):
    """Wrapper function with error handling for resume building"""
    try:
        progress(0.2, desc="Validating input data...")
        latex_content, pdf_path = process_resume_builder(
            name,
            email,
            phone,
            linkedin,
            github,
            education,
            experience,
            projects,
            skills,
            research_papers,
            achievements,
            others,
        )

        # If there's an error, latex_content will be the error message
        if isinstance(latex_content, str) and latex_content.startswith("## "):
            return latex_content, None, latex_content

        progress(0.6, desc="Generating LaTeX code...")

        # Format the output with both LaTeX code and PDF download
        output = f"""
## Resume Generated Successfully!

Your resume has been generated in both LaTeX and PDF formats.

### LaTeX Code
```latex
{latex_content}
```

### How to Use

1. **Copy the LaTeX code** above for customization
2. **Download the PDF** below for immediate use
3. **Compile LaTeX** using one of these methods:

#### Option 1: Online LaTeX Editor
- Go to [Overleaf](https://www.overleaf.com/) (free)
- Create a new project
- Paste the code and compile

#### Option 2: Local LaTeX Installation
- Install a LaTeX distribution (TeX Live, MiKTeX, etc.)
- Install a LaTeX editor (TeXstudio, TeXmaker, etc.)
- Open the `.tex` file and compile

#### Option 3: Command Line
```bash
pdflatex resume.tex
```

### Customization Tips

- **Fonts**: Uncomment different font options in the header
- **Colors**: Modify the color scheme in the header
- **Layout**: Adjust margins and spacing as needed
- **Content**: Edit the generated content to match your preferences

### ATS Optimization

This template is designed to be ATS-friendly with:
- Clean, readable formatting
- Standard section headers
- Machine-readable text
- Proper keyword placement

### Pro Tips

- Keep descriptions concise and action-oriented
- Use bullet points for easy scanning
- Include relevant keywords from job descriptions
- Proofread carefully before submitting
- Save both `.tex` and `.pdf` versions

---
**Need help?** The LaTeX community is very helpful - check out [TeX Stack Exchange](https://tex.stackexchange.com/) for questions!
"""

        progress(0.8, desc="Generating PDF...")

        return latex_content, pdf_path, output

    except Exception as e:
        error_msg = f"## Application Error\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support if the issue persists."
        print(f"Resume builder error: {traceback.format_exc()}")
        return error_msg, None, error_msg


def show_sample_resume(progress=gr.Progress()):
    """Show a complete sample resume"""
    try:
        progress(0.3, desc="Loading sample resume...")
        with open("sample_resume.tex", "r", encoding="utf-8") as f:
            sample_content = f.read()

        progress(0.6, desc="Preparing sample PDF...")
        # Get sample PDF path
        sample_pdf_path = get_sample_pdf_path()

        status_message = """
## Sample Resume Preview

This is a complete example of what your generated LaTeX resume will look like.

### Key Features of This Template:
- **Professional Layout**: Clean, modern design
- **ATS-Optimized**: Machine-readable formatting
- **Multiple Sections**: Education, Experience, Projects, Skills
- **Flexible Structure**: Easy to customize
- **Industry Standard**: Based on proven template

### How to Use Your Generated Resume:
1. Copy the LaTeX code from your generated resume
2. Paste it into Overleaf (overleaf.com) or save as `.tex` file
3. Compile to get a professional PDF
4. Customize further if needed

### Pro Tips:
- The template is designed to be ATS-friendly
- All sections are properly formatted for scanning
- Use action verbs and quantify achievements
- Keep descriptions concise and impactful
"""

        progress(1.0, desc="Sample ready!")
        return sample_content, sample_pdf_path, status_message

    except Exception as e:
        error_msg = f"## Error Loading Sample\n\nCould not load sample resume: {str(e)}"
        return error_msg, None, error_msg


# Create the main HireVision application
with gr.Blocks(
    title="HireVision - AI Career Coach", theme="soft", css=custom_css
) as demo:

    # Professional header
    with gr.Row():
        gr.HTML(
            """
        <div class="header-container">
            <h1>HireVision</h1>
            <p>Your AI-Powered Career Success Platform</p>
        </div>
        """
        )

    # Navigation tabs
    with gr.Tabs():

        # Homepage Tab
        with gr.Tab("Home", id=0):
            gr.Markdown(
                """
            # Welcome to HireVision
            
            **Your AI-Powered Career Success Platform**
            
            ---
            
            ## What We Offer
            
            ### Resume ATS Analyzer
            Upload your resume and get AI-powered analysis to optimize it for Applicant Tracking Systems (ATS). Get detailed feedback on:
            - **ATS Score** (0-100) - How well your resume matches job requirements
            - **Strengths & Weaknesses** - Comprehensive analysis
            - **Skills Gap Analysis** - Missing competencies
            - **Upskilling Recommendations** - Personalized learning suggestions
            
            ### Learning Path Analyzer
            Input your current skills and dream role to get a detailed roadmap to your career goals:
            - **Step-by-Step Learning Plan** - Phase-by-phase approach
            - **Curated Resources** - Specific courses, books, and tools
            - **Hands-on Projects** - Portfolio-building opportunities
            - **Timeline & Success Metrics** - Track your progress
            
            ### Resume Builder
            Create professional LaTeX resumes with our AI-powered builder:
            - **Professional Templates** - Clean, modern LaTeX design
            - **ATS-Optimized** - Machine-readable formatting
            - **Customizable Sections** - Education, experience, projects, skills
            - **Easy Export** - Generate LaTeX code for compilation
            
            ---
            
            ## Get Started
            
            Choose your path above to begin your career journey with AI-powered insights!
            
            ---
            
            **Pro Tip**: Use both tools together for maximum impact - analyze your resume first, then create a learning path to fill any gaps!
            """
            )

        # Resume Analyzer Tab
        with gr.Tab("Resume Analyzer", id=1):
            gr.Markdown(
                """
            # Resume ATS Analyzer & Career Coach
            
            Upload your resume (PDF) and provide a job description to get:
            - **ATS Score** - How well your resume matches the job requirements
            - **Detailed Analysis** - Strengths, weaknesses, and improvement areas
            - **Skills Gap Analysis** - Missing skills and competencies
            - **Upskilling Recommendations** - Personalized learning suggestions
            
            ---
            """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(
                        label="Upload Resume (PDF)",
                        file_types=[".pdf"],
                        type="filepath",
                    )

                    job_desc_input = gr.Textbox(
                        label="Job Description",
                        placeholder="Paste the job description here...",
                        lines=10,
                        max_lines=20,
                    )

                    analyze_btn = gr.Button(
                        "Analyze Resume", variant="primary", size="lg"
                    )

                    # Loading bar for resume analysis
                    analyze_progress = gr.Progress()

                with gr.Column(scale=2):
                    resume_output = gr.Markdown(
                        label="Analysis Results",
                        value="Upload your resume and job description to get started!",
                    )

            # Add some helpful tips
            with gr.Accordion("Tips for Better Results", open=False):
                gr.Markdown(
                    """
                **For Best Results:**
                - Ensure your PDF is text-based (not scanned images)
                - Include a comprehensive job description
                - Make sure your resume is up-to-date
                - The analysis works best with detailed job descriptions
                
                **What the ATS Score Means:**
                - **85-100**: Excellent match, high chance of passing ATS
                - **65-84**: Good match, some improvements needed
                - **45-64**: Fair match, significant improvements recommended
                - **Below 45**: Poor match, major revisions needed
                
                **Error Handling:**
                - If you encounter any errors, please try again
                - Ensure your PDF file is not corrupted
                - Check your internet connection
                - Contact support if issues persist
                """
                )

            # Connect the button to the processing function with error handling
            analyze_btn.click(
                fn=safe_process_resume_analysis,
                inputs=[pdf_input, job_desc_input],
                outputs=resume_output,
                show_progress="full",
            )

        # Learning Path Analyzer Tab
        with gr.Tab("Learning Path", id=2):
            gr.Markdown(
                """
            # Learning Path Analyzer & Career Coach
            
            Input your current skills and dream role to get:
            - **Detailed Learning Path** - Step-by-step roadmap to your dream role
            - **Skills Gap Analysis** - What you need to learn
            - **Curated Resources** - Specific courses, books, and tools
            - **Hands-on Projects** - Practical projects to build your portfolio
            - **Timeline & Success Metrics** - Track your progress effectively
            
            ---
            """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    current_skills_input = gr.Textbox(
                        label="Current Skills",
                        placeholder="List your current skills, experience, and knowledge...",
                        lines=8,
                        max_lines=15,
                    )

                    dream_role_input = gr.Textbox(
                        label="Dream Role",
                        placeholder="Describe your dream role, position, or career goal...",
                        lines=6,
                        max_lines=10,
                    )

                    learning_analyze_btn = gr.Button(
                        "Generate Learning Path", variant="primary", size="lg"
                    )

                    # Loading bar for learning path analysis
                    learning_progress = gr.Progress()

                with gr.Column(scale=2):
                    learning_output = gr.Markdown(
                        label="Learning Path Results",
                        value="Input your current skills and dream role to get started!",
                    )

            # Add some helpful tips
            with gr.Accordion("Tips for Better Results", open=False):
                gr.Markdown(
                    """
                **For Best Results:**
                - Be specific about your current skills and experience level
                - Include both technical and soft skills
                - Describe your dream role in detail (industry, company size, responsibilities)
                - Mention any constraints (time, budget, location)
                - Include your current education level and background
                
                **What You'll Get:**
                - **Phase-by-phase learning plan** with realistic timelines
                - **Specific resources** with links to courses, books, and tools
                - **Hands-on projects** to build your portfolio
                - **Success metrics** to track your progress
                - **Career advice** and networking tips
                
                **Resource Verification:**
                - All recommended resources are verified to exist
                - Unverified resources are clearly marked
                - Focus on well-known, established platforms
                - No fake or hallucinated links
                """
                )

            # Add example inputs
            with gr.Accordion("Example Inputs", open=False):
                gr.Markdown(
                    """
                **Example Current Skills:**
                ```
                • Python programming (intermediate level)
                • Basic web development (HTML, CSS, JavaScript)
                • Data analysis with Excel and basic SQL
                • Project management experience
                • Strong communication and teamwork skills
                • Bachelor's degree in Computer Science
                • 2 years of experience in IT support
                ```
                
                **Example Dream Role:**
                ```
                Data Scientist at a tech company like Google, Amazon, or Microsoft
                - Focus on machine learning and AI applications
                - Work with large datasets and predictive modeling
                - Collaborate with cross-functional teams
                - Salary range: $120k-150k
                - Remote work preferred
                - Industry: Technology/Software
                ```
                """
                )

            # Connect the button to the processing function with error handling
            learning_analyze_btn.click(
                fn=safe_process_learning_path_analysis,
                inputs=[current_skills_input, dream_role_input],
                outputs=learning_output,
                show_progress="full",
            )

        # Resume Builder Tab
        with gr.Tab("Resume Builder", id=3):
            gr.Markdown(
                """
            # AI Resume Builder
            
            Create a professional LaTeX resume with our AI-powered builder. Input your details and get a beautifully formatted resume that's ATS-friendly!
            
            **Features:**
            - Professional LaTeX template
            - ATS-optimized formatting
            - Customizable sections
            - Clean, modern design
            
            ---
            """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    # Basic Information
                    gr.Markdown("### Basic Information")
                    name_input = gr.Textbox(
                        label="Full Name *", placeholder="e.g., John Doe", lines=1
                    )

                    email_input = gr.Textbox(
                        label="Email", placeholder="e.g., john.doe@email.com", lines=1
                    )

                    phone_input = gr.Textbox(
                        label="Phone", placeholder="e.g., +1-234-567-8900", lines=1
                    )

                    linkedin_input = gr.Textbox(
                        label="LinkedIn",
                        placeholder="e.g., linkedin.com/in/johndoe",
                        lines=1,
                    )

                    github_input = gr.Textbox(
                        label="GitHub", placeholder="e.g., github.com/johndoe", lines=1
                    )

                    # Education Section
                    gr.Markdown("### Education *")
                    education_input = gr.Textbox(
                        label="Education (JSON format)",
                        placeholder='[{"institution": "University Name", "location": "City, State", "degree": "Bachelor of Science in Computer Science", "duration": "2020-2024"}]',
                        lines=6,
                        max_lines=10,
                    )

                    # Experience Section (Optional)
                    gr.Markdown("### Experience (Optional)")
                    experience_input = gr.Textbox(
                        label="Experience (JSON format)",
                        placeholder='[{"title": "Software Engineer", "company": "Tech Corp", "location": "San Francisco, CA", "duration": "2022-Present", "description": ["Developed web applications", "Led team of 5 developers"]}]',
                        lines=8,
                        max_lines=12,
                    )

                    # Projects Section
                    gr.Markdown("### Projects *")
                    projects_input = gr.Textbox(
                        label="Projects (JSON format)",
                        placeholder='[{"name": "E-commerce Platform", "tech_stack": "React, Node.js, MongoDB", "description": ["Built full-stack web application", "Implemented payment processing"]}]',
                        lines=8,
                        max_lines=12,
                    )

                    # Skills Section
                    gr.Markdown("### Skills *")
                    skills_input = gr.Textbox(
                        label="Skills (JSON format)",
                        placeholder='{"Programming Languages": ["Python", "JavaScript", "Java"], "Frameworks": ["React", "Django", "Spring"], "Tools": ["Git", "Docker", "AWS"]}',
                        lines=6,
                        max_lines=10,
                    )

                    # Optional Sections
                    gr.Markdown("### Optional Sections")
                    research_input = gr.Textbox(
                        label="Research Papers (JSON format)",
                        placeholder='[{"title": "AI in Healthcare", "authors": "J. Doe, S. Smith", "journal": "Nature", "year": "2023"}]',
                        lines=4,
                        max_lines=6,
                    )

                    achievements_input = gr.Textbox(
                        label="Achievements (JSON format)",
                        placeholder='["Dean\'s List 2023", "Hackathon Winner", "Published 3 research papers"]',
                        lines=3,
                        max_lines=5,
                    )

                    others_input = gr.Textbox(
                        label="Others (JSON format)",
                        placeholder='["Volunteer at local food bank", "Member of ACM", "Fluent in Spanish"]',
                        lines=3,
                        max_lines=5,
                    )

                    with gr.Row():
                        build_btn = gr.Button(
                            "Generate Resume", variant="primary", size="lg"
                        )

                        sample_btn = gr.Button(
                            "Show Complete Sample", variant="secondary", size="md"
                        )

                    # Loading bar for resume generation
                    build_progress = gr.Progress()

                with gr.Column(scale=2):
                    # LaTeX Code Display
                    gr.Markdown("### LaTeX Code")
                    latex_output = gr.Code(
                        label="LaTeX Code",
                        language="latex",
                        value="Fill in your details and click 'Generate Resume' to create your LaTeX resume!",
                        lines=20,
                        interactive=False,
                    )

                    # PDF Download
                    gr.Markdown("### Download PDF")
                    pdf_output = gr.File(
                        label="Generated PDF", file_types=[".pdf"], visible=False
                    )

                    # Status Message
                    status_output = gr.Markdown(
                        label="Status",
                        value="Fill in your details and click 'Generate Resume' to create your resume!",
                    )

            # Add sample preview and helpful tips
            with gr.Accordion("Sample Resume Preview", open=False):
                gr.Markdown(
                    """
                **Here's a sample of the LaTeX code your resume will generate:**
                
                ```latex
                %-------------------------
                % Resume in Latex
                % Author : Generated by HireVision
                % Based off of: https://github.com/jakeryang/resume
                % License : MIT
                %------------------------
                
                \\documentclass[letterpaper,11pt]{article}
                
                % ... (LaTeX packages and setup)
                
                \\begin{document}
                
                %----------HEADING----------
                \\begin{center}
                    \\textbf{\\Huge \\scshape John Doe} \\\\ \\vspace{1pt}
                    \\small +1-234-567-8900 $|$ \\href{mailto:john.doe@email.com}{\\underline{john.doe@email.com}} $|$ 
                    \\href{https://linkedin.com/in/johndoe}{\\underline{linkedin.com/in/johndoe}} $|$
                    \\href{https://github.com/johndoe}{\\underline{github.com/johndoe}}
                \\end{center}
                
                %-----------EDUCATION-----------
                \\section{Education}
                  \\resumeSubHeadingListStart
                    \\resumeSubheading
                      {Stanford University}{Stanford, CA}
                      {Master of Science in Computer Science, Minor in Business}{Aug. 2022 -- May 2024}
                    \\resumeSubheading
                      {MIT}{Cambridge, MA}
                      {Bachelor of Science in Computer Science}{Aug. 2018 -- May 2022}
                  \\resumeSubHeadingListEnd
                
                %-----------EXPERIENCE-----------
                \\section{Experience}
                  \\resumeSubHeadingListStart
                    \\resumeSubheading
                      {Senior Software Engineer}{2022-Present}
                      {Google}{Mountain View, CA}
                      \\resumeItemListStart
                        \\resumeItem{Led development of machine learning models}
                        \\resumeItem{Mentored 5 junior developers}
                        \\resumeItem{Improved system performance by 40\\%}
                      \\resumeItemListEnd
                  \\resumeSubHeadingListEnd
                
                %-----------PROJECTS-----------
                \\section{Projects}
                    \\resumeSubHeadingListStart
                      \\resumeProjectHeading
                          {\\textbf{AI Chatbot} $|$ \\emph{Python, TensorFlow, Flask}}{June 2023 -- Present}
                          \\resumeItemListStart
                            \\resumeItem{Built conversational AI using deep learning}
                            \\resumeItem{Deployed on AWS with 10K+ active users}
                          \\resumeItemListEnd
                    \\resumeSubHeadingListEnd
                
                %-----------PROGRAMMING SKILLS-----------
                \\section{Technical Skills}
                 \\begin{itemize}[leftmargin=0.15in, label={}]
                    \\small{\\item{
                     \\textbf{Languages}{: Python, JavaScript, Java, C/C++, SQL} \\\\
                     \\textbf{Frameworks}{: React, Node.js, Django, TensorFlow, Spring} \\\\
                     \\textbf{Developer Tools}{: Git, Docker, AWS, Kubernetes} \\\\
                     \\textbf{Libraries}{: pandas, NumPy, Matplotlib}
                    }}
                 \\end{itemize}
                
                \\end{document}
                ```
                
                **Key Features:**
                - Clean, professional layout
                - ATS-friendly formatting
                - Proper section organization
                - Machine-readable text
                - Modern typography
                
                **Note:** This is just a preview. The actual output will be complete LaTeX code that you can compile to PDF.
                """
                )

            with gr.Accordion("Tips & Examples", open=False):
                gr.Markdown(
                    """
                **Required Fields:**
                - **Name**: Your full name
                - **Education**: At least one education entry
                - **Projects**: At least one project
                - **Skills**: Your technical and non-technical skills
                
                **JSON Format Examples:**
                
                **Education:**
                ```json
                [
                  {
                    "institution": "Stanford University",
                    "location": "Stanford, CA",
                    "degree": "Master of Science in Computer Science",
                    "duration": "2022-2024"
                  },
                  {
                    "institution": "MIT",
                    "location": "Cambridge, MA", 
                    "degree": "Bachelor of Science in Engineering",
                    "duration": "2018-2022"
                  }
                ]
                ```
                
                **Experience:**
                ```json
                [
                  {
                    "title": "Senior Software Engineer",
                    "company": "Google",
                    "location": "Mountain View, CA",
                    "duration": "2022-Present",
                    "description": [
                      "Led development of machine learning models",
                      "Mentored 5 junior developers",
                      "Improved system performance by 40%"
                    ]
                  },
                  {
                    "title": "Software Engineer",
                    "company": "Microsoft",
                    "location": "Seattle, WA",
                    "duration": "2020-2022",
                    "description": [
                      "Developed full-stack web applications",
                      "Implemented REST APIs and databases"
                    ],
                    "positions": [
                      {
                        "title": "Software Engineer II",
                        "duration": "2021-2022",
                        "description": [
                          "Led team of 3 developers",
                          "Improved application performance by 30%"
                        ]
                      },
                      {
                        "title": "Software Engineer I", 
                        "duration": "2020-2021",
                        "description": [
                          "Developed React components",
                          "Worked on Azure integration"
                        ]
                      }
                    ]
                  }
                ]
                ```
                
                **Projects:**
                ```json
                [
                  {
                    "name": "AI Chatbot",
                    "tech_stack": "Python, TensorFlow, Flask",
                    "description": [
                      "Built conversational AI using deep learning",
                      "Deployed on AWS with 10K+ users",
                      "Achieved 95% accuracy in intent recognition"
                    ]
                  }
                ]
                ```
                
                **Skills:**
                ```json
                {
                  "Programming Languages": ["Python", "JavaScript", "Java", "C++"],
                  "Frameworks & Libraries": ["React", "Django", "TensorFlow", "PyTorch"],
                  "Tools & Technologies": ["Git", "Docker", "AWS", "Kubernetes"],
                  "Soft Skills": ["Leadership", "Problem Solving", "Team Collaboration"]
                }
                ```
                
                **Pro Tips:**
                - Use action verbs in descriptions
                - Quantify achievements when possible
                - Keep descriptions concise and impactful
                - Include relevant keywords for your target role
                - Proofread all content before generating
                """
                )

            # Connect the buttons to the processing functions
            build_btn.click(
                fn=safe_process_resume_builder,
                inputs=[
                    name_input,
                    email_input,
                    phone_input,
                    linkedin_input,
                    github_input,
                    education_input,
                    experience_input,
                    projects_input,
                    skills_input,
                    research_input,
                    achievements_input,
                    others_input,
                ],
                outputs=[latex_output, pdf_output, status_output],
                show_progress="full",
            )

            sample_btn.click(
                fn=show_sample_resume,
                inputs=[],
                outputs=[latex_output, pdf_output, status_output],
                show_progress="full",
            )

        # About Us Tab
        with gr.Tab("About Us", id=4):
            gr.Markdown(
                """
            # About HireVision
            
            **Empowering Careers Through AI Innovation**
            
            ---
            
            ## Our Mission
            
            At HireVision, we believe everyone deserves access to AI-powered career guidance. Our platform combines cutting-edge artificial intelligence with human expertise to help job seekers optimize their resumes and create personalized learning paths to their dream careers.
            
            ---
            
            ## Meet Our Team
            """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                    ### Hasib Mohammad Khan
                    **Lead Developer & AI Specialist**
                    
                    A passionate technologist with expertise in AI/ML, full-stack development, and career technology solutions. Hasib leads the technical architecture and AI integration for HireVision, ensuring our platform delivers cutting-edge career insights.
                    
                    **Expertise:** AI/ML, Full-Stack Development, Career Technology
                    """
                    )

                    # Placeholder for Hasib's picture
                    gr.Markdown(
                        """
                    <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                        <p style="color: #666; font-style: italic;">Photo of Hasib Mohammad Khan</p>
                        <p style="color: #999; font-size: 12px;">[Add profile picture here]</p>
                    </div>
                    """
                    )

                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                    ### L Karunya Ronith
                    **AI Specialist and Prompt Engineer**
                    
                    An innovative AI specialist with deep expertise in prompt engineering and machine learning. Karunya's expertise in AI optimization ensures HireVision delivers precise, contextually relevant career guidance through advanced prompt engineering techniques.
                    
                    **Expertise:** AI/ML, Prompt Engineering, Machine Learning
                    """
                    )

                    # Placeholder for Karunya's picture
                    gr.Markdown(
                        """
                    <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                        <p style="color: #666; font-style: italic;">Photo of L Karunya Ronith</p>
                        <p style="color: #999; font-size: 12px;">[Add profile picture here]</p>
                    </div>
                    """
                    )

                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                    ### Kondaveeti Antony Raju
                    **UI/UX Designer and Data Engineer**
                    
                    A creative professional with expertise in user experience design and data engineering. Antony combines design thinking with technical skills to create intuitive interfaces and robust data pipelines that power HireVision's insights.
                    
                    **Expertise:** UI/UX Design, Data Engineering, User Research
                    """
                    )

                    # Placeholder for Antony's picture
                    gr.Markdown(
                        """
                    <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                        <p style="color: #666; font-style: italic;">Photo of Kondaveeti Antony Raju</p>
                        <p style="color: #999; font-size: 12px;">[Add profile picture here]</p>
                    </div>
                    """
                    )

            gr.Markdown(
                """
            ---
            
            ## What Makes HireVision Special
            
            ### AI-Powered Insights
            Our advanced AI models analyze resumes and career goals to provide personalized, actionable recommendations.
            
            ### Data-Driven Approach
            Every recommendation is backed by extensive career data and industry research.
            
            ### User-Centric Design
            Intuitive interface designed to make career planning accessible and enjoyable.
            
            ### Continuous Learning
            Our platform evolves with industry trends and user feedback.
            
            ### Robust Error Handling
            Comprehensive error handling ensures a smooth user experience even when issues arise.
            
            ---
            
            ## Our Vision
            
            To democratize career success by making AI-powered career guidance accessible to everyone, regardless of their background or experience level.
            
            ---
            
            ## Get in Touch
            
            We're always looking to improve and help more people achieve their career goals. Your feedback and suggestions are invaluable to us!
            
            **Pro Tip**: Try both our Resume Analyzer and Learning Path tools to get the complete career development experience!
            """
            )

if __name__ == "__main__":
    demo.launch(share=False, debug=True)
