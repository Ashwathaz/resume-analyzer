from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_resume(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 50, "John Doe")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 70, "Software Engineer")
    c.drawString(100, height - 85, "john.doe@email.com | 123-456-7890")
    c.drawString(100, height - 100, "github.com/johndoe | linkedin.com/in/johndoe")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 130, "Summary")
    c.setFont("Helvetica", 11)
    c.drawString(100, height - 145, "Experienced software engineer with a focus on Python and Streamlit development.")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 175, "Skills")
    c.setFont("Helvetica", 11)
    c.drawString(100, height - 190, "Python, SQL, JavaScript, React, Docker, AWS, Git, NLP")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 220, "Experience")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 235, "Senior Developer @ Tech Corp (2020-Present)")
    c.setFont("Helvetica", 11)
    c.drawString(100, height - 250, "- Led development of AI-powered analysis tools.")
    c.drawString(100, height - 265, "- Optimized database queries using PostgreSQL.")
    
    c.save()

if __name__ == "__main__":
    create_test_resume("test_resume.pdf")
    print("Created test_resume.pdf")
