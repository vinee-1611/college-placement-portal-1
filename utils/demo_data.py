"""
demo_data.py

Reference companies and job openings used to populate the "Browse Jobs" page
on first run. Consumed by the ``_seed_demo_jobs()`` hook in app.py.
"""


DEMO_COMPANIES = [
    {
        "name": "Tata Consultancy Services",
        "industry": "Information Technology",
        "location": "Chennai",
        "website": "https://www.tcs.com",
        "email": "campus@tcs.com",
        "description": "Global IT services and consulting company delivering technology "
                       "solutions to enterprises across 55 countries.",
        "recruiter": {
            "name": "Meenakshi Iyer",
            "email": "tcs.recruiter@demo.edu",
            "designation": "Talent Acquisition Lead",
            "experience": "5-10 years",
        },
        "jobs": [
            {
                "title": "Software Engineer",
                "description": "Build and maintain large-scale Java and Python applications "
                               "for global banking and retail clients. Full-stack role with "
                               "on-the-job training and internal mobility.",
                "skills": "Java, Python, SQL, REST APIs",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 25, "package": 3.6,
                "employment_type": "Full-time",
                "days_to_deadline": 45,
            },
            {
                "title": "Systems Engineer",
                "description": "Support and troubleshoot infrastructure, network services and "
                               "cloud deployments for enterprise customers.",
                "skills": "Linux, Networking, Shell, AWS",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 10, "package": 3.6,
                "employment_type": "Full-time",
                "days_to_deadline": 45,
            },
        ],
    },
    {
        "name": "Infosys",
        "industry": "Information Technology",
        "location": "Mysuru",
        "website": "https://www.infosys.com",
        "email": "campus@infosys.com",
        "description": "Next-generation digital services and consulting company listed on "
                       "the NYSE, serving clients in 58 countries.",
        "recruiter": {
            "name": "Sandeep Nair",
            "email": "infosys.recruiter@demo.edu",
            "designation": "Senior Recruiter",
            "experience": "5-10 years",
        },
        "jobs": [
            {
                "title": "Software Developer",
                "description": "Develop web and mobile application features using modern "
                               "frameworks, working in an agile sprint-based environment.",
                "skills": "Java, Angular, React, SQL",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 20, "package": 3.8,
                "employment_type": "Full-time",
                "days_to_deadline": 40,
            },
            {
                "title": "System Engineer Trainee",
                "description": "Entry-level engineering role for graduates who want to build "
                               "a career in enterprise software delivery.",
                "skills": "Java, Communication, Problem Solving",
                "min_cgpa": 5.5, "max_backlogs": 3,
                "vacancies": 15, "package": 3.6,
                "employment_type": "Full-time",
                "days_to_deadline": 40,
            },
        ],
    },
    {
        "name": "Amazon",
        "industry": "E-Commerce & Cloud",
        "location": "Hyderabad",
        "website": "https://www.amazon.jobs",
        "email": "campus@amazon.in",
        "description": "Global e-commerce and cloud computing company operating the world's "
                       "largest AWS platform.",
        "recruiter": {
            "name": "Priya Raghavan",
            "email": "amazon.recruiter@demo.edu",
            "designation": "University Recruiting Manager",
            "experience": "5-10 years",
        },
        "jobs": [
            {
                "title": "Software Development Engineer",
                "description": "Design and build large-scale distributed systems that serve "
                               "millions of customers. Strong problem solving and data "
                               "structures foundation expected.",
                "skills": "C++, Java, Data Structures, Algorithms, OSD",
                "min_cgpa": 7.5, "max_backlogs": 1,
                "vacancies": 12, "package": 5.0,
                "employment_type": "Full-time",
                "days_to_deadline": 30,
            },
            {
                "title": "Data Analyst",
                "description": "Turn raw business data into dashboards, forecasts and "
                               "decision support for marketplace and operations teams.",
                "skills": "SQL, Python, Excel, Power BI",
                "min_cgpa": 7.0, "max_backlogs": 1,
                "vacancies": 6, "package": 4.8,
                "employment_type": "Full-time",
                "days_to_deadline": 30,
            },
        ],
    },
    {
        "name": "Accenture",
        "industry": "IT Services & Consulting",
        "location": "Bengaluru",
        "website": "https://www.accenture.com",
        "email": "campus@accenture.com",
        "description": "Professional services company providing strategy, consulting, "
                       "technology and operations services worldwide.",
        "recruiter": {
            "name": "Karthik Subramanian",
            "email": "accenture.recruiter@demo.edu",
            "designation": "Campus Recruiter",
            "experience": "2-5 years",
        },
        "jobs": [
            {
                "title": "Associate Software Engineer",
                "description": "Work with client delivery teams to implement, test and "
                               "support business applications across technology stacks.",
                "skills": "Java, .NET, SQL, SAP",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 30, "package": 4.5,
                "employment_type": "Full-time",
                "days_to_deadline": 35,
            },
            {
                "title": "Software Engineering Intern",
                "description": "Six-month internship on live client projects. Selected interns "
                               "are offered a pre-placement offer at the end of the term.",
                "skills": "JavaScript, SQL, Git",
                "min_cgpa": 6.0, "max_backlogs": 0,
                "vacancies": 20, "package": 3.5,
                "employment_type": "Internship",
                "days_to_deadline": 25,
            },
        ],
    },
    {
        "name": "Deloitte",
        "industry": "Consulting",
        "location": "Hyderabad",
        "website": "https://www.deloitte.com",
        "email": "campus@deloitte.com",
        "description": "One of the Big Four professional services firms offering audit, "
                       "consulting, tax and financial advisory services.",
        "recruiter": {
            "name": "Anjali Deshpande",
            "email": "deloitte.recruiter@demo.edu",
            "designation": "Talent Acquisition Specialist",
            "experience": "2-5 years",
        },
        "jobs": [
            {
                "title": "Analyst - Technology",
                "description": "Join technology consulting engagements and help clients "
                               "modernise their systems, data platforms and processes.",
                "skills": "SQL, Python, SAP, Excel",
                "min_cgpa": 7.0, "max_backlogs": 1,
                "vacancies": 10, "package": 4.6,
                "employment_type": "Full-time",
                "days_to_deadline": 28,
            },
            {
                "title": "Business Analyst Intern",
                "description": "Support requirement gathering, documentation and reporting "
                               "on consulting engagements while learning the domain.",
                "skills": "Excel, SQL, Communication",
                "min_cgpa": 6.5, "max_backlogs": 1,
                "vacancies": 8, "package": 3.5,
                "employment_type": "Internship",
                "days_to_deadline": 28,
            },
        ],
    },
    {
        "name": "HDFC Bank",
        "industry": "Banking & Financial Services",
        "location": "Mumbai",
        "website": "https://www.hdfcbank.com",
        "email": "campus@hdfcbank.com",
        "description": "One of India's largest private sector banks offering banking and "
                       "financial services to over 5 crore customers.",
        "recruiter": {
            "name": "Rohit Malhotra",
            "email": "hdfc.recruiter@demo.edu",
            "designation": "Assistant Vice President - Hiring",
            "experience": "10+ years",
        },
        "jobs": [
            {
                "title": "Junior Officer",
                "description": "Rotational role across retail banking, credit operations and "
                               "business analytics with structured certification tracks.",
                "skills": "Communication, Excel, Banking Operations",
                "min_cgpa": 6.5, "max_backlogs": 1,
                "vacancies": 25, "package": 4.5,
                "employment_type": "Full-time",
                "days_to_deadline": 50,
            },
        ],
    },
    {
        "name": "Zoho Corporation",
        "industry": "Software Products",
        "location": "Chennai",
        "website": "https://www.zoho.com",
        "email": "jobs@zoho.com",
        "description": "Independent software maker building productivity and business "
                       "applications for customers worldwide.",
        "recruiter": {
            "name": "Lakshmi Venkatesh",
            "email": "zoho.recruiter@demo.edu",
            "designation": "Technical Recruiter",
            "experience": "2-5 years",
        },
        "jobs": [
            {
                "title": "Software Engineer",
                "description": "Work on product engineering for a SaaS platform used by "
                               "small and medium businesses in 90+ countries.",
                "skills": "Java, Python, MySQL, APIs",
                "min_cgpa": 7.0, "max_backlogs": 0,
                "vacancies": 8, "package": 4.8,
                "employment_type": "Full-time",
                "days_to_deadline": 33,
            },
            {
                "title": "Software Engineering Intern",
                "description": "Work alongside the product team on real features. Preference "
                               "given to candidates who can start immediately after joining.",
                "skills": "Java, HTML, CSS",
                "min_cgpa": 6.5, "max_backlogs": 0,
                "vacancies": 10, "package": 3.4,
                "employment_type": "Internship",
                "days_to_deadline": 20,
            },
        ],
    },
    {
        "name": "Bosch Rexroth",
        "industry": "Automotive & Industrial Technology",
        "location": "Bengaluru",
        "website": "https://www.boschrexroth.com",
        "email": "campus@boschrexroth.com",
        "description": "Global supplier of industrial automation and drive technology "
                       "solutions, with a large engineering centre in Bengaluru.",
        "recruiter": {
            "name": "Farhan Ali",
            "email": "bosch.recruiter@demo.edu",
            "designation": "HR Business Partner",
            "experience": "5-10 years",
        },
        "jobs": [
            {
                "title": "Graduate Engineer Trainee",
                "description": "Engineering graduate role in design, development and testing "
                               "of industrial automation products and controllers.",
                "skills": "C, Embedded Systems, MATLAB",
                "min_cgpa": 7.0, "max_backlogs": 1,
                "vacancies": 14, "package": 5.0,
                "employment_type": "Full-time",
                "days_to_deadline": 38,
            },
            {
                "title": "Embedded Systems Intern",
                "description": "Assist the firmware team with board bring-up, testing and "
                               "documentation for embedded control units.",
                "skills": "C, RTOS, Debugging",
                "min_cgpa": 6.5, "max_backlogs": 0,
                "vacancies": 6, "package": 3.5,
                "employment_type": "Internship",
                "days_to_deadline": 22,
            },
        ],
    },
    {
        "name": "Cognizant",
        "industry": "Information Technology",
        "location": "Kochi",
        "website": "https://www.cognizant.com",
        "email": "campus@cognizant.com",
        "description": "World-class technology services company serving healthcare, banking "
                       "and manufacturing clients across six continents.",
        "recruiter": {
            "name": "Deepa Menon",
            "email": "cognizant.recruiter@demo.edu",
            "designation": "Recruitment Lead",
            "experience": "5-10 years",
        },
        "jobs": [
            {
                "title": "Software Engineer",
                "description": "Implement and maintain software solutions for healthcare and "
                               "financial services customers using Java and React.",
                "skills": "Java, React, SQL, Microservices",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 22, "package": 4.2,
                "employment_type": "Full-time",
                "days_to_deadline": 42,
            },
            {
                "title": "GenC Developer",
                "description": "Graduate entry programme covering Java, web technologies and "
                               "database fundamentals with certification support.",
                "skills": "Java, HTML, SQL",
                "min_cgpa": 5.5, "max_backlogs": 3,
                "vacancies": 30, "package": 4.0,
                "employment_type": "Full-time",
                "days_to_deadline": 42,
            },
        ],
    },
    {
        "name": "Capgemini",
        "industry": "IT Services & Consulting",
        "location": "Pune",
        "website": "https://www.capgemini.com",
        "email": "campus@capgemini.com",
        "description": "Global business and technology transformation partner helping "
                       "organisations move to a more sustainable digital model.",
        "recruiter": {
            "name": "Nikhil Joshi",
            "email": "capgemini.recruiter@demo.edu",
            "designation": "Talent Acquisition Manager",
            "experience": "5-10 years",
        },
        "jobs": [
            {
                "title": "Software Engineer",
                "description": "Full-stack development on digital transformation projects "
                               "for European and North American clients.",
                "skills": "Java, React, Node.js, SQL",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 18, "package": 4.6,
                "employment_type": "Full-time",
                "days_to_deadline": 36,
            },
            {
                "title": "Analyst",
                "description": "Business and technology analyst role supporting digital "
                               "product teams on requirement analysis and delivery.",
                "skills": "SQL, Excel, Communication",
                "min_cgpa": 6.0, "max_backlogs": 2,
                "vacancies": 12, "package": 4.2,
                "employment_type": "Full-time",
                "days_to_deadline": 36,
            },
        ],
    },
]
