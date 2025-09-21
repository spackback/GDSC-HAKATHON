# Create a simplified mermaid diagram for Cherry AI Desktop Assistant architecture
diagram_code = '''
flowchart TD
    U[User]
    
    subgraph "Cherry AI System"
        ST[System Tray]
        WW[Wake Word<br/>Detection]
        VI[Voice Input<br/>Speech Recognition]
        VO[Voice Output<br/>TTS]
        
        AI[AI Brain<br/>Gemini API]
        MEM[Memory<br/>RAG Context]
        
        VS[Vision System<br/>Screen Capture]
        DC[Desktop Control<br/>PyAutoGUI]
        GUI[GUI Interface<br/>Tkinter]
        AE[Action Executor]
    end
    
    subgraph "External"
        FS[File System]
        WB[Web Browser]
        SA[System APIs]
        GA[Gemini API]
    end
    
    %% Main flow
    U -->|"Cherry"| WW
    WW --> VI
    U -->|Voice| VI
    VI -->|Text| AI
    AI <--> MEM
    AI <--> GA
    AI --> AE
    AE --> VO
    AE --> DC
    AE --> GUI
    VO --> U
    GUI --> U
    
    %% Vision and control
    VS --> AI
    DC --> VS
    DC --> FS
    DC --> WB
    DC --> SA
    VS --> SA
    
    %% System management
    ST --> VI
    ST --> VO
    ST --> VS
'''

# Create the diagram and save as both PNG and SVG
png_path, svg_path = create_mermaid_diagram(diagram_code, 'cherry_ai_architecture.png', 'cherry_ai_architecture.svg', width=1200, height=800)

print(f"Simplified architecture diagram saved to: {png_path} and {svg_path}")