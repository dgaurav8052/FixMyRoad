# Fix My Road

## Project Overview
**Fix My Road** is a citizen-driven road maintenance platform designed to make reporting and resolving road-related issues seamless.  
Users can log complaints about potholes, damages, or other road problems, while authorities/administrators can track, manage, and resolve them efficiently.  

The platform ensures **transparency**, **community participation**, and **faster issue resolution** by bridging the gap between citizens and local authorities.  

---

## Features
- **User Complaint Submission** – Citizens can report road issues with details.  
- **Database Management** – All data is stored securely in **Supabase**.  
- **FastAPI Backend** – Provides REST APIs for user management, complaint handling, and updates.  
- **Admin Dashboard (Frontend)** – Helps authorities track, update, and resolve complaints.  
- **Authentication** – Secure login and role-based access using Supabase Auth.  

---

## Tech Stack
- **Backend:** FastAPI (Python)  
- **Database & Auth:** Supabase (PostgreSQL-based)  
- **Frontend:** HTML, CSS, JavaScript (can extend with React in future)  
- **Deployment Ready:** Can be hosted on Vercel/Netlify (Frontend) and Render/Heroku/DigitalOcean (Backend)  

---

##  Folder Structure
```
Fix-My-Road/
├─ Backend/
│  ├─ app/
│  │  ├─ main.py            
│  │  ├─ models.py          
│  │  ├─ crud.py            
│  │  ├─ db.py              
│  │  ├─ storage.py         
│  │  ├─ config.py          
│  │  └─ __init__.py
│  ├─ requirements.txt
│
├─ Frontend/
│  ├─ AboutUs.html
│  ├─ AdminAnalytics.html
│  ├─ AdminDashBoard.html
│  ├─ AdminLogin.html
│  ├─ AdminReports.html
│  ├─ Adminsettings.html
│  ├─ form.html
│  ├─ home.html
│  ├─ status.html
│  ├─ thankyou.html
│  ├─ form.js
│  ├─ home.js
│  └─ thankyou.js
│
└─ README.md
```

Team – Bit Coders

- Gaurav Dwivedi
- Mohd Faizan 
- Anshi
- Sharadveer Singh
- Divyanshu Yadav

