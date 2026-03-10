# Saeko API - Collection Summary

## Overview

The Saeko API is a comprehensive REST API for educational institution management, covering student lifecycle, academics, finance, scheduling, and more. It contains **833 endpoints** organized across **32 top-level modules**.

- **Base URL**: `{{api-url}}` (environment variable)
- **Authentication**: OAuth2 password grant with Bearer token refresh
- **Response Format**: JSON (with PDF, XLSX, CSV export endpoints)
- **Collection Variables**: `ssl_cacx_pem`, `ssl_cacx_curp`

---

## Authentication

### Pre-Request Script Logic

The collection uses a shared pre-request script that runs before every request:

1. **Bearer Token**: Automatically sets `Authorization: Bearer <token>` header
2. **Token Override**: If `access-token-override` variable is set, uses that token directly
3. **Skip Conditions**: Skips auth injection if the request already has an `Authorization` header, or if auth type is `noauth` or `bearer`
4. **X-Saeko-Branch Header**: Automatically adds `X-Saeko-Branch` header from variable if available
5. **Query Parameter Encoding**: Automatically URL-encodes all enabled query parameters, resolving `{{variable}}` references first

### Required Environment Variables

| Variable | Purpose |
|---|---|
| `api-url` | Base API URL |
| `auth-url` | OAuth2 token endpoint |
| `client-id` | OAuth2 client ID |
| `email` | User email for password grant |
| `password` | User password |
| `scopes` | OAuth2 scopes |
| `access-token` | Current access token (auto-refreshed) |
| `access-token-override` | Optional hard-coded token |
| `X-Saeko-Branch` | Optional branch header |

---

## Modules

| Module | Requests | Description |
|---|---|---|
| /core | ~202 | Students, enrollments, groups, courses, terms, programs, subjects, professors, employees, schools, classrooms, contacts, relatives, documents |
| /accounting | ~130 | Billing, payments, invoices, payment plans, scholarships, bank transactions, deposit slips |
| /activity_stream | 6 | Feed activities, mobile devices, notifications |
| /admissions_v2 | 28 | Applicants, submissions, admission tests, enrollment |
| /certification | ~40 | Transcripts, degree certificates, IEMS setups, signees |
| /community | 19 | Publications, comments, bookmarks, apples, black lists |
| /configurations | ~50 | Grading configs, attendance, holidays, mailer, remark types, reenrollment setups, whatsapp templates, tutoring categories |
| /drive | 1 | Google token |
| /finerio | 5 | Finerio customer, accounts, transactions |
| /forms | 4 | Custom forms, submissions |
| /flap | 6 | Flap payment intents and payments |
| /grading | ~100 | Activities, grades, assessment plans, enrolled courses, grading requests, report cards, student remarks, letter marks |
| /importation | 7 | Data import by type/group |
| /integrations | 2 | Integration credits |
| /joomla | 1 | Joomla banners |
| /location | 6 | Countries, states, cities, suburbs |
| /lounge | 1 | Lounge items |
| /modular_courses | 41 | Modular courses, activities, enrollments, reservations, grades, reservation slots |
| /openpay | 3 | Openpay payment intents and payments |
| /pricing | 5 | Subscriptions, product subscriptions, subscription invoices |
| /professor_reviews | 21 | Professor reviews, categories, scores, term setup |
| /provisioning | ~20 | Users, permissions, admin roles, whatsapp users/credits, provisioning logs |
| /service | 5 | Async services (mexpress, openpay, sftp, sns, whatsapp) |
| /sep | 4 | SEP levels, schools |
| /scheduling | 37 | Lectures, attendance logs, absences, weekly lectures, gate access, visitor logs, employee logs |
| /scholarship | 10 | Scholarship types, service areas |
| /stats | 17 | Buckets, aggregation logs, student results, school reports, grade averages |
| /sofiaxt | 8 | Sofiaxt sync logs, token |
| /stripe | 7 | Stripe customer, payment intents, setup intents |
| /transfers | 20 | Transfers, transfer documents, equivalent subjects/programs, transfer credits |
| /tutorings | 13 | Tutorings, enrollment tutorings, professor stats |
| /workflow | 1 | Workflow events |

---

## /core

Students, enrollments, groups, courses, terms, programs, subjects, professors, employees, schools, classrooms, contacts, relatives, documents, and more.

