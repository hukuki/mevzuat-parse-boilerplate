from docx import Document
from utils import get_attribute
from segment import segment2idx, SegmentClassifier
import csv

def merge_runs(runs):
    runs = [run for run in runs] #TODO: check empty spaces
    merged_runs = []
    current_run = runs[0]
    for run in runs[1:]:
        if (get_attribute(run, 'italic') == get_attribute(current_run, 'italic')and \
            get_attribute(run, 'bold') == get_attribute(current_run, 'bold') and \
            get_attribute(run, 'alignment') == get_attribute(current_run, 'alignment')) or \
                run.text.isspace():
            current_run.text += run.text
            current_run.footnotes.extend(run.footnotes)
        else:
            merged_runs.append(current_run)
            current_run = run
    
    merged_runs.append(current_run)
    return merged_runs

file_path = "mevzuat-raw/tck.docx"
document = Document(file_path)
output_file = open("output.csv", "w", encoding="utf-8")
csv_writer = csv.writer(output_file)


flattened_runs = []
for paragraph in document.paragraphs:
    if not paragraph.text: #TODO: check empty spaces
        continue
    
    flattened_runs.extend(merge_runs(paragraph.runs))

classifier = SegmentClassifier(flattened_runs)


for parag_idx, paragraph in enumerate(document.paragraphs):
    if not paragraph.text: #TODO: check empty spaces
        continue

    runs = [run for run in paragraph.runs] #TODO: check empty spaces
    merged_runs = merge_runs(runs)
    
    for run_idx, run in enumerate(merged_runs):
        if not run.text: #TODO: check empty spaces
            continue
        
        segment_class = classifier.classify_next(run, parag_idx, run_idx)
        csv_writer.writerow([parag_idx, run_idx, run.text, segment_class.name])
    

    for run in runs:
        for footnote_ref in run.footnotes:
            for foot_parag in footnote_ref.footnote.paragraphs:
                if foot_parag.text:
                    csv_writer.writerow([parag_idx, run_idx, run.text, segment2idx["FOOTNOTE"]])

output_file.close()