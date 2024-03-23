from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import plotly.express as px
import plotly.io as pio
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ad_reports.db'
db = SQLAlchemy(app)

class AdReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(100), nullable=False)
    adspend = db.Column(db.Float, nullable=False)
    cpl = db.Column(db.Float, nullable=False)
    leads = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

# Ensure the database tables are created within the application context
with app.app_context():
    db.create_all()

# Set the number of items to display per page
PER_PAGE = 5

@app.route('/')
def index():
    # Get the page from the query parameters, default to 1
    page = int(request.args.get('page', 1))

    # Calculate the start and end indices for pagination
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE

    # Query for reports for the current page
    reports = AdReport.query.all()[start_idx:end_idx]

    # Calculate the total number of pages
    total_pages = len(AdReport.query.all()) // PER_PAGE + 1

    return render_template('index.html', reports=reports, page=page, total_pages=total_pages)

@app.route('/form')
def form():
    return render_template('form.html')

# Import Plotly for graph generation
import plotly.express as px
import plotly.io as pio
import os

# ...

@app.route('/process_data', methods=['POST'])
def process_data():
    clinic_name = request.form.get('clinic_name', '')
    adspend = float(request.form.get('adspend', '0').replace(',', ''))
    cpl = float(request.form.get('cpl', '0').replace(',', ''))

    # Calculate the number of leads
    leads = int(adspend / cpl)

    date_str = request.form.get('date', '')
    date = datetime.strptime(date_str, "%d-%m-%Y").date()

    report = AdReport(clinic_name=clinic_name, adspend=adspend, cpl=cpl, leads=leads, date=date)
    db.session.add(report)
    db.session.commit()

    # Create a bar graph for leads
    fig = px.bar(
        x=['Leads'],
        y=[leads],
        labels={'x': 'Metrics', 'y': 'Values'},
        title=f'Ad Report for {clinic_name}',
    )

    # Add text annotations for amount spent per lead and total ad spend
    fig.update_layout(
        annotations=[
            dict(
                x=0.5,
                y=-0.2,
                showarrow=False,
                text=f'Amount Spent per Lead: €{cpl:.2f}',
                xref='paper',
                yref='paper',
            ),
            dict(
                x=0.5,
                y=-0.3,
                showarrow=False,
                text=f'Total Ad Spend: €{adspend:.2f}',
                xref='paper',
                yref='paper',
            ),
        ],
    )

    # Save the graph as an image (PNG) using Plotly's write_image
    graph_full_path = f'{clinic_name}_chart.png'


    return render_template('result.html', clinic_name=clinic_name, adspend=adspend, cpl=cpl, leads=leads, date=date, chart_title=f'Ad Report for {clinic_name}', chart_path=graph_full_path)

# ...



@app.route('/clinic_chart/<clinic_name>')
def clinic_chart(clinic_name):
    # Query data for the specific clinic
    clinic_data = AdReport.query.filter_by(clinic_name=clinic_name).all()

    # Extract relevant data for the chart
    dates = [report.date.strftime('%d-%m-%Y') for report in clinic_data]
    leads = [report.leads for report in clinic_data]
    cpl = [report.cpl for report in clinic_data]
    adspend = [report.adspend for report in clinic_data]

    # Create a bar graph for leads
    fig = px.bar(
        x=['Leads', 'Amount Spent per Lead', 'Total Ad Spend'],
        y=[sum(leads), sum(cpl), sum(adspend)],
        labels={'x': 'Metrics', 'y': 'Values'},
        title=f'Ad Report for {clinic_name}',
    )

    # Customize the layout to improve appearance
    fig.update_layout(
        annotations=[
            dict(
                x=0.5,
                y=-0.2,
                showarrow=False,
                text=f'Amount Spent per Lead: €{sum(cpl):.2f}',
                xref='paper',
                yref='paper',
            ),
            dict(
                x=0.5,
                y=-0.3,
                showarrow=False,
                text=f'Total Ad Spend: €{sum(adspend):.2f}',
                xref='paper',
                yref='paper',
            ),
            dict(
                x=0.5,
                y=-0.5,
                showarrow=False,
                text=f'Total Ad Spend: {", ".join(dates)}',  # Join dates into a string
                xref='paper',
                yref='paper',
            ),
        ],
        barmode='group',  # Display bars in groups
        margin=dict(t=50),  # Add margin at the top for better title appearance
    )

    # Save the graph as an image (PNG) using Plotly's write_image
    graph_full_path = f'{clinic_name}_chart.png'

    return render_template('clinic_chart.html', clinic_name=clinic_name, chart_path=graph_full_path)


@app.route('/edit_report/<int:id>', methods=['GET', 'POST'])
def edit_report(id):
    report = AdReport.query.get_or_404(id)

    if request.method == 'POST':
        report.clinic_name = request.form['clinic_name']
        report.adspend = float(request.form['adspend'].replace(',', ''))
        report.cpl = float(request.form['cpl'].replace(',', ''))
        report.date = datetime.strptime(request.form['date'], "%m-%d-%Y").date()

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_report.html', report=report)

@app.route('/delete_report/<int:id>', methods=['GET', 'POST'])
def delete_report(id):
    report = AdReport.query.get_or_404(id)

    if request.method == 'POST':
        db.session.delete(report)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('delete_report.html', report=report)

# Example Flask route for clinic_charts
# Example Flask route for clinic_charts
@app.route('/clinic_charts')
def clinic_charts():
    # Query all clinics
    all_clinics = AdReport.query.with_entities(AdReport.clinic_name).distinct().all()

    # Set the number of clinics to display per page
    clinics_per_page = 5

    # Calculate the total number of pages
    total_pages = (len(all_clinics) + clinics_per_page - 1) // clinics_per_page

    # Dummy data for demonstration (you should replace this with your actual query logic)
    # For demonstration purposes, I'm using a subset of clinics for the current page
    page = 1
    start_idx = (page - 1) * clinics_per_page
    end_idx = start_idx + clinics_per_page
    clinics = all_clinics[start_idx:end_idx]

    return render_template('clinic_charts.html', clinics=clinics, total_pages=total_pages)


if __name__ == '__main__':
    app.run(debug=True)