| Method | Name | Path |
|---|---|---|
| GET | Administrators: list | /core/administrators?include_fields=user |
| GET | Administrator: show (me) | /core/administrator |
| GET | Administrator: show | /core/administrators/:id?include_fields=user |
| PUT | Administrator: update | /core/administrators/:id |
| GET | Colegios: list | /core/colegios/:id |
| GET | Contacts: list | /core/contacts |
| GET | Contacts: search | /core/contacts?search=her&filters=type=professor;school_id=2179,21 |
| PUT | Contact: update | /core/contact_types/:contact_type_id/contacts/:id |
| PUT | Contact: upload avatar | {{avatar_upload_url}} |
| PUT | ScannedSignature: update (by contact) | /core/contact_types/:contact_type_id/contacts/:contact_id/scanned_signature |
| DELETE | ScannedSignature: destroy (by contact) | /core/contact_types/:contact_type_id/contacts/:contact_id/scanned_signature |
| GET | Courses: list | /core/courses?filters=active |
| GET | Courses: list (by enrollment) | /core/enrollments/:enrollment_id/courses?filters=enrollable;associations_by_course_id=1335705&include_fields=subject_id |
| GET | Courses: list (by group) | /core/groups/:group_id/courses |
| GET | Courses: list (by professor) | /core/professors/:professor_id/courses?filters=active&fields=id,name,weekly_lectures |
| GET | Courses: list (by reenrollment) | /core/reenrollments/:reenrollment_id/courses?include_fields=weekly_lectures,professor_names,enrollable,subject_type,subject_id |
| GET | Courses: list (by assessment plan) | /core/assessment_plans/:assessment_plan_id/courses?filters=term_id={{term_id}} |
| GET | Courses: list (by terms) | /core/terms/:term_id/courses |
| GET | Courses: list (by_terms) csv | /core/terms/:term_id/courses.csv?filters=professor=assigned |
| GET | Courses: show | /core/courses/:id |
| GET | Courses: summary stats | /core/courses/:id/summary_stats |
| POST | Courses: create | /core/groups/:group_id/courses?include_fields=professor_id,subject_id |
| POST | Courses: create (multiple) | /core/groups/:group_id/courses?include_fields=professor_id,subject_id |
| PUT | Courses: update | /core/courses/:id |
| DELETE | Courses: destroy | /core/courses/:id |
| GET | Enrollments: list | /core/enrollments?include_fields=extended&include_fields=student |
| GET | Enrollments: list csv | /core/enrollments.csv?filters=school_id=2179;status=4&columns=distance_traveled,road_type,age,ad_campaign |
| GET | Enrollments: list (by school) | /core/schools/:school_id/enrollments?include_fields=student,program_name,group_name,school_name,group_shift,billing_plan_name,date,student_employees,cumulative_grading_stats,modular_enro... |
| GET | Enrollments: list (by term) | /core/terms/:term_id/enrollments |
| GET | Enrollments: list (by term) csv | /core/terms/:term_id/enrollments.csv?filters=active;scholarship(billing_plan_applied)&columns=school,program,group,grade_level,cumulative_score_avg,billing_plan_name,billing_stats,schola... |
| GET | Enrollments: list (by student) | /core/students/:student_id/enrollments?include_fields=extended |
| POST | Enrollments: create (multiple) | /core/terms/:term_id/enrollments |
| POST | Enrollments: create (by term) | /core/terms/:term_id/enrollments |
| PUT | Enrollments: update | /core/enrollments/:id?include_fields=student_tutors, student_employees |
| DELETE | Enrollments: destroy | /core/enrollments/:id |
| GET | Enrollments: show | /core/enrollments/:id?include_fields=student_tutors, student_employees, modular_enrollment |
| GET | Enrollments: show (PDF) | /core/enrollments/:id.pdf |
| GET | Enrollments: export_students_911 (by term) | /core/terms/:term_id/enrollments/export_students_911.csv?previous_term_id=35878&export_term=current |
| GET | Enrollments: export_graduates_911 (by term) | /core/terms/:term_id/enrollments/export_graduates_911.csv |
| GET | Enrollments: proof_of_completion (by group) | /core/groups/:group_id/proof_of_completion.pdf |
| GET | Enrollment: proof_of_completion | /core/enrollments/:enrollment_id/proof_of_completion.pdf |
| GET | Enrollment: acknowledgement_of_receipt (pdf) | /core/enrollments/:enrollment_id/acknowledgement_of_receipt.pdf |
| GET | Enrollment: academic_record (PDF) | /core/enrollments/:enrollment_id/academic_record.pdf?fecha=&persona=&puesto=&tipo=&description=&folio=&start_date=&end_date=&status= |
| GET | Enrollment: preenrollment_slip (PDF) | /core/enrollments/:enrollment_id/preenrollment_slip.pdf?folio&date_preenrollment&date_exam |
| GET | Enrollment: internship_certificate (PDF) | /core/enrollments/:enrollment_id/internship_certificate.pdf?date&folio&coordination_manager&signee_position_manager&signee&signee_position&institution&addressee&activity&program&date_sta... |
| GET | Enrollment: internship_completion_letter (PDF) | /core/enrollments/:enrollment_id/internship_completion_letter.pdf?date&folio&signee&signee_position&signee2&signee_position2&type&period&program |
| GET | Enrollments: professional_intership_cover_letter (PDF) | /core/enrollments/:enrollment_id/professional_internship_cover_letter.pdf?date=&end_date=&start_date=&folio&signee&signee_position&type&addressee&addressee_position&institution&place&sch... |
| GET | DocumentRequest: PDF (by_enrollment) | /core/enrollments/:enrollment_id/document_request.pdf?document_type&folio&fecha=08-05-2024&person&position&person2&position2 |
| GET | SocialServiceCompletion: PDF (by_enrollment) | /core/enrollments/:enrollment_id/social_service_completion.pdf?signatory&hours&company_name&signatory_position&start_date_service&end_date_service&folio&coordination_manager&signee_posit... |
| GET | LeaveDocumentationReceipt: PDF (by_enrollment) | /core/enrollments/:enrollment_id/leave_documentation_receipt.pdf?signee&signee_position |
| GET | justification_letter: PDF (by_enrollment) | /core/enrollments/:enrollment_id/justification_letter.pdf?date=&signee=&signee_position=&start_date=&end_date=&schedule=&reason=&comments=&folio= |
| GET | TemporaryLeave.pdf (by enrollmet) | /core/enrollments/:enrollment_id/temporary_leave.pdf |
| GET | Groups: list | /core/groups?include_fields=grade_level,professor,courses(professor_names,professor_id) |
| GET | Groups: list (by school) | /core/schools/:school_id/groups?filters=program_id=178;term_id=55976&include_fields=courses(professor_names,professor_id),grade_level&group_summary_stats=true |
| GET | Groups: list (by term) | /core/terms/:term_id/groups?course_summary_stats=true |
| GET | Groups: list (by program) | /core/programs/:program_id/groups?include_fields=courses,grade_level,courses |
| GET | Groups: show | /core/groups/:id |
| POST | Groups: create (by term) | /core/terms/:term_id/groups |
| POST | Groups: create multiple | /core/terms/:term_id/groups |
| PUT | Groups: update | /core/groups/:id |
| DELETE | Groups: destroy | /core/groups/:id |
| GET | Groups: export_groups (by term) | /core/terms/:term_id/groups/export_groups.csv?previous_term_id=35878&export_term=current |
| GET | Groups: student_documents(PDF) | /core/groups/:group_id/student_documents.pdf?is_equivalence=false&signee=&signee_position= |
| GET | IncrementalPool: list | /core/incremental_pools?filters=type=1;school_id={{school_id}}&include_fields=school_ids |
| GET | IncrementalPool: show | /core/incremental_pools/:id?include_fields=school_ids |
| POST | IncrementalPool: create | /core/incremental_pools |
| PUT | IncrementalPool: update | /core/incremental_pools/:id |
| DELETE | IncrementalPool: destroy | /core/incremental_pools/:id |
| GET | IdCard: PDF | /core/enrollments/:enrollment_id/id_card.pdf?vigencia=&escuela_id={{school_id}} |
| GET | IdCards: PDF (by group) | /core/groups/:group_id/id_cards.pdf |
| GET | Leaves: show | /core/enrollments/:enrollment_id/leave |
| POST | Leaves: create | /core/enrollments/:enrollment_id/leave |
| PUT | Leaves: update | /core/enrollments/:enrollment_id/leave |
| DELETE | Leaves: destroy | /core/enrollments/:enrollment_id/leave |
| GET | Leaves: export_students (by term) | /core/terms/:term_id/leaves/export_students.csv |
| GET | Periods: show | /core/periods/:id |
| POST | Periods: create | /core/terms/:term_id/periods |
| POST | Periods: create (multiple) | /core/terms/:term_id/periods |
| DELETE | Periods: destroy | /core/periods/:id |
| GET | Professors: list | /core/professors?include_fields=professors_report,employee,phones,last_sign_in_at&filters=active |
| GET | Professors: list (CSV) | /core/professors.csv?columns=emergency_contacts |
| GET | Professors: list (by school) | /core/schools/:school_id/professors |
| GET | Professors: list (by term) | /core/terms/:term_id/professors?include_fields=professors_report,employee,phones,last_sign_in_at |
| GET | Professors: show | /core/professors/:id?include_fields=addresses,details,user |
| GET | Professors: show (PDF) | /core/professors/:id |
| GET | Professors: export_professors (by term) | /core/terms/:term_id/professors/export_professors.csv |
| GET | Professor: show (me) | /core/professor?include_fields=employee,details |
| GET | Programs: list | /core/programs?include_fields=internal_code |
| GET | Programs: list (by school) | /core/schools/:school_id/programs?include_fields=total_subjects,school_ids |
| GET | Programs: list (by term) | /core/terms/:term_id/programs?include_fields=school_ids |
| GET | Programs: show | /core/programs/:id |
| POST | Programs: create | /core/programs?include_fields=mec_config, competencies |
| PUT | Programs: update | /core/programs/:id?include_fields=competencies |
| DELETE | Programs: destroy | /core/programs/:id |
| GET | Reenrollments: list (by term) | /core/terms/:term_id/reenrollments.csv?filters=grade_level=3 |
| GET | Reenrollments: show (by setup) | /core/reenrollments_setups/:reenrollments_setup_id/reenrollment?include_fields=current_page |
| GET | Reenrollment: show (by enrollment) | /core/enrollments/:enrollment_id/reenrollment?include_fields=submission_form_pages |
| POST | Reenrollments: create (by setup) | /core/reenrollments_setups/:reenrollments_setup_id/reenrollment |
| PUT | Reenrollments: update (by setup) | /core/reenrollments_setups/:reenrollments_setup_id/reenrollment |
| GET | Relatives: list (by term) | /core/terms/:term_id/relatives?include_fields=user |
| GET | Relatives: show | /core/relatives/:id?include_fields=addresses,phones,occupations,student_relatives |
| PUT | Relatives: update | /core/relatives/:id?include_fields=addresses,phones,occupations,student_relatives |
| DELETE | Relatives: delete | /core/relatives/:id |
| GET | Schools: list | /core/schools?include_fields=cct,phones,addresses,geographical_zone_id |
| GET | Schools: list (by colegio) | /core/colegios/:colegio_id/schools |
| GET | Schools: show | /core/schools/:id?include_fields=mec_config |
| POST | Schools: create | /core/schools/?include_fields=addresses,contacts |
| POST | Schools: create (multiple) WIP | /core/schools/?include_fields=addresses,contacts |
| PUT | Schools: update | /core/schools/:id?include_fields=addresses,contacts,mec_config,gate_access_config,global_invoice_settings |
| DELETE | Schools: destroy | /core/schools/:id |
| GET | SchoolDocuments: list | /core/school_documents |
| GET | SchoolDocuments: list (by school) | /core/schools/:school_id/school_documents |
| GET | SchoolDocuments: list (by colegio) | /core/school_documents/ |
| POST | SchoolDocuments: create | /core/school_documents |
| PUT | SchoolDocuments: update | /core/school_documents/:id |
| DELETE | SchoolDocuments: destroy | /core/school_documents/:id |
| GET | Documents: list (by school) | /core/schools/:school_id/school_documents |
| GET | Students: list | /core/students?include_fields=current_enrollment(program_name,group_name),summary_stats |
| GET | Student: show | /core/students/:student_id?include_fields=distancia_recorrida,tipo_camino |
| PUT | Student: update | /core/students/:id?include_fields=distancia_recorrida,tipo_camino |
| DELETE | Student: delete | /core/students/:id |
| GET | Student: show (me) | /core/student?include_fields=student_relatives,enrollment_id,summary_stats,curp,addresses,phones,medical_details |
| PUT | Student: update (me) | /core/student |
| POST | Student: create (by term) | /core/terms/:term_id/students?include_fields=enrollments,distancia_recorrida,tipo_camino&dry_run=true&validate_uniqueness=true |
| GET | Students: list (by relative) | /core/relatives/:relative_id/students?include_fields=extended,current_enrollment(program_name,term),tolerance_overdue |
| GET | Students: list (by term) | /core/terms/:term_id/students?include_fields=extended |
| GET | Students: list (by course) | /core/courses/:course_id/students?include_fields=extended&filters=active |
| GET | Students: list (by group) | /core/groups/:group_id/students |
| GET | StudentDocuments: list (me) | /core/student_documents |
| GET | StudentDocuments: list (by student) | /core/students/:student_id/student_documents |
| GET | StudentDocuments: list (by group) | /core/groups/:group_id/student_documents?filters=enrollment(status=1,2)&summary_stats=true |
| GET | StudentDocuments: list (by group) | /core/groups/:group_id/student_documents |
| POST | StudentDocuments: create (me) | /core/student_documents |
| POST | StudentDocuments: create (by student) | /core/students/:student_id/student_documents |
| PUT | StudentDocuments: update (by student) | /core/students/:student_id/student_documents/:id |
| PUT | StudentDocuments: update (me) | /core/student_documents/:id |
| PUT | StudentDocuments: Delete file (only file) | /core/students/:student_id/student_documents/:id |
| DELETE | StudentDocuments: Destroy (document) | /core/students/:student_id/student_documents/:id |
| PUT | StudentDocuments: Upload file | {{student_document_upload_url}} |
| GET | StudentDocuments: PDF (by group) | /core/groups/:group_id/student_documents.pdf |
| GET | StudentDocuments: export (by group) | /core/groups/:group_id/student_documents/export |
| GET | StudentDocuments: export (by student) | /core/students/:student_id/student_documents/export |
| GET | StudentPreviousSchools: list (by student) | /core/students/:student_id/student_previous_schools?include_fields=sep_school_name |
| GET | Subjects: list | /core/subjects?include_fields=program_ids&filters=program_ids=202&summary_programs=true |
| GET | Subjects: list (by program) | /core/programs/:program_id/subjects |
| GET | Subjects: list(PDF) | /core/programs/:program_id/subjects.pdf |
| GET | Subjects: show | /core/subjects/:id?include_fields=type,absences_limit,hours,mec_config |
| POST | Subjects: create | /core/subjects/ |
| POST | Subjects: create multiple | /core/subjects/ |
| PUT | Subjects: update | /core/subjects/:id |
| DELETE | Subjects: destroy | /core/subjects/:id |
| GET | Terms: list | /core/terms |
| GET | Terms: list (by school) | /core/schools/:school_id/terms |
| GET | Terms: list (by professor) | /core/professors/:professor_id/terms?sort_by=begins_at:desc |
| GET | Terms: show | /core/terms/:id?include_fields=periods |
| POST | Terms: create (global) | /core/terms |
| POST | Terms: create (by school) | /core/schools/:school_id/terms |
| PUT | Terms: update | /core/terms/:id?include_fields=periods |
| DELETE | Terms: destroy | /core/terms/:id |
| GET | ToDoItems: list | /core/to_do_items |
| POST | ToDoItem: create | /core/to_do_items |
| PUT | ToDoItem: update | /core/to_do_items/:id |
| DELETE | ToDoItem: delete | /core/to_do_items/:id |
| GET | User: me | /core/user |
| PUT | User: update | /core/user?include_fields=user_apps |
| GET | Photos(temp): show | /core/user?include_fields=user_apps |
| GET | Employees: list | /core/employees?include_fields=employee_group_name |
| GET | Employees: list (by school) | /core/schools/:school_id/employees?include_fields=student_employees |
| GET | Employees: show | /core/employees/:id?include_fields=addresses,professor_details,medical_details,occupations, contact_id, category_level_cost(category_name) |
| GET | Employees: id card | /core/employees/:id/id_card.pdf?expiration=2020 |
| POST | Employees: create | (hardcoded URL) /core/employees?include_fields=administrator,category_level_cost(category_name) |
| PUT | Employees: update | /core/employees/:id?include_fields=emergency_contacts |
| DELETE | Employees: delete | /core/employees/:id |
| GET | EmployeeGroups: list | /core/employee_groups?filters=only_professors |
| GET | Classrooms: list | /core/classrooms |
| GET | Classroom: list (by school) | /core/schools/:school_id/classrooms |
| GET | Classroom: show | /core/classrooms/:id?summary_terms=true |
| GET | Courses: list (by classroom) | /core/classrooms/:classroom_id/courses?filters=term_id={{term_id}} |
| GET | Classroom: conflicting_courses (by term) | /core/terms/:term_id/classrooms/:id/conflicting_courses |
| POST | Classroom: create (by school) | /core/schools/:school_id/classrooms |
| PUT | Classroom: update | /core/classrooms/:id |
| DELETE | Classroom: delete | /core/classrooms/:id |
| GET | Audit: list (by admin) | /core/administrators/:administrator_id/audits?summary_contacts=true&summary_professors=true&summary_enrollments=true&summary_courses=true&summary_groups=true&summary_payment_plans=true&s... |
| GET | Audit: list (by student) | /core/students/:student_id/audits?summary_contacts=true&summary_professors=true&summary_enrollments=true&summary_courses=true&summary_groups=true&summary_payment_plans=true&summary_terms... |
| GET | Audit: list (professor) | /core/professors/:professor_id/audits?filters=administrator_id=6100&summary_contacts=true&summary_professors=true&summary_enrollments=true&summary_courses=true&summary_groups=true&summar... |
| GET | SubstituteProfessors: list (by term) | /core/terms/:term_id/substitute_professors |
| GET | SubstituteProfessors: list (by group) | /core/groups/:group_id/substitute_professors |
| GET | SubstituteProfessors: me | /core/substitute_professors |
| GET | Inquiry: list | /core/inquiries |
| GET | Inquiry: show | /core/inquiries/:id |
| POST | Inquiry: create | /core/inquiries |
| PUT | Inquiry: update | /core/inquiries/:id |
| PUT | Inquiry: publish (inquiry_files) | /core/inquiries/:inquiry_id/publish |
| GET | StudentEmployees: list (by school) | /core/schools/:school_id/student_employees/summary_stats?filters=enrollment(date_range=2023-01-01,2023-12-01); relation_type=1 |
| GET | StudentEmployees: list (by school) xlsx | /core/schools/:school_id/student_employees/summary_stats.xlsx?filters=enrollment(date_range=2023-01-01,2023-12-01); relation_type=1 |
| GET | Subscription: show | /core/subscription |
| GET | ReportLog: index (by standard_key) | /core/standard_keys/:standard_key/report_logs |
| GET | ReportLog: show | /core/report_logs/:id |
| PUT | ReportLog: update | /core/report_logs/:id |
| GET | Competence_Records: PDF (by group) | /core/groups/:group_id/competence_records.pdf?persona=&puesto=&escuela_id=2179&fecha= |
| GET | Attachments: thumbnail | (no URL) |
| PUT | ScannedSignature: upload | {{scanned_signature_url}} |
| GET | FinancialAid.pdf (by enrollment) | (no URL) |
| GET | Groups: monthly_attendance PDF | (no URL) |

