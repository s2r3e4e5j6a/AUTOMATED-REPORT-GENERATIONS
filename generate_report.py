import csv
from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Sales Data Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'R')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_table(self, data, headers):
        self.set_font('Arial', 'B', 10)
        # Add headers
        for header in headers:
            self.cell(40, 10, header, 1, 0, 'C')
        self.ln()

        self.set_font('Arial', '', 10)
        # Add data rows
        for row in data:
            for item in row:
                self.cell(40, 10, str(item), 1, 0, 'L')
            self.ln()

def analyze_data(data):
    total_sales = 0
    sales_by_region = {}
    sales_by_product = {}

    for row in data:
        try:
            sales = float(row['Sales'])
            total_sales += sales

            region = row['Region']
            sales_by_region[region] = sales_by_region.get(region, 0) + sales

            product = row['Product']
            sales_by_product[product] = sales_by_product.get(product, 0) + sales
        except ValueError:
            print(f"Skipping row due to invalid sales value: {row}")
            continue
        except KeyError as e:
            print(f"Missing expected column in row: {e} - {row}")
            continue

    # Sort sales by region and product for better reporting
    sorted_sales_by_region = sorted(sales_by_region.items(), key=lambda item: item[1], reverse=True)
    sorted_sales_by_product = sorted(sales_by_product.items(), key=lambda item: item[1], reverse=True)

    return total_sales, sorted_sales_by_region, sorted_sales_by_product

def generate_pdf_report(data_file='sample_data.csv', output_pdf='sales_report.pdf'):
    # Read data from file
    data = []
    try:
        with open(data_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: Data file '{data_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading data file: {e}")
        return

    if not data:
        print("No data to process. Exiting.")
        return

    # Analyze data
    total_sales, sales_by_region, sales_by_product = analyze_data(data)

    # Generate PDF report
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Introduction
    pdf.chapter_title('Overview')
    pdf.chapter_body(
        f"This report provides an analysis of sales data sourced from '{data_file}'. "
        f"The total sales across all products and regions amount to ${total_sales:,.2f}."
    )

    # Sales by Region
    pdf.add_page()
    pdf.chapter_title('Sales by Region')
    region_data = [[region, f"${sales:,.2f}"] for region, sales in sales_by_region]
    pdf.add_table(region_data, ['Region', 'Total Sales'])

    # Sales by Product
    pdf.add_page()
    pdf.chapter_title('Sales by Product')
    product_data = [[product, f"${sales:,.2f}"] for product, sales in sales_by_product]
    pdf.add_table(product_data, ['Product', 'Total Sales'])

    # Raw Data Table (optional, for detailed view)
    pdf.add_page()
    pdf.chapter_title('Raw Data Sample')
    if data:
        # Get headers from the first row (assuming all rows have same keys)
        raw_headers = list(data[0].keys())
        raw_rows = [[row[header] for header in raw_headers] for row in data]
        pdf.add_table(raw_rows, raw_headers)
    else:
        pdf.chapter_body("No raw data available to display.")

    pdf.output(output_pdf)
    print(f"Report '{output_pdf}' generated successfully!")

if __name__ == '__main__':
    generate_pdf_report()