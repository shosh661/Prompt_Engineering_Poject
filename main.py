import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import gradio as ui

# טעינת משתני הסביבה מקובץ .env
load_dotenv()

# אתחול הלקוח של Gemini באמצעות ה-SDK החדש
# ה-Client מזהה אוטומטית את משתנה הסביבה GEMINI_API_KEY
client = genai.Client()

SYSTEM_INSTRUCTION = """
You are an expert CLI agent. Your job is to translate natural language user requests into precise Windows Command Prompt (CMD) commands.
Guidelines:
1. Return ONLY the raw command that can be directly executed in the terminal.
2. Do NOT wrap the command in markdown code blocks (like ```bash).
3. Do NOT provide explanations, warnings, or intro/outro text.
4. If a request requires specific parameters (like a folder name), use the ones provided by the user or common defaults.
5. IMPORTANT: The commands must be formatted for direct execution in an interactive CMD terminal window, NOT for a batch script.
"""
#הגרסה הראשונה של הפרומפט הייתה ללא סעיף 5

def generate_cli_command(user_prompt: str) -> str:
    if not user_prompt.strip():
        return "בבקשה הזן הוראה כלשהי."
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,
            )
        )
        return response.text.strip()
        
    except Exception as e:
        return f"שגיאה בפנייה ל-API: {str(e)}"

# --- בניית ממשק המשתמש עם Gradio ---

# תיקון אזהרה: הסרנו את theme מכאן, השארנו רק את ה-title
with ui.Blocks(title="CLI Agent Launcher") as demo:
    ui.Markdown(
        """
        # 💻 NLP to CLI Agent
        הזן הוראה בשפה טבעית (עברית או אנגלית), וקבל את פקודת הטרמינל המתאימה להרצה ב-Windows.
        """
    )
    
    with ui.Row():
        with ui.Column():
            text_input = ui.Textbox(
                label="מה ברצונך לעשות?", 
                placeholder="למשל: איזה תהליכים רצים כרגע במערכת",
                lines=3
            )
            submit_btn = ui.Button("המר לפקודה ✨", variant="primary")
            
        with ui.Column():
            # תיקון השגיאה: שימוש ב-ui.Code במקום ב-ui.Textbox. 
            # הוא מגיע עם כפתור העתקה (Copy) מובנה ומציג פקודות בצורה ברורה.
            text_output = ui.Code(
                label="פקודת ה-CLI שנוצרה",
                language="python",
                interactive=False
            )
            
    submit_btn.click(fn=generate_cli_command, inputs=text_input, outputs=text_output)
    text_input.submit(fn=generate_cli_command, inputs=text_input, outputs=text_output)

    ui.Examples(
        examples=[
            ["מה כתובת ה-IP של המחשב שלי"],
            ["אני רוצה למחוק את כל הקבצים עם סיומת .tmp בתיקייה downloads"],
            ["לסדר את רשימת הקבצים לפי גודל מהגדול לקטן"],
            ["איזה תהליכים רצים כרגע במערכת"]
        ],
        inputs=text_input
    )

# הרצת השרת
if __name__ == "__main__":
    # תיקון אזהרה: העברנו את ה-theme לכאן (לתוך ה-launch) כפי שנדרש ב-Gradio 6
    demo.launch(theme=ui.themes.Soft(), share=False)