---

## /accounting

Billing, payments, invoices, payment plans, scholarships, bank transactions, deposit slips, and financial management.

| Method | Name | Path |
|---|---|---|
| GET | MonthlyIncomeExtended: XLSX (by school) | /accounting/schools/:school_id/monthly_income_extended.xlsx?filters=start_date=2020-01-01%3Bend_date=2020-06-01 |
| GET | MonthlyOverdue: XLSX (by school) | /accounting/schools/:school_id/monthly_overdue.xlsx?... |
| GET | BankAccounts: list | /accounting/bank_accounts |
| PUT | BankAccounts: update (multiple) | /accounting/bank_accounts/all |
| GET | BankReconciliation: show | /accounting/bank_reconciliations/:id |
| POST | BankReconciliation: create (by account) | /accounting/bank_accounts/:bank_account_id/bank_reconciliations |
| PUT | BankReconciliation: upload | {{bank_reconciliation_upload_url}} |
| PUT | BankReconciliation: import | /accounting/bank_reconciliations/:id/import |
| GET | BankTransactions: list | /accounting/bank_transactions?filters=date_range=2022-09-01,2022-09-10;bank_accounts=[10];student=true&include_fields=billing_details, payment_type,bank_account,invoice_folio_names&summa... |
| GET | BankTransactions: list csv | /accounting/bank_transactions.csv?... |
| PUT | BankTransactions: update | /accounting/bank_transactions/:id |
| PUT | BankTransactions: reconcile | /accounting/bank_transactions/reconcile?filters=... |
| GET | BankTransactions: show reconcile_log | /accounting/bank_transactions/reconcile_log/:id |
| GET | BillingPlan: index | /accounting/billing_plans |
| GET | BillingPlan: index (by student) | /accounting/students/:student_id/billing_plans |
| GET | BillingPlan: show (by enrollment) | /accounting/enrollments/:enrollment_id/billing_plan?include_fields=billing_items(folio_names,billing_concept_name),split_payments |
| GET | BillingPlan: show (by enrollment) | /accounting/enrollments/:enrollment_id/billing_plan?include_fields=billing_items(folio_names) |
| GET | BillingPlan: show | /accounting/billing_plans/:id?include_fields=billing_items(folio_names,billing_concept_name) |
| GET | BillingPlan: show PDF | /accounting/billing_plans/:id.pdf |
| POST | BillingPlan: create (by enrollment) | /accounting/enrollments/:enrollment_id/billing_plan?include_fields=scholarship_id,billing_items,payment_plan_name |
| POST | BillingPlan: create (multiple) | /accounting/terms/:term_id/billing_plans?include_fields=scholarship_id,billing_items,payment_plan_name |
| PUT | BillingPlan: update | /accounting/billing_plans/:id?include_fields=scholarship_id,billing_items,payment_plan_name |
| PUT | BillingPlan: update (by student) | /accounting/students/:student_id/billing_plan |
| GET | Invoices: list | /accounting/invoices?start_date=2021-12-01&end_date=2021-12-31&include_fields=emitter_rfc,emitter_name&sort_by=expedition_date:asc |
| GET | Invoices: list Zip | /accounting/invoices.zip?start_date=2021-12-01&end_date=2021-12-31&filters=type=2 |
| GET | Invoices: list (by school) | /accounting/schools/:school_id/invoices?... |
| GET | Invoices: list (by invoice emitter) | /accounting/invoice_emitters/:invoice_emitter_id/invoices?start_date=2023-07-01&end_date=2023-07-30 |
| GET | Invoices: list (by student) | /accounting/students/:student_id/invoices?include_fields=installment_method,payment_method,emitter_rfc,emitter_name,parent_invoices,child_invoices,invoice_payments,installments,invoice_r... |
| GET | Invoices: list (by school/student) | /accounting/schools/:school_id/students/:student_id/invoices?... |
| GET | Invoices: list (by school/invoice emitter) | /accounting/schools/:school_id/invoice_emitters/:invoice_emitter/invoices?... |
| GET | Invoices: show | /accounting/invoices/:id |
| POST | Invoices: send email | /accounting/invoices/:id/send_email |
| POST | Invoices: create (by emitter) | /accounting/invoice_emitters/:invoice_emitter_id/invoices |
| POST | Invoices: create (by billing_item) | /accounting/billing_items/:billing_item_id/invoice |
| PUT | Invoices: update | /accounting/invoices/:id |
| DELETE | Invoices: destroy | /accounting/invoices/:id |
| GET | Invoices: sat status | /accounting/invoices/:id/sat_status |
| GET | InvoiceCredits: list | /accounting/invoice_credits?filters=available |
| POST | InvoiceCredits: create | /accounting/invoice_credits |
| POST | InvoiceSignature: create (by invoice) | /accounting/invoices/:invoice_id/invoice_signature |
| POST | InvoiceSignatures: qa_global (by school) | /accounting/schools/:school_id/invoice_signatures/qa_global |
| GET | InvoiceReceivers: list (by student) | /accounting/students/:student_id/invoice_receivers |
| GET | InvoiceReceivers: list (by rfc) | /accounting/invoice_receivers?rfc=XAXX010101000 |
| POST | InvoicesReport: create (by invoice_issuer) | /accounting/invoice_issuers/:invoice_issuer_id/invoices_report |
| GET | InvoiceEmitter: list | /accounting/invoice_emitters?include_fields=invoice_series,ssl_expires_at,school_ids |
| POST | InvoiceEmitter: create | /accounting/invoice_emitters |
| PUT | InvoiceEmitter: update | /accounting/invoice_emitters/:id |
| DELETE | InvoiceEmitter: destroy | /accounting/invoice_emitters/:id |
| POST | InvoiceSeries: create (by_invoice_emitter) | /accounting/invoice_emitters/:invoice_emitter_id/invoice_series |
| PUT | InvoiceSeries: update | /accounting/invoice_series/:id |
| DELETE | InvoiceSeries: destroy | /accounting/invoice_series/:id |
| GET | IncomeReport: PDF | /accounting/billing_concepts/income_report.pdf?... |
| GET | BillingConcept: list | /accounting/billing_concepts?include_fields=subject_ids,extraordinary_type |
| GET | BillingConcept: list (by student) | /accounting/students/:student_id/billing_concepts?include_fields=subject_ids,extraordinary_type,program_ids,extraordinary |
| GET | BillingConcept: show | /accounting/billing_concepts/:id?include_fields=subject_ids,extraordinary_type,program_ids,extraordinary |
| POST | BillingConcept: create | /accounting/billing_concepts |
| PUT | BillingConcept: update | /accounting/billing_concepts/:id |
| DELETE | BillingConcept: delete | /accounting/billing_concepts/:id |
| GET | BillingItems: list | /accounting/billing_items?filters=outstanding |
| GET | BillingItems: list (by school) | /accounting/schools/:school_id/billing_items?include_fields=billing_payments(invoice)&limit=500&offset=0&filters=date_range=2024-09-01,2024-09-30;payments |
| GET | BillingItems: XLSX | /accounting/billing_items.xlsx?filters=date_range=2024-09-01,2024-09-30;payments |
| GET | BillingItems: CSV (by school) | /accounting/schools/:school_id/billing_items?filters=payments;date_range=2022-11-01,2022-12-31;&limit=10&offset=20&summary_latest_enrollments=true |
| GET | BillingItems: XLSX (by school) | /accounting/schools/:school_id/billing_items.xlsx?filters=payments;date_range=2024-01-01,2024-03-31 |
| GET | BillingItems: XLSX | /accounting/schools/:school_id/billing_items.xlsx?filters=date_range=2024-01-01,2024-03-31 |
| GET | BillingItems: list (by student) | /accounting/students/:student_id/billing_items |
| GET | BillingItems: list (by enrollment) | /accounting/enrollments/:enrollment_id/billing_items?include_fields=folio_names |
| GET | BillingItems: list (by applicant submission) | /accounting/applicant_submissions/:applicant_submission_id/billing_items |
| POST | BillingItems: create (by enrollment) | /accounting/enrollments/:enrollment_id/billing_items |
| POST | BillingItems: create (multiple) | /accounting/enrollments/:enrollment_id/billing_items |
| POST | BillingItems: create (by student) DEPRECATED | /accounting/students/:student_id/billing_items |
| PUT | BillingItems: update | /accounting/billing_items/:id |
| PUT | BillingItems: cancel | /accounting/billing_items/:id/cancel |
| PUT | BillingItems: split | /accounting/billing_items/:id/split |
| DELETE | BillingItems: delete | /accounting/billing_items/:id |
| GET | BillingItems: summary_report (PDF) | /accounting/billing_concepts/summary_report.pdf?... |
| GET | BillingItems: show PDF | /accounting/billing_items/:id.pdf |
| GET | BillingItems: PDF (by school) | /accounting/schools/:school_id/billing_items.pdf?filters=date_range=2022-11-01,2022-12-31 |
| GET | BillingItems: income_projection | /accounting/billing_items/income_projection?filters= |
| GET | BillingItems: income_projection CSV | /accounting/billing_items/income_projection.csv?... |
| GET | BillingPayment: list (by school) | /accounting/schools/:school_id/billing_payments?filters=date_range=2024-01-01,2024-01-31&include_fields=student,billing_concept_name,payment_type,outstanding_item |
| GET | BillingPayment: interval_summary | /accounting/billing_payments/interval_summary.csv?filters=date_range=2024-01-01,2024-12-31&interval=monthly |
| POST | BillingPayment: create (by student) | /accounting/students/:student_id/billing_payments?dry_run=true |
| GET | DepositSlip: ficha PDF (by student) | /accounting/students/:student_id/deposit_slip.pdf?filters=billing_item_ids=1474672,1474618;amount=0 |
| GET | DepositSlip: PDF | /accounting/deposit_slip.pdf?filters=billing_item_ids=1474672,1474618;amount=123 |
| GET | InstallmentFees: list | /accounting/installment_fees?include_fields=payment_plans_count |
| GET | InstallmentFees: show | /accounting/installment_fees/:id?include_fields=payment_plans |
| POST | InstallmentFees: create | /accounting/installment_fees |
| PUT | InstallmentFees: update | /accounting/installment_fees/:id |
| DELETE | InstallmentFees: destroy | /accounting/installment_fees/:id |
| GET | Installments: list (by payment plan) Copy | /accounting/payment_plans/:payment_plan_id/installments |
| POST | Installments: create (by payment plan) | /accounting/payment_plans/:payment_plan_id/installments |
| DELETE | Installments: destroy | /accounting/installments/:id |
| GET | PaymentPlans: list | /accounting/payment_plans?include_fields=program_ids,summary_stats,term_name,modular_course_ids&filters=modular_course_id=38 |
| GET | PaymentPlan: list (by term) | /accounting/terms/:term_id/payment_plans |
| GET | PaymentPlan: list (by reenrollment) | /accounting/reenrollments/:reenrollment_id/payment_plans?include_fields=instalments |
| GET | PaymentPlans: show | /accounting/payment_plans/:id?include_fields=installments,program_ids,modular_course_ids |
| POST | PaymentPlans: create (by term) | /accounting/terms/:term_id/payment_plans?include_fields=program_ids,course_ids |
| PUT | PaymentPlans: update | /accounting/payment_plans/:id?include_fields=program_ids,summary_stats,modular_course_ids |
| DELETE | PaymentPlans: destroy | /accounting/payment_plans/:id |
| GET | PaymentsProvider: show | /accounting/payments_provider |
| GET | PaymentsProvider: show (by student) | /accounting/students/:student_id/payments_provider |
| GET | PaymentsProvider: show (by school) | /accounting/schools/:school_id/payments_provider |
| PUT | PaymentsProvider: update | /accounting/payments_provider |
| PUT | PaymentsProvider: update (by school) | /accounting/schools/:school_id/payments_provider |
| GET | ProviderPayment: list | /accounting/provider_payments?filters=provider=1;status=4 |
| GET | ProviderPayment: show | /accounting/provider_payments/:id |
| GET | SatProductCode: list (query) | /accounting/sat_product_codes?query=01010101 |
| GET | Scholarships: index (by student) | /accounting/students/:student_id/scholarships |
| GET | Scholarship: show (by enrollment) | /accounting/enrollments/:enrollment_id/scholarship?include_fields=billing_plan_applied,memorandum,scholarship_service |
| GET | Scholarship: show (by enrollment) PDF | /accounting/enrollments/:enrollment_id/scholarship.pdf |
| POST | Scholarships: create | /accounting/enrollments/:enrollment_id/scholarship?include_fields=billing_plan_applied,memorandum,scholarship_service |
| PUT | Scholarships: update | /accounting/enrollments/:enrollment_id/scholarship?include_fields=billing_plan_applied,memorandum,scholarship_service(contact_in_charge_name) |
| DELETE | Scholarships: destroy | /accounting/enrollments/:enrollment_id/scholarship |
| GET | SummaryReport: PDF | /accounting/billing_concepts/summary_report.pdf?... |
| GET | BBVACustomer: show | /accounting/bbva_customer |
| GET | BBVACustomer: show (by student) | /accounting/bbva_customer |
| POST | BBVACustomer: create | /accounting/bbva_customer |
| PUT | BBVACustomer: update (otp) | /accounting/bbva_customer |
| PUT | BBVACustomer: update (create account) | /accounting/bbva_customer |
| GET | ProfessorAttendanceCosts: index | /accounting/professor_attendance_costs?filters=start_date=2024-07-15;end_date=2024-07-31&include_fields=extended |
| GET | OverdueStudents: list (by school) | /accounting/schools/:school_id/overdue_students?offset=0&limit=50&include_fields=enrollment(group_name,group_shift,term_name,student)&filters=enrollment_status=1,2,3 |
| GET | DepositSlipConfigs: list | /accounting/deposit_slip_configs?include_fields=school_ids |
| GET | DepositSlipConfigs: show | /accounting/deposit_slip_configs/:id?include_fields=school_ids |
| POST | DepositSlipConfigs: create | /accounting/deposit_slip_configs |
| PUT | DepositSlipConfigs: update | /accounting/deposit_slip_configs/:id?include_fields=school_ids |
| DELETE | DepositSlipConfigs: destroy | /accounting/deposit_slip_configs/:id |
| POST | invoicesReport ZIP | /accounting/invoice_issuers/:invoice_emitter_id/invoices_report |
| GET | InvoiceConfig: show | /configurations/invoice_config |
| GET | FinancialAid.pdf (by enrollment) | (no URL) |

