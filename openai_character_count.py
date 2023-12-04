import sys
import os
import docx
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import PyPDF2

# https://platform.openai.com/tokenizer

# Prices per 1K characters for each model
prices = {
    "Whisper": 0.006,
    "TTS": 0.015,
    "TTS HD": 0.030
}

def extract_text_and_count_characters(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension == ".pdf":
        return extract_text_and_count_characters_pdf(file_path)
    elif file_extension == ".txt":
        return extract_text_and_count_characters_text(file_path)
    elif file_extension == ".docx":
        return extract_text_and_count_characters_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_text_and_count_characters_pdf(pdf_filename):
    doc = fitz.open(pdf_filename)
    page_character_counts = []

    for page_number in range(doc.page_count):
        page = doc[page_number]
        text = page.get_text("text")  # Include spaces and new lines
        character_count = len(text)
        page_character_counts.append(character_count)

    doc.close()
    
    return page_character_counts

def extract_text_and_count_characters_text(txt_filename):
    with open(txt_filename, 'r', encoding='utf-8') as file:
        text = file.read()
        character_count = len(text)

    return [character_count]

def extract_text_and_count_characters_docx(docx_filename):
    doc = docx.Document(docx_filename)
    character_count = 0

    for paragraph in doc.paragraphs:
        text = paragraph.text
        character_count += len(text)

    return [character_count]

def calculate_cost(total_character_count, model):
    price_per_1k_characters = prices.get(model, 0)
    cost = (total_character_count * price_per_1k_characters) / 1000  # Calculate cost for total characters
    return cost

def main(file_path):
    page_character_counts = extract_text_and_count_characters(file_path)
    
    # Calculate the total character count
    total_character_count = sum(page_character_counts)
    
    # Calculate total costs for each model
    total_costs = {model: calculate_cost(total_character_count, model) for model in prices}
    
    print(f"Total Character Count: {total_character_count}")
    for model, cost in total_costs.items():
        print(f"Total {model} Price: ${cost:.2f}")

    # Create a PDF file to save the figures
    pdf_filename_output = "output.pdf"
    pdf_pages = PdfPages(pdf_filename_output)
    
    # Figure 1: Total Prices
    models = list(prices.keys())
    total_prices = list(total_costs.values())
    labels1 = [f"{model}\n{total_character_count} chars\n${price:.2f}" for model, price in zip(models, total_prices)]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    x = range(len(models))
    plt.figure(figsize=(8, 6))
    plt.bar(x, total_prices, color=colors)
    plt.ylabel("Total Price ($)")
    plt.title("Total Prices")
    plt.xticks(x, models, fontsize=8, ha='center', va='top')
    
    # Add numbers inside the bars with white color and adjusted placement
    for i, label in enumerate(labels1):
        plt.text(i, total_prices[i] * 0.95, label, ha='center', va='top', fontsize=8, color='white')
    
    pdf_pages.savefig()
    plt.close()
    
    # Figure 2: Cost per Page for TTS Model (Flipped)
    page_numbers = range(1, len(page_character_counts) + 1)
    
    model = "TTS"
    price = prices[model]
    
    costs = [calculate_cost(char_count, model) for char_count in page_character_counts]
    labels2 = [f"{char_count} chars\n${cost:.2f}" for char_count, cost in zip(page_character_counts, costs)]
    colors = ['#1f77b4'] * len(costs)
    plt.figure(figsize=(8, 10))
    plt.barh(page_numbers, costs, color=colors)
    plt.xlabel("Cost ($)")
    plt.ylabel("Page Number")
    plt.title(f"Cost per Page for {model} Model (Flipped)")
    
    # Add numbers inside the bars with white color and adjusted placement
    for i, label in enumerate(labels2):
        plt.text(costs[i] * 0.95, page_numbers[i], label, ha='right', va='center', fontsize=6, color='white')
    
    pdf_pages.savefig()
    plt.close()
    
    pdf_pages.close()
    
    print(f"Figures saved as {pdf_filename_output}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python character_count.py filename.pdf/txt/docx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path)
