from docx import Document


def create_doc(text):
    doc = Document()

    doc.add_paragraph(text)

    doc.save(f'нейронка.docx')