---

## /activity_stream

Feed activities, mobile devices, and notifications.

| Method | Name | Path |
|---|---|---|
| GET | FeedActivity: list | /activity_stream/feed_activities?gt=3279315247764288 |
| GET | FeedActivity: list (notifications) | /activity_stream/feed_activities?feed=notifications&include_fields=viewed |
| PUT | FeedActivity: update | /activity_stream/feed_activities/:id?feed=notifications |
| POST | MobileDevices: create | /activity_stream/mobile_devices |
| PUT | MobileDevice: update | /activity_stream/mobile_device |
| POST | FeedActivity: MarkAllViewed | /activity_stream/feed_activities/mark_all_viewed?feed=notifications |

---

## /admissions_v2

Applicants, submissions, admission tests, and enrollment processes.

| Method | Name | Path |
|---|---|---|
| GET | Applicant: show | /admissions_v2/applicant |
| GET | AdmissionsConfig: show | /admissions_v2/admissions_config |
| GET | ApplicantSubmissions: list (by student) | /admissions_v2/students/:student_id/applicant_submissions?include_fields=admission_test_group |
| POST | ApplicantSubmission: create | /admissions_v2/admissions_configs/:admissions_config_id/applicant_submission |
| GET | ApplicantSubmission: show (by config) | /admissions_v2/admissions_configs/:admissions_config_id/applicant_submission |
| GET | AdmissionTestGroups: list (by config) | /admissions_v2/admissions_configs/:admissions_config_id/admission_test_groups |
| GET | ApplicantDocuments: list (by submission) | /admissions_v2/applicant_submissions/:applicant_submission_id/applicant_documents |
| PUT | ApplicantDocument: upload | {{applicant_document_upload_url}} |
| POST | ApplicantDocuments: create (multiple by submission) | /admissions_v2/applicant_submissions/:applicant_submission_id/applicant_documents |
| PUT | ApplicantDocument: upload | (cloudfront URL) |
| GET | ApplicantGroupSubmission: show (by enrollment) | /admissions_v2/enrollments/:enrollment_id/applicant_group_submission |
| PUT | ApplicantGroupSubmission: update (by enrollment) | /admissions_v2/enrollments/:enrollment_id/applicant_group_submission |
| POST | ApplicantGroupSubmission: create (by enrollment) | /admissions_v2/enrollments/:enrollment_id/applicant_group_submission |
| GET | AdmissionPracticeTests: list (by config) | /admissions_v2/admissions_configs/:admissions_config_id/admission_practice_tests |
| GET | ApplicantPracticeTestSubmissions: list (by submission) | /admissions_v2/applicant_submissions/:applicant_submission_id/applicant_practice_test_submissions |
| POST | ApplicantPracticeTestSubmission: create (by practice test) | /admissions_v2/admission_practice_tests/:admission_practice_test_id/applicant_practice_test_submission |
| PUT | ApplicantPracticeTestSubmission: update (by practice test) | /admissions_v2/admission_practice_tests/:admission_practice_test_id/applicant_practice_test_submission |
| GET | Enrollment: show (by applicant submission) | /admissions_v2/applicant_submissions/:applicant_submission_id/enrollment?include_fields=term_name,school_name,student |
| POST | Enrollments: enroll (by term) | /admissions_v2/terms/:term_id/enrollments/enroll?program_id={{program_id}}&dry_run=true |
| GET | Groups: list (by admission config) | /admissions_v2/admissions_configs/:admissions_config_id/groups |
| GET | Groups: list (by term) | /admissions_v2/terms/:term_id/groups |
| GET | Programs: list (by config) | /admissions_v2/admissions_configs/:admissions_config_id/programs |
| GET | PaymentPlans: list (by admission config) | /admissions_v2/admissions_configs/:admissions_config_id/payment_plans |
| GET | Students: index (by admission config) | /admissions_v2/admissions_configs/:admissions_config_id/students?student_number=20010521 |
| GET | Terms: list (by config) | /admissions_v2/admissions_configs/:admissions_config_id/terms |
| GET | ApplicantSubmission: instructions (by admissions config) | /admissions_v2/admissions_configs/:admissions_config_id/applicant_submission/instructions.pdf |
| GET | ApplicanSubmission: open process(by admissions_config) | /admissions_v2/admissions_configs/:admissions_config_id/applicant_submissions?... |
| GET | ad_campaigns | /admissions/ad_campaigns |

---

## /certification

Transcripts, degree certificates, IEMS setups, and signees.

| Method | Name | Path |
|---|---|---|
| GET | DegreeCertificateSignees: list | /certification/degree_certificate_signees |
| POST | DegreeCertificateSignees: create | /certification/degree_certificate_signees |
| GET | DegreeCertificateSignees: show | /certification/degree_certificate_signees/:id?include_fields=ssl_key |
| PUT | DegreeCertificateSignees: update | /certification/degree_certificate_signees/:id |
| POST | DegreeCertificateBatches: create | /certification/terms/:term_id/degree_certificate_batches |
| GET | IEMSSetups: list | /certification/iems_setups |
| POST | IEMSSetups: create | /certification/iems_setups |
| PUT | IEMSSetups: update | /certification/iems_setups/:id |
| GET | IEMSSetups: show | /certification/iems_setups/:id |
| DELETE | IEMSSetups: destroy | /certification/iems_setups/:id |
| GET | Transcripts: list (by student) | /certification/students/:student_id/transcripts?include_fields=earned_credits,total_credits,score_avg,transcript_signatures |
| GET | Transcripst: list (by term) csv | /certification/terms/:term_id/transcripts.csv |
| GET | Transcript: show (by enrollment) | /certification/enrollments/:enrollment_id/transcript?include_fields=transcript_records,earned_credits |
| GET | Transcript: show (by enrollment) | /certification/enrollments/:enrollment_id/transcript?include_fields=earned_credits,total_credits,score_avg,transcript_records |
| PUT | Transcript: update (by enrollment) | /certification/enrollments/:enrollment_id/transcript |
| GET | TranscriptBatch: show (by term) | /certification/terms/:term_id/transcript_batches/:id?include_fields=transcript_signatures |
| POST | TranscriptBatch: create (by term) | /certification/terms/:term_id/transcript_batches |
| GET | TranscriptCredits: list | /certification/transcript_credits?filters=available |
| POST | TranscriptCredits: create | /certification/transcript_credits |
| GET | TranscriptSignatures: list (by student) | /certification/students/:student_id/transcript_signatures |
| GET | TranscriptSignature: show (PDF) | /certification/transcript_signatures/:id |
| PUT | TranscriptSignature: update | /certification/transcript_signatures/:id |
| POST | TranscriptSignature: update (multiple) | /certification/transcript_signatures |
| GET | TranscriptSignees: list | /certification/transcript_signees |
| POST | TranscriptSignees: list | /certification/transcript_signees |
| GET | TranscriptSignees: show | /certification/transcript_signees/:id |
| POST | TranscriptValidator: create (using qr) | /certification/transcript_validator |
| POST | TranscriptValidator: create (using folio) | /certification/transcript_validator |
| POST | TranscriptValidator: create (using XML) | /certification/transcript_validator |
| GET | DegreeCertificateBatch: show | /certification/degree_certificate_batches/:id |
| GET | DegreeCertificate: list | /certification/degree_certificate_credits |
| POST | DegreeCertificate: create | /certification/degree_certificate_credits |
| GET | Transcript: preview | /certification/enrollments/:enrollment_id/transcript_signatures/preview.pdf |
| PUT | DegreeCertificateSignature: update | /certification/terms/:term_id/degree_certificate_signatures/:id |
| GET | DegreeCertificateSignature: show | /certification/degree_certificate_signatures/:id |
| POST | Transcripts: create (by student) | /certification/students/:student_id/transcripts |
| POST | CustomTranscript: create (by enrollment) | /certification/enrollments/:enrollment_id/custom_transcript |
| POST | CustomTranscripts: create (by term/program) | /certification/terms/:term_id/programs/:program_id/custom_transcripts |
| GET | CustomTranscripts: list (by term/program) | /certification/terms/:term_id/programs/:program_id/custom_transcripts?filters=enrollment(last_term)&include_fields=custom_transcript_subjects |
| GET | CustomTranscripts: show (by enrollment) | /certification/enrollments/:enrollment_id/custom_transcript?include_fields=custom_transcript_subjects |

---

## /community

Publications, comments, bookmarks, apples, and black lists.

