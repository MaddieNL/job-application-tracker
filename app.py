
from flask import Flask, render_template, request, redirect
from database import get_db
import json

app = Flask(__name__, template_folder='templates')






def read_requirements():
    requirements_text = request.form.get('requirements', '').strip()

    if not requirements_text:
        return []

    try:
        return json.loads(requirements_text)
    except json.JSONDecodeError:
        return None



@app.route('/')
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS count FROM applications')
    applications = cursor.fetchone()

    cursor.execute('SELECT COUNT(*) AS count FROM companies')
    companies = cursor.fetchone()

    cursor.execute('SELECT COUNT(*) AS count FROM jobs')
    jobs = cursor.fetchone()

    cursor.execute('SELECT COUNT(*) AS count FROM contacts')
    contacts = cursor.fetchone()

    cursor.close()
    conn.close()

    stats = {
        'applications': applications['count'],
        'companies': companies['count'],
        'jobs': jobs['count'],
        'contacts': contacts['count']
    }

    return render_template('dashboard.html', stats=stats)


@app.route('/companies')
def companies():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM companies')
    company_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'companies.html',
        companies=company_list
    )



@app.route('/companies/add', methods=['POST'])
def add_company():
    company_name = request.form['company_name']
    industry = request.form.get('industry', '')
    website = request.form.get('website', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    notes = request.form.get('notes', '')

    conn = get_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO companies
        (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        company_name, industry, website,
        city, state, notes
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/companies')


@app.route('/companies/update/<int:company_id>', methods=['POST'])
def update_company(company_id):
    company_name = request.form['company_name']
    industry = request.form.get('industry', '')
    website = request.form.get('website', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    notes = request.form.get('notes', '')

    conn = get_db()
    cursor = conn.cursor()

    query = """
        UPDATE companies
        SET company_name = %s,
            industry = %s,
            website = %s,
            city = %s,
            state = %s,
            notes = %s
        WHERE company_id = %s
    """

    values = (
        company_name, industry, website,
        city, state, notes, company_id
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/companies')



@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM companies WHERE company_id = %s',
        (company_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/companies')




@app.route('/jobs')
def jobs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM companies')
    company_list = cursor.fetchall()

    cursor.execute("""
        SELECT jobs.*, companies.company_name
        FROM jobs
        JOIN companies
        ON jobs.company_id = companies.company_id
    """)

    job_list = cursor.fetchall()

   
    for job in job_list:
        requirements = job['requirements']

        if isinstance(requirements, str):
            try:
                requirements = json.loads(requirements)
            except json.JSONDecodeError:
                requirements = []

        job['requirements_text'] = json.dumps(requirements)

    cursor.close()
    conn.close()

    return render_template(
        'jobs.html',
        jobs=job_list,
        companies=company_list
    )




@app.route('/jobs/add', methods=['POST'])
def add_job():
    company_id = request.form['company_id']
    job_title = request.form['job_title']
    job_type = request.form['job_type']

    salary_min = request.form.get('salary_min') or None
    salary_max = request.form.get('salary_max') or None

    job_url = request.form.get('job_url', '')
    date_posted = request.form.get('date_posted') or None

    requirements = read_requirements()

    if requirements is None:
        return 'Invalid JSON in requirements. Please try again.', 400

    conn = get_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO jobs
        (company_id, job_title, job_type, salary_min,
         salary_max, job_url, date_posted, requirements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        company_id,
        job_title,
        job_type,
        salary_min,
        salary_max,
        job_url,
        date_posted,
        json.dumps(requirements)
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/jobs')




@app.route('/jobs/update/<int:job_id>', methods=['POST'])
def update_job(job_id):
    company_id = request.form['company_id']
    job_title = request.form['job_title']
    job_type = request.form['job_type']

    salary_min = request.form.get('salary_min') or None
    salary_max = request.form.get('salary_max') or None

    job_url = request.form.get('job_url', '')
    date_posted = request.form.get('date_posted') or None

    requirements = read_requirements()

    if requirements is None:
        return 'Invalid JSON in requirements. Please try again.', 400

    conn = get_db()
    cursor = conn.cursor()

    query = """
        UPDATE jobs
        SET company_id = %s,
            job_title = %s,
            job_type = %s,
            salary_min = %s,
            salary_max = %s,
            job_url = %s,
            date_posted = %s,
            requirements = %s
        WHERE job_id = %s
    """

    values = (
        company_id,
        job_title,
        job_type,
        salary_min,
        salary_max,
        job_url,
        date_posted,
        json.dumps(requirements),
        job_id
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/jobs')




@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM jobs WHERE job_id = %s',
        (job_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/jobs')




@app.route('/applications')
def applications():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

   
    cursor.execute("""
        SELECT jobs.job_id, jobs.job_title, companies.company_name
        FROM jobs
        JOIN companies
        ON jobs.company_id = companies.company_id
    """)
    job_list = cursor.fetchall()

    
    cursor.execute("""
        SELECT applications.*, jobs.job_title, companies.company_name
        FROM applications
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_id
    """)
    application_list = cursor.fetchall()

    
    for application in application_list:
        interview_data = application['interview_data']

        if isinstance(interview_data, str):
            try:
                interview_data = json.loads(interview_data)
            except json.JSONDecodeError:
                interview_data = {}

        application['interview_data_text'] = (
            json.dumps(interview_data) if interview_data is not None else ''
        )

    cursor.close()
    conn.close()

    return render_template(
        'applications.html',
        applications=application_list,
        jobs=job_list
    )



@app.route('/applications/add', methods=['POST'])
def add_application():
    job_id = request.form['job_id']
    application_date = request.form['application_date']
    status = request.form['status']
    resume_version = request.form.get('resume_version', '')
    cover_letter_sent = 1 if request.form.get('cover_letter_sent') else 0

    interview_text = request.form.get('interview_data', '').strip()

    if interview_text:
        try:
            interview_data = json.loads(interview_text)
        except json.JSONDecodeError:
            return 'Invalid JSON in interview data.', 400
        interview_data = json.dumps(interview_data)
    else:
        interview_data = None

    conn = get_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO applications
        (job_id, application_date, status, resume_version,
         cover_letter_sent, interview_data)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        job_id, application_date, status, resume_version,
        cover_letter_sent, interview_data
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/applications')




@app.route('/applications/update/<int:application_id>', methods=['POST'])
def update_application(application_id):
    job_id = request.form['job_id']
    application_date = request.form['application_date']
    status = request.form['status']
    resume_version = request.form.get('resume_version', '')
    cover_letter_sent = 1 if request.form.get('cover_letter_sent') else 0

    interview_text = request.form.get('interview_data', '').strip()

    if interview_text:
        try:
            interview_data = json.loads(interview_text)
        except json.JSONDecodeError:
            return 'Invalid JSON in interview data.', 400
        interview_data = json.dumps(interview_data)
    else:
        interview_data = None

    conn = get_db()
    cursor = conn.cursor()

    query = """
        UPDATE applications
        SET job_id = %s,
            application_date = %s,
            status = %s,
            resume_version = %s,
            cover_letter_sent = %s,
            interview_data = %s
        WHERE application_id = %s
    """

    values = (
        job_id, application_date, status, resume_version,
        cover_letter_sent, interview_data, application_id
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/applications')




@app.route('/applications/delete/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM applications WHERE application_id = %s',
        (application_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/applications')





@app.route('/contacts')
def contacts():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT contacts.*, companies.company_name
        FROM contacts
        JOIN companies
        ON contacts.company_id = companies.company_id
        ORDER BY contacts.contact_id
    """)
    contact_list = cursor.fetchall()

    cursor.execute("SELECT * FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'contacts.html',
        contacts=contact_list,
        companies=companies
    )


@app.route('/contacts/add', methods=['POST'])
def add_contact():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contacts
        (company_id, contact_name, title, email, phone, linkedin_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        request.form['company_id'],
        request.form['contact_name'],
        request.form.get('title'),
        request.form.get('email'),
        request.form.get('phone'),
        request.form.get('linkedin_url'),
        request.form.get('notes')
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/contacts')



@app.route('/contacts/update/<int:contact_id>', methods=['POST'])
def update_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE contacts
        SET company_id = %s,
            contact_name = %s,
            title = %s,
            email = %s,
            phone = %s,
            linkedin_url = %s,
            notes = %s
        WHERE contact_id = %s
    """, (
        request.form['company_id'],
        request.form['contact_name'],
        request.form.get('title'),
        request.form.get('email'),
        request.form.get('phone'),
        request.form.get('linkedin_url'),
        request.form.get('notes'),
        contact_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/contacts')



@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM contacts WHERE contact_id = %s",
        (contact_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/contacts')



@app.route('/job-match', methods=['GET', 'POST'])
def job_match():

    matched_jobs = []
    user_skills = ""

    if request.method == 'POST':

        user_skills = request.form.get('skills', '')

        # Convert entered skills into a lowercase list
        user_skill_list = [
            skill.strip().lower()
            for skill in user_skills.split(',')
            if skill.strip()
        ]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT jobs.*, companies.company_name
            FROM jobs
            JOIN companies
            ON jobs.company_id = companies.company_id
        """)

        jobs = cursor.fetchall()

        cursor.close()
        conn.close()

        for job in jobs:

            requirements = job['requirements']

       
            if isinstance(requirements, str):
                try:
                    requirements = json.loads(requirements)
                except (ValueError, TypeError):
                    requirements = []

            if not isinstance(requirements, list) or not requirements:
                continue

            required_skills = [
                str(skill).strip()
                for skill in requirements
                if str(skill).strip()
            ]

            if not required_skills:
                continue

            matched_skills = [
                skill for skill in required_skills
                if skill.lower() in user_skill_list
            ]

            missing_skills = [
                skill for skill in required_skills
                if skill.lower() not in user_skill_list
            ]

            match_percentage = (
                len(matched_skills) / len(required_skills)
            ) * 100

            job['matched_skills'] = matched_skills
            job['missing_skills'] = missing_skills
            job['match_percentage'] = round(match_percentage, 1)

            matched_jobs.append(job)

       
        matched_jobs.sort(
            key=lambda job: job['match_percentage'],
            reverse=True
        )

    return render_template(
        'job_match.html',
        matched_jobs=matched_jobs,
        user_skills=user_skills
    )






if __name__ == '__main__':
    app.run(debug=True)
