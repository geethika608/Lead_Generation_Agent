"""
Interface builder module for the Gradio interface
"""

import gradio as gr
# Import removed as it's not used in this file

class InterfaceBuilder:
    """Interface builder for creating UI components"""
    
    def __init__(self):
        """Initialize interface builder"""
        pass
    
    def get_custom_css(self) -> str:
        """Get custom CSS for styling the interface"""
        return """
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
        .main-header {
            text-align: center;
            margin-bottom: 2rem;
            color: #2c3e50;
        }
        .input-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .output-section {
            background: #e8f5e8;
            padding: 1.5rem;
            border-radius: 10px;
        }
        .progress-section {
            background: #fff3cd;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #ffc107;
        }
        .progress-bar {
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 20px;
            transition: width 0.3s ease;
        }
        """
    
    def create_input_section(self) -> tuple:
        """Create the input section with form fields"""
        with gr.Column(scale=1):
            gr.HTML('<div class="input-section">')
            
            # Basic Information
            gr.HTML("<h3>📋 Campaign Information</h3>")
            search_strategy = gr.Textbox(
                label="Search Strategy",
                placeholder="e.g., site:linkedin.com software engineer tech, site:linkedin.com CTO SaaS",
                info="Your search strategy for finding leads (e.g., LinkedIn searches, specific keywords)"
            )
            
            target_clients = gr.Textbox(
                label="Target Clients",
                placeholder="e.g., CTO, VP Engineering, Marketing Director",
                info="Comma-separated list of target job titles or roles"
            )
            
            campaign_agenda = gr.Textbox(
                label="Campaign Agenda",
                placeholder="e.g., Book a demo, Schedule a consultation, Download whitepaper",
                info="What action do you want prospects to take?"
            )
            
            
            # Advanced Settings
            gr.HTML("<h3>⚙️ Advanced Settings</h3>")
            
            with gr.Row():
                max_leads = gr.Slider(
                    minimum=10,
                    maximum=200,
                    value=50,
                    step=10,
                    label="Maximum Leads to Generate",
                    info="Number of leads to find and process"
                )
                
                search_depth = gr.Slider(
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1,
                    label="Search Depth",
                    info="How deep to search for leads (1=shallow, 5=comprehensive)"
                )
            
            # Action Buttons
            gr.HTML("<h3>🚀 Actions</h3>")
            
            with gr.Row():
                run_button = gr.Button(
                    "🚀 Start Lead Generation",
                    variant="primary",
                    size="lg"
                )
            
            
            gr.HTML('</div>')
            
            gr.HTML('</div>')
            
            return search_strategy, target_clients, campaign_agenda, max_leads, search_depth, run_button