| Method | Name | Path |
|---|---|---|
| POST | Apples: create (by publication) | /community/publications/:publication_id/apple |
| DELETE | Apples: destroy (by publication) | /community/publications/:publication_id/apple |
| POST | BlackList: create | /community/black_lists |
| PUT | BlackList: update | /community/black_lists/:filter_id |
| GET | BlackList: index | /community/black_lists |
| POST | Viewer: create (by publication) | /community/publications/:publication_id/viewer |
| GET | Bookmarks: index | /community/bookmarks |
| POST | Bookmarks: create (by publication) | /community/publications/:publication_id/bookmark |
| DELETE | Bookmarks: destroy (by publication) | /community/publications/:publication_id/bookmark |
| POST | Medias: create | /community/medias |
| POST | Publication: create | /community/publications |
| GET | Publications: index | /community/publications |
| GET | Publications: show | /community/publications/:publication_id |
| DELETE | Publication: destroy | /community/publications/:id |
| POST | Comment: create | /community/publications/:publication_id/publications |
| GET | Comment: index | /community/publications/:publication_id/publications |
| GET | Accounts: index | /community/publications/:publication_id/accounts?filters=favourited_by |
| POST | Comment: create DEPRECATED | /community/publications/:publication_id/comments |
| GET | Comment: index DEPRECATED | /community/publications/:publication_id/comments |

---

## /configurations

Grading configs, attendance configs, holidays, mailer configs, remark types, reenrollment setups, student portal configs, deposit slip configs, whatsapp templates, tutoring categories, admissions configs.

| Method | Name | Path |
|---|---|---|
| GET | RemarkTypes: index | /configurations/remark_types |
| GET | RemarkTypes: show | /configurations/remark_types/:id |
| GET | Holidays: list | /configurations/holidays |
| GET | Holidays: show | /configurations/holidays/:id |
| POST | Holidays: create/edit/delete | /configurations/holidays |
| GET | MailerConfigs: list | /configurations/mailer_configs |
| GET | MailerConfigs: show | /configurations/mailer_configs/:id |
| PUT | MailerConfigs: update | /configurations/mailer_configs/:id |
| POST | RemarkTypes: create | /configurations/remark_types |
| PUT | RemarkTypes: update | /configurations/remark_types/:id |
| DELETE | RemarkTypes: destroy | /configurations/remark_types/:id |
| GET | CustomDatasetItems: list (filter) | /configurations/custom_dataset_items?filters=dataset_type=3 |
| GET | LeaveReasons: list | /configurations/leave_reasons |
| DELETE | LeaveReasons: destroy | /configurations/leave_reasons/:leave_reason_id |
| GET | CustomDatasetItem: list (by admissions config) | /configurations/admissions_configs/:admissions_config_id/custom_dataset_items |
| POST | CustomDatasetItems | /configurations/custom_dataset_items |
| GET | ReenrollmentsSetups: list | /configurations/reenrollments_setups |
| GET | ReenrollmentsSetups: show (admin) | /configurations/reenrollments_setups/:id |
| GET | ReenrollmentsSetups: show (student) | /configurations/reenrollments_setup |
| POST | ReenrollmentsSetups: create | /configurations/reenrollments_setups |
| PUT | ReenrollmentsSetups: update | /configurations/reenrollments_setups/:id |
| GET | GradingConfigs: list | /configurations/grading_configs |
| GET | GradingConfigs: show (by term/program) | /configurations/terms/:term_id/programs/:program_id/grading_config |
| POST | GradingConfigs: create | /configurations/grading_configs |
| PUT | GradingConfigs: update | /configurations/grading_configs/:id |
| DELETE | GradingConfigs: destroy | /configurations/grading_configs/:id |
| POST | AttendanceConfig: create (by school) | /configurations/schools/:school_id/attendance_configs |
| POST | AttendanceConfig: create (by course) | /configurations/courses/:course_id/attendance_configs |
| POST | AttendanceConfig: create (by subject) | /configurations/subjects/:subject_id/attendance_configs |
| PUT | AttendanceConfig: update | /configurations/attendance_configs/:id |
| DELETE | AttendanceConfig: delete | /configurations/attendance_configs/:id |
| POST | AdmissionsConfigs: create | /configurations/admissions_configs |
| PUT | AdmissionsConfigs: update | /configurations/admissions_configs/:id |
| GET | AdmissionsConfigs: show | /configurations/admissions_configs/:id |
| GET | AdmissionsConfigs: list | /configurations/admissions_configs?include_fields=schools_count |
| POST | TutoringCategories: create | /configurations/tutoring_categories |
| PUT | TutoringCategories: update | /configurations/tutoring_categories/:id |
| GET | TutoringCategories: show | /configurations/tutoring_categories/:id |
| GET | TutoringCategories: list | /configurations/tutoring_categories |
| DELETE | TutoringCategories: destroy | /configurations/tutoring_categories/:id |
| POST | StudentPortalConfig: Create ( by school) | /configurations/schools/:school_id/student_portal_configs |
| GET | StudentPortalConfig: index ( by school) | /configurations/schools/:school_id/student_portal_configs |
| GET | StudentPortalConfig: index | /configurations/student_portal_configs |
| PUT | StudentPortalConfig: update | /configurations/student_portal_configs/:id |
| GET | CategoryLevelCosts: list | /configurations/category_level_costs?filters=category_id=111&include_fields=category_name |
| GET | GradingConfig: list | /configurations/grading_configs?filters=term_id=67 |
| PUT | GradingConfig: update | /configurations/grading_configs/:id |
| POST | GradingConfig: create | /configurations/grading_configs |
| DELETE | GradingConfig: destroy | /configurations/grading_configs/:id |
| GET | DepositSlipPrintConfigs: index (by school) | /configurations/schools/:school_id/deposit_slip_print_configs |
| PUT | DepositSlipPrintConfigs: update | /configurations/deposit_slip_print_config/:id |
| GET | DepositSlipPrintConfigs: index | /configurations/deposit_slip_print_configs |
| PUT | DepositSlipPrintConfigs: update_strict_mode | /configurations/deposit_slip_print_config/update_strict_mode?strict_mode=1 |
| GET | InvoiceConfig: show | /configurations/invoice_config |

### /configurations/whatsapp_templates

| Method | Name | Path |
|---|---|---|
| GET | WhatsappTemplates: list | /configurations/whatsapp_templates |
| PUT | WhatsappTemplates: toggle_enabled | /configurations/whatsapp_templates/:id/toggle_enabled |

---

## /drive

| Method | Name | Path |
|---|---|---|
| GET | GoogleTokens: show | /drive/google_token |

---

## /finerio

| Method | Name | Path |
|---|---|---|
| GET | FinerioCustomer: show | /finerio/finerio_customer |
| GET | FinerioAccounts: list | /finerio/finerio_accounts?credential_id=... |
| PUT | FinerioAccounts: update | /finerio/finerio_accounts/:id |
| GET | FinerioTransactions: list (by school) | /finerio/schools/:school_id/finerio_transactions?filters=date_range=... |
| PUT | FinerioTransaction: update | /finerio/finerio_transactions/:id?include_fields=billing_items |

---

## /forms

| Method | Name | Path |
|---|---|---|
| POST | SubmissionForm: create (by reenrollment / by custom form) | /forms/reenrollments/:reenrollment_id/custom_forms/:custom_form_id/submission_form |
| PUT | SubmissionForm: update (by reenrollment / by custom form) | /forms/reenrollments/:reenrollment_id/custom_forms/:custom_form_id/submission_form |
| GET | CustomForms: list (by context) | /forms/context_types/:context_types/custom_forms |
| GET | Submissions: list (by custom_form) | /forms/custom_forms/:id/submissions.csv |

---

## /flap

| Method | Name | Path |
|---|---|---|
| POST | FlapPaymentIntents: create | /flap/flap_payment_intents |
| POST | FlapPaymentIntents: create (by student) | /flap/flap_payment_intents |
| POST | FlapPayments: create | /flap/flap_payments |
| POST | FlapPayments: create (v2) | /flap/flap_payments |
| GET | FlapPaymentIntents: show | /flap/flap_payment_intents/:id |
| GET | FlapPaymentIntents: show (by student) | /flap/flap_payment_intents/:id |

---

## /grading

Activities, grades, assessment plans, enrolled courses, grading requests, report cards, student remarks, letter marks, extraordinary grades.

