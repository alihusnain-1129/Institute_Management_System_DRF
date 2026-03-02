# 🏫 Institute Management System (Multi-Tenant DRF + JWT)

A production-ready **Multi-Tenant Institute Management System** built with **Django REST Framework** implementing secure JWT authentication, strict data isolation, role-based access control, and scalable architecture.

This system allows multiple institutes to register and independently manage their own students, teachers, courses, exams, and results — with complete data isolation between institutes.

---

# 🚀 Core Features

## 🏢 Multi-Tenant Architecture
- Multiple institutes can register on the platform
- Strict data isolation between institutes
- Each institute can only access its own data
- No cross-institute data leakage

---

## 👑 Super Admin Approval System
- Institute registration request
- Super Admin approval required
- Approved institutes can access system features
- Centralized control and verification

---

## 🔐 JWT Authentication System

- Access Token (short-lived)
- Refresh Token (long-lived)
- Token blacklisting on logout
- Secure token expiration handling
- Protected API routes

Built using:
- Django REST Framework
- Simple JWT

---

## 🛡 Role-Based Access Control (RBAC)

Supported Roles:
- Super Admin
- Institute Admin
- Teacher
- Student

### Permission Rules:
- Super Admin can approve institutes
- Institute Admin manages institute data
- Teachers manage only assigned courses
- Students have restricted access
- Unauthorized access returns proper HTTP errors

---

# 📚 Functional Modules

## 👨‍🎓 Student Management
- Create, Read, Update, Delete students
- Unique roll number per institute
- Institute-level data isolation
- Filtering and search support
- Proper validation & error handling

---

## 📖 Course Management
- Create and manage courses
- Unique course code per institute
- Assign teachers to courses
- Teachers can only manage their assigned courses
- Validation for duplicate course codes

---

## 📝 Exam Management
- Create exams per course
- Institute-specific exams
- Controlled access permissions

---

## 📊 Result Management
- Add results per student and exam
- Prevent duplicate result entries
- Proper validation checks
- Institute-level data protection

---

# 🔎 API Features

- Pagination
- Filtering
- Search functionality
- Proper HTTP status codes
- Standardized API responses
- Clean serializer validation
- Custom permission classes

---

# 🧪 Unit Testing

Comprehensive unit tests included for:

- Authentication
- JWT token validation
- Role-based permissions
- Multi-tenant data isolation
- Duplicate prevention logic
- Protected route access

Test coverage ensures system reliability and security.

---

# 🏗 Clean Project Architecture

Project follows modular structure with separate apps:

```
institute_management_system/
│
├── accounts/        # Authentication & roles
├── institutes/      # Institute registration & approval
├── students/        # Student management
├── courses/         # Course management
├── exams/           # Exam management
├── results/         # Result management
├── core/            # Shared utilities & permissions
└── config/          # Project settings
```

Each app is:
- Decoupled
- Maintainable
- Scalable
- Production-ready

---

# 🛠 Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite (development)
- PostgreSQL (production-ready support)
- Postman for API testing

---

# ⚙️ Installation Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/institute-management-system-drf.git
cd institute-management-system-drf
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

## 3️⃣ Activate Environment

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 5️⃣ Configure Environment Variables

Create `.env` file in root directory:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1
```

⚠️ Do NOT upload `.env` file to GitHub.

## 6️⃣ Apply Migrations

```bash
python manage.py migrate
```

## 7️⃣ Run Development Server

```bash
python manage.py runserver
```

---

# 🔒 Security Considerations

- Environment variables protected via `.env`
- `.gitignore` excludes sensitive files
- JWT expiration enforced
- Token blacklisting implemented
- Role-based permission enforcement
- Data isolation at queryset level
- Unique constraints per institute

---

# 📌 Example API Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| POST | /api/institutes/register/ | Register Institute |
| POST | /api/login/ | Login |
| POST | /api/token/refresh/ | Refresh Token |
| GET | /api/students/ | List Students |
| POST | /api/courses/ | Create Course |
| POST | /api/exams/ | Create Exam |
| POST | /api/results/ | Add Result |

---

# 🧠 Design Principles

- Separation of concerns
- DRY principles
- Secure by default
- Scalable architecture
- Clean permission handling
- Defensive validation logic

---

# 🚀 Future Improvements

- Deployment on AWS / Render
- API documentation with Swagger
- CI/CD integration
- Docker support
- Performance optimization
- Caching support
- Audit logging

---

# ⭐ Project Status

Actively developed as an advanced backend system demonstrating:

✔ Multi-tenant architecture  
✔ JWT authentication  
✔ Role-based access control  
✔ Clean scalable structure  
✔ Unit testing coverage  
✔ Production-level backend design  

---

If you found this project useful, feel free to ⭐ star the repository.
