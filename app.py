# Improved Restaurant Management System

This version of the Restaurant Management System includes capabilities to export data in multiple formats: CSV, Excel, JSON, XML, PDF, PNG, JPG, JPEG.

## Features
- **CSV Export**: Easily export restaurant data to CSV files.
- **Excel Export**: Generate Excel spreadsheets with restaurant data.
- **JSON Export**: Export restaurant records in JSON format for APIs.
- **XML Export**: Supports XML data export for compatibility with other systems.
- **PDF Export**: Allows exporting reports in PDF format, suitable for printing.
- **Image Export**: Enables the export of images related to the restaurant in PNG, JPG, and JPEG formats.

## Installation
Ensure you have the necessary packages installed:
```bash
pip install pandas openpyxl fpdf
```

## Usage
Use the following functions to export your data:
- `export_to_csv(data)` - Exports data to a CSV file.
- `export_to_excel(data)` - Exports data to an Excel file.
- `export_to_json(data)` - Exports data as JSON.
- `export_to_xml(data)` - Exports data as XML.
- `export_to_pdf(data)` - Exports data as a PDF.
- `export_image(image_data, format)` - Exports image in the specified format (PNG, JPG, JPEG).
```python
# Example Usage
if __name__ == '__main__':
    restaurant_data = fetch_data()
    export_to_csv(restaurant_data)
    export_to_excel(restaurant_data)  
    export_image(restaurant_logo, 'PNG')
```