| Method | Name | Path |
|---|---|---|
| GET | Activities: list (by course) | /grading/courses/:course_id/activities?include_fields=attachments |
| GET | Activities: list (by enrollment) | /grading/enrollments/:enrollment_id/activities |
| GET | Activities: list (active) | /grading/activities?filters=active |
| GET | Activities: show | /grading/activities/:id |
| POST | Activities: create | /grading/activities |
| POST | Activities: create (multiple courses) | /grading/activities |
| DELETE | Activities: delete | /grading/activities/:id |
| PUT | Activities: update | /grading/activities/:id |
| GET | AssessmentPlans: list | /grading/assessment_plans?include_fields=program_ids |
| GET | AssessmentPlans: list (by course) | /grading/courses/:course_id/assessment_plans |
| GET | AssessmentPlans: show | /grading/assessment_plans/:id?include_fields=activities,subjects |
| DELETE | AssessmentPlans: destroy | /grading/assessment_plans/:id |
| POST | AssessmentPlans: create | /grading/assessment_plans |
| PUT | AssessmentPlans: update | /grading/assessment_plans/:id |
| POST | AssessmentPlans: install | /grading/assessment_plans/:id/install |
| GET | Courses: grading_status_report (by term) | /grading/terms/:term_id/courses/grading_status_report |
| GET | Courses: assessment_plan_periods (by group) | /grading/groups/:group_id/courses/assessment_plan_periods |
| GET | EnrolledCourses: list | /grading/enrolled_courses?include_fields=course_name,subject_type,module_subject_id |
| GET | EnrolledCourses: list (by student) | /grading/students/:student_id/enrolled_courses?include_fields=course_name,subject_type,enrolled_type,score_ordinary,score_extraordinary,score_final,module_subject_id,extraordinary_grade |
| GET | EnrolledCourses: list (by term) | /grading/terms/:term_id/enrolled_courses?summary_students=true&filters=enrollment(active) |
| GET | EnrolledCourses: list (by enrollment) | /grading/enrollments/:enrollment_id/enrolled_courses?include_fields=score_ordinary,score_extraordinary,score_final |
| GET | EnrolledCourses: list (by reenrollment) | /grading/reenrollments/:reenrollment_id/enrolled_courses?include_fields=course&filters=pending_failed |
| GET | EnrolledCourses: list (by course) | /grading/courses/:course_id/enrolled_courses?include_fields=score_ordinary,score_extraordinary,score_final |
| GET | EnrolledCourses: list (by term/program) | /grading/terms/:term_id/programs/:program_id/enrolled_courses?filters=enrollment(last_term)&complete_history=true&include_fields=term_id |
| POST | EnrolledCourses: create (by enrollment) | /grading/enrollments/:enrollment_id/enrolled_courses?include_fields=integrative_course_id |
| POST | EnrolledCourses: enroll (by term) | /grading/terms/:term_id/enrolled_courses/enroll?dry_run=true&program_id={{program_id}}&grade_level=1 |
| DELETE | EnrolledCourses: delete | /grading/enrolled_courses/:id?destroy_dependencies=true |
| GET | ExtraordinaryGrades: students_report list (by_term) | /grading/terms/{{term_id}}/extraordinary_grades/students_report?cursor=0&limit=3 |
| GET | ExtraordinaryGrades: students_report csv | /grading/terms/{{term_id}}/extraordinary_grades/students_report.csv |
| GET | ExtraordinaryGrades: list (by course) | /grading/courses/:courses_id/extraordinary_grades |
| GET | ExtraordinaryGrades: list (by student) | /grading/students/:student_id/extraordinary_grades?filters=active_grading_request&include_fields=course_id |
| POST | ExtraordinaryGrade: create (by course) | /grading/courses/:courses_id/extraordinary_grades |
| DELETE | ExtraordinaryGrade: destroy (by course) | /grading/courses/:courses_id/extraordinary_grades/:id |
| GET | Grades: list (by activity) | /grading/activities/:activity_id/grades |
| GET | Grades: list (by course) | /grading/courses/:course_id/grades?include_fields=published_score,period_id,activity_type |
| GET | Grades: list (by enrollment) | /grading/enrollments/:enrollment_id/grades?include_fields=period_id,activity_type,published_score,meta(period_averages) |
| POST | Grades: publish (by activity) | /grading/activities/:activity_id/publish |
| GET | Grades: export CSV (by term) | /grading/terms/:term_id/grades/export_grades.csv |
| GET | Grades: grades_report (PDF) | /grading/courses/:course_id/grades_report.pdf?... |
| GET | Grades: grades_reports (PDF) | /grading/groups/:group_id/grades_reports.pdf?... |
| GET | GradingLogs: list (by course) | /grading/courses/:course_id/grading_logs |
| GET | GradingRequests: list (by course) | /grading/courses/:course_id/grading_requests?include_fields=workflow |
| GET | GradingRequests: list (by activity) | /grading/activities/:activity_id/grading_requests |
| GET | GradingRequests: list (by term) | /grading/terms/:term_id/grading_requests?include_fields=student,program_name,group_name,school_name,cumulative_score_avg,group_shift,billing_plan_name,date,course_name,professor_name,wor... |
| GET | GradingRequest: show | /grading/grading_requests/:id?include_fields=workflow |
| POST | GradingRequest: create (by grading log) | /grading/grading_logs/:grading_log_id/grading_requests |
| POST | GradingRequest: create (by activity) | /grading/activities/:activity_id/grading_requests |
| GET | GradingConfig: list | /grading (see /configurations) |
| PUT | GradingConfig: update (see /configurations) | (see /configurations) |
| POST | GradingConfig: create (see /configurations) | (see /configurations) |
| DELETE | GradingConfig: destroy (see /configurations) | (see /configurations) |
| GET | GradingExtRequest: list | /grading/grading_ext_requests?include_fields=student,course_name,group_name |
| GET | GradingExtRequest: list (by course) | /grading/courses/:courses_id/grading_ext_requests?include_fields=professor_name,workflow |
| GET | GradingExtRequest: list (by student) | /grading/students/:student_id/grading_ext_requests?include_fields=professor_name,workflow |
| GET | GradingExtRequest: list (by term) | /grading/terms/:term_id/grading_ext_requests?... |
| PUT | GradingExtRequest: update [professor] | /grading/grading_ext_requests/:id |
| GET | GradingSheet: XLSX (by course) | /grading/courses/:courses_id/grading_sheet.xlsx |
| GET | LetterMarks: list (by course) | /grading/courses/:course_id/letter_marks |
| GET | LetterMarks: list (by program) | /grading/programs/:program_id/letter_marks?filters=applicable_type=subject |
| GET | ReportCard: pdf (by enrollment) | /grading/enrollments/:enrollment_id/report_card.pdf |
| GET | ReportCard: pdf (by student) | /grading/students/:student_id/report_card.pdf |
| GET | ReportCard: pdf (by course) | /grading/courses/:course_id/grades_report.pdf?... |
| PUT | StudentAssignments: update (by activity) | /grading/activities/:activity_id/student_assignment |
| GET | StudentAssignments: list (by course) | /grading/courses/:course_id/student_assignments |
| GET | StudentsAverages: XLSX | /grading/terms/:term_id/students_averages.xlsx |
| GET | StudentsAverages: CSV | /grading/terms/:term_id/students_averages.xlsx |
| GET | StudentRemarks: list | /grading/student_remarks |
| GET | StudentRemarks: list (by school) | /grading/schools/:school_id/student_remarks |
| GET | StudentRemarks: list (by course) | /grading/courses/:course_id/student_remarks |
| GET | StudentRemarks: list (by enrollment) | /grading/enrollments/:enrollment_id/student_remarks |
| GET | StudentRemarks: list (by term) | /grading/terms/:term_id/student_remarks |
| GET | StudentRemarks: list (by group) | /grading/groups/:group_id/student_remarks |
| GET | StudentRemarks: show | /grading/student_remarks/:id |
| POST | StudentRemarks: create (by enrollment) | /grading/enrollments/:enrollment_id/student_remarks |
| POST | StudentRemarks: create | /grading/student_remarks |
| PUT | StudentRemarks: update | /grading/student_remarks/:id |
| DELETE | StudentRemarks: destroy | /grading/student_remarks/:id |
| POST | SummaryResults: PDF (by group) | /grading/groups/:group_id/grades/summary_results.pdf |
| POST | ReportCard: PDF (by group) | /grading/groups/:group_id/grades_report.pdf |
| GET | Grades: students_results.xlsx (by group) | /grading/groups/:group_id/grades/students_results.xlsx?... |
| GET | Grades: students_results_extended (by term/program) | /grading/terms/:term_id/programs/:program_id/grades/students_results_extended.csv?... |
| POST | Transcript: PDF (by student) | /grading/students/:student_id/transcript.pdf |
| GET | Transcript: PDF (by group) | /grading/groups/:group_id/transcript.pdf?... |
| GET | Competence_Records: PDF (by group) | /grading/groups/:group_id/competence_records... |
| GET | DegreeExaminationResult: PDF (by student) | /api/v1/grading/enrollments/:enrollment_id/degree_examination_result.pdf?... |
| GET | DegreeExaminationResult: PDF (by student) Copy | /api/v1/grading/enrollments/:enrollment_id/degree_examination_result.pdf |
| GET | LetterMarks: list | /grading/letter_marks |
| POST | LetterMarks: create | /grading/letter_marks |
| PUT | LetterMarks: update | /grading/letter_marks/:id |
| DELETE | LetterMarks: delete | /grading/letter_marks/:id |
| GET | LetterMark: show | /grading/letter_marks/:id |
| GET | LetterMark: show (by term/program) | /grading/terms/:term_id/programs/:program_id/letter_mark |
| GET | LetterCredits: PDF (by enrollment) | /grading/enrollments/:enrollment_id/letter_credits.pdf |
| GET | StudentResults.xlsx | /grading/groups/:group_id/grades/students_results.xlsx |
| GET | GradingReport.PDF (by course) | /grading/courses/:course_id/grading_report.pdf |
| GET | AdvisoryNotice.pdf (by enrollment) | /grading/enrollments/:enrollment_id/advisory_notice.pdf |
| GET | GradingExtRequests: show PDF | /grading/grading_ext_requests/:id.pdf |
| POST | SendEmailReportCard | /grading/groups/:group_id/send_email_report_card |
| GET | Enrollments: top_grades (by term) | /grading/terms/:term_id/enrollments/top_grades?filters=final_cumulative |
| GET | Enrollments: graded_course_counts (by term) | /grading/terms/:term_id/enrollments/graded_course_counts?filters=failed;period_id={{period_id}} |
| GET | Groups: passed_failed_students (PDF) | /grading/groups/:group_id/passed_failed_students.pdf?... |

---

## /importation

| Method | Name | Path |
|---|---|---|
| GET | DataImport: show (by type) | /importation/types/:type_id/data_import |
| GET | DataImport: show (by type/group) | /importation/types/:type_id/groups/:group_id/data_import |
| POST | DataImport: create (by type) | /importation/types/:type_id/data_import |
| POST | DataImport: create (by type/group) | /importation/types/:type_id/groups/:group_id/data_import |
| PUT | DataImport: update (by type) | /importation/types/:type_id/data_import |
| PUT | DataImport: update (by type/group) | /importation/types/:type_id/groups/:group_id/data_import |
| PUT | DataImport: upload | {{data_import_upload_url}} |

---

## /integrations

| Method | Name | Path |
|---|---|---|
| POST | IntegrationCredits | /integrations/integration_credits |
| GET | IntegrationCredits: list | /integrations/integration_credits |

---

## /joomla

| Method | Name | Path |
|---|---|---|
| GET | JoomlaBanners: list | /joomla/joomla_banners?filters=category_id=64 |

---

## /location

| Method | Name | Path |
|---|---|---|
| GET | Countries: list | /location/countries |
| GET | States: list (by country_id) | /location/countries/:country_id/states |
| GET | Cities: list (by state_id) | /location/states/:state:id/cities |
| GET | Cities: show | /location/cities/:id |
| GET | Suburbs: list (by city_id) | /location/cities/:city_id/suburbs |
| GET | Suburbs: show | /location/suburbs/:id |

---

## /lounge

| Method | Name | Path |
|---|---|---|
| GET | LoungeItem: show (by room_id) | /lounge/rooms/:room_id/items/:id |

---

## /modular_courses

Modular courses, activities, enrollments, reservations, grades, and reservation slots.

| Method | Name | Path |
|---|---|---|
| GET | ModularActivities: list | /modular_courses/modular_courses/:modular_course_id/modular_activities?include_fields=modular_course_ids, required_modular_activity_ids&sort_by=serialization |
| GET | ModularActivities: list (by enrollment) | /modular_courses/modular_enrollments/:modular_enrollment_id/modular_activities?filters=available |
| GET | ModularActivities: show | /modular_courses/modular_activities/:id |
| POST | ModularActivities: create | /modular_courses/modular_activities |
| PUT | ModularActivities: update | /modular_courses/modular_activities/:id |
| DELETE | ModularActivities: destroy | /modular_courses/modular_activities/:id |
| GET | ModularCourses: list | /modular_courses/modular_courses |
| GET | ModularCourses: list (by school) | /modular_courses/schools/:school_id/modular_courses?include_fields=school_ids,modular_activities_count |
| GET | ModularCourses: show | /modular_courses/modular_courses/:id |
| POST | ModularCourses: create | /modular_courses/modular_courses |
| PUT | ModularCourses: update | /modular_courses/modular_courses/:id |
| DELETE | ModularCourses: destroy | /modular_courses/modular_courses/:id |
| GET | ModularReservationSlots: list (by school and modular course) | /modular_courses/schools/:school_id/modular_courses/:modular_course_id/modular_reservation_slots?... |
| GET | ModularReservationSlots: show | /modular_courses/modular_reservation_slots/:id |
| POST | ModularReservationSlots: create | /modular_courses/modular_reservation_slots |
| PUT | ModularReservationSlots: update | /modular_courses/modular_reservation_slots/:id |
| DELETE | ModularReservationSlots: destroy | /modular_courses/modular_reservation_slots/:id |
| GET | ModularReservation: list | /modular_courses/modular_reservation_slots/:modular_reservation_slot_id/modular_reservations?... |
| GET | ModularReservation: list (by school) | /modular_courses/schools/:school_id/modular_reservations?... |
| GET | ModularReservation: list (by course) | /modular_courses/modular_courses/:modular_course_id/modular_reservations |
| GET | ModularReservation: list (by course and student) | /modular_courses/modular_courses/:modular_course_id/students/:student_id/modular_reservations |
| GET | ModularReservation: list (by Student) | /modular_courses/modular_reservations?filters=current_week&include_fields=student, grade_level, modular_enrollment_activity_id, modular_activity, professor_lecture, modular_course |
| GET | ModularReservation: list (by Term) | /modular_courses/terms/:term_id/modular_reservations?... |
| GET | ModularReservation: list (by Term) xlsx | /modular_courses/terms/:term_id/modular_reservations.xlsx?filters=current_week |
| GET | ModularReservationsSummaryStats: list (by Term) | /modular_courses/terms/:term_id/modular_reservations/summary_stats?filters=current_week |
| GET | ModularReservationsSummaryStats: list (by Term) xlsx | /modular_courses/terms/:term_id/modular_reservations/summary_stats.xlsx |
| POST | ModularReservations: create (by reservation slot) | /modular_courses/modular_reservation_slots/:modular_reservation_slot_id/modular_reservations |
| PUT | ModularReservations: update | /modular_courses/modular_reservations/:id |
| GET | ModularEnrollments: list (by student) | /modular_courses/students/:student_id/modular_enrollments |
| GET | ModularEnrollments: list (by course) | /modular_courses/modular_courses/:modular_course_id/modular_enrollments?... |
| POST | ModularEnrollments: create | /modular_courses/enrollments/:enrollment_id/modular_enrollments |
| PUT | ModularEnrollments: update | /modular_courses/enrollments/:enrollment_id/modular_enrollments/:id |
| GET | ModularReservationPortalConfig: show (by school) | /modular_courses/schools/:school_id/modular_reservation_portal_config |
| POST | ModularReservationPortalConfig: create | /modular_courses/schools/:school_id/modular_reservation_portal_config |
| GET | ModularGrades: list (byCourse) | /modular_courses/modular_courses/:modular_course_id/modular_grades?filters |
| GET | ModularGrades: list (byLecture) | /modular_courses/modular_reservation_lectures/:modular_reservation_lecture_id/modular_grades?filters |
| GET | ModularGrades: list (byCourseAndStudent) | /modular_courses/modular_courses/:modular_course_id/students/:student_id/modular_grades?filters |
| POST | modularGrades: create/edit | /modular_courses/modular_reservation_lectures/:modular_reservation_lecture_id/modular_grades |
| POST | modularReservationProfessorLectures: create | /modular_courses/modular_reservation_professor_slots/:modular_reservation_professor_slot_id/modular_reservation_professor_lectures |
| PUT | modularReservationProfessorLectures: edit | /modular_courses/modular_reservation_professor_lectures/:id |
| GET | modularReservationProfessorLectures: List | /modular_courses/modular_reservation_lectures/:modular_reservation_lecture_id/modular_reservation_professor_lectures |

