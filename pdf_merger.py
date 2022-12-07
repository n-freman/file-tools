import os

from pdfrw import PdfReader, PdfWriter


def get_all_pdf_files():
    files = os.listdir()
    files = [
        file for file in files if file.endswith('.pdf')
    ]
    files.sort()
    return files


def merge(inputs):
    writer = PdfWriter()
    for inpfn in inputs:
        writer.addpages(PdfReader(inpfn).pages)
    writer.write('output.pdf')
