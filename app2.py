from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index2.html')

@app.route('/generate_diff', methods=['POST'])
def generate_diff():
    # Get the form data
    branch1 = request.form.get('branch1Dropdown')
    branch2 = request.form.get('branch2Dropdown')
    dropdown1 = request.form.get('dropdown1')
    dropdown2 = request.form.get('dropdown2')
    # files_ready = False

    # Path to the static directory
    static_folder = app.static_folder

    # Logic to generate new sets of HTML files based on the selections
    if branch1 == 'a' and branch2 == 'b' and dropdown1 == 'x' and dropdown2 == 'y':
        # files_ready = True
        # Load the content of the HTML files from static directory
        with open(os.path.join(static_folder, 'diff/line.html'), 'r') as file:
            line_html = file.read()
        with open(os.path.join(static_folder, 'diff/no_line.html'), 'r') as file:
            no_line_html = file.read()
        with open(os.path.join(static_folder, 'diff/side_by_side.html'), 'r') as file:
            side_by_side_html = file.read()
    else:
        line_html, no_line_html, side_by_side_html = '', '', ''

    # Render the template with the form data and the HTML content
    return render_template('index2.html', 
                           branch1=branch1, 
                           branch2=branch2, 
                           dropdown1=dropdown1, 
                           dropdown2=dropdown2, 
                           line_html=line_html, 
                           no_line_html=no_line_html, 
                           side_by_side_html=side_by_side_html)

if __name__ == '__main__':
    app.run(debug=True)