---

## /openpay

| Method | Name | Path |
|---|---|---|
| POST | OpenpayPaymentIntent: create | /openpay/openpay_payment_intents |
| GET | OpenpayPayments: show | /openpay/openpay_payments/:id?id=... |
| GET | OpenpayPaymentIntent: show | /openpay/openpay_payment_intents/:id |

---

## /pricing

| Method | Name | Path |
|---|---|---|
| GET | ProductSubscriptions: list | /pricing/product_subscriptions?filters=active |
| GET | Subscriptions: list | /pricing/subscriptions |
| GET | SubscriptionInvoices: list | /pricing/subscription_invoices |
| GET | SubscriptionInvoices: show | /pricing/subscription_invoices/:id |
| GET | SubscriptionInvoices: download | /pricing/subscription_invoices/:id/download?file_id={{subscription_invoice_file_id}} |

---

## /professor_reviews

Professor reviews, categories, scores, and term setup.

| Method | Name | Path |
|---|---|---|
| PUT | ProfessorReviewTermSetup: update (by term) | /professor_reviews/terms/:term_id/professor_review_term_setup |
| GET | ProfessorReviewTermSetup: show (by term) | /professor_reviews/terms/:term_id/professor_review_term_setup |
| GET | ProfessorReviewTermSetup: show | /professor_reviews/professor_review_term_setup |
| PUT | ProfessorReviewSetup: update | /professor_reviews/professor_review_setup |
| GET | ProfessorReviewSetup: show | /professor_reviews/professor_review_term_setup |
| POST | ProfessorReviewCategory: create (by_school) | /professor_reviews/schools/:school_id/professor_review_categories |
| PUT | ProfessorReviewCategory: update | /professor_reviews/professor_review_categories/67 |
| DELETE | ProfessorReviewCategory: delete | /professor_reviews/professor_review_categories/:id |
| GET | ProfessorReviewCategory: index | /professor_reviews/professor_review_categories |
| POST | ProfessorReview: create (by_course) | /professor_reviews/courses/:course_id/professor_reviews |
| PUT | ProfessorReview: update | /professor_reviews/professor_reviews/:id |
| GET | ProfessorReview: pending_courses | /professor_reviews/professor_reviews/pending_courses |
| GET | ProfessorReview: index (by_professor) | /professor_reviews/professors/:professor_id/professor_reviews |
| GET | ProfessorReview: index (by_professor) CSV | /professor_reviews/professors/:professor_id/professor_reviews.csv |
| GET | ProfessorReview: index (by_course) | /professor_reviews/courses/:course_id/professor_reviews?include_fields=category_reviews |
| GET | ProfessorReview: index (by_course) CSV | /professor_reviews/courses/:course_id/professor_reviews.csv |
| GET | ProfessorReview: index | /professor_reviews/professor_reviews?include_fields=category_reviews&sort_by=relevance:desc |
| GET | ProfessorReview: index CSV | /professor_reviews/professor_reviews.csv |
| GET | ProfessorReviewScores: index | /professor_reviews/terms/:term_id/professor_review_scores?filters=status=1 |
| GET | ProfessorReviewScore: index CSV | /professor_reviews/terms/:term_id/professor_review_scores.csv?filters=status=1 |
| PUT | ProfessorReview: update all | /professor_reviews/professors/:professor_id/professor_reviews/update_status?status=1 |

---

## /provisioning

Users, permissions, admin roles, whatsapp users/credits, provisioning logs, and applicant accounts.

| Method | Name | Path |
|---|---|---|
| POST | ApplicantAccount: create | /provisioning/applicant_accounts |
| POST | FacebookAccount: destroy callback | /provisioning/facebook_account/destroy_callback |
| GET | UsersSummaries: list | /provisioning/users_summaries?filters=active_term |
| GET | User: ping | (no URL) |
| GET | ProvisioningLog: show | /provisioning/groups/:group_id/provisioning_log |
| GET | ProvisioningLog: PDF | /provisioning/groups/:group_id/provisioning_log.pdf |

### /provisioning/admin_roles

| Method | Name | Path |
|---|---|---|
| GET | AdminRoles: list | /provisioning/admin_roles |
| GET | AdminRoles: show | /provisioning/admin_roles/:id |
| POST | AdminRoles: create | /provisioning/admin_roles |
| PUT | AdminRoles: update | /provisioning/admin_roles/:id |

### /provisioning/mobile_users

| Method | Name | Path |
|---|---|---|
| GET | MobileUsers: show | /provisioning/mobile_user |

### /provisioning/permissions

| Method | Name | Path |
|---|---|---|
| GET | Permissions: list (me) | /provisioning/permissions |
| GET | Permissions: list (by administrator) | /provisioning/administrators/:administrator_id/permissions |
| POST | Permissions: create (by administrator) | /provisioning/administrators/:administrator_id/permissions |
| PUT | Permissions: update (by administrator) | /provisioning/administrators/:administrator_id/permissions/:id |
| DELETE | Permissions: destroy (by administrator) | /provisioning/administrators/:administrator_id/permissions/:id |

### /provisioning/users

| Method | Name | Path |
|---|---|---|
| POST | User: create (by contactable) | /provisioning/:contactable_type/:contactable_id/user |
| POST | Users: create emails/restart passwords | /provisioning/groups/:group_id/users |
| PUT | User: udpate (by contactable) | /provisioning/:contactable_type/:contactable_id/user |
| DELETE | User: destroy (by contactable) | /provisioning/:contactable_type/:contactable_id/user?keep_vendor=true |
| DELETE | User: destroy recovery phone (by contactable) | /provisioning/:contactable_type/:contactable_id/user/recovery_phone |
| GET | User: suggestions | /provisioning/:contactable_type/:contactable_id/user/suggestions |
| PATCH | User: reset-password (by contactable) | /provisioning/:contactable_type/:contactable_id/user/reset_password |
| PATCH | User: supplant (by contactable) | /provisioning/:contactable_type/:contactable_id/user/supplant |

### /provisioning/whatsapp_users

| Method | Name | Path |
|---|---|---|
| GET | WhatsappUsers: list | /provisioning/whatsapp_users |
| GET | WhatsappUsers: list (by student) | /provisioning/students/:student_id/whatsapp_users |
| POST | WhatsappUsers: create | /provisioning/whatsapp_users |
| PUT | WhatsappUsers: confirm | /provisioning/whatsapp_users/:id/confirm |
| PUT | WhatsappUsers: toggle_mute | /provisioning/whatsapp_users/:id/toggle_mute |
| DELETE | WhatsappUsers: delete | /provisioning/whatsapp_users/:id |

### /provisioning/whatsapp_credits

| Method | Name | Path |
|---|---|---|
| GET | WhatsappCredits: list | /provisioning/whatsapp_credits |
| GET | WhatsappCredits: list (by school) | /provisioning/schools/:school_id/whatsapp_credits?filters=available |
| POST | WhatsappCredits: create | /provisioning/whatsapp_credits |

---

## /service

Async services for external integrations.

