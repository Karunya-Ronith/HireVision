import gradio as gr
from resume_analyzer import process_resume_analysis
from learning_path_analyzer import process_learning_path_analysis

# Create the main HireVision application
with gr.Blocks(title="HireVision - AI Career Coach", theme=gr.themes.Soft()) as demo:
    
    # Navigation tabs
    with gr.Tabs():
        
        # Homepage Tab
        with gr.Tab("🏠 Home", id=0):
            gr.Markdown("""
            # 🚀 Welcome to HireVision
            
            **Your AI-Powered Career Success Platform**
            
            ---
            
            ## 🎯 What We Offer
            
            ### 📄 Resume ATS Analyzer
            Upload your resume and get AI-powered analysis to optimize it for Applicant Tracking Systems (ATS). Get detailed feedback on:
            - **ATS Score** (0-100) - How well your resume matches job requirements
            - **Strengths & Weaknesses** - Comprehensive analysis
            - **Skills Gap Analysis** - Missing competencies
            - **Upskilling Recommendations** - Personalized learning suggestions
            
            ### 🎯 Learning Path Analyzer
            Input your current skills and dream role to get a detailed roadmap to your career goals:
            - **Step-by-Step Learning Plan** - Phase-by-phase approach
            - **Curated Resources** - Specific courses, books, and tools
            - **Hands-on Projects** - Portfolio-building opportunities
            - **Timeline & Success Metrics** - Track your progress
            
            ---
            
            ## 🚀 Get Started
            
            Choose your path above to begin your career journey with AI-powered insights!
            
            ---
            
            **💡 Pro Tip**: Use both tools together for maximum impact - analyze your resume first, then create a learning path to fill any gaps!
            """)
        
        # Resume Analyzer Tab
        with gr.Tab("📄 Resume Analyzer", id=1):
            gr.Markdown("""
            # 📄 Resume ATS Analyzer & Career Coach
            
            Upload your resume (PDF) and provide a job description to get:
            - **ATS Score** - How well your resume matches the job requirements
            - **Detailed Analysis** - Strengths, weaknesses, and improvement areas
            - **Skills Gap Analysis** - Missing skills and competencies
            - **Upskilling Recommendations** - Personalized learning suggestions
            
            ---
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(
                        label="📎 Upload Resume (PDF)",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    
                    job_desc_input = gr.Textbox(
                        label="💼 Job Description",
                        placeholder="Paste the job description here...",
                        lines=10,
                        max_lines=20
                    )
                    
                    analyze_btn = gr.Button(
                        "🔍 Analyze Resume",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    resume_output = gr.Markdown(
                        label="📊 Analysis Results",
                        value="Upload your resume and job description to get started!"
                    )
            
            # Add some helpful tips
            with gr.Accordion("💡 Tips for Better Results", open=False):
                gr.Markdown("""
                **For Best Results:**
                - Ensure your PDF is text-based (not scanned images)
                - Include a comprehensive job description
                - Make sure your resume is up-to-date
                - The analysis works best with detailed job descriptions
                
                **What the ATS Score Means:**
                - **90-100**: Excellent match, high chance of passing ATS
                - **70-89**: Good match, some improvements needed
                - **50-69**: Fair match, significant improvements recommended
                - **Below 50**: Poor match, major revisions needed
                """)
            
            # Connect the button to the processing function
            analyze_btn.click(
                fn=process_resume_analysis,
                inputs=[pdf_input, job_desc_input],
                outputs=resume_output
            )
        
        # Learning Path Analyzer Tab
        with gr.Tab("🎯 Learning Path", id=2):
            gr.Markdown("""
            # 🎯 Learning Path Analyzer & Career Coach
            
            Input your current skills and dream role to get:
            - **Detailed Learning Path** - Step-by-step roadmap to your dream role
            - **Skills Gap Analysis** - What you need to learn
            - **Curated Resources** - Specific courses, books, and tools
            - **Hands-on Projects** - Practical projects to build your portfolio
            - **Timeline & Success Metrics** - Track your progress effectively
            
            ---
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    current_skills_input = gr.Textbox(
                        label="🔧 Current Skills",
                        placeholder="List your current skills, experience, and knowledge...",
                        lines=8,
                        max_lines=15
                    )
                    
                    dream_role_input = gr.Textbox(
                        label="🎯 Dream Role",
                        placeholder="Describe your dream role, position, or career goal...",
                        lines=6,
                        max_lines=10
                    )
                    
                    learning_analyze_btn = gr.Button(
                        "🚀 Generate Learning Path",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    learning_output = gr.Markdown(
                        label="📚 Learning Path Results",
                        value="Input your current skills and dream role to get started!"
                    )
            
            # Add some helpful tips
            with gr.Accordion("💡 Tips for Better Results", open=False):
                gr.Markdown("""
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
                """)
            
            # Add example inputs
            with gr.Accordion("📝 Example Inputs", open=False):
                gr.Markdown("""
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
                """)
            
            # Connect the button to the processing function
            learning_analyze_btn.click(
                fn=process_learning_path_analysis,
                inputs=[current_skills_input, dream_role_input],
                outputs=learning_output
            )
        
        # About Us Tab
        with gr.Tab("👥 About Us", id=3):
            gr.Markdown("""
            # 👥 About HireVision
            
            **Empowering Careers Through AI Innovation**
            
            ---
            
            ## 🚀 Our Mission
            
            At HireVision, we believe everyone deserves access to AI-powered career guidance. Our platform combines cutting-edge artificial intelligence with human expertise to help job seekers optimize their resumes and create personalized learning paths to their dream careers.
            
            ---
            
            ## 🧠 Meet Our Team
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### 👨‍💻 Hasib Mohammad Khan
                    **Lead Developer & AI Specialist**
                    
                    A passionate technologist with expertise in AI/ML, full-stack development, and career technology solutions. Hasib leads the technical architecture and AI integration for HireVision, ensuring our platform delivers cutting-edge career insights.
                    
                    **Expertise:** AI/ML, Full-Stack Development, Career Technology
                    """)
                    
                    # Placeholder for Hasib's picture
                    gr.Markdown("""
                    <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                        <p style="color: #666; font-style: italic;">📸 Photo of Hasib Mohammad Khan</p>
                        <p style="color: #999; font-size: 12px;">[Add profile picture here]</p>
                    </div>
                    """)
                
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### 👩‍💼 L Karunya Ronith
                    **AI Specialist and Prompt Engineer**
                    
                    An innovative AI specialist with deep expertise in prompt engineering and machine learning. Karunya's expertise in AI optimization ensures HireVision delivers precise, contextually relevant career guidance through advanced prompt engineering techniques.
                    
                    **Expertise:** AI/ML, Prompt Engineering, Machine Learning
                    """)
                    
                    # Placeholder for Karunya's picture
                    gr.Markdown("""
                    <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                        <p style="color: #666; font-style: italic;">📸 Photo of L Karunya Ronith</p>
                        <p style="color: #999; font-size: 12px;">[Add profile picture here]</p>
                    </div>
                    """)
                
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### 👨‍🔬 Kondaveeti Antony Raju
                    **UI/UX Designer and Data Engineer**
                    
                    A creative professional with expertise in user experience design and data engineering. Antony combines design thinking with technical skills to create intuitive interfaces and robust data pipelines that power HireVision's insights.
                    
                    **Expertise:** UI/UX Design, Data Engineering, User Research
                    """)
                    
                    # Placeholder for Antony's picture
                    gr.Markdown("""
                    <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 10px 0;">
                        <p style="color: #666; font-style: italic;">📸 Photo of Kondaveeti Antony Raju</p>
                        <p style="color: #999; font-size: 12px;">[Add profile picture here]</p>
                    </div>
                    """)
            
            gr.Markdown("""
            ---
            
            ## 🎯 What Makes HireVision Special
            
            ### 🤖 AI-Powered Insights
            Our advanced AI models analyze resumes and career goals to provide personalized, actionable recommendations.
            
            ### 📊 Data-Driven Approach
            Every recommendation is backed by extensive career data and industry research.
            
            ### 🎨 User-Centric Design
            Intuitive interface designed to make career planning accessible and enjoyable.
            
            ### 🔄 Continuous Learning
            Our platform evolves with industry trends and user feedback.
            
            ---
            
            ## 🌟 Our Vision
            
            To democratize career success by making AI-powered career guidance accessible to everyone, regardless of their background or experience level.
            
            ---
            
            ## 📞 Get in Touch
            
            We're always looking to improve and help more people achieve their career goals. Your feedback and suggestions are invaluable to us!
            
            **💡 Pro Tip**: Try both our Resume Analyzer and Learning Path tools to get the complete career development experience!
            """)

if __name__ == "__main__":
    demo.launch(share=False, debug=True) 