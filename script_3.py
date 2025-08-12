# Create requirements.txt file
requirements_content = '''
streamlit==1.28.1
pandas==2.0.3
numpy==1.24.3
plotly==5.17.0
requests==2.31.0
selenium==4.15.2
beautifulsoup4==4.12.2
openpyxl==3.1.2
python-dateutil==2.8.2
'''

with open('requirements.txt', 'w') as f:
    f.write(requirements_content.strip())

print("Created requirements.txt with all necessary dependencies")
print("\nDependencies included:")
for line in requirements_content.strip().split('\n'):
    if line.strip():
        print(f"✅ {line.strip()}")