| Method | Name | Path |
|---|---|---|
| POST | Async: mexpress | /service/mexpress |
| POST | Async: openpay | (hardcoded: https://app.saeko.io/api/v1/service/openpay) |
| POST | Async: sftp | /service/sftp |
| POST | Async: sns | /service/sns |
| GET | Async: whatsapp | /service/whatsapp |

---

## /sep

SEP (Secretaría de Educación Pública) levels and schools.

| Method | Name | Path |
|---|---|---|
| GET | SepLevels: list | /sep/sep_levels |
| GET | SepSchools: list | /sep/sep_schools?filters=level={{sep_level_id}};state_id={{state_id}}&query=Continental |
| GET | SepSchool: show | /sep/sep_schools/:id?include_fields=city_name,state_name |
| POST | SepSchool: create | /sep/sep_schools |

---

## /scheduling

Lectures, attendance logs, absences, weekly lectures, gate access, visitor logs, and employee logs.

| Method | Name | Path |
|---|---|---|
| GET | Absence_logs: show | /scheduling/terms/:id/absence_logs |
| GET | Absence: list (by activity) | /scheduling/activities/:id/absences |
| GET | Absences: list (by course) | /scheduling/courses/:course_id/absences?include_fields=over_limit |
| GET | Absence: list (by enrollment) | /scheduling/enrollments/:enrollment_id/absences |
| GET | AbsenceLog: list | /scheduling/attendance_logs?include_fields=lecture_id&filters |
| GET | AttendanceLogs: list | /scheduling/attendance_logs?filters=latest&include_fields=lecture_id |
| GET | AttendanceLogs: list (by school) | /scheduling/schools/:school_id/attendance_logs?filters=latest |
| GET | AttendanceLogs: list (by lecture) | /scheduling/lectures/:lecture_id/attendance_logs?filters=latest&include_fields=absence_code |
| GET | AttendanceLogs: show | /scheduling/attendance_logs |
| POST | AttendanceLogs: create (by lecture) | /scheduling/lectures/:lecture_id/attendance_logs?mark_as_checked=true |
| POST | GateAccessLog: create | /scheduling/gate_access_logs |
| POST | GoogleCalendarEvent: create (by course) | /scheduling/courses/:course_id/google_calendar_event |
| GET | Lectures: list | /scheduling/lectures?start_date=2020-11-20&end_date=2020-11-27 |
| GET | Lectures: list (by group_id) | /scheduling/groups/:group_id/lectures?start_date=2020-06-01&limit=2&order=ASC&cursor=26068270449832 |
| GET | Lectures: list (by student) | /scheduling/students/:student_id/lectures?start_date=2023-03-01&end_date=2023-03-01&include_fields=student_attendance_log |
| GET | Lectures: list (by course) | /scheduling/courses/:courses_id/lectures?limit=10&order=desc |
| GET | Lectures: list (by professor) | /scheduling/professors/:professor_id/lectures?limit=3&order=ASC&filters=unchecked&start_date=2020-05-04&end_date=2020-05-08 |
| GET | Lectures: show | /scheduling/lectures/:id |
| PUT | Lectures: update | /scheduling/lectures/:id |
| PUT | Lectures: update (by student) | /scheduling/students/:student_id/lectures/:id |
| GET | VisitorLogs: list (by school) | /scheduling/schools/:school_id/visitor_logs |
| GET | WeeklyLectures: list (by enrollment) | /scheduling/enrollments/:enrollment_id/weekly_lectures |
| GET | WeeklyLecture: list (by professor) | /scheduling/professors/:professor_id/weekly_lectures?filters=term_id=61336,61334,61328 |
| GET | WeeklySchedule: list (by term) | /scheduling/terms/:term_id/weekly_schedule.pdf |
| GET | WeeklyLectures: list (by group) | /scheduling/groups/:group_id/weekly_lectures?include_fields=custom_dates |
| GET | WeeklyLectures: list (by group) PDF temp | /scheduling/groups/:group_id/weekly_lectures?include_fields=custom_dates |
| POST | WeeklyLectures: create (multiple by group) | /scheduling/groups/:group_id/weekly_lectures |
| DELETE | WeeklyLectures: destroy (by group) | /scheduling/groups/:group_id/weekly_lectures/:id |
| POST | WeeklyLectures: create (by group) | /scheduling/groups/:group_id/weekly_lectures |
| GET | GateAccessLog: list | /scheduling/gate_access_logs?filters=date_range=2023-07-01,2023-07-30&limit=200&offset=&summary_students=true&summary_stats=true&sort_by=recorded_at:DESC; |
| GET | AttendanceSheet: PDF (by course) | /scheduling/courses/:course_id/attendance_sheet.pdf?mes=Agosto&fecha=2023-08-04 |
| GET | Groups: monthly_attendance PDF | (no URL) |
| GET | Professors: lecture_status_summary (by school) | /scheduling/schools/:school_id/professors/lecture_status_summary?... |
| GET | Enrollments: absence_summary (by school) Copy | /scheduling/terms/:term_id/enrollments/absence_summary |
| GET | Professors: lecture_status_summary (by school) CSV | /scheduling/schools/:school_id/professors/lecture_status_summary.csv?... |
| POST | EmployeeLogs: create | /scheduling/employee_logs |
| GET | EmployeeLogs: qr_token | /scheduling/schools/:school_id/employee_logs/qr_token?session=123123 |

---

## /scholarship

Scholarship types and service areas.

| Method | Name | Path |
|---|---|---|
| GET | ScholarshipTypes: list (by name) | /scholarships/scholarship_types |
| GET | ScholarshipServiceAreas: list (by name) | /scholarships/scholarship_service_areas |
| POST | ScholarshipTypes: create | /scholarships/scholarship_types/ |
| POST | ScholarshipTypes: merge | /scholarships/scholarship_types/:id/merge |
| DELETE | ScholarshipTypes: delete (by type_id) | /scholarships/scholarship_types/:id |
| POST | ScholarshipServiceAreas: create | /scholarships/scholarship_service_areas |
| POST | ScholarshipServiceAreas: merge | /scholarships/scholarship_service_areas/:id/merge |
| DELETE | ScholarshipServiceAreas: destroy (by area_id) | /scholarships/scholarship_service_areas/:id |
| PUT | ScholarshipTypes: update | /scholarships/scholarship_types/:id |
| PUT | ScholarshipServiceAreas: update | /scholarships/scholarship_service_areas/:id |

---

## /stats

Buckets, aggregation logs, student results, school reports, and grade averages.

| Method | Name | Path |
|---|---|---|
| GET | Buckets: list (StudentResults) | /stats/buckets?include_fields=count,grade,grade_sum,grade_count&aggregation_name=GradeAveragesAggregator&filters=... |
| GET | SimpleBuckets: index (Enrollments) | /stats/simple_buckets?filters=term_id={{term_id}}; program_id={{program_id}};grade_level=*&include_fields=active,pending,enrolled,completed,cancelled,suspended,graduated,applicant,in_pro... |
| GET | SimpleBuckets: index (EnrolledCourses) | /stats/simple_buckets?filters=term_id={{term_id}};program_id=*&include_fields=passed&aggregator=enrolled_courses |
| GET | AggregationLogs: list (by term) | /stats/terms/:term_id/aggregation_logs?filters=name=StudentResultsAggregator |
| GET | StudentResults: active_groups (by term) | /stats/terms/:term_id/student_results/active_groups.xlsx |
| GET | StudentResults: passed_failed (by term) | /stats/terms/:term_id/student_results/passed_failed.xlsx |
| GET | GradingResults: active_subjects (by term) | /stats/terms/:term_id/grading_results/active_subjects.xlsx |
| GET | GradeAverages: grade_level_averages | /stats/terms/:term_id/grade_averages/grade_level_averages.xlsx |
| GET | SchoolReports: export_911_7g (by term) | /stats/terms/:term_id/school_reports/export_911_7g.pdf?... |
| POST | SchoolReports: export_911 (by term) | /stats/terms/:term_id/school_reports/export_911?... |
| POST | Students: groups_report (by term) | /stats/terms/:term_id/students/groups_report?include_leaves=true |
| POST | Students: leaves_report (by term) | /stats/terms/:term_id/students/leaves_report |
| POST | Students: grades_report (by term) | /stats/terms/:term_id/students/grades_report |
| POST | Students: grade_level_averages (by term) | /stats/terms/:term_id/students/grade_level_averages |
| POST | Students: course_grades_report (by term) | /stats/terms/:term_id/students/course_grades_report |
| POST | Students: subject_averages_report (by term) | /stats/terms/:term_id/students/subject_averages_report |
| POST | Students: group_pass_fail_report (by term) | /stats/terms/:term_id/students/group_pass_fail_report?with_final_ordinary_grade=true |

---

## /sofiaxt

Sofiaxt sync logs and token.

| Method | Name | Path |
|---|---|---|
| GET | SofiaxtToken: show | /sofiaxt/sofiaxt_token |
| GET | SofiaxtSyncLog: show (by period) | /sofiaxt/periods/:period_id/sofiaxt_sync_log |
| GET | SofiaxtSyncLog: list (by course) | /sofiaxt/courses/:course_id/sofiaxt_sync_logs |
| POST | SofiaxtSyncLog: create (by period) | /sofiaxt/periods/:period_id/sofiaxt_sync_log |
| GET | SofiaxtSyncLog: show (by activity) | /sofiaxt/activities/:activity_id/sofiaxt_sync_log |
| POST | SofiaxtSyncLog: create (by activity) | /sofiaxt/activities/:activity_id/sofiaxt_sync_log |
| GET | SofiaxtSyncLog: show (by term) | /sofiaxt/terms/:tem_id/sofiaxt_sync_log |
| POST | SofiaxtSyncLog: create (by term) | /sofiaxt/terms/:tem_id/sofiaxt_sync_log |

---

## /stripe

Stripe customer, payment intents, and setup intents.

| Method | Name | Path |
|---|---|---|
| GET | StripeCustomer: show (me) | /stripe/stripe_customer |
| PUT | StripeCustomer: update (me) | /stripe/stripe_customer |
| POST | StripePaymentIntent: create | /stripe/stripe_payment_intents |
| POST | StripePaymentIntent: create (by student) | /stripe/students/:student_id/stripe_payment_intents |
| PUT | StripePaymentIntent: update | /stripe/stripe_payment_intents/:id |
| PUT | StripePaymentIntent: update (by student) | /stripe/students/:student_id/stripe_payment_intents/:id |
| POST | StripeSetupIntent: create | /stripe/stripe_setup_intents |

---

## /transfers

Transfers, transfer documents, equivalent subjects/programs, and transfer credits.

| Method | Name | Path |
|---|---|---|
| GET | Transfers: index (by student) | /transfers/students/:student_id/transfers?include_fields=documents |
| GET | Transfer: show (by enrollment) | /transfers/enrollments/:enrollment_id/transfer |
| POST | Transfers: create (by student) | /transfers/students/:student_id/transfers |
| PUT | Transfers: update (by enrollment) | /transfers/enrollments/:enrollment_id/transfer |
| POST | TransferDocument: create (by transfer) | /transfers/transfers/:transfer_id/transfer_documents |
| GET | TransferDocuments: list (by transfer) | /transfers/transfers/:transfer_id/transfer_documents |
| PUT | TransferDocument: update (by transfer) | /transfers/transfers/:transfer_id/transfer_documents/:id |
| PUT | TransferDocument: upload | {{transfer_document_upload_url}} |
| DELETE | TransferDocument: destroy (by transfer) | /transfers/transfers/:transfer_id/transfer_documents/:id |
| GET | TransferGradeLevels: list (by transfer) | /transfers/transfers/:transfer_id/transfer_grade_levels |
| POST | TransferGradeLevels: create (by transfer) | /transfers/transfers/:transfer_id/transfer_grade_levels |
| GET | TransferCredits: list | /transfers/transfer_credits |
| POST | TransferCredits: create | /transfers/transfer_credits |
| GET | EquivalentPrograms: list (by sep_schools) | /transfers/sep_schools/:sep_school_id/equivalent_programs?filters=program_id=200 |
| GET | EquivalentPrograms: list (by origin program) | /transfers/origin_programs/:origin_program_id/equivalent_programs |
| GET | EquivalentSubjects: list (by equivalent_programs) | /transfers/equivalent_programs/:equivalent_program_id/equivalent_subjects |
| GET | EquivalentSubjects: list (by subject) | /transfers/subjects/:subject_id/equivalent_subjects |
| POST | EquivalentSubjects: create (by subject) | /transfers/subjects/:subject_id/equivalent_subjects |
| GET | New Request | (no URL) |
| GET | SelectableSubjects: list (by subject) | /transfers/subjects/:subject_id/selectable_subjects |

---

## /tutorings

Tutorings, enrollment tutorings, and professor stats.

| Method | Name | Path |
|---|---|---|
| POST | Tutorings: create (by term) | /tutorings/terms/:term_id/tutorings |
| PUT | Tutorings: update | /tutorings/tutorings/:id |
| GET | Tutorings: list | /tutorings/tutorings |
| GET | Tutorings: show | /tutorings/tutorings/:id?summary_enrollments=true&summary_employees=true |
| GET | Tutorings: list ( by term ) | /tutorings/terms/:term_id/tutorings |
| GET | Tutorings: list ( by enrollment ) | /tutorings/enrollments/:enrollment_id/tutorings |
| GET | Enrollments: list | /tutorings/enrollments?filters=tutorings(tutoring_date=2023-02-15) |
| GET | Enrollments: list ( by term ) | /tutorings/terms/:term_id/enrollments |
| GET | Professors: tutoring summary stats (by term) | /tutorings/terms/:term_id/professors/:id/summary_stats |
| GET | Professors: tutoring summary stats (by term) | /tutorings/terms/:term_id/professor/summary_stats |
| GET | Professors: tutoring summary stats | /tutorings/professor/summary_stats |
| GET | Professors: tutoring summary stats by professor | /tutorings/professors/:id/summary_stats |
| GET | Enrollments: list ( by courses over limit) | /tutorings/terms/:term_id/enrollments/courses_over_limit.csv |

---

## /workflow

| Method | Name | Path |
|---|---|---|
| POST | WorkflowEvent: create (by workflow) | /workflow/workflows/:workflow_id/workflow_events |

---

## Common Patterns

### URL Parameters
- `:id` - Resource ID
- `:student_id`, `:enrollment_id`, `:term_id`, `:school_id`, etc. - Parent resource IDs
- `{{variable}}` - Postman/environment variables

### Query Parameters
- `include_fields=` - Specify additional fields to include in response
- `filters=` - Filter results (semicolon-separated)
- `sort_by=` - Sort results (field:direction)
- `limit=` / `offset=` - Pagination
- `cursor=` - Cursor-based pagination
- `dry_run=true` - Preview operation without executing
- `summary_stats=true` - Include summary statistics

### Response Formats
- JSON (default)
- PDF: `.pdf` endpoints
- XLSX: `.xlsx` endpoints
- CSV: `.csv` endpoints
- ZIP: `.zip` endpoints

### Naming Convention
Endpoints follow the pattern: `ResourceName: action (scope)`
- `list` - GET collection
- `show` - GET single resource
- `create` - POST new resource
- `update` - PUT/PATCH existing resource
- `destroy`/`delete` - DELETE resource
- `export` - Download data export