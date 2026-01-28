import pikepdf

pdf = pikepdf.new()
page = pdf.add_blank_page()
print(dir(page))
